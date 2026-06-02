from . import signature
import lightrdf
from . import taxonomy
from collections import defaultdict
import random
import argparse
import time

total_start = time.perf_counter()

arg_parser = argparse.ArgumentParser(prog="extract.py")

_ = arg_parser.add_argument("--samples", type=int, help="number of samples for each Concept_Name-Extension")

args = arg_parser.parse_args()

domain = set()
sig = signature.Signature()
sig.write_custom_schema("custom-schema.owl")

all_individuals_for_concept = defaultdict(set)

print("Searching for all sublcasses")
start = time.perf_counter()

# Searching for all subclasses of all concept_names
concept_pool = {
    c: taxonomy.collect_subclasses(c) | {c}
    for c in sig.concept_names
}

all_concepts = set().union(*concept_pool.values())
target_pool = concept_pool[sig.target_concept]

# Searching for the most general class for our target, so that the individual will stay in our fragment
target_general_class = taxonomy.determine_most_general_class(sig.target_concept)

print(f"Done ({time.perf_counter() - start:.2f}s)")

rdf_parser = lightrdf.Parser()

f_full = open("result.nt", "w")
f_no_target = open("result_without_target.nt", "w")

written = set()
def write_triple(triple, write_in_both=True):
    if triple in written:
        return
    written.add(triple)

    f_full.write("{} {} {} .\n".format(*triple))
    if write_in_both:
        f_no_target.write("{} {} {} .\n".format(*triple))

# Part 1: SCHEMA
print("Processing yago-schema.ttl")
start = time.perf_counter()
for subj, pred, obj in rdf_parser.parse(sig.SCHEMA, base_iri=None):
    if not ("shacl" in pred or "shacl" in obj):
        write_triple((subj,pred,obj))
print(f"Done ({time.perf_counter() - start:.2f}s)")

# Part 2: TAXONOMY
print("Processing yago-taxonomy.ttl")
start = time.perf_counter()
for subj, pred, obj in rdf_parser.parse(sig.TAXONOMY, base_iri=None):
    if not ("shacl" in pred or "shacl" in obj):
        if (subj in target_pool or obj in target_pool):
            write_triple((subj,pred,obj), False)
        else:
            write_triple((subj,pred,obj))
print(f"Done ({time.perf_counter() - start:.2f}s)")

# Part 3: FACTS
# 3.1: First Pass: Gather all individuals and then take samples of them
print("Processing yago-facts.ttl == First Pass: Gather Samples")
start = time.perf_counter()
for subj, pred, obj in rdf_parser.parse(sig.FACTS, base_iri=None):
    if pred != sig.TYPE:
        continue

    for c in sig.domain_signature:
        if (obj in concept_pool[c]):
            all_individuals_for_concept[c].add(subj)

sampled = dict()
if args.samples:
    sampled = {
    c: set(
        random.sample(
            list(indivs),
            min(args.samples, len(indivs))
        )
    )
    for c, indivs in all_individuals_for_concept.items()
    }
else:
    sampled = all_individuals_for_concept


domain = set().union(*sampled.values())

print(f"Done ({time.perf_counter() - start:.2f}s)")

# 3.2: Gather neighbors of our sampled domain
print("Processing yago-facts.ttl == Second Pass : Gather Neighbors")
start = time.perf_counter()

neighbors = set()

for subj, pred, obj in rdf_parser.parse(sig.FACTS, base_iri=None):

    if pred not in sig.role_names:
        continue

    if subj in domain:
        neighbors.add(obj)

    if obj in domain:
        neighbors.add(subj)

domain |= neighbors

print(f"Done ({time.perf_counter() - start:.2f}s)")

# 3.3: Write the triples to both .nt files
print("Processing yago-facts.ttl == Third Pass: Write triples to both result files")
start = time.perf_counter()
for subj, pred, obj in rdf_parser.parse(sig.FACTS, base_iri=None):

    if pred in sig.role_names:

        if subj in domain and obj in domain:
            write_triple((subj, pred, obj), True)

    elif pred == sig.TYPE:
        if subj not in domain:
            continue

        if obj in target_pool:
            write_triple((subj, pred, sig.target_concept), False)
            write_triple((subj, pred, target_general_class), True)
        else:
            for c in sig.concept_names:
                if obj in concept_pool[c]:
                    write_triple((subj, pred, c), True)
                    #break

print(f"Done ({time.perf_counter() - start:.2f}s)")

f_full.close()
f_no_target.close()

print(f"Finished extraction in {time.perf_counter() - total_start:.2f}s")
print(f"Domain size: {len(domain)}")
print(f"Neighbors added: {len(neighbors)}")
print(f"Written triples: {len(written)}")
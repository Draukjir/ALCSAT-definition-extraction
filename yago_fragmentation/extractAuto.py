import json
import time
from collections import Counter, defaultdict

import lightrdf

from . import signature, taxonomy


def write_custom_schema(concept_names, role_names, out_file="custom-schema.owl"):

    with open(out_file, "w", encoding="utf-8") as f:
        f.write("""<?xml version="1.0"?>\n""")

        f.write("""<rdf:RDF
 xmlns="http://www.w3.org/2002/07/owl#"
 xml:base="http://www.w3.org/2002/07/owl"
 xmlns:owl="http://www.w3.org/2002/07/owl#"
 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">\n\n""")

        f.write("<Ontology/>\n\n")

        f.write("<!-- Classes -->\n")
        for c in sorted(concept_names):
            f.write(f'<Class rdf:about="{c.strip("<>")}"/>\n')

        f.write("\n<!-- Object Properties -->\n")
        for r in sorted(role_names):
            f.write(f'<ObjectProperty rdf:about="{r.strip("<>")}"/>\n')

        f.write("\n</rdf:RDF>\n")


def clean_name(uri):
    return (
        uri.replace("<http://yago-knowledge.org/resource/", "")
        .replace("<http://schema.org/", "")
        .replace(">", "")
    )


def write_triple(triple):
    if triple in written:
        return
    written.add(triple)

    f_full.write("{} {} {} .\n".format(*triple))


def print_result(
    subj_type: str,
    role_name: str,
    obj_type: str,
    count: int,
    coverage: float,
    recall: float,
    valid: bool,
):
    s_type = clean_name(subj_type)
    r_name = clean_name(role_name)
    o_type = clean_name(obj_type)
    cov = "NOT CALCULATED" if coverage == -1 else f"{coverage:.2f}"
    rec = "NOT CALCULATED" if recall == -1 else f"{recall:.2f}"

    result = "yes" if valid else "no"

    print("-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -")
    print(f"Triple:         ({s_type}, {r_name}, {o_type})")
    print(f"Count:          {count}")
    print(f"Coverage:       {cov}")
    print(f"Recall:         {rec}")
    print(f"Valid?          {result}")
    print("-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -")


parser = lightrdf.Parser()
sig = signature.Signature()

written = set()

sig_subclasses = {c: taxonomy.collect_subclasses(c) | {c} for c in sig.domain_signature}

sig_extensions = {c: set() for c in sig.domain_signature}

sig_concepts = set().union(*sig_subclasses.values())

individual_types = defaultdict(set)

sig_domain = set()

role_counts = Counter()

role_patterns: defaultdict[str, Counter] = defaultdict(Counter)

role_patterns_outgoing: defaultdict[tuple[str, str], Counter] = defaultdict(Counter)

role_patterns_incoming: defaultdict[tuple[str, str], Counter] = defaultdict(Counter)

pre_domain = set()

pre_domain_indiv_types = defaultdict(set)

valid_roles = set()

MIN_COVERAGE = 0.05

MIN_RECALL = 0.05

MIN_COUNT = 100

all_role_names = set()

all_concept_names = set(sig.domain_signature)

finalDomain = set()

f_full = open("result_auto.nt", "w")

print(
    f"Starting Extraction with MIN_COUNT = {MIN_COUNT}, MIN_COVERAGE = {MIN_COVERAGE}, MIN_RECALL = {MIN_RECALL}"
)

# Part 1: SCHEMA
print("Processing yago-schema.ttl")
start = time.perf_counter()
for subj, pred, obj in parser.parse(sig.SCHEMA):
    if not ("shacl" in pred or "shacl" in obj):
        write_triple((subj, pred, obj))
print(f"Done ({time.perf_counter() - start:.2f}s)")

# Part 2: TAXONOMY
print("Processing yago-taxonomy.ttl")
start = time.perf_counter()
for subj, pred, obj in parser.parse(sig.TAXONOMY):
    if not ("shacl" in pred or "shacl" in obj):
        write_triple((subj, pred, obj))
print(f"Done ({time.perf_counter() - start:.2f}s)")

# Part 3: FACTS
print(
    "Processing yago-facts.ttl == 1st PASS: Collecting Individuals of Domain Signature"
)
start = time.perf_counter()

for subj, pred, obj in parser.parse(sig.FACTS):
    if pred != sig.TYPE:
        continue

    if obj not in sig_concepts:
        continue

    for concept_name, subclasses in sig_subclasses.items():
        if obj in subclasses:
            individual_types[subj].add(concept_name)
            sig_extensions[concept_name].add(subj)
            sig_domain.add(subj)

print(f"Done ({time.perf_counter() - start:.2f}s)")
print(f"Collected {len(individual_types)} individuals")


print(
    "Processing yago-facts.ttl == 2nd PASS: Collecting Role-triples of Domain Signature"
)
start = time.perf_counter()

for subj, pred, obj in parser.parse(sig.FACTS):
    if (
        "shacl" in pred
        or "shacl" in obj
        or pred == sig.TYPE
        or not (subj in sig_domain or obj in sig_domain)
        or pred in sig.unwanted_roles
    ):
        continue

    role_counts[pred] += 1

    if subj in sig_domain and obj in sig_domain:
        for subj_type in individual_types[subj]:
            for obj_type in individual_types[obj]:
                role_patterns[pred][(subj_type, obj_type)] += 1
    elif subj in sig_domain and obj not in sig_domain:
        source_types = individual_types.get(subj)
        for source in source_types:
            role_patterns_outgoing[(source, pred)][obj] += 1
            pre_domain.add(obj)
    elif subj not in sig_domain and obj in sig_domain:
        target_types = individual_types.get(obj)
        for target in target_types:
            role_patterns_incoming[(pred, target)][subj] += 1
            pre_domain.add(subj)

print(f"Done ({time.perf_counter() - start:.2f}s)")

print("Processing yago-facts.ttl == 3rd PASS: Collecting Extensions of pre_domain")
start = time.perf_counter()
for subj, pred, obj in parser.parse(sig.FACTS):
    if pred != sig.TYPE or subj not in pre_domain:
        continue

    pre_domain_indiv_types[subj].add(obj)

print(f"Done ({time.perf_counter() - start:.2f}s)")

print("Analysing incoming and outgoing roles")
start = time.perf_counter()

for (subj_type, role), obj_counts in role_patterns_outgoing.items():
    for indiv, edge_count in obj_counts.items():
        for indiv_type in pre_domain_indiv_types[indiv]:
            role_patterns[role][(subj_type, indiv_type)] += edge_count

for (role, obj_type), subj_counts in role_patterns_incoming.items():
    for indiv, edge_count in subj_counts.items():
        for indiv_type in pre_domain_indiv_types[indiv]:
            role_patterns[role][(indiv_type, obj_type)] += edge_count

print(f"Done ({time.perf_counter() - start:.2f}s)")


print("Analysing Role Patterns:")
for role, patterns in sorted(
    role_patterns.items(), key=lambda x: sum(x[1].values()), reverse=True
):
    print("\n")
    print(role)
    print("Total: ", role_counts[role])

    for (subj_type, obj_type), count in patterns.most_common():
        found_valid_pattern = False

        if count < MIN_COUNT:
            print_result(subj_type, role, obj_type, count, -1, -1, found_valid_pattern)
            break

        coverage = count / role_counts[role]

        if coverage >= MIN_COVERAGE:
            if subj_type in sig.domain_signature:
                len_subj_type = len(sig_extensions[subj_type])
                if len_subj_type != 0:
                    subj_type_recall = count / len_subj_type
                else:
                    subj_type_recall = 0

                if subj_type_recall >= MIN_RECALL:
                    found_valid_pattern = True

                    valid_roles.add((subj_type, role, obj_type))
                    all_role_names.add(role)
                    all_concept_names.add(obj_type)

                    print_result(
                        subj_type,
                        role,
                        obj_type,
                        count,
                        coverage,
                        subj_type_recall,
                        found_valid_pattern,
                    )
                    continue

            if obj_type in sig.domain_signature and not found_valid_pattern:
                len_obj_type = len(sig_extensions[obj_type])
                if len_obj_type != 0:
                    obj_type_recall = count / len_obj_type
                else:
                    obj_type_recall = 0

                if obj_type_recall >= MIN_RECALL:
                    found_valid_pattern = True

                    valid_roles.add((subj_type, role, obj_type))
                    all_role_names.add(role)
                    all_concept_names.add(subj_type)

                    print_result(
                        subj_type,
                        role,
                        obj_type,
                        count,
                        coverage,
                        obj_type_recall,
                        found_valid_pattern,
                    )
                else:
                    print_result(
                        subj_type,
                        role,
                        obj_type,
                        count,
                        coverage,
                        obj_type_recall,
                        found_valid_pattern,
                    )
            else:
                print_result(
                    subj_type,
                    role,
                    obj_type,
                    count,
                    coverage,
                    subj_type_recall,
                    found_valid_pattern,
                )


role_triple_count = 0
all_individual_types = defaultdict(set)
for indiv, types in individual_types.items():
    all_individual_types[indiv].update(types)
for indiv, types in pre_domain_indiv_types.items():
    all_individual_types[indiv].update(types)

print(
    "Processing yago-facts.ttl == 4th PASS writing role-triples to result_pattern_oriented.nt"
)
start = time.perf_counter()

for subj, pred, obj in parser.parse(sig.FACTS):
    if pred not in all_role_names:
        continue

    subj_types = all_individual_types.get(subj, set())

    obj_types = all_individual_types.get(obj, set())

    match_found = False
    for s_type in subj_types:
        for t_type in obj_types:
            if (s_type, pred, t_type) in valid_roles:
                match_found = True
                break
        if match_found:
            break

    if match_found:
        write_triple((subj, pred, obj))
        role_triple_count += 1
        finalDomain.add(subj)
        finalDomain.add(obj)

print(f"Done ({time.perf_counter() - start:.2f}s)")
print(f"Extracted {role_triple_count} role triples.")
print(f"Domain size after collecting roles: {len(finalDomain)} Individuals.")

count_indiv_concept_name = Counter()

print("Writing type-triples to result_pattern_oriented.nt")
start = time.perf_counter()
type_triple_count = 0

for individual in all_individual_types:
    if individual in finalDomain:
        for concept_name in all_individual_types[individual]:
            if concept_name in all_concept_names:
                write_triple((individual, sig.TYPE, concept_name))
                type_triple_count += 1
                count_indiv_concept_name[concept_name] += 1

print(f"Done ({time.perf_counter() - start:.2f}s)")
print(f"Extracted {type_triple_count} Type-Triples")

f_full.close()

for concept_name, count in count_indiv_concept_name.most_common():
    print(f"{clean_name(concept_name)}: {count}")

write_custom_schema(concept_names=all_concept_names, role_names=all_role_names)

signature_data = {
    "concept_names": sorted(list(all_concept_names)),
    "role_names": sorted(list(all_role_names)),
}

with open("extracted_signature.json", "w", encoding="utf-8") as f_json:
    json.dump(signature_data, f_json, indent=4)

print("Extracted signature saved to extracted_signature.json")
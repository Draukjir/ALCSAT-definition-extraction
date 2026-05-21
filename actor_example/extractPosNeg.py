import lightrdf
import signature
import random
import argparse

arg_parser = argparse.ArgumentParser(prog="extractPosNeg.py")

_ = arg_parser.add_argument("--samples", type=int, help="number of positive/negative samples")

args = arg_parser.parse_args()

positives = set()
all_individuals = set()

rdf_parser = lightrdf.Parser()

sig = signature.Signature()

for triple in rdf_parser.parse("yago-fragment.owl", base_iri=None):
    subj, pred, obj = triple

    if pred == sig.TYPE and obj in sig.concept_names:
        all_individuals.add(subj.strip("<>"))

        if obj == sig.target_concept:
            positives.add(subj.strip("<>"))

negatives = all_individuals - positives

if args.samples:
    positives = random.sample(sorted(positives), min(args.samples, len(positives)))
    negatives = random.sample(sorted(negatives), min(args.samples, len(negatives)))


with open("P.txt", "w") as f:
    for x in positives:
        f.write(x + "\n")

with open("N.txt", "w") as f:
    for x in negatives:
        f.write(x + "\n")
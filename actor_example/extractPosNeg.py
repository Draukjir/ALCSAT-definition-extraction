import lightrdf
import constants as c
import random
import argparse

parser = argparse.ArgumentParser(prog="spell_cli.py")

_ = parser.add_argument("--samples", type=int, help="number of positive/negative samples")

args = parser.parse_args()

positives = set()
all_individuals = set()

parser = lightrdf.Parser()

# Konzeptnamen / YAGO-Klassen
concept_names = {
    c.ACTOR,
    c.FILM_DIRECTOR,
    c.MOVIE
}

for triple in parser.parse("yago-fragment.owl", base_iri=None):
    subj, pred, obj = triple

    if pred == c.TYPE and obj in concept_names:
        all_individuals.add(subj.strip("<>"))

        if obj == c.ACTOR:
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
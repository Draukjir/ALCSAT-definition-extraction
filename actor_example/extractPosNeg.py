import lightrdf
import constants as c

positives = set()
all_individuals = set()

parser = lightrdf.Parser()

for triple in parser.parse("yago-fragment.owl", base_iri=None):
    subj, pred, obj = triple

    if pred == c.TYPE:
        all_individuals.add(subj)

        if obj == c.ACTOR:
            positives.add(subj)

negatives = all_individuals - positives

with open("P.txt", "w") as f:
    for x in positives:
        f.write(x + "\n")

with open("N.txt", "w") as f:
    for x in negatives:
        f.write(x + "\n")
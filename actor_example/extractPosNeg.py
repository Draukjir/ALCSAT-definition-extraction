import lightrdf
import constants as c

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

        if obj == c.FILM_ACTOR:
            positives.add(subj.strip("<>"))

negatives = all_individuals - positives

with open("P.txt", "w") as f:
    for x in positives:
        f.write(x + "\n")

with open("N.txt", "w") as f:
    for x in negatives:
        f.write(x + "\n")
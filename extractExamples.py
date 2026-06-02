import lightrdf
from yago_fragmentation import signature
import random

def main():
    sig = signature.Signature()
    extract_Examples(sig.target_concept, sig)

def extract_Examples(target_concept: str, sig: signature.Signature, samples: int = 100):

    positives = set()
    all_individuals = set()

    rdf_parser = lightrdf.Parser()

    sig = signature.Signature()

    fragment_file = "yago-fragment.owl"

    for triple in rdf_parser.parse(fragment_file, base_iri=None):
        subj, pred, obj = triple

        if pred == sig.TYPE and obj in sig.concept_names:
            all_individuals.add(subj.strip("<>"))

            if obj == target_concept:
                positives.add(subj.strip("<>"))

    negatives = all_individuals - positives

    if samples:
        positives = random.sample(sorted(positives), min(samples, len(positives)))
        negatives = random.sample(sorted(negatives), min(samples, len(negatives)))


    with open("P.txt", "w") as f:
        for x in positives:
            f.write(x + "\n")

    with open("N.txt", "w") as f:
        for x in negatives:
            f.write(x + "\n")

if __name__ == "__main__":
    main()
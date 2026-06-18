import lightrdf
from yago_fragmentation import signature
import random

def main():
    sig = signature.Signature()
    extract_Examples(sig.target_concept, sig)

def extract_Examples(target_concept: str, sig: signature.Signature, samples: int = 100, mode: str = "definition"):

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
        if mode == "definition":
            positives = random.sample(sorted(positives), min(samples, len(positives)))
            negatives = random.sample(sorted(negatives), min(samples, len(negatives)))
        elif mode == "upper_bound": # 20 / 80 ratio
            positives = random.sample(sorted(positives), min(samples * 0.2, len(positives)))
            negatives = random.sample(sorted(negatives), min(samples * 0.8, len(negatives)))
        elif mode == "lower_bound": # 80 / 20 ratio
            positives = random.sample(sorted(positives), min(samples * 0.8, len(positives)))
            negatives = random.sample(sorted(negatives), min(samples * 0.2, len(negatives)))
        else:
            print(f"[WARN] This Mode {mode} does not exist")

    with open("P.txt", "w") as f:
        for x in positives:
            f.write(x + "\n")

    with open("N.txt", "w") as f:
        for x in negatives:
            f.write(x + "\n")

if __name__ == "__main__":
    main()
import random
import sys
from collections import defaultdict

import lightrdf

from yago_fragmentation import signature


def main():
    sig = signature.Signature()
    extract_Examples(sig.target_concept, sig)


def extract_Examples(
    target_concept: str,
    sig: signature.Signature,
    samples: int = 100,
    mode: str = "definition",
    fragment_file: str = "yago-fragment.owl",
    only_focus: bool = False,
):
    print(f"Starting Example-Extraction for {target_concept} with mode = {mode}")
    
    example_concepts = set()
    if only_focus:
        example_concepts = sig.domain_signature
    else:
        example_concepts = sig.concept_names

    positives = set()
    all_individuals = set()

    rdf_parser = lightrdf.Parser()

    for triple in rdf_parser.parse(fragment_file, base_iri=None):
        subj, pred, obj = triple

        if pred == sig.TYPE and obj in example_concepts:
            all_individuals.add(subj.strip("<>"))

            if obj == target_concept:
                positives.add(subj.strip("<>"))

    negatives = all_individuals - positives

    if samples:
        if mode == "definition":
            min_size = min(len(positives), len(negatives), samples)
            print(f"Taking {min_size} sample Examples")
            
            positives = random.sample(sorted(positives), min_size)
            negatives = random.sample(sorted(negatives), min_size)
        else:
            print(f"[WARN] This Mode {mode} does not work with samples")
            sys.exit(1)
    else:
        if mode == "nec_crit":
            k = max(10, int(0.001 * len(negatives)))
            print(f"Necessary Criterion: {len(positives)} positive examples, {k} negative examples")
                        
            negatives = random.sample(sorted(negatives), k)
            # negatives = set()
        elif mode == "suf_crit":
            k = max(10, int(0.01 * len(positives)))
            print(f"Sufficient Criterion: {k} positive examples, {len(negatives)} negative examples")
            
            positives = random.sample(sorted(positives), k)
            # positives = set()

    with open("P.txt", "w") as f:
        for x in positives:
            f.write(x + "\n")

    with open("N.txt", "w") as f:
        for x in negatives:
            f.write(x + "\n")

if __name__ == "__main__":
    main()
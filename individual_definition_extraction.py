import random
import sys
import time

import lightrdf

from spell.fitting import mode, solve_incr
from spell.fitting_alc import OP, FittingALC
from spell.instance import ALCConcept
from spell.structures import Structure, ind, structure_from_owl
from yago_fragmentation import signature

LANGUAGES = ["el", "el_alcsat", "fl0", "ex-or", "all-or", "elu", "alc", "alcq"]
L_OP = {
    "el": [OP.EX, OP.AND],
    "el_alcsat": [OP.EX, OP.AND],
    "fl0": [OP.ALL, OP.AND],
    "ex-or": [OP.EX, OP.OR],
    "all-or": [OP.ALL, OP.OR],
    "elu": [OP.EX, OP.OR, OP.AND],
    "alc": [OP.ALL, OP.EX, OP.OR, OP.AND, OP.NEG],
    "alcq": [OP.ALL, OP.EX, OP.OR, OP.AND, OP.NEG, OP.LE, OP.GE],
    "alc_pos": [OP.EX, OP.ALL, OP.OR, OP.AND],
    "alc_no_all": [OP.EX, OP.OR, OP.AND, OP.NEG],
    "alc_pos_no_all": [OP.EX, OP.OR, OP.AND]
}


def clean_name(uri):
    return (
        uri.replace("<http://yago-knowledge.org/resource/", "")
        .replace("<http://schema.org/", "")
        .replace(">", "")
        .replace("http://yago-knowledge.org/resource/", "")
        .replace("http://schema.org/", "")
    )
    
def extract_examples_indiv_extraction(individual_uri,
                                      fragment_file,
                                      sig,
                                      samples = 100):
    print(f"Starting Example-Extraction for {clean_name(individual_uri)}:")
    
    all_individuals = set()
    
    rdf_parser = lightrdf.Parser()
    
    for s,p,o in rdf_parser.parse(fragment_file):
        if p == sig.TYPE and o in sig.concept_names:
            all_individuals.add(s.strip("<>"))
            
    print(len(all_individuals))
            
    all_individuals.remove(individual_uri.strip("<>"))
    
    all_individuals = random.sample(sorted(all_individuals), min(len(all_individuals), samples))
    
    with open("P.txt", "w") as f:
        f.write(individual_uri.strip("<>") + "\n")            
        
    with open("N.txt", "w") as f:
        for x in all_individuals:
            f.write(x+ "\n")
            
def load_examples(path: str, owlfile: str, A: Structure) -> list[int]:
    examples: list[int] = []
    with open(path, encoding="UTF-8") as file:
        for line in file.readlines():
            individual = line.rstrip()
            if individual not in A.indmap:
                print(
                    "[ERR] The {}-example {} does not seem to occur in {}".format(
                        path, individual, owlfile
                    )
                )
                sys.exit(1)
            examples.append(A.indmap[individual])

    return examples

def main():
    time_start = time.perf_counter()
    
    sig = signature.Signature()
    
    # OTHER SETTINGS
    individual_uri = "<http://yago-knowledge.org/resource/Stephen_King>"
    fragment_file = "fragment-sample-22-07.owl"
    samples = 35000
    
    # SETTINGS FOR ALC SAT
    language = "alc"
    inverse_roles = False
    feature_values = False
    max_thresholds = 10
    max_size = 12
    max_q = 2
    md = mode.exact
    timeout = 500
    workers =1
    exclude_atomic = []
    
    extract_examples_indiv_extraction(individual_uri, fragment_file, sig, samples)
            
    print("== Loading {}".format(fragment_file))
    A = structure_from_owl(fragment_file)

    P = load_examples("P.txt", fragment_file, A)
    N = load_examples("N.txt", fragment_file, A)
    
    time_parsed = time.perf_counter()

    print("== Starting incremental search search for fitting query")
    time_start_solve = time.perf_counter()
    
    training_accuracy = 0.0
    output_definition = None
    if language != "el":
        ops = L_OP[language]
        if inverse_roles:
            ops.append(OP.INV)
        if feature_values:
            ops.append(OP.DGEQ)
        f = FittingALC(
            A,
            max_size,
            P,
            N,
            op=frozenset(ops),
            workers=workers,
            max_q=max_q,
            max_thresholds=max_thresholds,
            exclude_atomic=exclude_atomic,
        )
        remaining_time = -1
        if timeout != -1:
            remaining_time = timeout - (time.perf_counter() - time_start)
        if md == mode.exact:
            training_accuracy, _, concept = f.solve_incr(max_size, timeout=remaining_time)
        elif md == "full_approx":
            print("Starting with solving")
            training_accuracy, _, output_definition = f.solve_incr_approx(
                max_size, timeout=remaining_time
            )  # _ _ 3 beste Konzept hier zurückgeben
        else:
            print(f"Mode {md} is only supported for SPELL.")
    else:
        _, res = solve_incr(A, P, N, md, timeout=timeout, max_size=max_size)

    time_solved = time.perf_counter()

    print(
        "== Took {:.2f}s for reading input and {:.3f}s for solving".format(
            time_parsed - time_start, time_solved - time_start_solve
        )
    )
    print("== Reached accurary (Training data) {:.4f}".format(training_accuracy))

    definition = ALCConcept.to_dl_concept(concept)
    
    print(f"{clean_name(individual_uri)} = {clean_name(definition)}")
if __name__ == "__main__":
    main()
import sys
import time

from spell.fitting import mode, solve_incr
from spell.fitting_alc import FittingALC, OP
from spell.structures import structure_from_owl, ind, Structure
from spell.instance import ALCConcept
from yago_fragmentation.taxonomy import collect_superclasses
from yago_fragmentation import signature
import copy

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


def compute_overall_accuracy(
    A: Structure, output_definition: ALCConcept, target_extension: set
) -> float:
    """Computes the overall accuracy for a given definition ans it's original target extension"""

    if output_definition == None:
        print("[ERR] The Definition is None!")
        sys.exit(1)
        
    TP = set()  # True Positives
    FN = set()  # False Negatives
    TN = set()  # True Negatives
    FP = set()  # False Positives

    for a in ind(A):
        if output_definition.mc(A, a):
            if a in target_extension:
                TP.add(a)
            else:
                FP.add(a)
        else:
            if a in target_extension:
                FN.add(a)
            else:
                TN.add(a)

    overall_accuracy = (len(TP) + len(TN)) / (len(TP) + len(TN) + len(FP) + len(FN))

    return overall_accuracy


def definition_extraction(
    owlfile: str,
    pospath: str,
    negpath: str,
    sig: signature.Signature,
    target_concept_name: str,
    language: str = "alc",
    inverse_roles: bool = False,
    feature_values: bool = False,
    max_thresholds: int = 10,
    max_size: int = 12,
    max_q: int = 2,
    md: str = "full_approx",
    timeout=180,
    workers=1,
    exclude_atomic = [],
    exclude_top_classes: bool = False
):
    print(f"- - - - Starting Definition Extraction for {target_concept_name} - - - -")

    time_start = time.perf_counter()

    print("== Loading {}".format(owlfile))
    A_new = structure_from_owl(owlfile)

    A = copy.deepcopy(A_new)

    weird_concept = "http://www.w3.org/1999/02/22-rdf-syntax-ns#Description"
    A.cn_ext[weird_concept].clear()
    A.cn_ext["http://www.w3.org/2002/07/owl#Thing"].clear()

    P = load_examples(pospath, owlfile, A)
    N = load_examples(negpath, owlfile, A)

    time_parsed = time.perf_counter()

    if len(A.cn_ext[target_concept_name.strip("<>")]) == 0:
        print(
            f"[WARN] The target_concept_name-Extension {target_concept_name} is EMPTY!"
        )
        sys.exit(1)

    # save the target extension locally and then clear it in the A structure, so that we will not get a trivial solution
    target_extension = A.cn_ext[target_concept_name.strip("<>")].copy()
    A.cn_ext[target_concept_name.strip("<>")].clear()

    # If we only remove the target concept, we get just a trivial solution of one of it's superclasses, therefore we have to remove those superclasses that are equivalent to our target_extension
    target_superclasses = collect_superclasses(target_concept_name)
    if not exclude_top_classes:
        target_superclasses -= set(sig.top_level_classes) | {sig.THING}

    for concept_name in target_superclasses:
        concept_name = concept_name.strip("<>")

        if concept_name not in A.cn_ext:
            print(f"[WARN] Concept_name {concept_name} does not exist!")
            sys.exit(1)
        elif len(A.cn_ext[concept_name]) == 0:
            print(f"[WARN] Concept {concept_name} has no individuals!")
            continue
        else:
            #concept_name_extension = A.cn_ext[concept_name]
            # removed = 0

            # if concept_name_extension == target_extension:
            #     removed = len(A.cn_ext[concept_name])
            #     A.cn_ext[concept_name].clear()

            removed = len(A.cn_ext[concept_name])
            A.cn_ext[concept_name].clear()

            print(f"Removed {removed} individuals of {concept_name}")

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
            training_accuracy, _, output_definition = f.solve_incr(max_size, timeout=remaining_time)
        elif md == "full_approx":
            print("Starting with solving")
            training_accuracy, _, output_definition = f.solve_incr_approx(
                max_size, timeout=remaining_time
            ) 
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

    overall_accuracy = compute_overall_accuracy(
        A_new, output_definition, target_extension
    )

    print("== Reached accurary (Overall data) {:.4f}".format(overall_accuracy))

    return (
        (training_accuracy, overall_accuracy),
        output_definition,
        A,
        P,
        N,
        target_extension,
    )

def main():
    target_concept = "f"

if __name__ == "__main__":
    main()

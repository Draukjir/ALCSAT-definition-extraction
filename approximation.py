from yago_fragmentation import signature
from extractExamples import extract_Examples
from definition_extraction import definition_extraction, compute_overall_accuracy
from spell.structures import ind, Structure
from spell.instance import ALCConcept
import time
from spell.fitting import mode, solve_incr
from spell.fitting_alc import FittingALC, OP

LANGUAGES = ["el", "el_alcsat", "fl0", "ex-or", "all-or", "elu", "alc", "alcq"]
L_OP = {
    "el": [OP.EX, OP.AND],
    "el_alcsat": [OP.EX, OP.AND],
    "fl0": [OP.ALL, OP.AND],
    "ex-or": [OP.EX, OP.OR],
    "all-or": [OP.ALL, OP.OR],
    "elu": [OP.EX, OP.OR, OP.AND],
    "alc": [OP.ALL, OP.EX, OP.OR, OP.AND, OP.NEG],
    "alc_pos": [OP.ALL, OP.EX, OP.OR, OP.AND],
    "alcq": [OP.ALL, OP.EX, OP.OR, OP.AND, OP.NEG, OP.LE, OP.GE],
    "alc_no_all": [OP.EX, OP.OR, OP.AND, OP.NEG],
    "alc_pos_no_all": [OP.EX, OP.OR, OP.AND]
}


def compute_extension(A: Structure, concept: ALCConcept) -> set:
    extension = set()
    for a in ind(A):
        if concept.mc(A, a):
            extension.add(a)

    return extension


def continue_extraction(
    A: Structure,
    P: list[int],
    N: list[int],
    sig: signature.Signature,
    target_concept: str,
    language: str = "alc",
    inverse_roles: bool = False,
    feature_values: bool = False,
    max_thresholds: int = 10,
    max_size: int = 12,
    max_q: int = 2,
    md: str = "full_approx",
    timeout=180,
    workers=1,
):

    time_start = time.perf_counter()

    time_parsed = time.perf_counter()

    print("== Starting incremental search search for fitting query")
    time_start_solve = time.perf_counter()

    acc = 0.0
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
        )
        remaining_time = -1
        if timeout != -1:
            remaining_time = timeout - (time.perf_counter() - time_start)
        if md == mode.exact:
            acc, _, _ = f.solve_incr(max_size, timeout=remaining_time)
        elif md == "full_approx":
            print("Starting with solving")
            acc, _, output_definition = f.solve_incr_approx(
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
    print("== Reached accurary {:.4f}".format(acc))

    return output_definition


def approximation_step(
    extension: set,
    P: set,
    N: set,
    concept: ALCConcept,
    sig: signature.Signature,
    target_concept: str,
    A: Structure,
    size: int,
    language:str = "alc",
    inverse: bool = False,
    exclude_atomic = []
):

    P_1 = list(P & extension)  # True Positives
    N_1 = list(N & extension)  # False Positives

    P_2 = list(P - extension)  # False Negatives
    N_2 = list(N - extension)  # True Negatives

    print(f"found {len(P_1)} true positives")
    print(f"found {len(N_2)} true negatives")
    print(f"found {len(N_1)} false positives")
    print(f"found {len(P_2)} false negatives")

    if len(N_1) == 0 and len(P_2) == 0:
        new_concept = concept
    elif len(N_1) == 0 and len(P_2) != 0:
        conc_2 = continue_extraction(A, P_2, N_2, sig, target_concept, max_size=size, language=language, inverse_roles=inverse)

        new_concept = ALCConcept(
            operation=OP.OR, name="", value=0, children=(concept, conc_2)
        )
    elif len(N_1) != 0 and len(P_2) == 0:
        conc_1 = continue_extraction(A, P_1, N_1, sig, target_concept, max_size=size, language=language, inverse_roles=inverse)

        new_concept = ALCConcept(
            operation=OP.AND, name="", value=0, children=(concept, conc_1)
        )
    else:
        conc_1 = continue_extraction(A, P_1, N_1, sig, target_concept, max_size=size, language=language, inverse_roles=inverse)
        conc_2 = continue_extraction(A, P_2, N_2, sig, target_concept, max_size=size, language=language, inverse_roles=inverse)

        not_c = ALCConcept(operation=OP.NEG, name="", value=0, children=(concept,))
        left = ALCConcept(
            operation=OP.AND, name="", value=0, children=(concept, conc_1)
        )
        right = ALCConcept(operation=OP.AND, name="", value=0, children=(not_c, conc_2))
        new_concept = ALCConcept(
            operation=OP.OR, name="", value=0, children=(left, right)
        )

    return new_concept


def approximation(
    target_concept: str,
    sig: signature.Signature,
    iterations: int,
    size: int,
    fragment_file: str,
    samples: int = 100,
    language: str = "alc",
    inverse: bool = False,
    exclude_atomic = [],
    exclude_top_classes = False,
):

    extract_Examples(target_concept, sig, samples, fragment_file=fragment_file)

    accuracy, concept, A, P, N, target_extension = definition_extraction(
        fragment_file, "P.txt", "N.txt", sig, target_concept, language=language, inverse_roles=inverse, max_size=size, exclude_atomic=exclude_atomic, exclude_top_classes=exclude_top_classes
    )

    old_definition = ALCConcept.to_dl_concept(concept)
    old_training_accuracy = accuracy[0]
    old_overall_accuracy = accuracy[1]

    print(f"Result for {target_concept}\n")

    print(f"Reached Training Accuracy: {accuracy[0]}")
    print(f"Reached Overall Accuracy: {accuracy[1]}")

    print(f"\nExtracted Concept:\n{old_definition}")

    if old_training_accuracy == 1.0:
        print(
            "The Accuracy on the training data is already 1, nothing to improve. No Approximation needed!"
        )
        return (
            old_definition,
            old_definition,
            old_training_accuracy,
            old_training_accuracy,
            old_overall_accuracy,
            old_overall_accuracy,
        )

    extension = compute_extension(A, concept)

    P = set(P)
    N = set(N)

    for i in range(iterations):
        print(f"Approximation step: {i}")

        concept = approximation_step(
            extension, P, N, concept, sig, target_concept, A, size, language, inverse=inverse, exclude_atomic=exclude_atomic
        )
        extension = compute_extension(A, concept)

    final_TP = len(P & extension)
    final_TN = len(N - extension)

    print("DEBUG ZEICHEN")

    new_training_accuracy = (final_TP + final_TN) / (len(P) + len(N))
    new_overall_accuracy = compute_overall_accuracy(A, concept, target_extension)
    new_definition = ALCConcept.to_dl_concept(concept)

    print(
        f"Extracted concept for {target_concept} after {iterations} iterations: {ALCConcept.to_dl_concept(concept)}"
    )

    print(
        "----------------------------------------------------------------------------"
    )
    print(
        f"Accuracy before approximation: TRAINING: {old_training_accuracy} - - - OVERALL: {old_overall_accuracy}"
    )
    print(
        f"Accuracy after approximation: TRAINING{new_training_accuracy} - - - OVERALL: {new_overall_accuracy}"
    )

    return (
        old_definition,
        new_definition,
        old_training_accuracy,
        new_training_accuracy,
        old_overall_accuracy,
        new_overall_accuracy,
    )

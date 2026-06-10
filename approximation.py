from yago_fragmentation import signature
from extractExamples import extract_Examples
from definition_extraction import definition_extraction
from spell.structures import ind, structure_from_owl, Structure
from spell.instance import ALCConcept
import time
from yago_fragmentation.taxonomy import collect_superclasses
from spell.fitting import mode, solve_incr
from spell.fitting_alc import FittingALC, OP
import sys

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
}

def main():
    sig = signature.Signature()

    extract_Examples(sig.target_concept, sig)

    acc, concept, A, P, N= definition_extraction("yago-fragment.owl",
                            "P.txt",
                            "N.txt",
                            sig,
                            sig.target_concept,
                            max_size=9
                            )

    definition = ALCConcept.to_dl_concept(concept)

    print(f"Reached Training Accuracy: {acc[0]}")
    print(f"Reached Overall Accuracy: {acc[1]}")
    print(f"Found Definition for {sig.target_concept}:\n{definition}")

    print("Start Approximation:")
    extension = set()
    for a in ind(A):
        if concept.mc(A,a):
            extension.add(a)

    P = set(P)
    N = set(N)

    TP = P & extension
    TN = N - extension
    FP = N & extension
    FN = P - extension

    print(f"found {len(TP)} true positives")
    print(f"found {len(TN)} true negatives")
    print(f"found {len(FP)} false positives")
    print(f"found {len(FN)} false negatives")

    P_1 = list(TP)
    N_1 = list(FP)
    P_2 = list(FN)
    N_2 = list(TN)

    acc_1, conc_1, _, _, _ = continue_extraction(A, P_1, N_1, sig, sig.target_concept, max_size=9)
    acc_2, conc_2, _, _, _ = continue_extraction(A, P_2, N_2, sig, sig.target_concept, max_size=9)

    print(f"Reached an accuracy of {acc_1} for the following dividing concept for True Positives and False Positves: {ALCConcept.to_dl_concept(conc_1)}")
    print(f"Reached an accuracy of {acc_2} for the following dividing concept for True Positives and False Positves: {ALCConcept.to_dl_concept(conc_2)}")

    not_c = ALCConcept(operation=OP.NEG, name="", value=0, children=(concept,))
    left = ALCConcept(operation=OP.AND,name="",value=0,children=(concept, conc_1))
    right = ALCConcept(operation=OP.AND,name="",value=0,children=(not_c, conc_2))
    final_concept = ALCConcept(operation=OP.OR,name="",value=0,children=(left, right))

    final_extension = set()
    for a in ind(A):
        if final_concept.mc(A,a):
            final_extension.add(a)

    final_TP = len(P & final_extension)
    final_TN = len(N - final_extension)

    final_accuracy = (final_TP + final_TN) / (len(P)+len(N))

    print(f"Final Accuracy: {final_accuracy} with the following concept: {ALCConcept.to_dl_concept(final_concept)}")

    print("----------------------------------------------------------------------------")
    print(f"Accuracy before approximation: {acc}")
    print(f"Accuracy after approximation: {final_accuracy}")

def compute_extension(A: Structure, concept: ALCConcept) -> set:
    extension = set()
    for a in ind(A):
        if concept.mc(A,a):
            extension.add(a)
    
    return extension

def continue_extraction(A: Structure, 
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
                          timeout = 180,
                          workers = 1,):

    time_start = time.perf_counter()

    time_parsed = time.perf_counter()

    print("== Starting incremental search search for fitting query")
    time_start_solve = time.perf_counter()

    acc = 0
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
            max_thresholds=max_thresholds
        )
        remaining_time = -1
        if timeout != -1:
            remaining_time = timeout - (time.perf_counter() - time_start)
        if md == mode.exact:
            acc, _, _ = f.solve_incr(max_size, timeout=remaining_time)
        elif md == "full_approx":
            print("Starting with solving")
            acc, _, output_definition = f.solve_incr_approx(max_size, timeout=remaining_time) # _ _ 3 beste Konzept hier zurückgeben
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

def approximation_step(extension: set, P: list[int], N: list[int], concept: ALCConcept, sig: signature.Signature, target_concept: str, A: Structure):

        P_1 = list(P & extension) # True Positives
        N_1 = list(N & extension) # False Positives
        
        P_2= list(P - extension) # False Negatives
        N_2 = list(N - extension) # True Negatives

        print(f"found {len(P_1)} true positives")
        print(f"found {len(N_2)} true negatives")
        print(f"found {len(N_1)} false positives")
        print(f"found {len(P_2)} false negatives")

        conc_1 = continue_extraction(A, P_1, N_1, sig, target_concept, max_size=9)
        conc_2 = continue_extraction(A, P_2, N_2, sig, target_concept, max_size=9)

        not_c = ALCConcept(operation=OP.NEG, name="", value=0, children=(concept,))
        left = ALCConcept(operation=OP.AND,name="",value=0,children=(concept, conc_1))
        right = ALCConcept(operation=OP.AND,name="",value=0,children=(not_c, conc_2))
        new_concept = ALCConcept(operation=OP.OR,name="",value=0,children=(left, right))

        return new_concept

def approximation(target_concept: str,
                  sig: signature.Signature,
                  iterations: int):
    
    extract_Examples(target_concept, sig)

    accuracy, concept, A, P, N= definition_extraction("yago-fragment.owl",
                            "P.txt",
                            "N.txt",
                            sig,
                            target_concept,
                            max_size=9
                            )

    definition = ALCConcept.to_dl_concept(concept)

    print(f"Result for {target_concept}\n")

    print(f"Reached Training Accuracy: {accuracy[0]}")
    print(f"Reached Overall Accuracy: {accuracy[1]}")

    print(f"\nExtracted Concept:\n{definition}")

    extension = compute_extension(A, concept)

    P = set(P)
    N = set(N)

    for i in range(iterations):
        print(f"Approximation step: {i}")

        concept = approximation_step(extension, P, N, concept, sig, target_concept, A)
        extension = compute_extension(A, concept)

    final_TP = len(P & extension)
    final_TN = len(N - extension)

    print("DEBUG ZEICHEN")

    final_accuracy = (final_TP + final_TN) / (len(P)+len(N))

    print(f"Extracted concept for {target_concept} after {iterations} iterations: {ALCConcept.to_dl_concept(concept)}")

    print("----------------------------------------------------------------------------")
    print(f"Accuracy before approximation: {accuracy[1]}")
    print(f"Accuracy after approximation: {final_accuracy}")

    improvement = final_accuracy - accuracy[1]
    print(f"The accuracy has increased by {improvement}")

    return improvement, concept

if __name__ == "__main__":
    main()

# Beispielausgabe:
# ...........
# ..........
# ----------------------------------------------------------------------------
# Accuracy before approximation: 0.86
# Accuracy after approximation: 0.91
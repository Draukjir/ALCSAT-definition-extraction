import sys
import time

from definition_extraction import compute_overall_accuracy, definition_extraction
from extractExamples import extract_Examples
from spell.fitting import mode, solve_incr
from spell.fitting_alc import OP, FittingALC
from spell.instance import ALCConcept
from spell.structures import Structure, ind
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
    "alc_pos": [OP.ALL, OP.EX, OP.OR, OP.AND],
    "alcq": [OP.ALL, OP.EX, OP.OR, OP.AND, OP.NEG, OP.LE, OP.GE],
}


def clean_name(uri):
    return (
        uri.replace("<http://yago-knowledge.org/resource/", "")
        .replace("<http://schema.org/", "")
        .replace(">", "")
        .replace("http://yago-knowledge.org/resource/", "")
        .replace("http://schema.org/", "")
    )


def compute_extension(A: Structure, concept: ALCConcept) -> set:
    extension = set()
    for a in ind(A):
        if concept.mc(A, a):
            extension.add(a)

    return extension


def solve(
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
        # ops = L_OP[language]
        ops = list(L_OP[language])
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
    print("== Reached accurary {:.4f}".format(acc))

    return output_definition


def approx(A, P, N, sig, target_concept, language, inverse, max_size, depth, threshold):
    print(f"Approx step - depth {depth}")

    concept = solve(
        A=A,
        P=P,
        N=N,
        sig=sig,
        target_concept=target_concept,
        language=language,
        inverse_roles=inverse,
        max_size=max_size,
    )

    P = set(P)
    N = set(N)
    extension = compute_extension(A, concept)

    TP = list(P & extension)
    FP = list(N & extension)
    FN = list(P - extension)
    TN = list(N - extension)

    print(f"TP: {len(TP)}")
    print(f"FP: {len(FP)}")
    print(f"FN: {len(FN)}")
    print(f"TN: {len(TN)}")

    if depth == 0:
        print("CASE: final depth reached")
        return concept

    depth -= 1

    if len(FP) < threshold and len(FN) < threshold:
        print("CASE: finished")
        return concept
    elif len(FP) < threshold:
        print("CASE: FP < threshold")
        right_rec = approx(
            A,
            FN,
            TN,
            sig,
            target_concept,
            language,
            inverse,
            max_size,
            depth,
            threshold,
        )

        new_concept = ALCConcept(
            operation=OP.OR, name="", value=0, children=(concept, right_rec)
        )
        return new_concept
    elif len(FN) < threshold:
        print("CASE: FN < threshold")
        left_rec = approx(
            A,
            TP,
            FP,
            sig,
            target_concept,
            language,
            inverse,
            max_size,
            depth,
            threshold,
        )

        new_concept = ALCConcept(
            operation=OP.AND, name="", value=0, children=(concept, left_rec)
        )
        return new_concept
    else:
        print("CASE: else")
        left_rec = approx(
            A,
            TP,
            FP,
            sig,
            target_concept,
            language,
            inverse,
            max_size,
            depth,
            threshold,
        )
        right_rec = approx(
            A,
            FN,
            TN,
            sig,
            target_concept,
            language,
            inverse,
            max_size,
            depth,
            threshold,
        )

        left_concept = ALCConcept(
            operation=OP.AND, name="", value=0, children=(concept, left_rec)
        )

        not_concept = ALCConcept(
            operation=OP.NEG, name="", value=0, children=(concept,)
        )
        right_concept = ALCConcept(
            operation=OP.AND, name="", value=0, children=(not_concept, right_rec)
        )

        new_concept = ALCConcept(
            operation=OP.OR, name="", value=0, children=(left_concept, right_concept)
        )
        return new_concept


def approx_start(
    target_concept: str,
    sig: signature.Signature,
    recursive_depth: int,
    concept_size: int,
    fragment_file: str,
    samples: int,
    language: str,
    inverse: bool,
    exclude_atomic=[],
    threshold=0,
):
    print(f"Start Recursive Approx for {clean_name(target_concept)}")
    extract_Examples(target_concept, sig, samples, fragment_file=fragment_file)

    acc, concept, A, P, N, target_extension = definition_extraction(
        fragment_file,
        "P.txt",
        "N.txt",
        sig,
        target_concept,
        language=language,
        inverse_roles=inverse,
        max_size=concept_size,
        exclude_atomic=exclude_atomic,
    )

    old_def = ALCConcept.to_dl_concept(concept)
    old_train_acc = acc[0]
    old_overall_acc = acc[1]

    print(f"Result for {clean_name(target_concept)}")
    print(f"Extracted Concept: {old_def}")
    print(f"Train Acc: {old_train_acc}")
    print(f"Overall Acc: {old_overall_acc}")

    P = set(P)
    N = set(N)

    if recursive_depth == 0 or old_train_acc == 1.0:
        print("Finished")
        print("Final Concept Already Found")

        final_concept = concept
    else:
        print(f"Starting approx with depth {recursive_depth}")
        extension = compute_extension(A, concept)

        # final_concept = approx(A, P, N, sig, target_concept, language, inverse, concept_size, recursive_depth)

        TP = list(P & extension)
        FP = list(N & extension)
        FN = list(P - extension)
        TN = list(N - extension)

        print(f"TP: {len(TP)}")
        print(f"FP: {len(FP)}")
        print(f"FN: {len(FN)}")
        print(f"TN: {len(TN)}")

        recursive_depth -= 1

        if len(FP) < threshold and len(FN) < threshold:
            print("CASE: finished")

            final_concept = concept
        elif len(FP) < threshold:
            print("CASE: FP < threshold")
            right_rec = approx(
                A,
                FN,
                TN,
                sig,
                target_concept,
                language,
                inverse,
                concept_size,
                recursive_depth,
                threshold,
            )

            final_concept = ALCConcept(
                operation=OP.OR, name="", value=0, children=(concept, right_rec)
            )
        elif len(FN) < threshold:
            print("CASE: FN < threshold")
            left_rec = approx(
                A,
                TP,
                FP,
                sig,
                target_concept,
                language,
                inverse,
                concept_size,
                recursive_depth,
                threshold,
            )

            final_concept = ALCConcept(
                operation=OP.AND, name="", value=0, children=(concept, left_rec)
            )
        else:
            print("CASE: else")
            left_rec = approx(
                A,
                TP,
                FP,
                sig,
                target_concept,
                language,
                inverse,
                concept_size,
                recursive_depth,
                threshold,
            )
            right_rec = approx(
                A,
                FN,
                TN,
                sig,
                target_concept,
                language,
                inverse,
                concept_size,
                recursive_depth,
                threshold,
            )

            left_concept = ALCConcept(
                operation=OP.AND, name="", value=0, children=(concept, left_rec)
            )

            not_concept = ALCConcept(
                operation=OP.NEG, name="", value=0, children=(concept,)
            )
            right_concept = ALCConcept(
                operation=OP.AND, name="", value=0, children=(not_concept, right_rec)
            )

            final_concept = ALCConcept(
                operation=OP.OR,
                name="",
                value=0,
                children=(left_concept, right_concept),
            )

    final_extension = compute_extension(A, final_concept)

    P = set(P)
    N = set(N)

    final_TP = len(P & final_extension)
    final_TN = len(N - final_extension)

    new_train_acc = (final_TP + final_TN) / (len(P) + len(N))
    new_overall_acc = compute_overall_accuracy(A, final_concept, target_extension)
    new_def = ALCConcept.to_dl_concept(final_concept)

    return (
        old_def,
        new_def,
        old_train_acc,
        new_train_acc,
        old_overall_acc,
        new_overall_acc,
    )


def main():

    # SETTINGS
    target_concept = "<http://yago-knowledge.org/resource/Politician>"
    sig = signature.Signature()
    samples = 100
    fragment_file = "fragment-sample-22-07.owl"

    language = "alc_pos"
    inverse = True
    size = 4
    exclude_atomic = []

    recursive_depth = 1
    threshold = 10
    # END SETTINGS

    print("TEST")

    result = approx_start(
        target_concept,
        sig,
        recursive_depth,
        size,
        fragment_file,
        samples,
        language,
        inverse,
        exclude_atomic,
        threshold,
    )

    print(f"old def: {result[0]}")
    print(f"new def: {result[1]}")
    print(f"old_train_acc: {result[2]}")
    print(f"new_train_acc: {result[3]}")
    print(f"old_overall_acc: {result[4]}")
    print(f"new_overall_acc: {result[5]}")


if __name__ == "__main__":
    main()

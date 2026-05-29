import argparse
import sys
import time

from spell.fitting import mode, solve_incr
from spell.fitting_alc import FittingALC, OP
from spell.structures import solution2sparql, structure_from_owl
from spell.instance import ALCConcept
from yago_fragmentation.taxonomy import collect_superclasses
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
}

def main():
    sig = signature.Signature()

    a, d = definition_extraction("yago_fragmentation/yago-fragment.owl",
                          "P.txt",
                          "N.txt",
                          sig,
                          sig.target_concept,
                          max_size=9
                          )
    
    print(f"Reached Accuracy: {a}")
    print(f"Found Definition for {sig.target_concept}:\n{d}")

def definition_extraction(owlfile: str, 
                          pospath: str, 
                          negpath: str,
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

    print("== Loading {}".format(owlfile))
    A = structure_from_owl(owlfile)

    P: list[int] = []
    with open(pospath, encoding="UTF-8") as file:
        for line in file.readlines():
            ind = line.rstrip()
            if ind not in A.indmap:
                print(
                    "[ERR] The positive example {} does not seem to occur in {}".format(
                        ind, owlfile
                    )
                )
                sys.exit(1)
            P.append(A.indmap[ind])

    N: list[int] = []
    with open(negpath, encoding="UTF-8") as file:
        for line in file.readlines():
            ind = line.rstrip()
            if ind not in A.indmap:
                print(
                    "[ERR] The negative example {} does not seem to occur in {}".format(
                        ind, owlfile
                    )
                )
                sys.exit(1)
            N.append(A.indmap[ind])

    time_parsed = time.perf_counter()

    # Target Removal: 
    # If we only remove the target concept, we get just a trivial solution of one of it's superclasses, therefore we have to remove them aswell

    target_concepts = collect_superclasses(target_concept) | {target_concept}

    target_concepts -= set(sig.top_level_classes) | {sig.THING}

    if len(A.cn_ext[target_concept.strip("<>")]) == 0:
        print(f"[WARN] Target Concept {target_concept} has no individuals")
        return -1, None

    for concept in target_concepts:
        concept = concept.strip("<>")

        if concept not in A.cn_ext:
            print(f"[WARN] Concept {concept} not found.")
            return -1, None
        elif len(A.cn_ext[concept]) == 0:
            print(f"[WARN] Concept {concept} has no individuals")
            continue
        else:
            removed = len(A.cn_ext[concept])
            A.cn_ext[concept].clear()
            print(f"Removed {removed} individuals of {concept}")

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
    
    return acc, ALCConcept.to_dl_concept(output_definition)


if __name__ == "__main__":
    main()
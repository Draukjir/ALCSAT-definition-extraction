import argparse
import sys
import time

from spell.fitting import mode, solve_incr
from spell.fitting_alc import FittingALC, OP
from spell.structures import solution2sparql, structure_from_owl

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
    parser = argparse.ArgumentParser(prog="spell_cli.py")

    _ = parser.add_argument(
        "kb_owl_file", help="path to a OWL knowledge base in RDF/XML format"
    )
    _ = parser.add_argument(
        "pos_example_list", help="path to a textfile containing positive examples"
    )
    _ = parser.add_argument(
        "neg_example_list", help="path to a textfile containing negative examples"
    )

    _ = parser.add_argument(
        "--language",
        type=str,
        default="el",
        choices=LANGUAGES,
        help="language to learn in, el: {exists,and}, el_alcsat: {exists,and}, fl0: {forall,and}, ex-or: {exists,or}, all-or: {forall,or}, elu: {exists,and,or}, alc: {forall,exists,and,or,neg}, alc: {forall,exists,and,or,neg, le, ge} (default=el)",
    )

    _ = parser.add_argument("--max_size", type=int, default=12, help="(default=12)")
    _ = parser.add_argument("--max_q", type=int, default=2, help="(default=2)")
    _ = parser.add_argument(
        "--mode",
        choices=["exact", "neg_approx", "full_approx"],
        default=mode.exact,
        help="(default=exact)",
    )

    _ = parser.add_argument(
        "--output", type=str, help="write best fitting SPARQL query to a file"
    )
    _ = parser.add_argument(
        "--timeout", type=float, default=-1, help="in seconds (default=-1)"
    )

    _ = parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="number of worker processes (default = 1)",
    )

    args = parser.parse_args()

    owlfile = args.kb_owl_file
    pospath = args.pos_example_list
    negpath = args.neg_example_list

    md = args.mode

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

    print("== Starting incremental search search for fitting query")
    time_start_solve = time.perf_counter()

    acc = 0
    if args.language != "el":
        f = FittingALC(
            A,
            args.max_size,
            P,
            N,
            op=frozenset(L_OP[args.language]),
            workers=args.workers,
            max_q=args.max_q,
        )
        remaining_time = -1
        if args.timeout != -1:
            remaining_time = args.timeout - (time.perf_counter() - time_start)
        if args.mode == mode.exact:
            acc, _, _ = f.solve_incr(args.max_size, timeout=remaining_time)
        elif args.mode == "full_approx":
            acc, _, _ = f.solve_incr_approx(args.max_size, timeout=remaining_time)
        else:
            print(f"Mode {args.mode} is only supported for SPELL.")
    else:
        _, res = solve_incr(A, P, N, md, timeout=args.timeout, max_size=args.max_size)

    time_solved = time.perf_counter()

    print(
        "== Took {:.2f}s for reading input and {:.3f}s for solving".format(
            time_parsed - time_start, time_solved - time_start_solve
        )
    )
    print("== Reached accurary {:.4f}".format(acc))

    if args.output is not None:
        print("== Writing result to {}".format(args.output))
        with open(args.output, "w", encoding="UTF-8") as file:
            file.write(solution2sparql(res))


if __name__ == "__main__":
    main()

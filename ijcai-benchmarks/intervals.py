from spell.preprocessing import ThresholdMethod
import time
from alcsat import L_OP
from spell.structures import structure_from_owl
from spell.fitting_alc import FittingALC


def main():
    runs = 3
    benchmarks = ["carcinogenesis"]
    intervals = [0, 2, 5, 10, 20, 40, 1000]

    for benchmark in benchmarks:
        A = structure_from_owl(f"../sml-benchmarks/{benchmark}/{benchmark}.owl")
        pospath = f"../sml-benchmarks/{benchmark}/full/pos.txt"
        negpath = f"../sml-benchmarks/{benchmark}/full/neg.txt"

        P: list[int] = []
        with open(pospath, encoding="UTF-8") as file:
            for line in file.readlines():
                ind = line.rstrip()
                P.append(A.indmap[ind])

        N: list[int] = []
        with open(negpath, encoding="UTF-8") as file:
            for line in file.readlines():
                ind = line.rstrip()
                N.append(A.indmap[ind])

        accuracies: dict[int, list[float]] = {}

        for i in intervals:
            accuracies[i] = []
            for run in range(runs):
                start = time.perf_counter()

                f = FittingALC(
                    A,
                    15,
                    P,
                    N,
                    op=frozenset(L_OP["alcqf"]),
                    workers=15,
                    max_q=2,
                    max_thresholds=i,
                    clustering = ThresholdMethod.INTERVALS

                )

                acc, _, _ = f.solve_incr_approx(15, timeout = 10)

                end = time.perf_counter()

                print("==== TOOK {}".format(end - start))
                accuracies[i].append(acc)

        for i in intervals:
            print(f"Benchmark {benchmark}, Intervals {i} : {sum(accuracies[i]) / runs}s")


if __name__ == "__main__":
    main()

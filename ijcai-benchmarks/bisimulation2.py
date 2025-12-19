import time
from alcsat import L_OP
from spell.structures import structure_from_owl
from spell.fitting_alc import FittingALC



def main():
    workers = 8
    runs = 1
    benchmarks = ["mammographic", "hepatitis", "lymphography"]
    language = "alcq"
    timeout = 10
    max_k = 15

    accuracies_with = {}
    accuracies_without = {}
    for benchmark in benchmarks:
        accuracies_with[benchmark] = []
        accuracies_without[benchmark] = []

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


        for run in range(runs):
            start = time.perf_counter()

            f = FittingALC(
                A,
                max_k,
                P,
                N,
                op=frozenset(L_OP[language]),
                workers=workers,
                max_q=2,
                bisim_reduction=False,
            )

            acc, _, _ = f.solve_incr_approx(max_k, timeout = timeout)

            accuracies_without[benchmark].append(acc)

            end = time.perf_counter()

            print("==== TOOK {}".format(end - start))
            t1 = end - start
            
            start = time.perf_counter()
            f = FittingALC(
                A,
                max_k,
                P,
                N,
                op=frozenset(L_OP[language]),
                workers=workers,
                max_q=2,
                bisim_reduction=True
            )

            acc, _, _ = f.solve_incr_approx(max_k, timeout = timeout)

            end = time.perf_counter()

            print("==== TOOK {}".format(end - start))
            t2 = end - start

            accuracies_with[benchmark].append(acc)

    for benchmark in benchmarks:
        print(f"Benchmark {benchmark} : {sum(accuracies_with[benchmark]) / runs} {sum(accuracies_without[benchmark]) / runs}" )


if __name__ == "__main__":
    main()

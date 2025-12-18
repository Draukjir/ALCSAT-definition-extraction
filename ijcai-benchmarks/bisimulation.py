import time
from alcsat import L_OP
from spell.structures import structure_from_owl
from spell.fitting_alc import FittingALC



def main():
    workers = [8]
    runs = 3
    benchmarks = ["mammographic", "hepatitis", "lymphography"]
    max_k = 8
    language = "alc"

    factors = {}
    for benchmark in benchmarks:
        factors[benchmark] = []

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
                workers=8,
                max_q=2,
                bisim_reduction=False
            )

            acc, _, _ = f.solve_incr_approx(max_k)

            end = time.perf_counter()

            print("==== TOOK {}".format(end - start))
            t1 = end - start
            
            start = time.perf_counter()
            f = FittingALC(
                A,
                max_k,
                P,
                N,
                op=frozenset(L_OP["alcq"]),
                workers=8,
                max_q=2,
                bisim_reduction=True
            )

            acc, _, _ = f.solve_incr_approx(max_k)

            end = time.perf_counter()

            print("==== TOOK {}".format(end - start))
            t2 = end - start

            factors[benchmark].append(t2 / t1)

    for benchmark in benchmarks:
        print(f"Benchmark {benchmark} : {sum(factors[benchmark]) / runs}s " )


if __name__ == "__main__":
    main()

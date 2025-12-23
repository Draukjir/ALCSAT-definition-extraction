from spell.fitting_alc import perfect_fitting
from spell.preprocessing import (
    encode_dataproperties,
    color_refinement,
    ThresholdMethod,
    decode_dataproperties,
)
from spell.fitting import non_empty_symbols
from spell.instance import ALCConcept, OP, Instance
from spell.structures import Signature, Structure, structure_from_owl


def main():
    benchmarks = ["carcinogenesis"]

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

        sig = non_empty_symbols(A)

        inst = Instance(A, P, N, sig, frozenset(), 2)


        c = perfect_fitting(inst)


        print(c.to_tree())
        print(c.size())

        ext: set[int] = set()
        for a in set(P).union(set(N)):
            if c.mc(A, a):
                ext.add(a)

        acc = Instance(A, P, N, sig, frozenset(), 2).accuracy(frozenset(ext))

        print(acc)


if __name__ == "__main__":
    main()

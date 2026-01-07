from owlapy.owl_individual import OWLNamedIndividual
from ontolearn.learning_problem import PosNegLPStandard
from sklearn.model_selection import StratifiedKFold
from ontolearn.utils.static_funcs import compute_f1_score
import time
from ontolearn.learners import TDL
from ontolearn.knowledge_base import KnowledgeBase
from spell.fitting import determine_relevant_symbols
import sys
from spell.structures import structure_from_owl
from spell.fitting_alc import FittingALC
from spell.preprocessing import ThresholdMethod
import random
from spell.instance import Instance, OP
import numpy as np


def chunks(lst: list[int], n: int):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def kfold(
    inst: Instance,
    folds: int = 10,
    max_k=10,
    timeout: float = 30,
    tm: ThresholdMethod = ThresholdMethod.INTERVALS,
):
    all_p = list(inst.P)
    all_n = list(inst.N)

    random.shuffle(all_p)
    random.shuffle(all_n)

    # TODO: aufrunden
    p_chunks = list(chunks(all_p, len(all_p) // folds))
    n_chunks = list(chunks(all_n, len(all_n) // folds))

    for i in range(folds):
        this_p = [p for j in range(folds) for p in p_chunks[j] if j != i]
        this_n = [n for j in range(folds) for n in n_chunks[j] if j != i]

        f = FittingALC(inst.A, max_k, this_p, this_n, inst.op, 8, 2, clustering=tm)
        (acc, n, concept) = f.solve_incr_approx(max_k, timeout=timeout)

        other_p = p_chunks[i]
        other_n = n_chunks[i]

        tp = 0
        fp = 0
        tn = 0
        fn = 0

        for p in other_p:
            if concept.mc(inst.A, p):
                tp += 1
            else:
                fn += 1
        for n in other_n:
            if concept.mc(inst.A, n):
                fp += 1
            else:
                tn += 1

        acc2 = (tp + tn) / (tp + fn + fp + tn)
        f1 = (2 * tp) / (2 * tp + fp + fn)

        yield (i, concept, acc2, f1)


def sml_benchmark_cross_validate(resultpath: str, tm: ThresholdMethod):
    with open(resultpath, mode="w") as outfile:
        _ = outfile.write("bench, fold, acc, f1, size, evo_size, concept\n")
        for bench in [
            # "carcinogenesis",
            # "hepatitis",
            # "lymphography",
            # "mammographic",
            # "mutagenesis",
            "nctrer",
            "premierleague",
            "pyrimidine",
        ]:
            owlfile = f"../sml-benchmarks/{bench}/{bench}.owl"
            pospath = f"../sml-benchmarks/{bench}/full/pos.txt"
            negpath = f"../sml-benchmarks/{bench}/full/neg.txt"

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

            sigma = determine_relevant_symbols(A, P + N, 1, 10)
            inst = Instance(
                A,
                P,
                N,
                sigma,
                frozenset(
                    [OP.ALL, OP.EX, OP.OR, OP.AND, OP.NEG, OP.LE, OP.GE, OP.DGEQ]
                ),
                2,
            )
            for fold, concept, acc, f1 in kfold(inst, 10, max_k=10, timeout=300, tm=tm):
                _ = outfile.write(
                    f"{bench}, {fold}, {acc}, {f1}, {concept.size()}, {concept.evo_size()}, {concept.to_dl_concept()} \n"
                )
                outfile.flush()


def cross_validate_tdl(kbpath: str, pos_path: str, neg_path: str, max_runtime: int):
    kb = KnowledgeBase(path=kbpath)

    tdl = TDL(
        knowledge_base=kb,
        kwargs_classifier={"random_state": 1},
        max_runtime=max_runtime,
        verbose=1,
    )

    data = dict()

    p: list[str] = []
    with open(pos_path, encoding="UTF-8") as file:
        for line in file.readlines():
            ind = line.rstrip()
            p.append(ind)

    n: list[str] = []
    with open(neg_path, encoding="UTF-8") as file:
        for line in file.readlines():
            ind = line.rstrip()
            n.append(ind)

    kf = StratifiedKFold(n_splits=10, shuffle=True, random_state=1)
    X = np.array(p + n)
    y = np.array([1.0 for _ in p] + [0.0 for _ in n])

    for ith, (train_index, test_index) in enumerate(kf.split(X, y)):
        #
        data.setdefault("LP", []).append(kbpath)
        data.setdefault("Fold", []).append(ith)
        # () Extract positive and negative examples from train fold
        train_pos = {
            pos_individual for pos_individual in X[train_index][y[train_index] == 1]
        }
        train_neg = {
            neg_individual for neg_individual in X[train_index][y[train_index] == 0]
        }

        # Sanity checking for individuals used for training.
        assert train_pos.issubset(p)
        assert train_neg.issubset(n)

        # () Extract positive and negative examples from test fold
        test_pos = {
            pos_individual for pos_individual in X[test_index][y[test_index] == 1]
        }
        test_neg = {
            neg_individual for neg_individual in X[test_index][y[test_index] == 0]
        }

        # Sanity checking for individuals used for testing.
        assert test_pos.issubset(p)
        assert test_neg.issubset(n)

        train_lp = PosNegLPStandard(
            pos={OWLNamedIndividual(i) for i in train_pos},
            neg={OWLNamedIndividual(i) for i in train_neg},
        )

        test_lp = PosNegLPStandard(
            pos={OWLNamedIndividual(i) for i in test_pos},
            neg={OWLNamedIndividual(i) for i in test_neg},
        )

        print("TDL starts..", end="\t")
        start_time = time.time()
        # () Fit model on training dataset
        pred_tdl = tdl.fit(train_lp).best_hypotheses(n=1)
        print("TDL ends..", end="\t")
        rt_tdl = time.time() - start_time

        # () Quality on the training data
        train_f1_tdl = compute_f1_score(
            individuals=frozenset({i for i in kb.individuals(pred_tdl)}),
            pos=train_lp.pos,
            neg=train_lp.neg,
        )
        # () Quality on test data
        test_f1_tdl = compute_f1_score(
            individuals=frozenset({i for i in kb.individuals(pred_tdl)}),
            pos=test_lp.pos,
            neg=test_lp.neg,
        )

        data.setdefault("Train-F1-TDL", []).append(train_f1_tdl)
        data.setdefault("Test-F1-TDL", []).append(test_f1_tdl)
        data.setdefault("RT-TDL", []).append(rt_tdl)
        print(f"TDL Train Quality: {train_f1_tdl:.3f}", end="\t")
        print(f"TDL Test Quality: {test_f1_tdl:.3f}", end="\t")
        print(f"TDL Runtime: {rt_tdl:.3f}")
        return


def main():
    # examples_from_bisim(sys.argv[1], sys.argv[2], n_ex = 100)
    # examples_from_bisim_evo(sys.argv[2])
    # alcq_benchmarks_to_csv(sys.argv[2])
    # test_evo_data_properties_write_file()
    # sml_benchmark_cross_validate(
    #     "out-intervall-2026-01-06.txt", ThresholdMethod.INTERVALS
    # )
    # sml_benchmark_cross_validate(
    #     "out-kmeans-2026-01-06-nctrer.txt", ThresholdMethod.KMEANS
    # )
    bench = "carcinogenesis"
    cross_validate_tdl(
        f"../sml-benchmarks/{bench}/{bench}.owl",
        f"../sml-benchmarks/{bench}/full/pos.txt",
        f"../sml-benchmarks/{bench}/full/neg.txt",
        max_runtime=10,
    )


if __name__ == "__main__":
    main()

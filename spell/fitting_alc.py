from collections.abc import Iterable
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
import time
from typing import Any


from pysat.card import CardEnc, EncType
from pysat.solvers import Solver


from .structures import (
    Signature,
    Structure,
    restrict_to_neighborhood,
)

from .fitting import (
    determine_relevant_symbols,
)

# There should be 2079 trees with 13 nodes. Seems like a sensible limit
# BUT: experiments suggest that when finding a single path of size k, there is a slowdown for 11 and above
# Indeed, 10 seems to be a local minimum
TREE_TEMPLATE_LIMIT = 10

d_op = {0: "TOP", 1: "BOT", 2: "NEG", 3: "AND", 4: "OR", 5: "EX", 6: "ALL"}
TOP = 0
BOT = 1
NEG = 2
AND = 3
OR = 4
EX = 5
ALL = 6
ALC_OP = frozenset({NEG, AND, OR, EX, ALL})
ALC_OP_B = {NEG, AND, OR}

X = 0
Z = 2
V = 4
L = 5
T = 6


def bisim(
    A: Structure, sigma: Signature, P: list[int], N: list[int], max_k: int
) -> tuple[Structure, list[int], list[int]]:

    color_register: dict[Any, int] = {}
    color: dict[int, int] = {}

    for i in range(A.max_ind):
        tp = frozenset(cn for cn in sigma.conceptnames if i in A.cn_ext[cn])
        if tp not in color_register:
            color_register[tp] = len(color_register)
        color[i] = color_register[tp]

    for _ in range(max_k):
        ncolor = {}
        for a in range(A.max_ind):
            tp2: list[tuple[int, str]] = [(color[a], "")]
            for b, r in A.rn_ext[a]:
                tp2.append((color[b], r))
            tpf2 = frozenset(tp2)

            if tpf2 not in color_register:
                color_register[tpf2] = len(color_register)
            ncolor[a] = color_register[tpf2]

        color = ncolor

    color2class: dict[int, int] = {}
    for a in range(A.max_ind):
        if color[a] not in color2class:
            color2class[color[a]] = len(color2class)

    B = Structure(len(color2class), {}, {}, {}, A.nsmap)

    for cn in sigma.conceptnames:
        B.cn_ext[cn] = set()
        for a in A.cn_ext[cn]:
            B.cn_ext[cn].add(color2class[color[a]])

    for a in range(A.max_ind):
        ca = color2class[color[a]]
        if ca not in B.rn_ext:
            B.rn_ext[ca] = set()
        for b, r in A.rn_ext[a]:
            cb = color2class[color[b]]
            B.rn_ext[ca].add((cb, r))

    print(
        "== Bisimulation reduction reduced from size {} to size {}".format(
            A.max_ind, B.max_ind
        )
    )

    return (
        B,
        [color2class[color[p]] for p in P],
        [color2class[color[n]] for n in N],
    )


def cn_types(A: Structure, sigma: Signature) -> set[frozenset[str]]:
    res: set[frozenset[str]] = set()
    for i in range(A.max_ind):
        tp = frozenset(cn for cn in sigma.conceptnames if i in A.cn_ext[cn])
        res.add(tp)
    return res


@dataclass
class STree:
    label: str
    children: list["STree"]

    def to_tree_int(self) -> list[str]:
        res = [self.label]
        for c in self.children:
            cs = c.to_tree_int()
            res.append(" +-- " + cs[0])
            res.extend(["    " + s for s in cs[1:]])
        return res

    def to_tree(self) -> str:
        return "\n".join(self.to_tree_int())

    def to_string(self):
        ns = str(self.label)
        if len(self.children) == 0:
            return ns
        elif len(self.children) == 1:
            if self.label.startswith("all"):
                nss = f"∀.{ns[4:]}"
            elif self.label.startswith("ex"):
                nss = f"∃.{ns[3:]}"
            else:
                nss = ns
            return f"{nss} {self.children[0].to_string()}"
        elif len(self.children) == 2:
            return f"({self.children[0].to_string()} {self.label} {self.children[1].to_string()})"
        else:
            return ""


@dataclass(slots=True)
class Instance:
    A: Structure
    P: list[int]
    N: list[int]
    sigma: Signature
    op: frozenset[int]

    def op_b(self):
        return self.op.intersection(ALC_OP_B)

    def op_r(self):
        return self.op.difference(ALC_OP_B)


class ALCSATEncoding:

    def __init__(self, instance: Instance, tree_templates: bool, type_encoding: bool):
        self.inst: Instance = instance
        self.tree_templates: bool = tree_templates
        self.type_encoding: bool = type_encoding
        self.solver: Solver | None = None
        self.k: int = 0
        self.vars: dict[Any, int] = {}
        self.max_var: int = 0
        self.types: set[frozenset[str]] = set()
        self.clauses: list[Iterable[int]] = []

    def add_clause(self, c: Iterable[int]):
        self.clauses.append(c)

    def create_vars(self):
        d: dict[Any, int] = {}
        i = 1
        d[X, TOP] = i
        d[X, BOT] = i * self.k + 1
        i += 1
        for cn in self.inst.sigma.conceptnames:
            d[X, cn] = i * self.k + 1
            i += 1
        for op in self.inst.op_b():
            d[X, op] = i * self.k + 1
            i += 1
        if EX in self.inst.op:
            for c in self.inst.sigma.rolenames:
                d[X, EX, c] = i * self.k + 1
                i += 1
        if ALL in self.inst.op:
            for c in self.inst.sigma.rolenames:
                d[X, ALL, c] = i * self.k + 1
                i += 1
        for a in range(self.inst.A.max_ind):
            d[Z, a] = i * self.k + 1
            i += 1
        for j in range(self.k):
            d[V, 1, j] = i * self.k + 1
            i += 1
        for j in range(self.k):
            d[V, 2, j] = i * self.k + 1
            i += 1

        if self.type_encoding:
            for tp in self.types:
                d[X, tp] = i * self.k + 1
                i += 1

            # For leaves
            d[L] = i * self.k + 1
            i += 1

        self.max_var = i * self.k + 1

        if self.tree_templates:
            tree_k = min(self.k, TREE_TEMPLATE_LIMIT)
            for idx, _ in enumerate(all_trees(tree_k, 0)):
                d[T, idx] = self.max_var
                self.max_var += 1

        self.vars = d

    def syn_tree_encoding(self):
        for i in range(self.k):
            x_vars = (
                [self.vars[X, o] + i for o in self.inst.op_b()]
                + [
                    self.vars[X, o, r] + i
                    for o in self.inst.op_r()
                    for r in self.inst.sigma.rolenames
                ]
                + [self.vars[X, cn] + i for cn in self.inst.sigma.conceptnames]
                + [self.vars[X, TOP] + i, self.vars[X, BOT] + i]
            )

            for clause in CardEnc.equals(lits=x_vars, encoding=EncType.pairwise):
                self.add_clause(clause)

        for i in range(self.k):
            v_vars = [self.vars[V, 1, i] + j for j in range(i + 1, self.k)] + [
                self.vars[V, 2, i] + j for j in range(i + 1, self.k - 1)
            ]

            # At most one of the y-vars
            for clause in CardEnc.atmost(lits=v_vars, encoding=EncType.pairwise):
                self.add_clause(clause)

            for r in self.inst.sigma.rolenames:
                for op in self.inst.op_r():
                    self.add_clause(
                        [-(self.vars[X, op, r] + i)]
                        + [self.vars[V, 1, i] + j for j in range(i + 1, self.k)]
                    )
                    for j in range(i + 1, self.k - 1):
                        self.add_clause(
                            [-(self.vars[X, op, r] + i), -(self.vars[V, 2, i] + j)]
                        )

            if NEG in self.inst.op_b():
                self.add_clause(
                    [-(self.vars[X, NEG] + i)]
                    + [self.vars[V, 1, i] + j for j in range(i + 1, self.k)]
                )
                for j in range(i + 1, self.k):
                    self.add_clause(
                        [-(self.vars[X, NEG] + i), -(self.vars[V, 2, i] + j)]
                    )

            for op in self.inst.op_b() - {NEG}:
                self.add_clause(
                    [-(self.vars[X, op] + i)]
                    + [self.vars[V, 2, i] + j for j in range(i + 1, self.k - 1)]
                )
                for j in range(i + 1, self.k):
                    self.add_clause(
                        [-(self.vars[X, op] + i), -(self.vars[V, 1, i] + j)]
                    )

            for cn in self.inst.sigma.conceptnames:

                if self.type_encoding:
                    # Is a leaf
                    self.add_clause((-(self.vars[X, cn] + i), (self.vars[L] + i)))

            for j in range(i + 1, self.k):
                for cn in self.inst.sigma.conceptnames:
                    self.add_clause(
                        (-(self.vars[X, cn] + i), -(self.vars[V, 1, i] + j))
                    )
                    self.add_clause(
                        (-(self.vars[X, cn] + i), -(self.vars[V, 2, i] + j))
                    )

                for b in {TOP, BOT}:
                    self.add_clause((-(self.vars[X, b] + i), -(self.vars[V, 1, i] + j)))
                    self.add_clause((-(self.vars[X, b] + i), -(self.vars[V, 2, i] + j)))

            # Exactly one predecessor
            possible_preds = (
                [self.vars[V, 1, j] + i for j in range(0, i)]
                + [self.vars[V, 2, j] + i for j in range(0, i)]
                + [self.vars[V, 2, j] + i - 1 for j in range(0, i - 1)]
            )
            if len(possible_preds) > 0:
                for clause in CardEnc.equals(
                    lits=possible_preds, encoding=EncType.pairwise
                ):
                    self.add_clause(clause)

    def symmetry_breaking(self):

        # Symmetry breaking: associativity of sqcap and sqcup
        # There is always a syntax tree where one of the successors of AND is not an AND
        for i in range(self.k):
            for j in range(i + 1, self.k - 1):
                if AND in self.inst.op_b():
                    self.add_clause(
                        (
                            -(self.vars[X, AND] + i),
                            -(self.vars[V, 2, i] + j),
                            -(self.vars[X, AND] + j),
                            -(self.vars[X, AND] + j + 1),
                        )
                    )
                if OR in self.inst.op_b():
                    self.add_clause(
                        (
                            -(self.vars[X, OR] + i),
                            -(self.vars[V, 2, i] + j),
                            -(self.vars[X, OR] + j),
                            -(self.vars[X, OR] + j + 1),
                        )
                    )

        # Symmetry breaking: there is always a syntax tree where NEG is not nested directly under ALL or EX or NEG
        if (
            EX in self.inst.op_r()
            and ALL in self.inst.op_r()
            and NEG in self.inst.op_b()
        ):
            for i in range(self.k):
                for j in range(i + 1, self.k):
                    self.add_clause(
                        (-(self.vars[V, 1, i] + j), -(self.vars[X, NEG] + j))
                    )

        # Symmetry breaking: rewrites involving TOP and BOT?
        for i in range(self.k):
            for j in range(i + 1, self.k - 1):
                if AND in self.inst.op_b():
                    self.add_clause(
                        (
                            -(self.vars[X, AND] + i),
                            -(self.vars[V, 2, i] + j),
                            -(self.vars[X, TOP] + j),
                        )
                    )
                    self.add_clause(
                        (
                            -(self.vars[X, AND] + i),
                            -(self.vars[V, 2, i] + j),
                            -(self.vars[X, TOP] + j + 1),
                        )
                    )
                    self.add_clause(
                        (
                            -(self.vars[X, AND] + i),
                            -(self.vars[V, 2, i] + j),
                            -(self.vars[X, BOT] + j),
                        )
                    )
                    self.add_clause(
                        (
                            -(self.vars[X, AND] + i),
                            -(self.vars[V, 2, i] + j),
                            -(self.vars[X, BOT] + j + 1),
                        )
                    )
                if OR in self.inst.op_b():
                    self.add_clause(
                        (
                            -(self.vars[X, OR] + i),
                            -(self.vars[V, 2, i] + j),
                            -(self.vars[X, TOP] + j),
                        )
                    )
                    self.add_clause(
                        (
                            -(self.vars[X, OR] + i),
                            -(self.vars[V, 2, i] + j),
                            -(self.vars[X, TOP] + j + 1),
                        )
                    )
                    self.add_clause(
                        (
                            -(self.vars[X, OR] + i),
                            -(self.vars[V, 2, i] + j),
                            -(self.vars[X, BOT] + j),
                        )
                    )
                    self.add_clause(
                        (
                            -(self.vars[X, OR] + i),
                            -(self.vars[V, 2, i] + j),
                            -(self.vars[X, BOT] + j + 1),
                        )
                    )

        if self.tree_templates:

            tree_k = min(self.k, TREE_TEMPLATE_LIMIT)

            tree_vars = []
            for idx, _ in enumerate(all_trees(tree_k)):
                tree_vars.append(self.vars[T, idx])

            for clause in CardEnc.equals(lits=tree_vars, encoding=EncType.pairwise):
                self.add_clause(clause)

            for idx, t in enumerate(all_trees(tree_k)):
                for i in range(tree_k):

                    # Only restrict leaves if the tree template is not a prefix
                    if len(t[i]) == 0 and tree_k == self.k:
                        for j in range(i + 1, tree_k):
                            self.add_clause(
                                (-tree_vars[idx], -(self.vars[V, 1, i] + j))
                            )
                            self.add_clause(
                                (-tree_vars[idx], -(self.vars[V, 2, i] + j))
                            )

                    if len(t[i]) == 1:
                        self.add_clause(
                            (-tree_vars[idx], (self.vars[V, 1, i] + t[i][0]))
                        )
                    if len(t[i]) == 2:
                        self.add_clause(
                            (-tree_vars[idx], (self.vars[V, 2, i] + t[i][0]))
                        )

    def evaluation_constraints(self):

        for a in range(self.inst.A.max_ind):
            for i in range(self.k):
                if NEG in self.inst.op_b():
                    for j in range(i + 1, self.k):
                        self.add_clause(
                            (
                                -(self.vars[X, NEG] + i),
                                -(self.vars[Z, a] + i),
                                -(self.vars[V, 1, i] + j),
                                -(self.vars[Z, a] + j),
                            )
                        )
                        self.add_clause(
                            (
                                -(self.vars[X, NEG] + i),
                                (self.vars[Z, a] + i),
                                -(self.vars[V, 1, i] + j),
                                (self.vars[Z, a] + j),
                            )
                        )

                if AND in self.inst.op_b():
                    for j in range(i + 1, self.k - 1):
                        self.add_clause(
                            (
                                -(self.vars[X, AND] + i),
                                -(self.vars[Z, a] + i),
                                -(self.vars[V, 2, i] + j),
                                self.vars[Z, a] + j,
                            )
                        )
                        self.add_clause(
                            (
                                -(self.vars[X, AND] + i),
                                -(self.vars[Z, a] + i),
                                -(self.vars[V, 2, i] + j),
                                self.vars[Z, a] + j + 1,
                            )
                        )
                        self.add_clause(
                            (
                                -(self.vars[X, AND] + i),
                                (self.vars[Z, a] + i),
                                -(self.vars[V, 2, i] + j),
                                -(self.vars[Z, a] + j + 1),
                                -(self.vars[Z, a] + j),
                            )
                        )

                if OR in self.inst.op_b():
                    for j in range(i + 1, self.k - 1):
                        self.add_clause(
                            (
                                -(self.vars[X, OR] + i),
                                (self.vars[Z, a] + i),
                                -(self.vars[V, 2, i] + j),
                                -(self.vars[Z, a] + j),
                            )
                        )
                        self.add_clause(
                            (
                                -(self.vars[X, OR] + i),
                                (self.vars[Z, a] + i),
                                -(self.vars[V, 2, i] + j),
                                -(self.vars[Z, a] + j + 1),
                            )
                        )
                        self.add_clause(
                            (
                                -(self.vars[X, OR] + i),
                                -(self.vars[Z, a] + i),
                                -(self.vars[V, 2, i] + j),
                                (self.vars[Z, a] + j + 1),
                                (self.vars[Z, a] + j),
                            )
                        )

                if ALL in self.inst.op_r():
                    for r in self.inst.sigma.rolenames:
                        successors = [b for (b, p) in self.inst.A.rn_ext[a] if p == r]
                        if len(successors) == 0:
                            # Optimization: most individuals don't have successors
                            self.add_clause(
                                (-(self.vars[X, ALL, r] + i), (self.vars[Z, a] + i))
                            )
                        else:
                            for j in range(i + 1, self.k):
                                self.add_clause(
                                    [
                                        -(self.vars[X, ALL, r] + i),
                                        (self.vars[Z, a] + i),
                                        -(self.vars[V, 1, i] + j),
                                    ]
                                    + [-(self.vars[Z, b] + j) for b in successors]
                                )
                                for b in successors:
                                    self.add_clause(
                                        (
                                            -(self.vars[X, ALL, r] + i),
                                            -(self.vars[Z, a] + i),
                                            -(self.vars[V, 1, i] + j),
                                            self.vars[Z, b] + j,
                                        )
                                    )

                if EX in self.inst.op_r():
                    for r in self.inst.sigma.rolenames:
                        successors = [b for (b, p) in self.inst.A.rn_ext[a] if p == r]
                        if len(successors) == 0:
                            # Optimization: most individuals don't have successors
                            self.add_clause(
                                (-(self.vars[X, EX, r] + i), -(self.vars[Z, a] + i))
                            )
                        else:
                            for j in range(i + 1, self.k):
                                self.add_clause(
                                    [
                                        -(self.vars[X, EX, r] + i),
                                        -(self.vars[Z, a] + i),
                                        -(self.vars[V, 1, i] + j),
                                    ]
                                    + [(self.vars[Z, b] + j) for b in successors]
                                )
                                for b in successors:
                                    self.add_clause(
                                        (
                                            -(self.vars[X, EX, r] + i),
                                            (self.vars[Z, a] + i),
                                            -(self.vars[V, 1, i] + j),
                                            -(self.vars[Z, b] + j),
                                        )
                                    )

                self.add_clause((-(self.vars[X, TOP] + i), (self.vars[Z, a] + i)))
                self.add_clause((-(self.vars[X, BOT] + i), -(self.vars[Z, a] + i)))

        if not self.type_encoding:
            for cn in self.inst.sigma.conceptnames:
                for i in range(self.k):
                    for a in range(self.inst.A.max_ind):
                        if a in self.inst.A.cn_ext[cn]:
                            self.add_clause(
                                (-(self.vars[X, cn] + i), self.vars[Z, a] + i)
                            )
                        else:
                            self.add_clause(
                                (-(self.vars[X, cn] + i), -(self.vars[Z, a] + i))
                            )

        if self.type_encoding:
            for i in range(self.k):
                for tp in self.types:
                    for cn in self.inst.sigma.conceptnames:
                        if cn in tp:
                            self.add_clause(
                                (-(self.vars[X, cn] + i), self.vars[X, tp] + i)
                            )
                        if cn not in tp:
                            self.add_clause(
                                (-(self.vars[X, cn] + i), -(self.vars[X, tp] + i))
                            )

            for a in range(self.inst.A.max_ind):
                tp = frozenset(
                    {
                        cn
                        for cn in self.inst.sigma.conceptnames
                        if a in self.inst.A.cn_ext[cn]
                    }
                )
                assert tp in self.types
                for i in range(self.k):
                    self.add_clause((-(self.vars[X, tp] + i), self.vars[Z, a] + i))
                    # Problem: the following should only happen for CONCEPT NAME NODES. We thus need an additional variable that is true iff a node is a concept name node
                    self.add_clause(
                        (
                            (self.vars[X, tp] + i),
                            -(self.vars[Z, a] + i),
                            -(self.vars[L] + i),
                        )
                    )

    def fitting_constraints_approximate(self, n: int):
        assert self.solver
        lits = [self.vars[Z, a] for a in self.inst.P] + [
            -self.vars[Z, b] for b in self.inst.N
        ]

        enc = CardEnc.atleast(
            lits, bound=n, top_id=self.max_var, encoding=EncType.kmtotalizer
        )
        self.max_var = max(enc.nv, self.max_var)
        for clause in enc.clauses:
            self.solver.add_clause(clause)

    def model_n(self) -> int:
        assert self.solver and self.solver.get_status()
        # Return the number of positive/negative examples that is claimed to be covered by a model
        m = self.solver.get_model()
        assert isinstance(m, list)

        res: int = 0
        for p in self.inst.P:
            if self.vars[Z, p] + 0 in m:
                res += 1

        for n in self.inst.N:
            if self.vars[Z, n] + 0 not in m:
                res += 1
        return res

    def nodelabel(self, i: int) -> str:
        assert self.solver and self.solver.get_status()
        m = self.solver.get_model()
        assert isinstance(m, list)
        if (self.vars[X, TOP] + i) in m:
            return d_op[TOP]
        if (self.vars[X, BOT] + i) in m:
            return d_op[BOT]
        for cn in self.inst.sigma.conceptnames:
            if (self.vars[X, cn] + i) in m:
                return cn
        for op in self.inst.op_b():
            if (self.vars[X, op] + i) in m:
                return d_op[op]
        if EX in self.inst.op:
            for r in self.inst.sigma.rolenames:
                if (self.vars[X, EX, r] + i) in m:
                    return f"ex.{r}"
        if ALL in self.inst.op:
            for r in self.inst.sigma.rolenames:
                if (self.vars[X, ALL, r] + i) in m:
                    return f"all.{r}"
        assert False

    def modelToTree(self, i: int = 0) -> STree:
        assert self.solver and self.solver.get_status()
        m = self.solver.get_model()
        assert isinstance(m, list)

        label = self.nodelabel(i)

        children: list[STree] = []
        for j in range(i + 1, self.k):
            if (self.vars[V, 1, i] + j) in m:
                children.append(self.modelToTree(j))
            if j < self.k - 1 and (self.vars[V, 2, i] + j) in m:
                children.append(self.modelToTree(j))
                children.append(self.modelToTree(j + 1))
        return STree(label, children)


ApproxTask = tuple[ALCSATEncoding, int, int, float, list[int]]


def solve_approx(task: ApproxTask):

    enc, k, min_n, timeout, tt = task

    time_start = time.perf_counter()
    n = max(len(enc.inst.P), len(enc.inst.N), min_n)

    dt = time.perf_counter() - time_start

    best_sol = None
    best_accuracy = 0
    best_n = 0

    if len(tt) > 0:
        enc.add_clause([enc.vars[T, t] for t in tt])

    enc.solver = Solver(name="g4", incr=True, bootstrap_with=enc.clauses)

    while n <= len(enc.inst.P) + len(enc.inst.N) and (dt < timeout or timeout == -1):
        enc.fitting_constraints_approximate(n)

        dt = time.perf_counter() - time_start
        remaining_time = -1
        if timeout != -1:
            remaining_time = timeout - dt

        if not enc.solver.solve():
            # print(f"Not satisfiable for k={k}, n={n}, tt = {tt}")
            return best_accuracy, best_n, k, best_sol

        best_sol = enc.modelToTree()
        model_n = enc.model_n()

        best_accuracy = model_n / (len(enc.inst.P) + len(enc.inst.N))
        best_n = model_n
        print(f"Satisfiable for k={k}, n={model_n}, acc={best_accuracy}")
        print(best_sol.to_tree())
        n = model_n + 1
        dt = time.perf_counter() - time_start

    return best_accuracy, best_n, k, best_sol


class FittingALC:
    def __init__(
        self,
        A: Structure,
        max_k: int,
        P: list[int],
        N: list[int],
        op=ALC_OP,
        tree_templates=True,
        type_encoding=True,
        workers: int = 1,
    ):
        A2, m = restrict_to_neighborhood(max_k - 1, A, P + N)
        P2: list[int] = [m[a] for a in P]
        N2: list[int] = [m[b] for b in N]
        sigma: Signature = determine_relevant_symbols(A, P + N, 1, max_k - 1)
        self.max_k: int = max_k
        self.inst: Instance = Instance(A2, P2, N2, sigma, op)
        self.tree_templates: bool = tree_templates
        self.type_encoding: bool = type_encoding
        self.workers: int = workers

    def solve(self):
        acc, _, _ = self.solve_incr(self.max_k, self.max_k)
        return acc == 1.0

    def solve_incr(self, max_k: int, start_k: int = 1, timeout: float = -1):
        return self.solve_incr_approx(
            max_k, start_k, len(self.inst.P) + len(self.inst.N), timeout=timeout
        )

    def solve_incr_approx(
        self, max_k: int, start_k: int = 1, min_n: int = 1, timeout: float = -1
    ):
        time_start = time.perf_counter()
        k: int = start_k
        n: int = max(len(self.inst.P), len(self.inst.N), min_n)
        best_sol: STree = STree(d_op[TOP], [])
        best_acc = 0
        dt = time.perf_counter() - time_start

        self.inst.A, self.inst.P, self.inst.N = bisim(
            self.inst.A, self.inst.sigma, self.inst.P, self.inst.N, max_k
        )

        with ProcessPoolExecutor(self.workers) as p:

            while k <= max_k and (dt < timeout or timeout == -1) and best_acc < 1.0:
                remaining_time = -1
                if timeout != -1:
                    remaining_time = timeout - dt

                enc = ALCSATEncoding(self.inst, True, True)
                enc.k = k
                enc.types = cn_types(enc.inst.A, enc.inst.sigma)
                enc.create_vars()
                enc.syn_tree_encoding()
                enc.evaluation_constraints()
                enc.symmetry_breaking()

                if self.workers > 1:
                    tree_k = min(k, TREE_TEMPLATE_LIMIT)
                    tasks: list[ApproxTask] = [
                        (enc, k, n, remaining_time, [tt])
                        for tt in range(len(all_trees(tree_k)))
                    ]
                else:
                    tasks = [(enc, k, n, remaining_time, [])]

                fts = [p.submit(solve_approx, task) for task in tasks]

                progress = 0
                for ft in concurrent.futures.as_completed(fts):
                    k_acc, k_n, _, k_sol = ft.result()
                    progress += 1

                    print(
                        "Searching with k = {}, progress {}/{}".format(
                            k, progress, len(tasks)
                        )
                    )

                    if k_acc > best_acc:
                        assert k_sol
                        best_sol = k_sol
                        best_acc = k_acc
                        n = k_n + 1

                k += 1
                dt = time.perf_counter() - time_start

        return best_acc, k, best_sol


# Generate non-isomorphic trees of size n with at most binary outdegree
def all_trees(
    k: int, start: int = 0
) -> list[list[tuple[int] | tuple[int, int] | tuple[()]]]:
    if k == 1:
        return [[()]]

    res = []
    for i in range(1, (k - 1) // 2 + 1):
        for idx_a, a in enumerate(all_trees(i, start + 2)):
            for idx_b, b in enumerate(all_trees((k - 1) - i, start + i + 1)):
                # If a, b have the same size, skip pairs that already occured
                if i == (k - 1) - i and idx_b < idx_a:
                    continue
                # Whacky tree composition to ensure that children of binary nodes are always adjacent
                # (the start + 2 for the a trees is for the same purpose)
                res.append([(start + 1, start + 2)] + [a[0]] + [b[0]] + a[1:] + b[1:])

    for a in all_trees(k - 1, start + 1):
        res.append([(start + 1,)] + a)

    return res

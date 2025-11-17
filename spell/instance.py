from dataclasses import dataclass
from enum import IntEnum
from typing import Any

from spell.structures import Signature, Structure, ind


class OP(IntEnum):
    CN = -1
    TOP = 0
    BOT = 1
    NEG = 2
    AND = 3
    OR = 4
    EX = 5
    ALL = 6
    LE = 7
    GE = 8


ALC_OP = frozenset({OP.NEG, OP.AND, OP.OR, OP.EX, OP.ALL})
ALC_OP_B = frozenset({OP.NEG, OP.AND, OP.OR})
ALC_OP_R = frozenset({OP.EX, OP.ALL})
ALC_OP_Q = frozenset({OP.LE, OP.GE})

d_op = {
    0: "TOP",
    1: "BOT",
    2: "NEG",
    3: "AND",
    4: "OR",
    5: "EX",
    6: "ALL",
    7: "LE",
    8: "GE",
}


@dataclass(slots=True)
class ALCConcept:
    operation: OP
    name: str
    value: Any
    children: list["ALCConcept"]

    def to_tree_int(self) -> list[str]:
        if self.operation == OP.CN:
            # concept name
            res = [self.name]
        elif self.operation in {OP.ALL, OP.EX}:
            res = [f"{d_op[self.operation]}.{self.name}"]
        elif self.operation in {OP.GE, OP.LE}:
            res = [f"{d_op[self.operation]}{self.value} {self.name}"]
        else:
            res = [f"{d_op[self.operation]}"]

        for c in self.children:
            cs = c.to_tree_int()
            res.append(" +-- " + cs[0])
            res.extend(["    " + s for s in cs[1:]])
        return res

    def to_tree(self) -> str:
        return "\n".join(self.to_tree_int())

    def mc(self, A: Structure, a: int) -> bool:
        assert a in ind(A)

        if self.operation == OP.TOP:
            return True
        if self.operation == OP.BOT:
            return False
        if self.operation == OP.CN:
            return a in A.cn_ext[self.name]
        if self.operation == OP.AND:
            assert len(self.children) == 2
            return self.children[0].mc(A, a) and self.children[1].mc(A, a)
        if self.operation == OP.OR:
            assert len(self.children) == 2
            return self.children[0].mc(A, a) or self.children[1].mc(A, a)
        if self.operation == OP.NEG:
            assert len(self.children) == 1
            return not self.children[0].mc(A, a)
        if self.operation == OP.EX:
            assert len(self.children) == 1
            cnt = len(
                [
                    b
                    for (b, r) in A.rn_ext[a]
                    if r == self.name and self.children[0].mc(A, b)
                ]
            )
            return cnt >= 1
        if self.operation == OP.ALL:
            assert len(self.children) == 1
            cnt = len(
                [
                    b
                    for (b, r) in A.rn_ext[a]
                    if r == self.name and not self.children[0].mc(A, b)
                ]
            )
            return cnt == 0
        if self.operation == OP.GE:
            assert len(self.children) == 1
            cnt = len(
                [
                    b
                    for (b, r) in A.rn_ext[a]
                    if r == self.name and self.children[0].mc(A, b)
                ]
            )
            return cnt >= self.value
        if self.operation == OP.LE:
            assert len(self.children) == 1
            cnt = len(
                [
                    b
                    for (b, r) in A.rn_ext[a]
                    if r == self.name and self.children[0].mc(A, b)
                ]
            )
            return cnt <= self.value
        assert False


@dataclass(slots=True)
class Instance:
    A: Structure
    P: list[int]
    N: list[int]
    sigma: Signature
    op: frozenset[OP]
    max_q: int = 2

    def op_b(self):
        return self.op.intersection(ALC_OP_B)

    def op_r(self):
        return self.op.intersection(ALC_OP_R)

    def op_q(self):
        return self.op.intersection(ALC_OP_Q)

    def accuracy(self, st: frozenset[int]) -> float:
        tp = 0
        tn = 0

        for a in self.P:
            if a in st:
                tp += 1

        for a in self.N:
            if a not in st:
                tn += 1

        return (tp + tn) / (len(self.P) + len(self.N))

    def f1score(self, st: frozenset[int]) -> float:
        tp = 0
        fn = 0
        fp = 0

        for a in self.P:
            if a in st:
                tp += 1
            else:
                fn += 1

        for a in self.N:
            if a in st:
                fp += 1

        return (2 * tp) / (2 * tp + fp + fn)

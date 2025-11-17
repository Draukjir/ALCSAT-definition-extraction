from dataclasses import dataclass
from enum import IntEnum

from spell.structures import Signature, Structure


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

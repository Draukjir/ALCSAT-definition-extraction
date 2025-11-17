from dataclasses import dataclass
from enum import IntEnum

from spell.structures import Signature, Structure


class OP(IntEnum):
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

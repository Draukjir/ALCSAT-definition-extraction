from typing import Any
from spell.instance import Instance
from spell.structures import Signature, Structure


def prune_conceptnames(inst: Instance) -> Instance:
    A = inst.A
    sigma = Signature(inst.sigma.conceptnames, inst.sigma.rolenames)

    redundant: set[str] = set()
    for cn1 in sigma.conceptnames:
        for cn2 in sigma.conceptnames:
            if cn1 < cn2 and A.cn_ext[cn1] == A.cn_ext[cn2]:
                redundant.add(cn2)

    print(f"== Pruning {len(redundant)} redundant concept names")

    sigma.conceptnames = [cn for cn in sigma.conceptnames if cn not in redundant]

    return Instance(A, inst.P, inst.N, sigma, inst.op, inst.max_q)


def pick_data_thresholds(ranges: dict[str, set[Any]]) -> dict[str, set[Any]]:
    result: dict[str, set[Any]] = {}

    for p, values in ranges.items():
        if values == {True, False}:
            result[p] = {True}
        elif len(values) <= 10:
            result[p] = values
        else:
            thresholds = set()
            vs = list(values)
            vs.sort()
            for i in range(20):
                thresholds.add(vs[int(len(vs) / 20 * i) - 1])
            result[p] = thresholds

    return result


def encode_dataproperties(inst: Instance) -> Instance:
    A = inst.A
    sigma = Signature(inst.sigma.conceptnames, inst.sigma.rolenames)

    ranges: dict[str, set[Any]] = {}

    for a in range(A.max_ind):
        for v, t, p in A.dp_ext[a]:
            if p not in ranges:
                ranges[p] = set()
            ranges[p].add(v)

    thresholds = pick_data_thresholds(ranges)

    B = Structure(A.max_ind, {}, {}, {}, {}, A.nsmap)

    for cn in sigma.conceptnames:
        B.cn_ext[cn] = set(A.cn_ext[cn])

    for a in range(A.max_ind):
        B.rn_ext[a] = set(A.rn_ext[a])

    for a in range(A.max_ind):
        for v, t, p in A.dp_ext[a]:
            for r in thresholds[p]:
                cn = f"{p}>={r}"
                if cn not in B.cn_ext:
                    B.cn_ext[cn] = set()
                    sigma.conceptnames.append(cn)
                if v >= r:
                    B.cn_ext[cn].add(a)

    return Instance(B, inst.P, inst.N, sigma, inst.op, inst.max_q)


def color_refinement(
    A: Structure, sigma: Signature, alc_q: bool, iterations: int
) -> dict[int, int]:
    color_register: dict[tuple[tuple[int, str], ...], int] = {}
    color: dict[int, int] = {}

    for a in range(A.max_ind):
        tp = tuple([(0, cn) for cn in sigma.conceptnames if a in A.cn_ext[cn]])
        if tp not in color_register:
            color_register[tp] = len(color_register)
        color[a] = color_register[tp]

    for _ in range(iterations):
        ncolor: dict[int, int] = {}
        for a in range(A.max_ind):
            tp2 = list((0, cn) for cn in sigma.conceptnames if a in A.cn_ext[cn])
            for b, r in A.rn_ext[a]:
                tp2.append((color[b], r))
            if not alc_q:
                tp2 = list(set(tp2))
            tp2.sort()
            tpf2 = tuple(tp2)

            if tpf2 not in color_register:
                color_register[tpf2] = len(color_register)
            ncolor[a] = color_register[tpf2]

        color = ncolor

    return color


def bisimulation_reduction(inst: Instance, max_k: int) -> Instance:
    # TODO: this ignores datatypes for now
    color = color_refinement(inst.A, inst.sigma, True, max_k)

    A = inst.A
    sigma = inst.sigma

    color2class: dict[int, int] = {}
    for a in range(A.max_ind):
        if color[a] not in color2class:
            color2class[color[a]] = len(color2class)

    B = Structure(len(color2class), {}, {}, {}, {}, A.nsmap)

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

    return Instance(
        B,
        [color2class[color[p]] for p in inst.P],
        [color2class[color[n]] for n in inst.N],
        sigma,
        inst.op,
    )

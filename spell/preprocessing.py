from collections import defaultdict
from typing import Any
from spell.instance import ALCConcept, Instance, OP
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


def decode_dataproperties(
    c: ALCConcept, reverse_mapping: dict[str, ALCConcept]
) -> ALCConcept:
    if c.operation == OP.CN and c.name in reverse_mapping:
        return reverse_mapping[c.name]

    nchildren = [decode_dataproperties(d, reverse_mapping) for d in c.children]

    return ALCConcept(c.operation, c.name, c.value, nchildren)


def encode_dataproperties(inst: Instance) -> tuple[Instance, dict[str, ALCConcept]]:
    A = inst.A
    sigma = Signature(list(inst.sigma.conceptnames), list(inst.sigma.rolenames))

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
        B.dp_ext[a] = []

    reverse_mapping: dict[str, ALCConcept] = {}

    for a in range(A.max_ind):
        for v, t, p in A.dp_ext[a]:
            for r in thresholds[p]:
                cn = f"{p}>={r}"
                if cn not in B.cn_ext:
                    B.cn_ext[cn] = set()
                    sigma.conceptnames.append(cn)
                    reverse_mapping[cn] = ALCConcept(OP.DGEQ, p, r, [])
                if v >= r:
                    B.cn_ext[cn].add(a)

    return Instance(B, inst.P, inst.N, sigma, inst.op, inst.max_q), reverse_mapping


def compute_multiplicities(
    color_register: dict[tuple[tuple[int, str], ...], int],
) -> tuple[dict[int, int], dict[tuple[int, int, str], int]]:
    color_multiplicities: dict[int, int] = defaultdict(lambda: 1)
    edge_multiplicities: dict[tuple[int, int, str], int] = defaultdict(int)

    for desc, c in color_register.items():
        for d, r in desc:
            if d != -1:
                edge_multiplicities[(c, d, r)] += 1

    for c, d, r in edge_multiplicities:
        color_multiplicities[d] = max(
            color_multiplicities[d], edge_multiplicities[(c, d, r)]
        )

    return color_multiplicities, edge_multiplicities


def color_refinement(
    A: Structure, sigma: Signature, alc_q: bool, iterations: int
) -> tuple[dict[int, int], dict[tuple[tuple[int, str], ...], int]]:
    color: dict[int, int] = dict.fromkeys(range(A.max_ind), 0)
    color_register: dict[tuple[tuple[int, str], ...], int] = {}

    local_types: dict[int, list[tuple[int, str]]] = {a: [] for a in range(A.max_ind)}
    for cn in sigma.conceptnames:
        for a in A.cn_ext[cn]:
            local_types[a].append((-1, cn))

    i = 0
    while i <= iterations or iterations == -1:
        i += 1
        ncolor: dict[int, int] = {}
        color_register = {}

        for a in range(A.max_ind):
            tp2 = list(local_types[a])
            for b, r in A.rn_ext[a]:
                tp2.append((color[b], r))
            if not alc_q:
                tp2 = list(set(tp2))
            tp2.sort()
            tpf2 = tuple(tp2)

            if tpf2 not in color_register:
                color_register[tpf2] = len(color_register)
            ncolor[a] = color_register[tpf2]

        if color == ncolor:
            # No change happened
            return color, color_register

        color = ncolor

    return color, color_register


def bisimulation_reduction(inst: Instance, max_k: int) -> Instance:
    color, color_register = color_refinement(inst.A, inst.sigma, True, max_k)

    color_multiplicities, edge_multiplicities = compute_multiplicities(color_register)

    A = inst.A
    sigma = inst.sigma

    color2ind: dict[tuple[int, int], int] = {}
    for a in range(A.max_ind):
        c = color[a]
        for i in range(color_multiplicities[c]):
            if (c, i) not in color2ind:
                color2ind[(c, i)] = len(color2ind)

    B = Structure(len(color2ind), {}, {}, {}, {}, A.nsmap)

    for cn in sigma.conceptnames:
        B.cn_ext[cn] = set()
        for a in A.cn_ext[cn]:
            for i in range(color_multiplicities[color[a]]):
                B.cn_ext[cn].add(color2ind[(color[a], i)])

    for c in color.values():
        for i in range(color_multiplicities[c]):
            ca = color2ind[(c, i)]
            if ca not in B.rn_ext:
                B.rn_ext[ca] = set()
                B.dp_ext[ca] = []

    for (c, d, r), n in edge_multiplicities.items():
        for i in range(color_multiplicities[c]):
            ca = color2ind[(c, i)]
            for j in range(n):
                cb = color2ind[(d, j)]
                B.rn_ext[ca].add((cb, r))

    print(
        f"== Bisimulation reduction reduced from size {A.max_ind} to size {B.max_ind}"
    )

    return Instance(
        B,
        [color2ind[(color[p], 0)] for p in inst.P],
        [color2ind[(color[n], 0)] for n in inst.N],
        sigma,
        inst.op,
    )


# Returns A restricted to individuals that can be reached in k steps from a
# Renames individuals
def restrict_to_neighborhood(
    k: int, A: Structure, starts: list[int]
) -> tuple[Structure, dict[int, int]]:
    cns = [cn for cn in A.cn_ext if A.cn_ext[cn]]

    # This has its own distance calculation to avoid computing the distance
    # for the entirety of A
    inds = set(starts)
    dist = dict.fromkeys(starts, 0)
    for r in range(k):
        step = set()
        for i1 in inds:
            for i2, rn in A.rn_ext[i1]:
                step.add(i2)
        inds = inds.union(step)
        for i in step:
            if i in dist:
                dist[i] = min(r + 1, dist[i])
            else:
                dist[i] = r + 1

    mapping = {old_ind: new_ind for (new_ind, old_ind) in enumerate(inds)}

    n_indmap = {
        name: mapping[old_ind]
        for name, old_ind in A.indmap.items()
        if old_ind in mapping
    }

    B = Structure(
        max_ind=len(inds),
        cn_ext={cn: set() for cn in cns},
        rn_ext={a: set() for a in range(len(inds))},
        dp_ext={a: set() for a in range(len(inds))},
        indmap=n_indmap,
        nsmap=A.nsmap,
    )

    for cn in cns:
        B.cn_ext[cn] = {mapping[ind] for ind in A.cn_ext[cn] & inds}

    for i1 in inds:
        B.rn_ext[mapping[i1]] = set()
        B.dp_ext[mapping[i1]] = A.dp_ext[i1]
        for i2, rn in A.rn_ext[i1]:
            if i2 in inds and dist[i1] < k:
                B.rn_ext[mapping[i1]].add((mapping[i2], rn))

    return (B, mapping)


def restrict_neighborhood(inst: Instance, k: int) -> Instance:
    A, mapping = restrict_to_neighborhood(k - 1, inst.A, inst.P + inst.N)
    P2 = [mapping[a] for a in inst.P]
    N2 = [mapping[a] for a in inst.N]
    return Instance(A, P2, N2, inst.sigma, inst.op, inst.max_q)

from spell.fitting import non_empty_symbols
from spell.instance import ALCConcept, OP, Instance
from spell.structures import Signature, Structure, structure_from_owl


def color_refinement(A: Structure, sigma: Signature, alc_q: bool, iterations: int):
    color: dict[int, int] = dict.fromkeys(range(A.max_ind), 0)
    color_register: list[dict[tuple[tuple[int, str], ...], int]] = []

    local_types: dict[int, list[tuple[int, str]]] = {a: [] for a in range(A.max_ind)}
    for cn in sigma.conceptnames:
        for a in A.cn_ext[cn]:
            local_types[a].append((-1, cn))

    i = 0
    while i <= iterations or iterations == -1:
        i += 1
        ncolor: dict[int, int] = {}
        color_register.append({})

        for a in range(A.max_ind):
            tp2 = list(local_types[a])
            for b, r in A.rn_ext[a]:
                tp2.append((color[b], r))
            if not alc_q:
                tp2 = list(set(tp2))
            tp2.sort()
            tpf2 = tuple(tp2)

            if tpf2 not in color_register[-1]:
                color_register[-1][tpf2] = len(color_register[-1])
            ncolor[a] = color_register[-1][tpf2]

        if color == ncolor:
            # No change happened
            return color, color_register

        color = ncolor

    return color, color_register


def merge_conj(conj: list[ALCConcept], op: OP) -> ALCConcept:
    if len(conj) == 0 and op == OP.AND:
        return ALCConcept(OP.TOP, "", None, tuple())
    if len(conj) == 0 and op == OP.OR:
        return ALCConcept(OP.BOT, "", None, tuple())

    if len(conj) == 1:
        return conj[0]

    d1 = merge_conj(conj[: len(conj) // 2], op)
    d2 = merge_conj(conj[len(conj) // 2 :], op)
    return ALCConcept(op, name="", value=None, children=(d1, d2))


def extract_alc_concept(color_register, color_a, color_b) -> ALCConcept:
    assert len(color_register) >= 1
    assert color_a != color_b
    assert color_a in color_register[-1].values()
    assert color_b in color_register[-1].values()

    rev = {id: c for (c, id) in color_register[-1].items()}
    ca = rev[color_a]
    cb = rev[color_b]

    props = set(ca)

    for c, r in props:
        count_a = list(ca).count((c, r))
        count_b = list(cb).count((c, r))

        if count_a == count_b:
            continue

        if c == -1:
            return ALCConcept(OP.CN, name=r, value=None, children=tuple())

        conj = set()

        for c2, s in cb:
            if s != r or c == c2:
                continue
            d = extract_alc_concept(color_register[0:-1], c, c2)
            conj.add(d)

        d = merge_conj(list(conj), OP.AND)

        if count_a > count_b:
            return ALCConcept(OP.GE, name=r, value=count_a, children=(d,))
        else:
            return ALCConcept(OP.LE, name=r, value=count_a, children=(d,))

    return ALCConcept(
        OP.NEG, "", None, (extract_alc_concept(color_register, color_b, color_a),)
    )

    return ALCConcept(OP.TOP, "", None, [])


def main():
    rn2 = {i: {} for i in range(7)}
    rn2[0] = {(1, "r")}
    rn2[2] = {(3, "r"), (4, "r")}
    rn2[5] = {(6, "r")}
    cn2 = {"A": {6}}
    A2 = Structure(7, cn2, rn2, {i: set() for i in range(6)}, {}, {})

    colors_alcq, cr = color_refinement(A2, Signature(["A"], ["r"]), True, -1)

    print(cr)

    print(colors_alcq)

    res = extract_alc_concept(cr, 0, 2)

    print(res.to_tree())

    benchmarks = ["mammographic"]

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

        colors_alcq, cr = color_refinement(A, sig, True, -1)

        pos_colors = {}
        neg_colors = {}
        for p in P:
            c = colors_alcq[p]
            if c not in pos_colors:
                pos_colors[c] = 0
            pos_colors[c] += 1

        for n in N:
            c = colors_alcq[n]
            if c not in neg_colors:
                neg_colors[c] = 0
            neg_colors[c] += 1

        cache = {}

        disj = set()
        for cp in pos_colors.keys():
            if cp in neg_colors and pos_colors[cp] < neg_colors[cp]:
                # Including this positive example would include a lot of negative
                # examples and thus not be beneficial for accuracy
                continue

            conj = set()
            for cn in neg_colors.keys():
                if cp == cn:
                    continue

                res = extract_alc_concept(cr, cp, cn)

                conj.add(res)

            d = merge_conj(list(conj), OP.AND)
            disj.add(d)

        c = merge_conj(list(disj), OP.OR)

        print(c.to_tree())
        print(c.size())

        ext: set[int] = set()
        for a in range(A.max_ind):
            if c.mc(A, a):
                ext.add(a)

        acc = Instance(A, P, N, sig, frozenset(), 2).accuracy(frozenset(ext))

        print(acc)


if __name__ == "__main__":
    main()

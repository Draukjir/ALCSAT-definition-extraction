from spell.fitting_alc import *


def test_trees():
    # See https://en.wikipedia.org/wiki/Wedderburn%E2%80%93Etherington_number
    assert len(all_trees(10)) == 207


def test_color_refinement():
    rn2 = {i: {} for i in range(7)}
    rn2[0] = {(1, "r")}
    rn2[2] = {(3, "r"), (4, "r")}
    rn2[5] = {(6, "r")}
    cn2 = {"A": {6}}
    A2 = Structure(7, cn2, rn2, {i: set() for i in range(6)}, {}, {})

    colors_alcq = color_refinement_alc(A2, Signature(["A"], ["r"]), True, 10)

    assert colors_alcq[0] != colors_alcq[2]
    assert colors_alcq[0] != colors_alcq[5]
    assert colors_alcq[2] != colors_alcq[5]
    assert colors_alcq[1] == colors_alcq[3]

    colors_alc = color_refinement_alc(A2, Signature(["A"], ["r"]), False, 10)
    assert colors_alc[0] == colors_alc[2]
    assert colors_alc[0] != colors_alc[5]
    assert colors_alc[1] == colors_alc[3]


def test1():
    A1 = Structure(
        3,
        {"A": {0, 1}, "B": {0, 2}},
        {i: {} for i in range(3)},
        {i: set() for i in range(6)},
        {},
        {},
    )
    P1 = [0]
    N1 = [1, 2]
    i = (A1, 3, P1, N1)
    f = FittingALC(*i, op={EX, ALL, OR, AND})
    assert f.solve()


def test2():
    rn2 = {i: {} for i in range(3)}
    rn2[0] = {(2, "r")}
    cn2 = {"A": {0, 1, 2}, "B": {0, 1}}
    A2 = Structure(3, cn2, rn2, {i: set() for i in range(6)}, {}, {})
    P2 = [0]
    N2 = [1]
    i = (A2, 3, P2, N2)
    f = FittingALC(*i, op={EX, ALL, OR, AND})
    assert f.solve()


def test3():
    A3 = Structure(
        3,
        {"A": {1}, "B": {2}},
        {i: {} for i in range(3)},
        {i: set() for i in range(6)},
        {},
        {},
    )
    P3 = [1, 2]
    N3 = [0]
    i = (A3, 3, P3, N3)
    f = FittingALC(*i, op={EX, ALL, OR, AND})
    assert f.solve()


def test4():
    rn4 = dict()
    rn4[0] = {(0, "r")}
    rn4[1] = {(2, "r")}
    rn4[2] = {(3, "r")}
    rn4[3] = {}
    A4 = Structure(4, {"A": {0}, "B": {3}}, rn4, {i: set() for i in range(6)}, {}, {})

    P4 = [1]
    N4 = [0]
    i = (A4, 3, P4, N4)
    f = FittingALC(*i, op={EX, ALL, OR, AND})
    assert f.solve()


def test5():
    A5 = Structure(
        2,
        {"A": {1}, "B": {1}},
        {i: {} for i in range(2)},
        {i: set() for i in range(6)},
        {},
        {},
    )
    P5 = [0]
    N5 = []
    i = (A5, 1, P5, N5)
    f = FittingALC(*i, op={EX, ALL, OR, AND})
    assert f.solve()


def test6():
    A6 = Structure(
        3,
        {"A": {1}, "B": {0, 1}},
        {i: {} for i in range(3)},
        {i: set() for i in range(6)},
        {},
        {},
    )
    P6 = [0]
    N6 = [1]
    i = (A6, 2, P6, N6)
    f = FittingALC(*i, op={EX, ALL, OR, AND, NEG})
    assert f.solve()


def test_alcq():
    d = {
        1: {(2, "r"), (2, "r")},
        4: {(5, "r"), (6, "r")},
        7: {(8, "r"), (9, "r"), (10, "r"), (11, "r")},
    }
    for i in [0, 2, 3, 5, 6, 8, 9, 10, 11]:
        d[i] = {}
    A = Structure(
        11,
        {"A": {2, 8}, "B": {3, 9}, "C": {5, 10}, "D": {6, 11}},
        d,
        {i: set() for i in range(12)},
        {},
        {},
    )
    P = [1, 4]
    N = [7]
    i = (A, 2, P, N)
    f = FittingALC(*i, op={EX, ALL, OR, AND, NEG, LE, GE})
    assert f.solve()


def testEx():
    A = Structure(
        5,
        {"A": {2, 4, 5}, "B": {3}},
        {0: {(2, "r"), (3, "r")}, 1: {(4, "r"), (5, "r")}, 2: {}, 3: {}, 4: {}, 5: {}},
        {i: set() for i in range(6)},
        {},
        {},
    )

    i = (A, 2, [0], [1])
    f = FittingALC(*i, op={EX})
    assert f.solve()

    i2 = (A, 2, [1], [0])
    f2 = FittingALC(*i2, op={EX})
    assert not f2.solve()


def testAnd():
    A = Structure(
        5,
        {"A": {1, 2, 3}, "B": {1, 3, 4}, "C": {1, 2, 4}},
        {0: set(), 1: set(), 2: set(), 3: set(), 4: set()},
        {i: set() for i in range(6)},
        {},
        {},
    )

    i = (A, 4, [1], [2, 3, 4])
    f = FittingALC(*i, op={AND})
    assert not f.solve()

    i2 = (A, 5, [1], [2, 3, 4])
    f2 = FittingALC(*i2, op={AND})
    assert f2.solve()


def testAll():
    A = Structure(
        5,
        {"A": {2, 4, 5}, "B": {3}},
        {0: {(2, "r"), (3, "r")}, 1: {(4, "r"), (5, "r")}, 2: {}, 3: {}, 4: {}, 5: {}},
        {i: set() for i in range(6)},
        {},
        {},
    )

    i = (A, 2, [0], [1])
    f = FittingALC(*i, op={ALL})
    assert not f.solve()

    i2 = (A, 2, [1], [0])
    f2 = FittingALC(*i2, op={ALL})
    assert f2.solve()


def testSize():
    k = 10
    # TODO: the SAT formula for this takes a surprising amount of time to solve
    # i.e. it is not instant
    # I believe if we modify our encoding such that this becomes instant, we can gain
    # a lot of speed on realistic benchmarks
    A = Structure(
        max_ind=k,
        cn_ext={},
        rn_ext={i: {(i + 1, "r")} for i in range(k - 1)},
        indmap={},
        nsmap={},
        dp_ext={i: set() for i in range(k + 1)},
    )
    A.rn_ext[k - 1] = set()

    i = (A, k, [0], [1])
    f = FittingALC(*i, op={EX, AND})
    assert f.solve()

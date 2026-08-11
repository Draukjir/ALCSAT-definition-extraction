from collections import defaultdict, deque

import lightrdf

from . import signature


def collect_subclasses(target_class: str):
    parser = lightrdf.Parser()

    sig = signature.Signature()

    children = defaultdict(set)

    for s, p, o in parser.parse(sig.TAXONOMY, base_iri=None):
        if p == sig.SUBCLASS:
            children[o].add(s)

    subclasses = set()
    queue = deque([target_class])

    while queue:
        current = queue.popleft()

        for child in children[current]:
            if child not in subclasses:
                subclasses.add(child)
                queue.append(child)

    return subclasses


def collect_superclasses(target_class: str):
    parser = lightrdf.Parser()
    sig = signature.Signature()

    parents = defaultdict(set)

    for s, p, o in parser.parse(sig.TAXONOMY, base_iri=None):
        if p == sig.SUBCLASS:
            parents[s].add(o)

    superclasses = set()
    queue = deque([target_class])

    while queue:
        current = queue.popleft()

        for parent in parents[current]:
            if parent not in superclasses:
                superclasses.add(parent)
                queue.append(parent)

    return superclasses


def determine_most_general_class(target_class: str):

    sig = signature.Signature()

    superclasses = collect_superclasses(target_class)

    for cls in sig.top_level_classes:
        if cls in superclasses:
            return cls

    print(f"[WARN] No top-level class found for {target_class}")
    return sig.THING

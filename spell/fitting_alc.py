from dataclasses import dataclass
from threading import Timer
import time
from typing import Any


from pysat.card import CardEnc, EncType, ITotalizer
from pysat.solvers import Glucose4


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

d_op = {
     0 : "TOP",
     1 : "BOT",
     2: "NEG",
     3: "AND",
     4: "OR",
     5: "EX",
     6: "ALL"
}
TOP = 0
BOT = 1
NEG = 2
AND = 3
OR = 4
EX = 5
ALL = 6
ALC_OP = {NEG,AND,OR,EX,ALL}
ALC_OP_B = {NEG,AND,OR}
X = 0
Z = 2
V = 4
L = 5
T = 6


NNF: bool = False


def interrupt(s):
    s.interrupt()


def solver_solve(solver : Glucose4, timeout : float):
    if timeout != -1 and timeout < 0:
        return False

    if timeout != -1:
        timer = Timer(timeout, interrupt, [solver])
        timer.start()
    
    res = solver.solve()

    if timeout != -1:
        timer.cancel()

    return res

def bisim(A : Structure, sigma : Signature, P : list[int], N: list[int], max_k: int) -> tuple[Structure, list[int], list[int]]:

    color_register: dict[Any, int] = {}
    color: dict[int, int] = {}

    for i in range(A.max_ind):
        tp: list[str] = []
        for cn in sigma[0]:
            if i in A.cn_ext[cn]:
                tp.append(cn)
        tpf = frozenset(tp)
        if tpf not in color_register:
            color_register[tpf] = len(color_register)
        color[i] = color_register[tpf] 

    for i in range(max_k):
        ncolor = {}
        for a in range(A.max_ind):
            tp2 : list[tuple[int, str]] = [ (color[a], "") ]
            for (b, r) in A.rn_ext[a]:
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

    for cn in sigma[0]:
        B.cn_ext[cn] = set()
        for a in A.cn_ext[cn]:
            B.cn_ext[cn].add(color2class[color[a]])

    for a in range(A.max_ind):
        ca = color2class[color[a]]
        if ca not in B.rn_ext:
            B.rn_ext[ca] = set()
        for (b, r) in A.rn_ext[a]:
            cb = color2class[color[b]]
            B.rn_ext[ca].add((cb, r))

    print("== Bisimulation reduction reduced from size {} to size {}".format(A.max_ind, B.max_ind))

    return B, list( color2class[color[p]] for p in P), list(color2class[color[n]] for n in N)

def cn_types(A : Structure, sigma : Signature) -> set[frozenset[str]]:
    res: set[frozenset[str]] = set()
    for i in range(A.max_ind):
        tp: list[str] = []
        for cn in sigma[0]:
            if i in A.cn_ext[cn]:
                tp.append(cn)
        res.add(frozenset(tp))
    return res

@dataclass
class STree():
    label : str
    children : list["STree"]

    def to_tree_int(self) -> list[str]:
        res = [self.label]
        for c in self.children:
            cs = c.to_tree_int()
            res.append(" +-- " + cs[0])
            res.extend([ "    " + s for s in cs[1:]])
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



class FittingALC:
    def __init__(self, A: Structure, k : int, P: list[int],
        N: list[int], op = ALC_OP, cov_p = - 1, cov_n = -1, tree_templates = True, type_encoding = True):
        B,m = restrict_to_neighborhood(k-1,A,P + N)
        self.tree_templates = tree_templates
        self.type_encoding = type_encoding
        self.P : list[int] = [m[a] for a in P]
        self.N : list[int] = [m[b] for b in N]
        self.A : Structure = B
        self.sigma : Signature = determine_relevant_symbols(A, P + N, 1, k - 1)
        self.k = k
        self.op = op
        self.op_b = ALC_OP_B.intersection(op)
        self.op_r = op.difference(ALC_OP_B)
        self.types = cn_types(self.A, self.sigma)
        self.vars : dict[Any, int] = self._vars()
        self.n_op = len(op)        
        self.cov_p = len(P) if cov_p == -1 else cov_p
        self.cov_n = len(N) if cov_n == -1 else cov_n
        self.solver = Glucose4()
        self.max_var = 0
        
        
    def _vars(self):
        d = dict()
        i = 1
        d[X,TOP] = i
        d[X,BOT] = i * self.k + 1
        i+=1
        for cn in self.sigma[0]:
            d[X,cn] = i * self.k+1
            i += 1
        for op in self.op_b:
            d[X,op]=i * self.k+1
            i+=1
        if EX in self.op:
            for c in self.sigma[1]:
                d[X,EX,c] = i * self.k+1
                i += 1
        if ALL in self.op:
            for c in self.sigma[1]:
                d[X,ALL,c] = i * self.k+1
                i+=1
        for a in range(self.A.max_ind):
            d[Z,a] = i * self.k+1
            i += 1
        for j in range(self.k):
            d[V,1,j] = i*self.k+1
            i+=1
        for j in range(self.k):
            d[V,2,j] = i*self.k+1
            i+=1

        if self.type_encoding:
            for tp in self.types:
                d[X, tp] = i * self.k + 1
                i += 1

            # For leaves
            d[L] = i* self.k + 1
            i += 1
        
        self.max_var = i * self.k + 1
        
        if self.tree_templates:
            tree_k = min(self.k, TREE_TEMPLATE_LIMIT)
            for idx, t in enumerate(all_trees(tree_k, 0)):
                d[T, idx] = self.max_var
                self.max_var += 1


        return d

    def _syn_tree_encoding(self):
        for i in range(self.k):            
            x_vars = [self.vars[X,o]+i for o in self.op_b] + [self.vars[X,o,r]+i for o in self.op_r for r in self.sigma[1]] + [self.vars[X,cn] +i for cn in self.sigma[0]] + [self.vars[X,TOP]+i,self.vars[X,BOT]+i]

            for clause in CardEnc.equals(lits = x_vars, encoding = EncType.pairwise):
                self.solver.add_clause(clause)

        for i in range(self.k):
            v_vars = [self.vars[V, 1, i] + j for j in range(i + 1, self.k)] + [self.vars[V, 2, i] + j for j in range(i + 1, self.k - 1)]

            # At most one of the y-vars
            for clause in CardEnc.atmost(lits = v_vars, encoding = EncType.pairwise):
                self.solver.add_clause(clause)

            for r in self.sigma[1]:
                for op in self.op_r:
                    self.solver.add_clause([-(self.vars[X,op,r]+i)] + [self.vars[V,1,i]+j for j in range(i+1,self.k)])
                    for j in range(i + 1, self.k - 1):
                        self.solver.add_clause([-(self.vars[X,op,r]+i), -(self.vars[V,2,i]+j)])

            if NEG in self.op_b:
                self.solver.add_clause([-(self.vars[X,NEG]+i)] + [self.vars[V,1,i]+j for j in range(i+1,self.k)])
                for j in range(i + 1, self.k):
                    self.solver.add_clause([-(self.vars[X,NEG]+i), -(self.vars[V,2,i]+j)])


            for op in self.op_b - {NEG}:
                self.solver.add_clause([-(self.vars[X,op]+i)] + [self.vars[V,2,i]+j for j in range(i+1,self.k-1)])
                for j in range(i + 1, self.k):
                    self.solver.add_clause([-(self.vars[X,op]+i), -(self.vars[V,1,i]+j)])

            for cn in self.sigma[0]:

                if self.type_encoding:
                    # Is a leaf
                    self.solver.add_clause((-(self.vars[X,cn]+i),(self.vars[L] + i)))

            for j in range(i + 1, self.k):
                for cn in self.sigma[0]:
                    self.solver.add_clause((-(self.vars[X,cn]+i),-(self.vars[V,1, i]+j)))
                    self.solver.add_clause((-(self.vars[X,cn]+i),-(self.vars[V,2, i]+j)))


                for b in {TOP,BOT}:
                    self.solver.add_clause((-(self.vars[X,b]+i),-(self.vars[V,1,i]+j)))
                    self.solver.add_clause((-(self.vars[X,b]+i),-(self.vars[V,2,i]+j)))


            # Exactly one predecessor
            possible_preds = [ self.vars[V, 1, j] + i for j in range(0, i)] + [self.vars[V, 2, j] + i for j in range(0, i)] + [self.vars[V, 2, j] + i - 1 for j in range(0, i - 1)]
            if len(possible_preds) > 0:
                for clause in CardEnc.equals( lits = possible_preds, encoding= EncType.pairwise):
                    self.solver.add_clause(clause)


    def _symmetry_breaking(self):

        #TODO: reformulate this to work with the tree templates
        # Symmetry breaking: crossing free syntax tree
        # for i in range(self.k):
        #     for j in range(i + 1, self.k):
        #         for i2 in range(i + 1, j):
        #             for j2 in range(j + 1, self.k):
        #                 self.solver.add_clause((-(self.vars[V,1,i]+j),-(self.vars[V,1,i2]+j2)))
        #                 self.solver.add_clause((-(self.vars[V,1,i]+j),-(self.vars[V,2,i2]+j2)))
        #                 self.solver.add_clause((-(self.vars[V,2,i]+j),-(self.vars[V,1,i2]+j2)))
        #                 self.solver.add_clause((-(self.vars[V,2,i]+j),-(self.vars[V,2,i2]+j2)))

        # Symmetry breaking: associativity of sqcap and sqcup
        # There is always a syntax tree where one of the successors of AND is not an AND
        for i in range(self.k):
            for j in range(i + 1, self.k - 1):
                if AND in self.op_b:
                    self.solver.add_clause( (- (self.vars[X, AND] + i), - (self.vars[V, 2, i] + j), - (self.vars[X, AND] + j), - (self.vars[X, AND] + j + 1)))
                if OR in self.op_b:
                    self.solver.add_clause( (- (self.vars[X, OR] + i), - (self.vars[V, 2, i] + j), - (self.vars[X, OR] + j), - (self.vars[X, OR] + j + 1)))

        # Symmetry breaking: there is always a syntax tree where NEG is not nested directly under ALL or EX or NEG
        if not NNF and EX in self.op_r and ALL in self.op_r and NEG in self.op_b:
            for i in range(self.k):
                for j in range(i + 1, self.k):
                        self.solver.add_clause( (- (self.vars[V, 1, i] + j), - (self.vars[X, NEG] + j)))

        # Symmetry breaking: rewrites involving TOP and BOT?
        for i in range(self.k):
            for j in range(i + 1, self.k - 1):
                if AND in self.op_b:
                    self.solver.add_clause( (- (self.vars[X, AND] + i), - (self.vars[V, 2, i] + j), - (self.vars[X, TOP] + j)))
                    self.solver.add_clause( (- (self.vars[X, AND] + i), - (self.vars[V, 2, i] + j), - (self.vars[X, TOP] + j + 1)))
                    self.solver.add_clause( (- (self.vars[X, AND] + i), - (self.vars[V, 2, i] + j), - (self.vars[X, BOT] + j)))
                    self.solver.add_clause( (- (self.vars[X, AND] + i), - (self.vars[V, 2, i] + j), - (self.vars[X, BOT] + j + 1)))
                if OR in self.op_b:
                    self.solver.add_clause( (- (self.vars[X, OR] + i), - (self.vars[V, 2, i] + j), - (self.vars[X, TOP] + j)))
                    self.solver.add_clause( (- (self.vars[X, OR] + i), - (self.vars[V, 2, i] + j), - (self.vars[X, TOP] + j + 1)))
                    self.solver.add_clause( (- (self.vars[X, OR] + i), - (self.vars[V, 2, i] + j), - (self.vars[X, BOT] + j)))
                    self.solver.add_clause( (- (self.vars[X, OR] + i), - (self.vars[V, 2, i] + j), - (self.vars[X, BOT] + j + 1)))

        # Symmetry breaking: limited commutativity
        # Not advantageous right now
        # for i in range(self.k):
        #     for j in range(i + 1, self.k):
        #         # This orders the node types. Binary operators are smallest, the unary operators, then conceptnames, then top and bot
        #         x_varsj = [self.vars[X,cn] +j for cn in self.sigma[0]] + [self.vars[X,TOP]+j,self.vars[X,BOT]+j]
        #         x_varsj1 = [self.vars[X,cn] +j + 1 for cn in self.sigma[0]] + [self.vars[X,TOP]+j + 1,self.vars[X,BOT]+j + 1]
        #         assert(len(x_varsj) == len(x_varsj1))
        #         for k1 in range(len(x_varsj)):
        #             for k2 in range(k1 + 1, len(x_varsj1)):
        #                 # left must be "bigger" than right
        #                 self.solver.add_clause( ( - (self.vars[V, 2, i] + j), - x_varsj[k1], -x_varsj1[k2]))


        # NNF    
        if NNF:
            for i in range(self.k):
                for j in range(i + 1, self.k):
                    for j2 in range(j + 1, self.k):
                        self.solver.add_clause (( - (self.vars[X, NEG] + i),   - (self.vars[V, 1, i] + j), - (self.vars[V, 1, j] + j2)))
                        self.solver.add_clause (( - (self.vars[X, NEG] + i),   - (self.vars[V, 1, i] + j), - (self.vars[V, 2, j] + j2)))

        if self.tree_templates:

            tree_k = min(self.k, TREE_TEMPLATE_LIMIT)

            tree_vars = []
            for idx, t in enumerate(all_trees(tree_k)):
                tree_vars.append(self.vars[T, idx])

            for clause in CardEnc.equals(lits = tree_vars, encoding=EncType.pairwise):
                self.solver.add_clause(clause)

            for idx, t in enumerate(all_trees(tree_k)):
                for i in range(tree_k):
                    
                    # Only restrict leaves if the tree template is not a prefix
                    if len(t[i]) == 0 and tree_k == self.k:
                        for j in range(i + 1, tree_k):
                            self.solver.add_clause( ( - tree_vars[idx], - ( self.vars[V, 1, i] + j)))
                            self.solver.add_clause( ( - tree_vars[idx], - ( self.vars[V, 2, i] + j)))

                    if len(t[i]) == 1:
                        self.solver.add_clause( ( - tree_vars[idx], ( self.vars[V, 1, i] + t[i][0])))
                    if len(t[i]) == 2:
                        self.solver.add_clause( ( - tree_vars[idx],  ( self.vars[V, 2, i] + t[i][0])))

    def _evaluation_constraints(self):

        for a in range(self.A.max_ind):
            for i in range(self.k):                
                if NEG in self.op_b:
                    for j in range(i + 1, self.k):
                        self.solver.add_clause((-(self.vars[X,NEG]+i), -(self.vars[Z,a]+i), -(self.vars[V,1,i]+j), - (self.vars[Z, a] + j)))
                        self.solver.add_clause((-(self.vars[X,NEG]+i), (self.vars[Z,a]+i), -(self.vars[V,1,i]+j), (self.vars[Z, a] + j)))

                if AND in self.op_b:
                    for j in range(i + 1, self.k - 1):
                        self.solver.add_clause((-(self.vars[X,AND]+i), -(self.vars[Z,a]+i), -(self.vars[V,2,i]+j), self.vars[Z, a] + j))
                        self.solver.add_clause((-(self.vars[X,AND]+i), -(self.vars[Z,a]+i), -(self.vars[V,2,i]+j), self.vars[Z, a] + j + 1))
                        self.solver.add_clause((-(self.vars[X,AND]+i), (self.vars[Z,a]+i), -(self.vars[V,2,i]+j), -(self.vars[Z, a] + j + 1), -(self.vars[Z, a] + j)))

                if OR in self.op_b:
                    for j in range(i + 1, self.k - 1):
                        self.solver.add_clause((-(self.vars[X,OR]+i), (self.vars[Z,a]+i), -(self.vars[V,2,i]+j), -(self.vars[Z, a] + j)))
                        self.solver.add_clause((-(self.vars[X,OR]+i), (self.vars[Z,a]+i), -(self.vars[V,2,i]+j), -(self.vars[Z, a] + j + 1)))
                        self.solver.add_clause((-(self.vars[X,OR]+i), -(self.vars[Z,a]+i), -(self.vars[V,2,i]+j), (self.vars[Z, a] + j + 1), (self.vars[Z, a] + j)))
                
                if ALL in self.op_r:
                    for r in self.sigma[1]:
                        successors = [ b for (b, p) in self.A.rn_ext[a] if p == r]
                        if len(successors) == 0:
                            # Optimization: most individuals don't have successors
                            self.solver.add_clause( ( - ( self.vars[X, ALL, r] + i), (self.vars[Z, a] + i)))
                        else:
                            for j in range(i + 1, self.k):
                                self.solver.add_clause([-(self.vars[X,ALL,r]+i), (self.vars[Z,a]+i), -(self.vars[V, 1, i] + j)] + [ -(self.vars[Z, b]+j) for b in successors ])                            
                                for b in successors:
                                    self.solver.add_clause((-(self.vars[X,ALL,r]+i), -(self.vars[Z,a]+i), -(self.vars[V, 1, i] + j), self.vars[Z, b] + j))

                if EX in self.op_r:
                    for r in self.sigma[1]:
                        successors = [ b for (b, p) in self.A.rn_ext[a] if p == r]
                        if len(successors) == 0:
                            # Optimization: most individuals don't have successors
                            self.solver.add_clause( ( - (self.vars[X, EX, r] + i), -(self.vars[Z, a] + i)))
                        else:
                            for j in range(i + 1, self.k):
                                self.solver.add_clause([-(self.vars[X,EX,r]+i), -(self.vars[Z,a]+i), -(self.vars[V, 1, i] + j)] + [ (self.vars[Z, b]+j) for b in successors ])                            
                                for b in successors:
                                    self.solver.add_clause((-(self.vars[X,EX,r]+i), (self.vars[Z,a]+i), -(self.vars[V, 1, i] + j), -(self.vars[Z, b] + j)))

                self.solver.add_clause((-(self.vars[X,TOP]+i),(self.vars[Z,a]+i)))
                self.solver.add_clause((-(self.vars[X,BOT]+i),-(self.vars[Z,a]+i)))


        if not self.type_encoding:
            for cn in self.sigma[0]:
                for i in range(self.k):
                    for a in range(self.A.max_ind):                    
                        if a in self.A.cn_ext[cn]:                                            
                            self.solver.add_clause((-(self.vars[X,cn]+i), self.vars[Z,a]+i))
                        else:
                            self.solver.add_clause((-(self.vars[X,cn]+i),-(self.vars[Z,a]+i)))

        if self.type_encoding:
            for i in range(self.k):
                for tp in self.types:
                    for cn in self.sigma[0]:
                        if cn in tp:
                            self.solver.add_clause((-(self.vars[X, cn] + i), self.vars[X, tp] + i))
                        if cn not in tp: 
                            self.solver.add_clause((-(self.vars[X, cn] + i), -(self.vars[X, tp] + i)))


            for a in range(self.A.max_ind):
                tp = frozenset({ cn for cn in self.sigma[0] if a in self.A.cn_ext[cn]})
                assert tp in self.types
                for i in range(self.k):
                    self.solver.add_clause( ( - (self.vars[X, tp] + i),   self.vars[Z, a] + i))
                    # Problem: the following should only happen for CONCEPT NAME NODES. We thus need an additional variable that is true iff a node is a concept name node
                    self.solver.add_clause( ( (self.vars[X, tp] + i) ,   - (self.vars[Z, a] + i), - (self.vars[L] + i)))
                


    def _fitting_constraints(self):
        for a in self.P:
            self.solver.add_clause([self.vars[Z,a]])            
        for a in self.N:
            self.solver.add_clause([-(self.vars[Z,a])])       

    def _fitting_constraints_approximate(self, k: int):
        lits = [self.vars[Z, a] for a in self.P] + [-self.vars[Z, b] for b in self.N]
        
        enc = CardEnc.atleast(
            lits, bound=k, top_id=self.max_var, encoding=EncType.kmtotalizer
        )
        for clause in enc.clauses:
            self.solver.add_clause(clause)

    def _fitting_constraints_approximate_incr_initial(self, k: int):
        lits = [-self.vars[Z, a] for a in self.P] + [self.vars[Z, b] for b in self.N]                
        self.totalizer = ITotalizer(lits, ubound = k,top_id=self.max_var)
        for clause in self.totalizer.cnf.clauses:
            self.solver.add_clause(clause)

    def _fitting_constraints_approximate_incr_increase(self, k: int): 
        self.solver.add_clause([-self.totalizer.rhs[k]])

    def solve(self):
        acc, n, sol = self.solve_incr(self.k, self.k)
        if acc == 1.0:
            return True
        else:
            return False
    
    def solve_incr(self,max_k :int, start_k : int =1, return_string = False, timeout : float = -1):
        return self.solve_incr_approx(max_k, start_k, len(self.P) + len(self.N), timeout=timeout)


    def solve_approx(self, k: int, min_n: int, timeout : float = -1):
        time_start = time.perf_counter()
        self.k = k
        n = max(len(self.P), len(self.N), min_n)
        
        dt = time.perf_counter() - time_start

        best_sol = None
        best_accuracy = 0
        best_n = 0
        
        self.solver = Glucose4(incr=True)
        self.vars = self._vars()
        self._syn_tree_encoding()
        self._evaluation_constraints()
        self._symmetry_breaking()

        while n <= len(self.P) + len(self.N) and (dt < timeout or timeout == -1):
            self._fitting_constraints_approximate(n)
            
            dt = time.perf_counter() - time_start
            remaining_time = -1
            if timeout != -1:
                remaining_time = timeout - dt

            if not solver_solve(self.solver, remaining_time):
                print(f"Not satisfiable for k={self.k}, n={n}")
                return best_accuracy, best_n, self.k, best_sol

            best_sol = self.modelToTree()
            model_n = self._model_n()

            best_accuracy = model_n / (len(self.P) + len(self.N))
            best_n = model_n
            print(f"Satisfiable for k={self.k}, n={model_n}, acc={best_accuracy}")
            print(best_sol.to_tree())
            n = model_n + 1
            dt = time.perf_counter() - time_start
        
        return best_accuracy, best_n, self.k, best_sol


    def solve_incr_approx(self, max_k : int , start_k : int =1, min_n: int = 1, timeout : float = -1):
        time_start = time.perf_counter()
        self.k = start_k
        n = max(len(self.P), len(self.N), min_n)
        best_sol: STree = STree(d_op[TOP], [])
        best_acc = 0
        dt = time.perf_counter() - time_start

        # self.A, self.P, self.N = bisim(self.A, self.sigma, self.P, self.N, max_k)

        while self.k <= max_k and (dt < timeout or timeout == -1) and best_acc < 1.0:
            remaining_time = -1
            if timeout != -1:
                remaining_time = timeout - dt

            k_acc, k_n, _, k_sol = self.solve_approx(self.k, n, remaining_time)

            if k_acc > best_acc:
                assert k_sol
                best_sol = k_sol
                best_acc = k_acc
                n = k_n + 1

            self.k += 1
            dt = time.perf_counter() - time_start

        return best_acc, self.k, best_sol

    def _model_n(self)-> int:
        # Return the number of positive/negative examples that is claimed to be covered by a model
        m = self.solver.get_model()
        assert isinstance(m, list)

        res: int = 0
        for p in self.P:
            if self.vars[Z, p] + 0 in m:
                res += 1
        
        for n in self.N:
            if self.vars[Z, n] + 0 not in m:
                res += 1
        return res

    def nodelabel(self, i : int) -> str:
        m = self.solver.get_model()
        assert isinstance(m, list)
        if (self.vars[X, TOP] + i) in m:
            return d_op[TOP]
        if (self.vars[X, BOT] + i) in m:
            return d_op[BOT]
        for cn in self.sigma[0]:
            if (self.vars[X, cn] + i) in m:
                return cn
        for op in self.op_b:
            if (self.vars[X, op] + i) in m:
                return d_op[op]
        if EX in self.op:
            for r in self.sigma[1]:
                if (self.vars[X, EX, r] + i) in m:
                    return f"ex.{r}"
        if ALL in self.op:
            for r in self.sigma[1]:
                if (self.vars[X, ALL, r] + i) in m:
                    return f"all.{r}"
        assert False

    def modelToTree(self, i = 0) -> STree:
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



# Generate (almost) non-isomorphic trees of size n
# Why almost? The case there the left and right subtree are of the same size is
# currently not handled correctly and from size 7 on, some isomorphic trees are generated
def all_trees(k: int, start: int = 0) -> list[list[tuple[int] | tuple[int, int] | tuple[()]]]:
    if k == 1:
        return [ [()] ]

    res = []
    for i in range(1, (k - 1) // 2 + 1):
        for a in all_trees(i, start + 2):
            for b in all_trees((k - 1) - i, start + i + 1):
                # Whacky tree composition to ensure that children of binary nodes are always adjacent
                # (the start + 2 for the a trees is for the same purpose)
                res.append([ (start + 1, start + 2)] + [ a[0] ] + [b[0]] + a[1:] + b[1:])


    for a in all_trees(k - 1, start + 1):
        res.append( [ ( start + 1, )] + a)
    
    return res

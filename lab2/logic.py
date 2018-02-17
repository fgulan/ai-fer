import util
import functools

class Labels:
    """
    Labels describing the WumpusWorld
    """
    WUMPUS = 'w'
    TELEPORTER = 't'
    POISON = 'p'
    SAFE = 'o'

    """
    Some sets for simpler checks
    >>> if literal.label in Labels.DEADLY:
    >>>     # Don't go there!!!
    """
    DEADLY = set([WUMPUS, POISON])
    WTP = set([WUMPUS, POISON, TELEPORTER])

    UNIQUE = set([WUMPUS, POISON, TELEPORTER, SAFE])

    POISON_CHEMICALS = 'c'
    TELEPORTER_GLOW = 'g'
    WUMPUS_STENCH = 's'

    INDICATORS = set([POISON_CHEMICALS, TELEPORTER_GLOW, WUMPUS_STENCH])


def stateWeight(state):
    """
    To ensure consistency in exploring states, they will be sorted
    according to a simple linear combination.
    The maps will never be larger than 20x20, and therefore this
    weighting will be consistent.
    """
    x, y = state
    return 20*x + y


@functools.total_ordering
class Literal:
    """
    A literal is an atom or its negation
    In this case, a literal represents if a certain state (x,y) is or is not
    the location of GhostWumpus, or the poisoned pills.
    """

    def __init__(self, label, state, negative=False):
        """
        Set all values. Notice that the state is remembered twice - you
        can use whichever representation suits you better.
        """
        x,y = state

        self.x = x
        self.y = y
        self.state = state

        self.negative = negative
        self.label = label

    def __key(self):
        """
        Return a unique key representing the literal at a given point
        """
        return (self.x, self.y, self.negative, self.label)

    def __hash__(self):
        """
        Return the hash value - this operator overloads the hash(object) function.
        """
        return hash(self.__key())

    def __eq__(first, second):
        """
        Check for equality - this operator overloads '=='
        """
        return first.__key() == second.__key()

    def __lt__(self, other):
        """
        Less than check
        by using @functools decorator, this is enough to infer ordering
        """
        return stateWeight(self.state) < stateWeight(other.state)

    def __str__(self):
        """
        Overloading the str() operator - convert the object to a string
        """
        if self.negative: return '~' + self.label
        return self.label

    def __repr__(self):
        """
        Object representation, in this case a string
        """
        return self.__str__()

    def copy(self):
        """
        Return a copy of the current literal
        """
        return Literal(self.label, self.state, self.negative)

    def negate(self):
        """
        Return a new Literal containing the negation of the current one
        """
        return Literal(self.label, self.state, not self.negative)

    def isDeadly(self):
        """
        Check if a literal represents a deadly state
        """
        return self.label in labels.DEADLY

    def isWTP(self):
        """
        Check if a literal represents GhostWumpus, the Teleporter or
        a poisoned pill
        """
        return self.label in labels.WTP

    def isSafe(self):
        """
        Check if a literal represents a safe spot
        """
        return self.label == Labels.SAFE

    def isTeleporter(self):
        """
        Check if a literal represents the teleporter
        """
        return self.label == Labels.TELEPORTER


class Clause:
    """
    A disjunction of finitely many unique literals.
    The Clauses have to be in the CNF so that resolution can be applied to them. The code
    was written assuming that the clauses are in CNF, and will not work otherwise.

    A sample of instantiating a clause (~B v C):

    >>> premise = Clause(set([Literal('b', (0, 0), True), Literal('c', (0, 0), False)]))

    or; written more clearly
    >>> LiteralNotB = Literal('b', (0, 0), True)
    >>> LiteralC = Literal('c', (0, 0), False)

    >>> premise = Clause(set([[LiteralNotB, LiteralC]]))
    """

    def __init__(self, literals):
        """
        The constructor for a clause. The clause assumes that the data passed
        is an iterable (e.g., list, set), or a single literal in case of a unit clause.
        In case of unit clauses, the Literal is wrapped in a list to be safely passed to
        the set.
        """
        if not type(literals) == set and not type(literals) == list:
            self.literals = set([literals])
        else:
            self.literals = set(literals)

    def isResolveableWith(self, otherClause):
        """
        Check if a literal from the clause is resolveable by another clause -
        if the other clause contains a negation of one of the literals.
        e.g., (~A) and (A v ~B) are examples of two clauses containing opposite literals
        """
        for literal in self.literals:
            if literal.negate() in otherClause.literals:
                return True
        return False

    def isUnimportant(self):
        for literal in self.literals:
            if literal.negate() in self.literals:
                return True
        return False

    def isRedundant(self, otherClauses):
        """
        Check if a clause is a subset of another clause.
        """
        for clause in otherClauses:
            if self == clause: continue
            if clause.literals.issubset(self.literals):
                return True
        return False

    def negateAll(self):
        """
        Negate all the literals in the clause to be used
        as the supporting set for resolution.
        """
        negations = set()
        for literal in self.literals:
            clause = Clause(literal.negate())
            negations.add(clause)
        return negations

    def __str__(self):
        """
        Overloading the str() operator - convert the object to a string
        """
        return ' V '.join([str(literal) for literal in self.literals])

    def __repr__(self):
        """
        The representation of the object
        """
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, Clause):
            return NotImplemented
        elif self is other:
            return True
        else:
            return tuple(self.literals) == tuple(other.literals)

    def __hash__(self):
        return hash(tuple(self.literals))

def resolution2(clauses, goal):
    """
    Implement refutation resolution.

    The pseudocode for the algorithm of refutation resolution can be found
    in the slides. The implementation here assumes you will use set of support
    and simplification strategies. We urge you to go through the slides and
    carefully design the code before implementing.
    """

    resolvedPairs = set()
    setOfSupport = goal.negateAll()

    clauses = clauses.union(setOfSupport)
    while True:
        newClauses = set()
        for clause1, clause2 in selectClauses(clauses, setOfSupport, resolvedPairs):
            resolvants = resolvePair(clause1, clause2)
            if checkIfContainsNilClause(resolvants):
                return True

            for resolvantClause in resolvants:
                newClauses.add(resolvantClause)
                setOfSupport.add(resolvantClause)
        if newClauses <= clauses:
            return False
        clauses = clauses.union(newClauses)
        clauses = set(removeRedundant(clauses))
        clauses = set(removeUnimportant(clauses))


def resolution(clauses, goal):
    """
    Implement refutation resolution.

    The pseudocode for the algorithm of refutation resolution can be found
    in the slides. The implementation here assumes you will use set of support
    and simplification strategies. We urge you to go through the slides and
    carefully design the code before implementing.
    """

    resolvedPairs = set()
    new = set()
    setOfSupport = goal.negateAll()

    while True:

        for clause in clauses:
            for sosClause in setOfSupport:
                if clause == sosClause:
                    continue
                if (clause, sosClause) in resolvedPairs or not clause.isResolveableWith(sosClause):
                    continue
                firstClause, secondClause = clause, sosClause
                resolvents = resolvePair(firstClause, secondClause)

                if checkIfContainsNilClause(resolvents):
                    return True
                resolvedPairs.add((firstClause, secondClause))
                for clause in resolvents:
                    new.add(clause)

        if new <= clauses:
            return False

        for clause in new:
            clauses.add(clause)
            setOfSupport.add(clause)
        setOfSupport = removeRendudantAndUnimportant(setOfSupport)

def checkIfContainsNilClause(clauses):
    for clause in clauses:
        if len(clause.literals) == 0:
            return True
    return False

def removeRendudantAndUnimportant(clauses):
    clauses = removeRedundant(clauses)
    return removeUnimportant(clauses)

def removeRedundant(clauses):
    newClauses = set()
    for clause in clauses:
        if clause.isRedundant(clauses):
            continue
        newClauses.add(clause)

    return newClauses

def removeUnimportant(clauses):
    newClauses = set()
    for clause in clauses:
        if clause.isUnimportant():
            continue
        newClauses.add(clause)

    return newClauses

def resolvePair(firstClause, secondClause):
    """
    Resolve a pair of clauses.
    """
    # if not firstClause.isResolveableWith(secondClause):
    #     raise "Given clauses are not resolvable."
    literals = set()
    for literal in firstClause.literals:
            if not literal.negate() in secondClause.literals:
                literals.add(literal)

    for literal in secondClause.literals:
            if not literal.negate() in firstClause.literals:
                literals.add(literal)

    return [Clause(literals)]

def selectClauses(clauses, setOfSupport, resolvedPairs):
    """
    Select pairs of clauses to resolve.
    """
    for clause in clauses:
        for sosClause in setOfSupport:
            if clause == sosClause:
                continue
            if (clause, sosClause) not in resolvedPairs and clause.isResolveableWith(sosClause):
                return clause, sosClause
    return None, None

def testResolution():
    """
    A sample of a resolution problem that should return True.
    You should come up with your own tests in order to validate your code.
    """
    premise1 = Clause(set([Literal('a', (0, 0), True), Literal('b', (0, 0), False)]))
    premise2 = Clause(set([Literal('b', (0, 0), True), Literal('c', (0, 0), False)]))
    premise3 = Clause(Literal('a', (0,0)))

    goal = Clause(Literal('c', (0,0)))
    print resolution(set([premise1, premise2, premise3]), goal)
    print resolution(set([Clause(set([Literal('a', (0, 0), False)])), Clause(set([Literal('b', (0, 0), False)]))]), Clause(Literal('a', (0, 0))))
    print resolution(set([Clause(set([Literal('a', (0, 0), True)])), Clause(set([Literal('a', (0, 0), False)]))]), Clause(Literal('c', (0, 0))))

    premise1 = Clause(set([Literal('A', (0,0), False), Literal('B', (0,0), False), Literal('C', (0,0), False), Literal('D', (0,0), False)]))
    premise2 = Clause(set([Literal('A', (0,0), True), Literal('B', (0,0), True), Literal('C', (0,0), True)]))
    premise3 = Clause(Literal('D', (0,0), True))
    goal = Clause(Literal('D', (0,0)))
    print resolution(set([premise1, premise2, premise3]), goal)

if __name__ == '__main__':
    """
    The main function - if you run logic.py from the command line by
    >>> python logic.py

    this is the starting point of the code which will run.
    """
    testResolution()
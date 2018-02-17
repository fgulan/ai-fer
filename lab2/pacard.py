
"""
In pacard.py, you will implement the search algorithm  based on refutation resolution 
which will lead Pacard through the cave of the evil GhostWumpus.
"""

import util
from logic import * 

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
        state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
        actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def miniWumpusSearch(problem):
    """
    A sample pass through the miniWumpus layout. Your solution will not contain
    just three steps! Optimality is not the concern here.
    """
    from game import Directions
    e = Directions.EAST
    n = Directions.NORTH
    return  [e, n, n]

def logicBasedSearch(problem):
    # array in order to keep the ordering
    visitedStates = []
    startState = problem.getStartState()

    knowledge = set()
    knowledge.add(Clause({Literal(Labels.SAFE, startState, False)}))

    costFunctionLambda = lambda state: stateWeight(state)
    safe = util.PriorityQueueWithFunction(costFunctionLambda)
    safe.push(startState)

    state = startState
    while True:
        if problem.isGoalState(state):
            return problem.reconstructPath(visitedStates)

        unknown = util.PriorityQueueWithFunction(costFunctionLambda)

        successors = problem.getSuccessors(state)
        clausesCreator(state, successors, Labels.POISON, problem.isPoisonCapsuleClose(state), knowledge)
        clausesCreator(state, successors, Labels.WUMPUS, problem.isWumpusClose(state), knowledge)
        clausesCreator(state, successors, Labels.TELEPORTER, problem.isTeleporterClose(state), knowledge)
        if not problem.isWumpusClose(state) and not problem.isPoisonCapsuleClose(state):
            for successor in successors:
                knowledge.add(Clause({Literal(Labels.SAFE, successor[0], False)}))

        for successor in successors:
            teleporterGoal = Clause({Literal(Labels.TELEPORTER, successor[0], False)})
            if resolution(knowledge, teleporterGoal):
                visitedStates.append(successor[0])
                return problem.reconstructPath(visitedStates)

            notWumpus = Clause({Literal(Labels.WUMPUS, successor[0], True)})
            notPoison = Clause({Literal(Labels.POISON, successor[0], True)})
            isSafe = Clause({Literal(Labels.SAFE, successor[0], False)})

            isPoison = Clause(Literal(Labels.POISON, successor[0], False))
            isWumpus = Clause(Literal(Labels.WUMPUS, successor[0], False))

            if resolution(knowledge, isSafe) or resolution(knowledge, notWumpus) and resolution(knowledge, notPoison):
                if successor[0] not in visitedStates:
                    safe.push(successor[0])
            elif not resolution(knowledge, isPoison) and not resolution(knowledge, isWumpus):
                if successor[0] not in visitedStates:
                    unknown.push(successor[0])

        if not safe.isEmpty():
            state = safe.pop()
        elif not unknown.isEmpty():
            state = unknown.pop()
        else:
            print "Cekam pomoc s paceeartha"
            exit(0)

        visitedStates.append(state)

    return problem.reconstructPath(visitedStates)

def clausesCreator(state, successors, type, prefix, knowledge):
    if prefix:
        literals = set()
        for successor in successors:
            literals.add(Literal(type, successor[0], False))
        knowledge.add(Clause(literals))
    else:
        for successor in successors:
            knowledge.add(Clause({Literal(type, successor[0], True)}))

def securePlace(state, problem, successors):
    clauses = []
    if not problem.isPoisonCapsuleClose(state) and not problem.isWumpusClose(state) and not problem.isTeleporterClose(state):
        for neighbour, action, cost in successors:
            literal = Literal(Labels.SAFE, neighbour, False)
            clauses.append(Clause(set([literal])))
    return set(clauses)

# Abbreviations
lbs = logicBasedSearch

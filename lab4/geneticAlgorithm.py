import numpy as np


class GeneticAlgorithm(object):
    """
        Implement a simple generationl genetic algorithm as described in the instructions
    """

    def __init__(self, chromosomeShape,
                 errorFunction,
                 elitism=1,
                 populationSize=25,
                 mutationProbability=.1,
                 mutationScale=.5,
                 numIterations=10000,
                 errorTreshold=1e-6
                 ):
        self.populationSize = populationSize  # size of the population of units
        self.p = mutationProbability  # probability of mutation
        self.numIter = numIterations  # maximum number of iterations
        self.e = errorTreshold  # threshold of error while iterating
        self.f = errorFunction  # the error function (reversely proportionl to fitness)
        self.keep = elitism  # number of units to keep for elitism
        self.k = mutationScale  # scale of the gaussian noise

        self.i = 0  # iteration counter
        # initialize the population randomly from a gaussian distribution
        # with noise 0.1 and then sort the values and store them internally

        self.population = []
        for _ in range(populationSize):
            chromosome = np.random.randn(chromosomeShape) * 0.1

            fitness = self.calculateFitness(chromosome)
            self.population.append((chromosome, fitness))

        # sort descending according to fitness (larger is better)
        self.population = sorted(self.population, key=lambda t: -t[1])

    def step(self):
        """
            Run one iteration of the genetic algorithm. In a single iteration,
            you should create a whole new population by first keeping the best
            units as defined by elitism, then iteratively select parents from
            the current population, apply crossover and then mutation.

            The step function should return, as a tuple:

            * boolean value indicating should the iteration stop (True if
                the learning process is finished, False othwerise)
            * an integer representing the current iteration of the
                algorithm
            * the weights of the best unit in the current iteration

        """

        self.i += 1

        #############################
        #       YOUR CODE HERE      #
        #############################
        new_population = self.bestN(self.keep)
        while len(new_population) < self.populationSize:
            first_parent, second_parent = self.selectParents()
            child = self.crossover(first_parent, second_parent)
            chromosome = np.array(self.mutate(child))
            fitness = self.calculateFitness(chromosome)
            new_population.append((chromosome, fitness))
        self.population = sorted(new_population, key=lambda t: -t[1])
        should_stop = self.i > self.numIter or self.best() < self.e
        return should_stop, self.i, self.best()[0]

    def calculateFitness(self, chromosome):
        """
            Implement a fitness metric as a function of the error of
            a unit. Remember - fitness is larger as the unit is better!
        """
        chromosomeError = self.f(chromosome)

        #############################
        #       YOUR CODE HERE      #
        #############################
        return 1 / chromosomeError

    def bestN(self, n):
        """
            Return the best n units from the population
        """
        #############################
        #       YOUR CODE HERE      #
        #############################
        return self.population[0:n]

    def best(self):
        """
            Return the best unit from the population
        """
        #############################
        #       YOUR CODE HERE      #
        #############################
        return self.population[0]

    def selectParents(self):
        """
            Select two parents from the population with probability of
            selection proportional to the fitness of the units in the
            population
        """
        #############################
        #       YOUR CODE HERE      #
        #############################
        fitness_sum = 0
        for value in self.population:
            fitness_sum += value[1]

        first_parent = self.roulette_wheel_selection(fitness_sum)
        second_parent = self.roulette_wheel_selection(fitness_sum)

        return first_parent, second_parent

    def roulette_wheel_selection(self, fitness_sum):
        pointer = np.random.uniform(0, fitness_sum)
        current_fittness = 0
        for chromosome, fitness in self.population:
            current_fittness += fitness
            if current_fittness > pointer:
                return chromosome

    def crossover(self, p1, p2):
        """
            Given two parent units p1 and p2, do a simple crossover by
            averaging their values in order to create a new child unit
        """
        #############################
        #       YOUR CODE HERE      #
        #############################
        return (p1 + p2) / 2

    def mutate(self, chromosome):
        """
            Given a unit, mutate its values by applying gaussian noise
            according to the parameter k
        """

        #############################
        #       YOUR CODE HERE      #
        #############################
        for index in range(len(chromosome)):
            if np.random.random() < self.p:
                chromosome[index] += np.random.normal(0, self.k)
        return chromosome

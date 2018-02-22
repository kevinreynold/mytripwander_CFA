import numpy as np
import copy

class ackley():
    def getLowerBound(self):
        return -32

    def getUpperBound(self):
        return 32

    def getDimension(self):
        return 30

    def calculateFitnessMinimum(self, individual):
        n = self.getDimension()
        return (1 / (-20.0 * np.exp(-0.2 * np.sqrt(sum(map(lambda nb: nb ** 2, individual)) / n)) - np.exp(
            sum(map(lambda nb: np.cos(2.0 * np.pi * nb), individual)) / n) + 20 + np.e))

class step():
    def getLowerBound(self):
        return -5.12

    def getUpperBound(self):
        return 5.12

    def getDimension(self):
        return 30

    def calculateFitnessMinimum(self, individual):
        return (1/(sum(map(lambda nb: (nb+.5)**2, individual))))

class CCells():
    def __init__(self,points = None,fitness = -999):
        self.points = points
        self.fitness = fitness

class CFA():
    def __init__(self,iteration,pop_size,R1,R2,V1,V2,problem):
        self.cells = []
        self.best_cell = CCells()
        self.problem = problem
        self.iteration = iteration
        self.population_size = pop_size
        self.R1 = R1
        self.R2 = R2
        self.V1 = V1
        self.V2 = V2

    def init_population(self):
        for i in range(self.population_size):
            cells_points = np.random.uniform(self.problem.getLowerBound(), self.problem.getUpperBound(),self.problem.getDimension()) # min,max,size
            cell_fitness = self.problem.calculateFitnessMinimum(cells_points)
            temp_cell = CCells(cells_points,cell_fitness)
            self.cells.append(temp_cell)

            #cek Best Cells
            #fitness makin bagus makin baik
            if temp_cell.fitness > self.best_cell.fitness:
                self.best_cell = copy.copy(temp_cell)

    def run(self):
        self.init_population() #init random population

        self.group_size = int(self.population_size/4)
        self.first_group = []
        self.second_group = []
        self.third_group = []
        self.fourth_group = []

        #bagi populasi pada tiap group
        ctr = 0
        for i in range(self.group_size):
            self.first_group.append(self.cells[ctr])
            ctr+=1

        for i in range(self.group_size):
            self.second_group.append(self.cells[ctr])
            ctr+=1

        for i in range(self.group_size):
            self.third_group.append(self.cells[ctr])
            ctr+=1

        for i in range(self.population_size - self.group_size * 3):
            self.fourth_group.append(self.cells[ctr])
            ctr+=1

        #start
        for itr in range(self.iteration):
            #calculate average_best
            self.average_best = np.mean(self.best_cell.points)

            #case 1 & 2 (GLOBAL SEARCH)
            for i in range(len(self.first_group)):
                reflection = np.add(np.random.uniform(self.R1,self.R2,self.problem.getDimension()), self.first_group[i].points)
                #visibility = np.subtract(self.best_cell.points, self.first_group[i].points)
                visibility = np.multiply(np.random.uniform(self.V1, self.V2, self.problem.getDimension()), np.subtract(self.best_cell.points, self.first_group[i].points))

                new_cell_points = np.add(reflection, visibility)
                new_cell_points[new_cell_points>self.problem.getUpperBound()] = self.problem.getUpperBound()
                new_cell_points[new_cell_points<self.problem.getLowerBound()] = self.problem.getLowerBound()

                new_cell_fitness = self.problem.calculateFitnessMinimum(new_cell_points)
                new_cell = CCells(new_cell_points,new_cell_fitness)

                #cek new_cell vs best_cell
                if new_cell.fitness > self.best_cell.fitness:
                    self.best_cell = copy.copy(new_cell)

                #cek new_cell vs old_cell
                if new_cell.fitness > self.first_group[i].fitness:
                    self.first_group[i] = copy.copy(new_cell)

            #case 3 & 4 (LOCAL SEARCH)
            for i in range(len(self.second_group)):
                reflection = self.best_cell.points
                #visibility = np.subtract(self.best_cell.points, self.second_group[i].points)
                visibility = np.multiply(np.random.uniform(self.V1, self.V2, self.problem.getDimension()), np.subtract(self.best_cell.points, self.second_group[i].points))

                new_cell_points = np.add(reflection, visibility)
                new_cell_points[new_cell_points>self.problem.getUpperBound()] = self.problem.getUpperBound()
                new_cell_points[new_cell_points<self.problem.getLowerBound()] = self.problem.getLowerBound()

                new_cell_fitness = self.problem.calculateFitnessMinimum(new_cell_points)
                new_cell = CCells(new_cell_points,new_cell_fitness)

                # cek new_cell vs best_cell
                if new_cell.fitness > self.best_cell.fitness:
                    self.best_cell = copy.copy(new_cell)

                # cek new_cell vs old_cell
                if new_cell.fitness > self.second_group[i].fitness:
                    self.first_group[i] = copy.copy(new_cell)

            #case 5 (LOCAL SEARCH)
            for i in range(len(self.third_group)):
                reflection = self.best_cell.points
                #visibility = np.subtract(self.best_cell.points, self.average_best)
                visibility = np.multiply(np.random.uniform(self.V1, self.V2, self.problem.getDimension()), np.subtract(self.best_cell.points, self.average_best))

                new_cell_points = np.add(reflection, visibility)
                new_cell_points[new_cell_points>self.problem.getUpperBound()] = self.problem.getUpperBound()
                new_cell_points[new_cell_points<self.problem.getLowerBound()] = self.problem.getLowerBound()

                new_cell_fitness = self.problem.calculateFitnessMinimum(new_cell_points)
                new_cell = CCells(new_cell_points,new_cell_fitness)

                # cek new_cell vs best_cell
                if new_cell.fitness > self.best_cell.fitness:
                    self.best_cell = copy.copy(new_cell)

                # cek new_cell vs old_cell
                if new_cell.fitness > self.third_group[i].fitness:
                    self.first_group[i] = copy.copy(new_cell)

            #case 6 (GLOBAL SEARCH)
            for i in range(len(self.fourth_group)):
                reflection = np.random.uniform(self.problem.getLowerBound(), self.problem.getUpperBound(), self.problem.getDimension())
                visibility = 0

                new_cell_points = np.add(reflection, visibility)
                new_cell_points[new_cell_points>self.problem.getUpperBound()] = self.problem.getUpperBound()
                new_cell_points[new_cell_points<self.problem.getLowerBound()] = self.problem.getLowerBound()

                new_cell_fitness = self.problem.calculateFitnessMinimum(new_cell_points)
                new_cell = CCells(new_cell_points,new_cell_fitness)

                # cek new_cell vs best_cell
                if new_cell.fitness > self.best_cell.fitness:
                    self.best_cell = copy.copy(new_cell)

                # cek new_cell vs old_cell
                if new_cell.fitness > self.fourth_group[i].fitness:
                    self.first_group[i] = copy.copy(new_cell)

            print("Best Fitness Iterasi " + str(itr + 1) + ": " + str(1 / self.best_cell.fitness))
        print(self.best_cell.points)

step = step()
ackley = ackley()
cfa = CFA(2000,24,0.5,-0.5,2,-2,ackley)
cfa.run()

import numpy as np
import copy
from trip import trip

class CCells():
    def __init__(self, points = [], fitness = -999, other={}):
        self.points = points
        self.fitness = fitness
        self.other = other

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
            cells_points = self.problem.randomPopulation()
            cell_fitness_result = self.problem.calculateFitness(cells_points)
            cell_fitness = cell_fitness_result['fitness']
            cell_other = {}
            cell_other['time'] = cell_fitness_result['time']
            cell_other['stop_sign'] = cell_fitness_result['stop_sign']
            cell_other['is_too_late'] = cell_fitness_result['is_too_late']
            cell_other['route'] = cell_fitness_result['route']
            cell_other['misc'] = cell_fitness_result['misc']
            cell_other['misc2'] = cell_fitness_result['misc2']
            cell_other['last_place_id'] = cell_fitness_result['last_place_id']
            cell_other['other'] = cell_fitness_result['other']
            temp_cell = CCells(cells_points,cell_fitness,cell_other)
            self.cells.append(temp_cell)

            #cek Best Cells
            #fitness makin kecil makin baik
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
                reflection = np.multiply(np.random.uniform(self.R1,self.R2,self.problem.getDimension()), self.first_group[i].points)
                visibility = np.subtract(self.best_cell.points, self.first_group[i].points)

                new_cell_points = np.add(reflection, visibility)
                new_cell_fitness_result = self.problem.calculateFitness(new_cell_points)
                new_cell_fitness = new_cell_fitness_result['fitness']
                new_cell_other = {}
                new_cell_other['time'] = new_cell_fitness_result['time']
                new_cell_other['stop_sign'] = new_cell_fitness_result['stop_sign']
                new_cell_other['is_too_late'] = new_cell_fitness_result['is_too_late']
                new_cell_other['route'] = new_cell_fitness_result['route']
                new_cell_other['misc'] = new_cell_fitness_result['misc']
                new_cell_other['misc2'] = new_cell_fitness_result['misc2']
                new_cell_other['last_place_id'] = new_cell_fitness_result['last_place_id']
                new_cell_other['other'] = new_cell_fitness_result['other']
                new_cell = CCells(new_cell_points,new_cell_fitness,new_cell_other)

                # new_cell.points[new_cell.points<self.problem.getLowerBound()] = self.problem.getLowerBound()
                # new_cell.points[new_cell.points>self.problem.getUpperBound()] = self.problem.getUpperBound()

                #cek new_cell vs best_cell
                if new_cell.fitness > self.best_cell.fitness:
                    self.best_cell = copy.copy(new_cell)

                #cek new_cell vs old_cell
                if new_cell.fitness > self.first_group[i].fitness:
                    self.first_group[i] = copy.copy(new_cell)

            #case 3 & 4 (LOCAL SEARCH)
            for i in range(len(self.second_group)):
                reflection = self.best_cell.points
                visibility = np.multiply(np.random.uniform(self.V1, self.V2, self.problem.getDimension()), np.subtract(self.best_cell.points, self.second_group[i].points))

                new_cell_points = np.add(reflection, visibility)
                new_cell_fitness_result = self.problem.calculateFitness(new_cell_points)
                new_cell_fitness = new_cell_fitness_result['fitness']
                new_cell_other = {}
                new_cell_other['time'] = new_cell_fitness_result['time']
                new_cell_other['stop_sign'] = new_cell_fitness_result['stop_sign']
                new_cell_other['is_too_late'] = new_cell_fitness_result['is_too_late']
                new_cell_other['route'] = new_cell_fitness_result['route']
                new_cell_other['misc'] = new_cell_fitness_result['misc']
                new_cell_other['misc2'] = new_cell_fitness_result['misc2']
                new_cell_other['last_place_id'] = new_cell_fitness_result['last_place_id']
                new_cell_other['other'] = new_cell_fitness_result['other']
                new_cell = CCells(new_cell_points,new_cell_fitness,new_cell_other)

                # new_cell.points[new_cell.points < self.problem.getLowerBound()] = self.problem.getLowerBound()
                # new_cell.points[new_cell.points > self.problem.getUpperBound()] = self.problem.getUpperBound()

                # cek new_cell vs best_cell
                if new_cell.fitness > self.best_cell.fitness:
                    self.best_cell = copy.copy(new_cell)

                # cek new_cell vs old_cell
                if new_cell.fitness > self.second_group[i].fitness:
                    self.second_group[i] = copy.copy(new_cell)

            #case 5 (LOCAL SEARCH)
            for i in range(len(self.third_group)):
                reflection = self.best_cell.points
                visibility = np.multiply(np.random.uniform(self.V1, self.V2, self.problem.getDimension()), np.subtract(self.best_cell.points, self.average_best))

                new_cell_points = np.add(reflection, visibility)
                new_cell_fitness_result = self.problem.calculateFitness(new_cell_points)
                new_cell_fitness = new_cell_fitness_result['fitness']
                new_cell_other = {}
                new_cell_other['time'] = new_cell_fitness_result['time']
                new_cell_other['stop_sign'] = new_cell_fitness_result['stop_sign']
                new_cell_other['is_too_late'] = new_cell_fitness_result['is_too_late']
                new_cell_other['route'] = new_cell_fitness_result['route']
                new_cell_other['misc'] = new_cell_fitness_result['misc']
                new_cell_other['misc2'] = new_cell_fitness_result['misc2']
                new_cell_other['last_place_id'] = new_cell_fitness_result['last_place_id']
                new_cell_other['other'] = new_cell_fitness_result['other']
                new_cell = CCells(new_cell_points,new_cell_fitness,new_cell_other)

                # new_cell.points[new_cell.points < self.problem.getLowerBound()] = self.problem.getLowerBound()
                # new_cell.points[new_cell.points > self.problem.getUpperBound()] = self.problem.getUpperBound()

                # cek new_cell vs best_cell
                if new_cell.fitness > self.best_cell.fitness:
                    self.best_cell = copy.copy(new_cell)

                # cek new_cell vs old_cell
                if new_cell.fitness > self.third_group[i].fitness:
                    self.third_group[i] = copy.copy(new_cell)

            #case 6 (GLOBAL SEARCH)
            for i in range(len(self.fourth_group)):
                reflection = self.problem.randomPopulation()
                visibility = 0

                new_cell_points = np.add(reflection, visibility)
                new_cell_fitness_result = self.problem.calculateFitness(new_cell_points)
                new_cell_fitness = new_cell_fitness_result['fitness']
                new_cell_other = {}
                new_cell_other['time'] = new_cell_fitness_result['time']
                new_cell_other['stop_sign'] = new_cell_fitness_result['stop_sign']
                new_cell_other['is_too_late'] = new_cell_fitness_result['is_too_late']
                new_cell_other['route'] = new_cell_fitness_result['route']
                new_cell_other['misc'] = new_cell_fitness_result['misc']
                new_cell_other['misc2'] = new_cell_fitness_result['misc2']
                new_cell_other['last_place_id'] = new_cell_fitness_result['last_place_id']
                new_cell_other['other'] = new_cell_fitness_result['other']
                new_cell = CCells(new_cell_points,new_cell_fitness,new_cell_other)

                # new_cell.points[new_cell.points > self.problem.getUpperBound()] = self.problem.getUpperBound()
                # new_cell.points[new_cell.points < self.problem.getLowerBound()] = self.problem.getLowerBound()

                # cek new_cell vs best_cell
                if new_cell.fitness > self.best_cell.fitness:
                    self.best_cell = copy.copy(new_cell)

                # cek new_cell vs old_cell
                if new_cell.fitness > self.fourth_group[i].fitness:
                    self.fourth_group[i] = copy.copy(new_cell)

            # print("Best Fitness Iterasi " + str(itr + 1) + ": " + self.problem.convertFitnessValue(self.best_cell.fitness) + " | "+str(self.best_cell.other['time']) + " | " + str(self.best_cell.other['stop_sign'] + 1))
            print("Best Fitness Iterasi " + str(itr + 1) + ": " + str(1/self.best_cell.fitness) + " | "+str(self.best_cell.other['time']) + " | " + str(self.best_cell.other['stop_sign']))

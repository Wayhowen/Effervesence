import numpy as np
import random
from fitness_simulation import Evaluator
from chromosome import Chromosome
from typing import List, Dict

class Evolve:
    def __init__(self, population_size, selection_size, truncation_size=4, statistical_significance=0.2) -> None:
        self.population_size = population_size
        self.selection_size = selection_size
        self.truncation_size = truncation_size
        self.statistical_significance = statistical_significance

        self._last_fitness_score = 0
        self.evaluator = Evaluator()
        

    def work(self):
        initial_population = self._generate_population()
        offspring_with_fitness = {offspring: self._compute_fitness(offspring) for offspring in initial_population}

        # while not converged
        while not self._is_converged(offspring_with_fitness):
            new_offspring: List[Chromosome] = []

            # select
            selected_offspring = self._select_offspring(offspring_with_fitness)
            new_offspring.extend(selected_offspring)

            # crossover
            crossed_over_offspring = self._crossover(selected_offspring)
            new_offspring.extend(crossed_over_offspring)

            # mutate
            mutated_offspring = self._mutate(new_offspring)
            new_offspring.extend(mutated_offspring)
            
            # compute fitness
            offspring_with_fitness = {offspring: self._compute_fitness(offspring) for offspring in new_offspring}

    def _generate_population(self, size=60) -> List[Chromosome]:
        return [Chromosome() for _ in range(size)]

    """
    combination of truncation and roulette
    """
    def _select_offspring(self, offspring_with_fitness: Dict[Chromosome, float]) -> List[Chromosome]:
        sorted_offspring = dict(sorted(offspring_with_fitness.items(), key=lambda offspring: offspring[1]))

        # truncation
        new_offspring = list(sorted_offspring.keys())[:self.truncation_size]

        # roulette
        for _ in range(self.selection_size - self.truncation_size):
            new_offspring.extend(random.choice(list(sorted_offspring.keys())[self.truncation_size:]))

        return new_offspring

    def _crossover(self, selected_offspring: List[Chromosome]) -> List[Chromosome]:
        new_offspring: List[Chromosome] = []
        pairs = [[x, y] for x in selected_offspring for y in selected_offspring]
        for pair in pairs:
            new_offspring.extend(Chromosome((pair[0].q_table + pair[1].q_table) / 2))
        return new_offspring


    def _mutate(self, new_offspring: List[Chromosome]) -> List[Chromosome]:
        #mut = np.random.uniform(-20, 20, (4,3))
        pass

    def _compute_fitness(self, offspring: Chromosome) -> float:
        return self.evaluator.eval(offspring.q_table)

    def _is_converged(self, offspring_with_fitness: Dict[Chromosome, float]) -> bool:
        current_fitness_score = sum(offspring_with_fitness.values()) / len(offspring_with_fitness)
        if self._last_fitness_score == 0:
            self._last_fitness_score = current_fitness_score
            return False 
        return abs(current_fitness_score - self._last_fitness_score) < self.statistical_significance


if __name__ == "__main__":
    e = Evolve(60, 8)
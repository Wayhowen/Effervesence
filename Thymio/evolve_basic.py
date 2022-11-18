import time
import numpy as np
import random

from simulator.behaviors.evolution.tagger_maximizer import TaggerMaximizer
from simulator.robot_model.controller import Controller
from simulator_main import Main
from evolution.chromosome import Chromosome
from typing import List, Dict


class Evolve:
    def __init__(self, population_size, selection_size, truncation_size=4, statistical_significance=0.2) -> None:
        self.population_size = population_size
        self.selection_size = selection_size
        self.truncation_size = truncation_size
        self.statistical_significance = statistical_significance

        # change this to maximize different behavior
        self._maximizer_to_use = TaggerMaximizer

        self._last_fitness_score = 0
        self.evaluator = Main(number_of_robots=5, frequency_of_saves=50, number_of_steps=5000)

    def get_maximizer(self, q_table):
        return TaggerMaximizer(
            self.evaluator.simulator,
            Controller(self.evaluator.simulator.W, self.evaluator.simulator.H), q_table,
            self.evaluator.number_of_steps
        )

    def work(self):
        # mock maximizer, useless
        mock_maximizer = self.get_maximizer([])
        initial_population = self._generate_population(len(mock_maximizer.states), len(mock_maximizer.actions))

        offspring_with_fitness = {offspring: self._compute_fitness(offspring) for offspring in initial_population}
        n = 0

        # while not converged
        while not self._is_converged(offspring_with_fitness):
            print("Gen:", n)
            n += 1

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
            best = sorted(offspring_with_fitness.items(), key=lambda offspring: offspring[1], reverse=True)[0]
            print("Best table this gen:", best[0].get_table())
            print("Score:", best[1])

        best = sorted(offspring_with_fitness.items(), key=lambda offspring: offspring[1], reverse=True)[0]
        return best

    def _generate_population(self, x, y) -> List[Chromosome]:
        return [Chromosome(x=x, y=y) for _ in range(self.population_size)]

    """
    combination of truncation and roulette
    """
    def _select_offspring(self, offspring_with_fitness: Dict[Chromosome, float]) -> List[Chromosome]:
        sorted_offspring = dict(sorted(offspring_with_fitness.items(), key=lambda offspring: offspring[1], reverse=True))

        # truncation
        new_offspring = list(sorted_offspring.keys())[:self.truncation_size]

        # roulette
        i = list(sorted_offspring.keys())[self.truncation_size:]
        new_offspring.extend(list(random.sample(i, self.selection_size - self.truncation_size)))

        return new_offspring

    def _crossover(self, selected_offspring: List[Chromosome]) -> List[Chromosome]:
        new_offspring: List[Chromosome] = []
        pairs = [[x, y] for x in selected_offspring for y in selected_offspring]
        for pair in pairs:
            new_offspring.append(Chromosome((pair[0].q_table + pair[1].q_table) / 2))
        return new_offspring

    def _mutate(self, offspring: List[Chromosome]) -> List[Chromosome]:
        new_offspring: List[Chromosome] = []
        for _ in range(self.population_size - len(offspring)):
            random_chromosome = np.random.choice(new_offspring)
            random_mask = np.stack([np.random.choice(a=[0, 1], size=random_chromosome.q_table.shape[1], p=[0.25, 0.75]) for _ in range(random_chromosome.q_table.shape[0])])
            masked_q_table = random_chromosome.q_table * random_mask
            masked_q_table[masked_q_table == 0] = random.uniform(np.min(masked_q_table), np.max(masked_q_table))
            new_offspring.append(Chromosome(masked_q_table))
        return new_offspring

    def _compute_fitness(self, offspring: Chromosome) -> float:
        print("Evaluating...")
        return self.evaluator.eval(self.get_maximizer(offspring.get_table()))

    def _is_converged(self, offspring_with_fitness: Dict[Chromosome, float]) -> bool:
        current_fitness_score = sum(offspring_with_fitness.values()) / len(offspring_with_fitness)
        if self._last_fitness_score == 0:
            self._last_fitness_score = current_fitness_score
            return False 
        return abs(current_fitness_score - self._last_fitness_score) < self.statistical_significance


if __name__ == "__main__":
    print("Setup...")
    start = time.time()
    e = Evolve(15, 4, 2, 1000)
    print("Training Started...")
    result = e.work()
    print("Training Complete")
    print("Best table:", result[0].get_table())
    print("Score:", result[1])
    end = time.time()
    print("Time training:", end - start)
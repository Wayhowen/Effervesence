import time
from datetime import datetime
import numpy as np
import random
from itertools import combinations

from simulator.behaviors.behavior import Behavior
from simulator.behaviors.evolution.avoider_maximizer import AvoiderMaximizer
from simulator.behaviors.evolution.reverse_avoider import ReverseAvoider
from simulator.behaviors.evolution.tagger_maximizer import TaggerMaximizer
from simulator.robot_model.controller import Controller
from simulator_main import Main
from evolution.chromosome import Chromosome
from typing import List, Dict, Tuple


class Evolve:
    def __init__(self, population_size, selection_size, truncation_size=4, statistical_significance=0.2, reverse=False) -> None:
        self.population_size = population_size
        self.selection_size = selection_size
        self.truncation_size = truncation_size
        self.statistical_significance = statistical_significance
        self._reverse = reverse
        self.date_time = datetime.now().strftime("%m%d%Y_%H%M%S")
        self.n = 0

        self._last_tagger_fitness_score = 0
        self._last_avoider_fitness_score = 0

        self.evaluator = Main(number_of_robots=5, frequency_of_saves=50, number_of_steps=1800, reverse=reverse)
        self.mock_tagger = self.get_tagger([])
        self.mock_avoider = self.get_avoider([])
        self.best_avoider = (Chromosome(len(self.mock_tagger.states), len(self.mock_tagger.actions)), 0.0)
        self.best_avoider = (Chromosome(len(self.mock_avoider.states), len(self.mock_avoider.actions)), 0.0)

    def get_tagger(self, q_table):
        return TaggerMaximizer(
            self.evaluator.simulator,
            Controller(self.evaluator.simulator.W, self.evaluator.simulator.H), q_table,
            self.evaluator.number_of_steps
        )

    def get_avoider(self, q_table):
        if self._reverse:
            return ReverseAvoider(
                self.evaluator.simulator,
                Controller(self.evaluator.simulator.W, self.evaluator.simulator.H, self._reverse), q_table,
                self.evaluator.number_of_steps
            )
        return AvoiderMaximizer(
            self.evaluator.simulator,
            Controller(self.evaluator.simulator.W, self.evaluator.simulator.H), q_table,
            self.evaluator.number_of_steps
        )

    def work(self):
        # mock maximizer, useless

        initial_population = self._generate_population(len(self.mock_tagger.states), len(self.mock_tagger.actions))

        offspring_with_fitness = {offspring: self._compute_fitness(self.get_avoider(offspring.get_table())) for
                                  offspring in initial_population}
        self.best_tagger = sorted(offspring_with_fitness.items(), key=lambda offspring: offspring[1], reverse=True)[0]
        print(f"Sorted scores are : {list(self.best_tagger)}")
        print("Best table this gen:", repr(self.best_tagger[0].get_table()))
        print("Score:", self.best_tagger[1])
        self.save_stats("tagger")
        self.save_table("tagger")

        # while not converged
        while not self._update_and_check_convergence(offspring_with_fitness):
            print("Gen:", self.n)
            self.n += 1

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
            offspring_with_fitness = {offspring: self._compute_fitness(self.get_avoider(offspring.get_table())) for
                                      offspring in new_offspring}
            self.best_tagger = sorted(offspring_with_fitness.items(), key=lambda offspring: offspring[1], reverse=True)[
                0]
            print(f"Sorted scores are : {list(self.best_avoider)}")
            print("Best table this gen:", repr(self.best_avoider[0].get_table()))
            print("Score:", self.best_avoider[1])
            self.save_stats("tagger")
            self.save_table("tagger")

        return self.best_avoider

    def work_dual(self, tagger_q_table=None, avoider_q_table=None):
        # initial populations
        if tagger_q_table is not None:
            init_tag_pop = self._generate_population_based_on_table(tagger_q_table)
        else:
            init_tag_pop = self._generate_population(
                len(self.mock_tagger.states), len(self.mock_tagger.actions)
            )
        if avoider_q_table is not None:
            init_avoid_pop = self._generate_population_based_on_table(avoider_q_table)
        else:
            init_avoid_pop = self._generate_population(
                len(self.mock_avoider.states), len(self.mock_avoider.actions)
            )

        tagger_offspring = {offspring: self._compute_fitness(self.get_tagger(offspring.get_table())) for offspring in
                            init_tag_pop}
        self.best_tagger = sorted(tagger_offspring.items(), key=lambda offspring: offspring[1], reverse=True)[0]
        # print(f"Sorted scores are : {list(self.best_tagger)}")
        print("Best tagger table this gen:", repr(self.best_tagger[0].get_table()))
        print("Tagger score:", self.best_tagger[1])
        self.save_stats("tagger")
        self.save_table("tagger")

        avoider_offspring = {offspring: self._compute_fitness(self.get_avoider(offspring.get_table()),
                                                              self.get_tagger(self.best_tagger[0].get_table())) for
                             offspring in init_avoid_pop}
        self.best_avoider = sorted(avoider_offspring.items(), key=lambda offspring: offspring[1], reverse=True)[0]
        # print(f"Sorted scores are : {list(self.best_tagger)}")
        print("Best avoider table this gen:", repr(self.best_avoider[0].get_table()))
        print("Avoider score:", self.best_avoider[1])
        self.save_stats("avoider")
        self.save_table("avoider")

        print("Setup finished")

        # while not converged
        t_convergence = False
        a_convergence = False
        while not (t_convergence and a_convergence):
            self.n += 1
            print("Run:", self.n)

            t_convergence = self._update_and_check_convergence(tagger_offspring, "tagger")
            a_convergence = self._update_and_check_convergence(avoider_offspring, "avoider")
            print(f"tagger off {t_convergence}")
            print(f"avoider off {a_convergence}")
            current_offspring = tagger_offspring if self.n % 2 != 0 else avoider_offspring
            competitive = self.get_tagger(self.best_tagger[0].get_table()) if self.n % 2 != 0 else self.get_avoider(
                self.best_avoider[0].get_table())
            print(current_offspring)
            # print(competitive)

            new_offspring: List[Chromosome] = []

            # select
            selected_offspring = self._select_offspring(current_offspring)
            new_offspring.extend(selected_offspring)

            # crossover
            crossed_over_offspring = self._crossover(selected_offspring)
            new_offspring.extend(crossed_over_offspring)

            # mutate
            mutated_offspring = self._mutate(new_offspring)
            new_offspring.extend(mutated_offspring)

            # compute fitness
            if self.n % 2 != 0:
                print("Training tagger")
                tagger_offspring = {
                    offspring: self._compute_fitness(self.get_tagger(offspring.get_table()), competitive) for offspring
                    in new_offspring}
                self.best_tagger = sorted(tagger_offspring.items(), key=lambda offspring: offspring[1], reverse=True)[
                    0]
                # print(f"Sorted scores are : {list(self.best_tagger)}")
                print("Best table this gen:", repr(self.best_tagger[0].get_table()))
                print("Score:", self.best_tagger[1])
                self.save_stats("tagger")
                self.save_table("tagger")
            else:
                print("Training avoider")
                avoider_offspring = {
                    offspring: self._compute_fitness(self.get_avoider(offspring.get_table()), competitive) for offspring
                    in new_offspring}
                self.best_avoider = sorted(avoider_offspring.items(), key=lambda offspring: offspring[1], reverse=True)[
                    0]
                # print(f"Sorted scores are : {list(self.best_avoider)}")
                print("Best table this gen:", repr(self.best_avoider[0].get_table()))
                print("Score:", self.best_avoider[1])
                self.save_stats("avoider")
                self.save_table("avoider")

        return self.best_tagger, self.best_avoider

    def _generate_population(self, x, y) -> List[Chromosome]:
        return [Chromosome(x=x, y=y) for _ in range(self.population_size)]

    def _generate_population_based_on_table(self, q_table: np.array):
        population = [Chromosome(q_table) for _ in range(self.population_size)]
        population = self._mutate(population, probabilities=(0.75, 0.25), all_population=True)

        return population

    """
    combination of truncation and roulette
    """

    def _select_offspring(self, offspring_with_fitness: Dict[Chromosome, float]) -> List[Chromosome]:
        sorted_offspring = dict(
            sorted(offspring_with_fitness.items(), key=lambda offspring: offspring[1], reverse=True))

        # truncation
        new_offspring = list(sorted_offspring.keys())[:self.truncation_size]

        # roulette
        i = list(sorted_offspring.keys())[self.truncation_size:]
        new_offspring.extend(list(random.sample(i, self.selection_size - self.truncation_size)))

        return new_offspring

    def _crossover(self, selected_offspring: List[Chromosome]) -> List[Chromosome]:
        new_offspring: List[Chromosome] = []
        pairs = [comb for comb in combinations(selected_offspring, 2)]
        for pair in pairs:
            new_offspring.append(Chromosome((pair[0].q_table + pair[1].q_table) / 2))
        return list(random.sample(new_offspring, int((self.population_size - len(selected_offspring)) / 2)))

    def _mutate(self, offspring: List[Chromosome], probabilities: Tuple[float, float] = (0.25, 0.75), all_population = False) -> List[
        Chromosome]:
        new_offspring: List[Chromosome] = []
        size = self.population_size if all_population else self.population_size - len(offspring)
        for _ in range(size):
            random_chromosome = np.random.choice(offspring)
            mask_elems = [np.random.choice(a=[0, 1], size=random_chromosome.q_table.shape[1], p=probabilities) for _ in
                 range(random_chromosome.q_table.shape[0])]
            random_mask = np.stack(mask_elems)
            masked_q_table = random_chromosome.q_table * random_mask
            masked_q_table[masked_q_table == 0] = random.uniform(np.min(masked_q_table), np.max(masked_q_table))
            new_offspring.append(Chromosome(masked_q_table))
        return new_offspring

    def _compute_fitness(self, maximizer: Behavior, competitive_behavior: Behavior = None) -> float:
        print("Evaluating...")
        fit = self.evaluator.eval(
            maximizer,
            competitive_behavior
        )
        print(fit)
        return fit

    def _update_and_check_convergence(self, offspring_with_fitness: Dict[Chromosome, float],
                                      population_type: str) -> bool:
        current_fitness_score = sum(offspring_with_fitness.values()) / len(offspring_with_fitness)
        print("Generation average:", current_fitness_score)

        if population_type == "tagger":
            if self._last_tagger_fitness_score == 0:
                self._last_tagger_fitness_score = current_fitness_score
                return False
            change = abs(current_fitness_score - self._last_tagger_fitness_score)
            print("Significance of tagger generation:", change)
            self._last_tagger_fitness_score = current_fitness_score
            return change < self.statistical_significance
        else:
            if self._last_avoider_fitness_score == 0:
                self._last_avoider_fitness_score = current_fitness_score
                return False
            change = abs(current_fitness_score - self._last_avoider_fitness_score)
            print("Significance of avoider generation:", change)
            self._last_avoider_fitness_score = current_fitness_score
            return change < self.statistical_significance

    def save_table(self, behavior_type: str):
        to_save = self.best_avoider[0].get_table() if behavior_type == "avoider" else self.best_tagger[0].get_table()
        with open(f"data/tables/Q_table_{self.date_time}_{behavior_type}.txt", "ab") as file:
            np.save(file, to_save, allow_pickle=True)

    def save_stats(self, behavior_type: str):
        to_use = f"{self.best_avoider[1] if behavior_type == 'avoider' else self.best_tagger[1]}"
        with open(f"data/stats/Stats_{self.date_time}_{behavior_type}.txt", "a") as file:
            file.write(to_use)


if __name__ == "__main__":
    print("Setup...")
    start = time.time()
    # this for better pcs
    # e = Evolve(15, 4, 2, 1000)
    e = Evolve(20, 4, 2, 1000)

    try:
        print("Training Started...")
        result = e.work()
        print("Training Complete")
        print("Best table:", repr(result[0].get_table()))

        print("Score:", result[1])
        end = time.time()
        print("Time training:", end - start)
    finally:
        print("Saving...")
        e.save_table("tagger")
        e.save_stats("tagger")

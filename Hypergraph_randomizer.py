import random
from Hypergraph import hypergraph
from Brute_force_immersion import brute_force_immersion
from Immersion import immersion
import time


class hypergraph_ramdomizer:

    def __init__(self, min_node_count: int, max_node_count: int, min_edge_count: int, max_edge_count: int) -> None:
        '''
        :param min_node_count: the minimum initial node count
        :param max_node_count: the maximum initial node count
        :param min_edge_count: the minimum initial edge count
        :param max_edge_count: the maximum initial edge count
        '''

        self.__min_node_count = min_node_count
        self.__max_node_count = max_node_count
        self.__min_edge_count = min_edge_count
        self.__max_edge_count = max_edge_count
        self.generated_hypergraphs = []
        self.generated_immersions = []
        self.combos = []
        self.selected_H = None
        self.selected_G = None
        pass
    
    def clear(self) -> None:
        self.generated_hypergraphs.clear()
        self.generated_immersions.clear()
        self.combos.clear()
        pass

    def random_hypergraph(self) -> hypergraph:
        return random.choice(self.generated_hypergraphs)

    def generate(self, power: int = 2, skim: bool = True, write = True) -> hypergraph:
        '''
        :param skim: true if you want to use the skim function befure returning the result
        '''

        node_count = random.randint(self.__min_node_count, self.__max_node_count)
        edge_count = random.randint(min(1, self.__min_edge_count), self.__max_edge_count)

        possibilities = []
        for n in range(power):
            possibilities.append(random.randint(2, node_count))
        initial_edge_size = min(possibilities)
        edges = dict()
        edges[0] = set(range(initial_edge_size))
        interconnected_pool = set(range(initial_edge_size))
        for edge_number in range(1, edge_count):
            possibilities.clear()
            for n in range(power):
                possibilities.append(random.randint(1, node_count))
            edge_size = min(possibilities)
            edges[edge_number] = {random.choice(list(interconnected_pool)),}
            for useless in range(1, edge_size):
                edges[edge_number].add(random.randrange(0, node_count))
            interconnected_pool |= edges[edge_number]
        
        graph = hypergraph(interconnected_pool, edges)
        if skim:
            graph.skim()
        for index in range(len(self.generated_hypergraphs)):
            if self.generated_hypergraphs[index] >= graph:
                self.combos.append((index, len(self.generated_hypergraphs)))
            elif self.generated_hypergraphs[index] <= graph:
                self.combos.append((len(self.generated_hypergraphs), index))
        if write:
            self.generated_hypergraphs.append(graph)
        return graph
    
    def select_graphs(self) -> bool:
        if len(self.combos) == 0:
            return False
        combo = self.combos.pop(random.randrange(len(self.combos)))
        self.selected_G = self.generated_hypergraphs[combo[0]]
        self.selected_H = self.generated_hypergraphs[combo[1]]
        return True
    
    # retruns a list of every immersion function, if there are none, returns an empty list
    def random_brute_force_immersion(self, dupe_check: bool = False, immersion_check: bool = False) -> list:
        '''
        :param dupe_check: if true, performs a check for duplicate immersions
        :param immersion_check: if true, checks to see if every outputted immersion is an actual immersion
        '''
        if self.select_graphs():
            alpha = brute_force_immersion(self.selected_G, self.selected_H)
            alpha.immerse()
            self.generated_immersions += alpha.immersions
            if immersion_check:
                real_immersions = 0
                false_immersions = 0
                for i in alpha.immersions:
                    if i.is_immersion():
                        real_immersions += 1
                    else:
                        false_immersions += 1
                print("Verified Immersions:", real_immersions)
                print("False Outputs:", false_immersions)
            if dupe_check:
                for i in range(len(alpha.immersions)):
                    for j in range(i):
                        if alpha.immersions[i].equal_edge_mapping(alpha.immersions[j]):
                            print("duplicate output below:")
                            print(alpha.immersions[i])
                            print()
                            print(alpha.immersions[j])
                            print()
                            return alpha.immersions
            return alpha.immersions
        return []
    
    # retruns a list of every immersion function, if there are none, returns an empty list
    def random_immersion(self, dupe_check: bool = False, immersion_check: bool = False) -> list:
        '''
        :param dupe_check: if true, performs a check for duplicate immersions
        :param immersion_check: if true, checks to see if every outputted immersion is an actual immersion
        '''
        if self.select_graphs():
            alpha = immersion(self.selected_G, self.selected_H)
            alpha.immerse()
            self.generated_immersions += alpha.immersions
            if immersion_check:
                real_immersions = 0
                false_immersions = 0
                for i in alpha.immersions:
                    if i.is_immersion():
                        real_immersions += 1
                    else:
                        false_immersions += 1
                print("Verified Immersions:", real_immersions)
                print("False Outputs:", false_immersions)
            if dupe_check:
                for i in range(len(alpha.immersions)):
                    for j in range(i):
                        if alpha.immersions[i].equal_edge_mapping(alpha.immersions[j]):
                            print("duplicate output below:")
                            print(alpha.immersions[i])
                            print()
                            print(alpha.immersions[j])
                            print()
                            return alpha.immersions
            return alpha.immersions
        return []
    
    def compare(self, max_immersion_count: int, use_random_priority: bool = False) -> None:
        '''
        :param max_immersion_count: how many times it will attempt to do a random immersion opperation
        :param use_random_priority: if True, the priority for the main immersion algorithom will be random, and if False, it will use a specific higharchy to set priority
        '''
        if len(self.combos) == 0:
            print("Unable to perform any immersions. Generate more graphs.")
            return None
        
        # getting the list of immersions to do
        combos = self.combos.copy()
        immersion_count = min(len(self.combos), max_immersion_count)
        immersion_list = []
        for u in range(immersion_count):
            immersion_list.append(combos.pop(random.randrange(len(combos))))

        print("Performing", immersion_count, "imersions...")

        # timing brute force immersions
        brute_force_immersions = []
        start = time.perf_counter()
        for i in immersion_list:
            alpha = brute_force_immersion(self.generated_hypergraphs[i[0]].copy(), self.generated_hypergraphs[i[1]].copy())
            alpha.immerse()
            brute_force_immersions += alpha.immersions
        stop = time.perf_counter()
        brute_force_time = stop - start

        print("Brute Force Immersion Time:", brute_force_time)

        # timing for regular immersions
        immersions = []
        start = time.perf_counter()
        for i in immersion_list:
            alpha = immersion(self.generated_hypergraphs[i[0]].copy(), self.generated_hypergraphs[i[1]].copy())
            alpha.immerse(use_random_priority)
            immersions += alpha.immersions
        stop = time.perf_counter()
        regular_time = stop - start

        print("Regular immersion time:", regular_time)

        # checking for any errors
        if len(immersions) > len(brute_force_immersions):
            print("The regular immersion algrithom generated more results")
        elif len(brute_force_immersions) > len(immersions):
            print("The brute force immersion algrithom generated more results")
        for i in immersions:
            found = False
            for j in brute_force_immersions:
                if i.equal_edge_mapping(j):
                    found = True
                    break
            if not found:
                print("The brute force immersion failed to generate an immersion:")
                print(i.is_immersion())
                print(i)
                break
        for i in brute_force_immersions:
            found = False
            for j in immersions:
                if i.equal_edge_mapping(j):
                    found = True
                    break
            if not found:
                print("The regular immersion failed to generate an immersion:")
                print(i.is_immersion())
                print(i)
                break
        '''
        # dupe checking
        regular_dupe = False
        brute_force_dupe = False
        for i in range(len(immersions)):
            for j in range(i):
                if immersions[i].equal_edge_mapping(immersions[j]):
                    print("regular duplicate output!!!")
                    regular_dupe = True
                    break
            if regular_dupe:
                break
        for i in range(len(brute_force_immersions)):
            for j in range(i):
                if brute_force_immersions[i].equal_edge_mapping(brute_force_immersions[j]):
                    print("brute force duplicate output!!!")
                    brute_force_dupe = True
                    break
            if brute_force_dupe:
                break
        '''
        pass

    def single_time_compare(self, use_random_priority: bool = False) -> None:
        '''
        :param use_random_priority: if True, the priority for the main immersion algorithom will be random, and if False, it will use a specific higharchy to set priority
        '''
        if self.select_graphs():
            print("G:", self.selected_G)
            print("H:", self.selected_H)
            print("\n")

            alpha = immersion(self.selected_G.copy(), self.selected_H.copy())
            start = time.perf_counter()
            alpha.immerse(use_random_priority)
            stop = time.perf_counter()

            print("Regular immersion time:", stop - start)
            print("Immersions Found:", len(alpha.immersions))
            print()

            alpha = brute_force_immersion(self.selected_G.copy(), self.selected_H.copy())
            start = time.perf_counter()
            alpha.immerse()
            stop = time.perf_counter()

            print("Brute Force immersion time:", stop - start)
            print("Immersions Found:", len(alpha.immersions))
            print()

            self.generated_immersions += alpha.immersions
            return None
        print("No combonations available for immersion testing")
        return None

import time
import networkx as nx
import matplotlib.pyplot as plt
from IPython.display import clear_output

class Problem:

    def __init__(self, initial_state, actions, transition_model, goal_test):

        self.initial_state = initial_state
        self.actions = actions
        self.transition_model = transition_model
        self.goal_test = goal_test


class ComputerAssemblyProblem(Problem):
    
    """Modela o problema de montar um computador."""
    
    def __init__(self):

        super().__init__(initial_state = 'Peças na Mesa',
                         actions = self.get_actions,
                         transition_model = self.apply_action,
                         goal_test = self.goal_test)
        
        self.actions_map = {'Peças na Mesa':['Montar Componentes'],
                            'Componentes Montados':['Ligar para Teste'],
                            'Sucesso no Teste':['Instalar SO'],
                            'Erro no Teste':['Diagnosticar Erro'],
                            'Erro Diagnosticado':['Corrigir e Testar']}
        
        self.transitions_map = {('Peças na Mesa', 'Montar Componentes'):'Componentes Montados',
                                ('Componentes Montados', 'Ligar para Teste'):['Sucesso no Teste', 'Erro no Teste'],
                                ('Sucesso no Teste', 'Instalar SO'):'PC Pronto',
                                ('Erro no Teste', 'Diagnosticar Erro'):'Erro Diagnosticado',
                                ('Erro Diagnosticado', 'Corrigir e Testar'):'Sucesso no Teste'}
                            
        self.goal = 'PC Pronto'

    
    def get_actions(self, state):
        return self.actions_map.get(state, [])

    def apply_action(self, state, action):
        return self.transitions_map.get((state, action), None)

    def goal_test(self, state):
        return state == self.goal


def plot_solution_graph(problem, plan):

    G = nx.DiGraph()
    edge_labels = {}

    initial_state = problem.initial_state
    G.add_node(initial_state)

    def build_graph_from_plan(parent_state, current_plan):
        
        if not current_plan: 
            return

        action = current_plan['action']
        sub_plan = current_plan['plan']
        
        if len(sub_plan) > 1: 
            and_node = f'AND_{action[:10].replace(" ", "_")}'
            
            G.add_node(and_node, shape = 's', color = 'black', size = 100)
            G.add_edge(parent_state, and_node)
            
            edge_labels[(parent_state, and_node)] = action
            
            for state, next_plan_part in sub_plan.items():
                G.add_edge(and_node, state)
                build_graph_from_plan(state, next_plan_part)
        
        else: 
            next_state = list(sub_plan.keys())[0]
            next_plan_part = sub_plan[next_state]
            
            G.add_edge(parent_state, next_state)
            
            edge_labels[(parent_state, next_state)] = action
            build_graph_from_plan(next_state, next_plan_part)

    build_graph_from_plan(initial_state, plan)
    
    node_colors = []

    for node in G:
        if node == problem.initial_state:
            node_colors.append('tab:blue')
        
        elif problem.goal_test(node):
            node_colors.append('tab:red')
        
        elif isinstance(node, str) and node.startswith('AND_'):
            node_colors.append('tab:green')
        
        else:
            node_colors.append('tab:orange')

    node_sizes = [100 if isinstance(node, str) and node.startswith('AND_') else 2000 for node in G]
    
    plt.figure(figsize = (12, 7))
    pos = nx.spring_layout(G, k = 5.0) 
    
    nx.draw(G, pos, with_labels = True, node_color = node_colors, node_size = node_sizes, 
            arrowsize = 20, font_size = 9, font_weight = 'bold', alpha = 0.5)
    
    nx.draw_networkx_edge_labels(G, pos, edge_labels = edge_labels, 
                                 font_color='red', font_size = 8)
    
    plt.show()


def simulate_online_search(model, max_iterations = 100):

    current_state = model.problem.initial_state
    path = [current_state]
    iterations = 0

    def print_maze(current_pos):

        clear_output(wait = True)
        
        print(f"Agente em: {current_pos} | Objetivo: {model.problem.goal}")
        print("--------------------")
        for r, row in enumerate(model.problem.maze_map):
            line = ""
            for c, char in enumerate(row):
                if (r, c) == current_pos:
                    line += " A " 
                else:
                    line += f" {char} "
            print(line)
        print("--------------------")
         
        time.sleep(0.2)

    while True:
        print_maze(current_state)
        
        if iterations >= max_iterations:
            print(f"\nLimite de {max_iterations} iterações atingido!")
            break

        iterations += 1

        action = model.decide_next_action(current_state)
        
        print(f"Agente decide: {action} (Passo: {iterations})")
        
        if action == "stop":
            if model.problem.goal_test(current_state):
                print("\nObjetivo alcançado!")
            else:
                print("\nAgente ficou preso e não encontrou solução.")
            break
            
        current_state = model.problem.apply_action(current_state, action)
        path.append(current_state)

    print("\nCaminho total percorrido pelo agente (incluindo backtrack):")
    print(" -> ".join(map(str, path)))
    
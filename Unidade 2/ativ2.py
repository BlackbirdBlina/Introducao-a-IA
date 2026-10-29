import os
import time

def manhattan_heuristic(state, goals):
    """
    Calcula a menor distância de Manhattan da posição atual (x, y)
    até qualquer uma das células objetivo contidas em 'goals'.
    """
    
    if not goals:
        return 0
    
    x, y, _ = state
    
    return min(abs(x - gx) + abs(y - gy) for gx, gy in goals)


def generate_wumpus_kb0():
    """Gera o conjunto inicial de cláusulas em CNF (KB_0) para o Mundo do Wumpus 4x4."""
    
    kb0_clauses = []

    def get_adjacent(x, y):
        adj = []
        
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            
            if 1 <= nx <= 4 and 1 <= ny <= 4:
                adj.append((nx, ny))
        
        return adj

    # 1. A célula (1,1) é segura no início: sem Poço e sem Wumpus
    kb0_clauses.append(["-P_1_1"])
    kb0_clauses.append(["-W_1_1"])

    # 2. Regras de Brisa e Poços: B_x,y <=> (P_adj1 \/ P_adj2 \/ ...)
    for x in range(1, 5):
        for y in range(1, 5):
            breeze = f"B_{x}_{y}"
            adj_pits = [f"P_{ax}_{ay}" for ax, ay in get_adjacent(x, y)]

            # B_x,y => (P_adj1 \/ P_adj2 \/ ...) === (-B_x,y \/ P_adj1 \/ P_adj2 ...)
            kb0_clauses.append([f"-{breeze}"] + adj_pits)

            # Para cada vizinho: P_adj => B_x,y === (-P_adj \/ B_x,y)
            for pit in adj_pits:
                kb0_clauses.append([f"-{pit}", breeze])

    # 3. Regras de Fedor e Wumpus: S_x,y <=> (W_adj1 \/ W_adj2 \/ ...)
    for x in range(1, 5):
        for y in range(1, 5):
            stench = f"S_{x}_{y}"
            adj_wumpus = [f"W_{ax}_{ay}" for ax, ay in get_adjacent(x, y)]

            # S_x,y => (W_adj1 \/ W_adj2 \/ ...) === (-S_x,y \/ W_adj1 \/ W_adj2 ...)
            kb0_clauses.append([f"-{stench}"] + adj_wumpus)

            # Para cada vizinho: W_adj => S_x,y === (-W_adj \/ S_x,y)
            for wumpus in adj_wumpus:
                kb0_clauses.append([f"-{wumpus}", stench])

    return kb0_clauses


class WumpusEnvironment:
    """
    Simulador do ambiente do Mundo do Wumpus (Grid 4x4).
    Mantém o estado real/oculto do mapa (Poços, Wumpus, Ouro) e processa
    a física do agente, retornando percepções e atualizando a pontuação.
    """

    ORIENTATIONS = ['N', 'E', 'S', 'W']
    OFFSETS = {'N': (0, 1), 'E': (1, 0), 'S': (0, -1), 'W': (-1, 0)}

    
    def __init__(self, pit_locations, wumpus_location, gold_location, agent_start=(1, 1, 'E')):
        """
        pit_locations: Lista/Set de tuplas (x, y) com a posição dos poços
        wumpus_location: Tupla (x, y) com a posição do Wumpus
        gold_location: Tupla (x, y) com a posição da pepita de ouro
        agent_start: Tupla (x, y, orientacao) inicial do agente
        """
        
        self.pits = set(pit_locations)
        self.wumpus = wumpus_location
        self.gold = gold_location

        # Estado do agente no ambiente
        self.agent_loc = agent_start  # (x, y, orientacao)
        self.has_gold = False
        self.is_wumpus_alive = True
        self.agent_alive = True
        self.agent_exited = False
        self.score = 0

        
    def get_percept(self):
        """
        Gera o dicionário de percepções locais na posição atual do agente.
        > return: dict {'stench': bool, 'breeze': bool, 'glitter': bool}
        """
        
        x, y, _ = self.agent_loc

        # Fedor (Stench): Wumpus está vivo e está na mesma célula ou em célula adjacente
        stench = self.is_wumpus_alive and ((x, y) == self.wumpus or self._is_adjacent((x, y), self.wumpus))

        # Brisa (Breeze): Pelo menos um poço está em célula adjacente
        breeze = any(self._is_adjacent((x, y), pit) for pit in self.pits)

        # Brilho (Glitter): Agente está na mesma célula do ouro e ainda não o pegou
        glitter = ((x, y) == self.gold) and not self.has_gold

        return {'stench':stench, 'breeze':breeze, 'glitter':glitter}

    
    def step(self, action):
        """
        Executa a ação enviada pelo agente no ambiente.

        action: String ('Forward', 'TurnLeft', 'TurnRight', 'Grab', 'Climb', 'NoOp')
        > return: Tupla (percept, score, is_terminal)
        """
        
        if not self.agent_alive or self.agent_exited:
            return self.get_percept(), self.score, True

        # Custo de penalização por ação realizada
        self.score -= 1

        x, y, orient = self.agent_loc

        # 1. Rotação do agente
        if action == 'TurnLeft':
            idx = self.ORIENTATIONS.index(orient)
            self.agent_loc = (x, y, self.ORIENTATIONS[(idx - 1) % 4])

        elif action == 'TurnRight':
            idx = self.ORIENTATIONS.index(orient)
            self.agent_loc = (x, y, self.ORIENTATIONS[(idx + 1) % 4])

        # 2. Avanço do agente
        elif action == 'Forward':
            dx, dy = self.OFFSETS[orient]
            nx, ny = x + dx, y + dy

            # Avança apenas se estiver dentro dos limites do grid 4x4
            if 1 <= nx <= 4 and 1 <= ny <= 4:
                self.agent_loc = (nx, ny, orient)
                x, y = nx, ny

            # Verificação de perigos mortais
            if (x, y) in self.pits:
                self.agent_alive = False
                self.score -= 1000
                print(f"💀 O agente caiu em um poço em ({x}, {y})!")

            elif (x, y) == self.wumpus and self.is_wumpus_alive:
                self.agent_alive = False
                self.score -= 1000
                print(f"💀 O agente foi devorado pelo Wumpus em ({x}, {y})!")

        # 3. Interações com itens/ambiente
        elif action == 'Grab':
            if (x, y) == self.gold and not self.has_gold:
                self.has_gold = True
                self.score += 1000
                print(f"✨ O agente pegou a pepita de ouro em ({x}, {y})!")

        elif action == 'Climb':
            if (x, y) == (1, 1):
                self.agent_exited = True
                print("🚪 O agente escalou a escada e saiu da caverna com sucesso!")

        is_terminal = not self.agent_alive or self.agent_exited
        
        return self.get_percept(), self.score, is_terminal

    def _is_adjacent(self, pos1, pos2):
        """Verifica se duas posições (x1, y1) e (x2, y2) são adjacentes no grid."""
        x1, y1 = pos1
        x2, y2 = pos2
        
        return abs(x1 - x2) + abs(y1 - y2) == 1


class WumpusSimulation:
    """
    Gerenciador da simulação do Mundo do Wumpus com animação em tempo real.
    Garante que o mapa atualizado substitua o anterior a cada movimento do agente,
    compatível com Terminal e Jupyter Notebook.
    """

    ORIENT_ICONS = {'N': 'A▲', 'E': 'A►', 'S': 'A▼',  'W': 'A◄'}

    def __init__(self, pit_locations, wumpus_location, gold_location, max_steps=100, delay=0.5, verbose=True):
        """
        pit_locations: Lista/Set de tuplas (x, y) com a localização dos poços.
        wumpus_location: Tupla (x, y) com a posição do Wumpus.
        gold_location: Tupla (x, y) com a posição do Ouro.
        max_steps: Limite máximo de passos de execução.
        delay: Tempo de espera (em segundos) entre frames.
        verbose: Se True, exibe a animação do mapa no terminal.
        """
        
        self.env = WumpusEnvironment(pit_locations=pit_locations, 
                                     wumpus_location=wumpus_location, 
                                     gold_location=gold_location)
        
        initial_kb = KnowledgeBase(generate_wumpus_kb0())
        self.agent = HybridWumpusAgent(initial_kb=initial_kb, initial_location=(1, 1, 'E'))
        
        self.max_steps = max_steps
        self.delay = delay
        self.verbose = verbose

    
    def _clear_screen(self):
        """
        Substitui o quadro anterior limpando o console/notebook antes de desenhar o novo.
        Suporta tanto terminal tradicional (Windows/Linux/macOS) quanto Jupyter Notebook.
        """

        try:
            from IPython.display import clear_output
            clear_output(wait=True)
        except ImportError:
            os.system('cls' if os.name == 'nt' else 'clear')

    
    def _render_map(self, step, action, percept):
        """Desenha o grid 4x4 do Mundo do Wumpus e o painel de telemetria."""
        
        self._clear_screen()

        print("=" * 55)
        print("            🎮 SIMULAÇÃO: MUNDO DO WUMPUS")
        print("=" * 55)

        # Construção visual do Grid 4x4 (da linha y=4 no topo até y=1 na base):
        grid_str = "    +" + "-------+" * 4 + "\n"
        
        for y in range(4, 0, -1):
            row_str = f" y={y}|"
            for x in range(1, 5):
                cell_items = []

                # Renderiza o agente na posição atual:
                ax, ay, aorient = self.env.agent_loc
                if (x, y) == (ax, ay) and self.env.agent_alive:
                    cell_items.append(self.ORIENT_ICONS.get(aorient, 'A'))

                # Renderiza o Ouro (se ainda não coletado):
                if (x, y) == self.env.gold and not self.env.has_gold:
                    cell_items.append("✨")

                # Renderiza Poços:
                if (x, y) in self.env.pits:
                    cell_items.append("🕳️")

                # Renderiza o Wumpus (vivo ou morto):
                if (x, y) == self.env.wumpus:
                    cell_items.append("👾" if self.env.is_wumpus_alive else "💀")

                content = " ".join(cell_items)
                row_str += f" {content:<5}|"

            grid_str += row_str + "\n"
            grid_str += "    +" + "-------+" * 4 + "\n"

        grid_str += "        x=1     x=2     x=3     x=4\n"
        print(grid_str)

        # Telemetria do movimento e estado do agente:
        print("-" * 55)
        print(f"⏱️  Passo: {step} | Tempo Lógico (Agent): t={self.agent.t}")
        print(f"🎬 Ação Executada: '{action}'")
        print(f"📍 Pos. Atual Agente: {self.env.agent_loc}")
        print(f"👁️  Percepção Atual: Stench={percept['stench']}, Breeze={percept['breeze']}, Glitter={percept['glitter']}")
        print(f"📜 Plano Pendente: {self.agent.plan}")
        print(f"🏆 Pontuação Acumulada: {self.env.score}")
        print("=" * 55)

    
    def run(self):
        """Executa a simulação atualizando e substituindo o mapa a cada movimento."""
        
        step_count = 0
        is_terminal = False

        # Percepção e renderização do estado inicial (t=0, Posição 1,1):
        percept = self.env.get_percept()
        if self.verbose:
            self._render_map(step_count, "Início", percept)
            time.sleep(self.delay)

        # Loop principal da simulação:
        while not is_terminal and step_count < self.max_steps:
            # 1. Agente toma a decisão baseada na percepção atual
            action = self.agent.hybrid_wumpus_agent(percept)
            
            # 2. O ambiente aplica o novo movimento
            percept, score, is_terminal = self.env.step(action)
            step_count += 1

            # 3. O novo mapa substitui o quadro anterior
            if self.verbose:
                self._render_map(step_count, action, percept)
                time.sleep(self.delay)

        # Tela final com o resultado:
        if self.env.agent_exited:
            status = "SOBREVIVEU E ESCAPOU COM SUCESSO 🚪"
        elif not self.env.agent_alive:
            status = "O AGENTE MORREU EM COMBATE/POÇO 💀"
        else:
            status = "TEMPO EXCEDIDO ⏱️"

        print(f"\n📢 RESULTADO FINAL: {status}")
        print(f"Total de Passos: {step_count} | Ouro Resgatado: {'Sim 🏆' if self.env.has_gold else 'Não ❌'} | Score Final: {self.env.score}\n")
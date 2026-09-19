import numpy as np
import matplotlib.pyplot as plt

class Node:
    
    def __init__(self, state):
        self.state = state


class Problem:

    def __init__(self, initial_state, actions, transition_model):
        
        self.initial_state = initial_state
        self.actions = actions
        self.transition_model = transition_model
        

def plot_board(ax, state, title):
    
    """Desenha um tabuleiro de xadrez com as rainhas posicionadas."""
    
    n = len(state)
    board = np.zeros((n, n))
    board[1::2, 0::2] = 1
    board[0::2, 1::2] = 1
    
    ax.imshow(board, cmap = 'binary', alpha = 0.5)
    
    for col, row in enumerate(state):
        ax.text(col, row, '♕', fontsize = 20, ha = 'center', va = 'center', color = 'black')
        
    ax.set_xticks(np.arange(n))
    ax.set_yticks(np.arange(n))
    ax.set_title(title)
    ax.grid(which = 'both', color = 'black', linewidth = 1)


def plot_result(final_state, initial_state = None):

    if initial_state is not None:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize = (10, 5))
        plot_board(ax1, initial_state, 'Estado Inicial')
        plot_board(ax2, final_state, 'Estado Final')
        plt.tight_layout()
        plt.show()
    else:
        fig, ax = plt.subplots(1, 1, figsize = (6, 6))
        plot_board(ax, final_state, 'Estado final')
        plt.show()

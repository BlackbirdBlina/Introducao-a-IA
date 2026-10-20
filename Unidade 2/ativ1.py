
def play_game(agent):

    # definindo o tipo de jogada do usuário:
    while True:
        human_player = input("Você quer ser 'X' (primeiro a jogar) ou 'O' (segundo)? ").upper()
        if human_player in ['X', 'O']:
            break
        print("Escolha inválida. Por favor, digite 'X' ou 'O'.")

    state = agent.problem.initial_state

    # loop principal do jogo:
    while not agent.problem.terminal_test(state):
        current_player = agent.problem.player(state)
        agent.problem.display(state)
        
        if current_player != human_player:
            print(f"É a vez do agente ('{current_player}')... 🧠")
            
            move = agent.decision(state)
            print(f"Agente jogou em: {move}")
        
        else:
            print(f"É a sua vez ('{current_player}').")
            legal_moves = agent.problem.actions(state)
            
            while True:
                try:
                    move_str = input("Digite sua jogada no formato 'linha,coluna' (ex: 0,2): ")
                    row, col = map(int, move_str.split(','))
                    
                    move = (row, col)
                    
                    if move in legal_moves:
                        break
                    
                    else:
                        print("Jogada ilegal ou casa ocupada! Tente novamente.")
                
                except (ValueError, IndexError):
                    print("Formato inválido. Use 'linha,coluna' sem espaços.")
        
        state = agent.problem.result(state, move)

    # fim de jogo:
    print("\n## FIM DE JOGO! ##")
    
    agent.problem.display(state)
    winner_utility = agent.problem.utility(state)
    
    if (winner_utility == 1 and human_player == 'X') or \
       (winner_utility == -1 and human_player == 'O'):
        print("Parabéns, você venceu! 🏆")
    elif winner_utility == 0:
        print("O jogo terminou em empate! 🤝")
    else:
        print("O agente venceu. Mais sorte na próxima vez! 🤖")
        
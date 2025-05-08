import random
import copy
import time

class TicTacToe:
    def __init__(self):
        self.board = [' '] * 9
        self.current_player = 'X'

    def available_moves(self):
        return [i for i, spot in enumerate(self.board) if spot == ' ']

    def make_move(self, move):
        self.board[move] = self.current_player
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def undo_move(self, move):
        self.board[move] = ' '
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def is_winner(self, player):
        wins = [(0,1,2), (3,4,5), (6,7,8),
                (0,3,6), (1,4,7), (2,5,8),
                (0,4,8), (2,4,6)]
        return any(self.board[a] == self.board[b] == self.board[c] == player for a,b,c in wins)

    def is_draw(self):
        return ' ' not in self.board and not self.is_winner('X') and not self.is_winner('O')

    def game_over(self):
        return self.is_winner('X') or self.is_winner('O') or self.is_draw()

    def clone(self):
        clone = TicTacToe()
        clone.board = self.board[:]
        clone.current_player = self.current_player
        return clone

def simulate_random_game(game):
    while not game.game_over():
        move = random.choice(game.available_moves())
        game.make_move(move)
    if game.is_winner('X'):
        return 1
    elif game.is_winner('O'):
        return -1
    else:
        return 0

def mcts(game, simulations=100):
    moves = game.available_moves()
    move_stats = {move: {'wins': 0, 'plays': 0} for move in moves}

    for move in moves:
        for _ in range(simulations):
            sim_game = game.clone()
            sim_game.make_move(move)
            result = simulate_random_game(sim_game)
            move_stats[move]['plays'] += 1
            move_stats[move]['wins'] += result

    # Se escoge el movimiento con mayor promedio de ganancia
    best_move = max(moves, key=lambda m: move_stats[m]['wins'] / move_stats[m]['plays'])
    return best_move

# Simulación para evaluar rendimiento
def run_mcts_simulation(n_games=1000, simulations_per_move=50, x_starts=True):
    wins = 0
    draws = 0
    losses = 0
    total_nodes = 0

    for _ in range(n_games):
        game = TicTacToe()
        if not x_starts:
            game.make_move(random.choice(game.available_moves()))  # "O" comienza al azar

        nodes = 0
        while not game.game_over():
            move = mcts(game, simulations=simulations_per_move)
            nodes += simulations_per_move * len(game.available_moves())
            game.make_move(move)

        total_nodes += nodes

        if game.is_winner('X'):
            wins += 1
        elif game.is_winner('O'):
            losses += 1
        else:
            draws += 1

    print(f'Victorias: {wins}, Empates: {draws}, Derrotas: {losses}')
    print(f'Nodos promedio explorados: {total_nodes / n_games:.2f}')

# Ejecutar 1000 partidas donde "X" empieza
if __name__ == "__main__":
    start_time = time.time()
    run_mcts_simulation(n_games=1000, simulations_per_move=500, x_starts=True)
    print(f"Tiempo de ejecución: {time.time() - start_time:.2f} segundos")
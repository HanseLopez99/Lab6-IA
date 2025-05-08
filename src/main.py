# main.py

import random
import time
import copy
from typing import List, Tuple
from colorama import init, Fore, Style

init(autoreset=True)

# ────────────────────────────────────────────────────────────────────────────────
# Clase TicTacToe con Minimax puro, Minimax α–β y MCTS

class TicTacToe:
    WIN_LINES = (
        (0,1,2),(3,4,5),(6,7,8),
        (0,3,6),(1,4,7),(2,5,8),
        (0,4,8),(2,4,6)
    )

    def __init__(self):
        self.board: List[str] = [' '] * 9
        self.current_player: str = 'X'

    def reset(self):
        self.board = [' '] * 9
        self.current_player = 'X'

    def available_moves(self) -> List[int]:
        return [i for i, c in enumerate(self.board) if c == ' ']

    def make_move(self, move: int, player: str = None):
        p = player if player else self.current_player
        self.board[move] = p

    def undo_move(self, move: int):
        self.board[move] = ' '

    def is_winner(self, player: str) -> bool:
        return any(
            self.board[a] == self.board[b] == self.board[c] == player
            for a,b,c in TicTacToe.WIN_LINES
        )

    def is_draw(self) -> bool:
        return ' ' not in self.board and not self.is_winner('X') and not self.is_winner('O')

    def is_terminal(self) -> bool:
        return self.is_winner('X') or self.is_winner('O') or self.is_draw()

    def utility(self) -> int:
        if self.is_winner('X'): return  1
        if self.is_winner('O'): return -1
        return 0

    def heuristic(self) -> int:
        # Heurística simple: #X en líneas libres - #O en líneas libres
        score = 0
        for a,b,c in TicTacToe.WIN_LINES:
            line = [self.board[a], self.board[b], self.board[c]]
            if 'O' not in line:
                score += line.count('X')
            if 'X' not in line:
                score -= line.count('O')
        return score

    # -- Minimax puro --
    def _minimax(self, depth:int, maximizing:bool) -> Tuple[int,int]:
        if self.is_terminal() or depth==0:
            return (self.utility() if self.is_terminal() else self.heuristic(), -1)

        if maximizing:
            best_val, best_mv = -float('inf'), -1
            for mv in self.available_moves():
                self.make_move(mv, 'X')
                val, _ = self._minimax(depth-1, False)
                self.undo_move(mv)
                if val > best_val:
                    best_val, best_mv = val, mv
            return best_val, best_mv

        else:
            best_val, best_mv = float('inf'), -1
            for mv in self.available_moves():
                self.make_move(mv, 'O')
                val, _ = self._minimax(depth-1, True)
                self.undo_move(mv)
                if val < best_val:
                    best_val, best_mv = val, mv
            return best_val, best_mv

    def get_best_plain(self, depth:int) -> int:
        _, mv = self._minimax(depth, True)
        return mv if mv != -1 else random.choice(self.available_moves())

    # -- Minimax con poda α–β --
    def _minimax_ab(self, depth:int, alpha:float, beta:float, maximizing:bool) -> Tuple[int,int]:
        if self.is_terminal() or depth==0:
            return (self.utility() if self.is_terminal() else self.heuristic(), -1)

        if maximizing:
            best_val, best_mv = -float('inf'), -1
            for mv in self.available_moves():
                self.make_move(mv, 'X')
                val, _ = self._minimax_ab(depth-1, alpha, beta, False)
                self.undo_move(mv)
                if val > best_val:
                    best_val, best_mv = val, mv
                alpha = max(alpha, best_val)
                if beta <= alpha:
                    break
            return best_val, best_mv

        else:
            best_val, best_mv = float('inf'), -1
            for mv in self.available_moves():
                self.make_move(mv, 'O')
                val, _ = self._minimax_ab(depth-1, alpha, beta, True)
                self.undo_move(mv)
                if val < best_val:
                    best_val, best_mv = val, mv
                beta = min(beta, best_val)
                if beta <= alpha:
                    break
            return best_val, best_mv

    def get_best_ab(self, depth:int) -> int:
        _, mv = self._minimax_ab(depth, -float('inf'), float('inf'), True)
        return mv if mv != -1 else random.choice(self.available_moves())

    # -- MCTS --
    def clone(self) -> 'TicTacToe':
        copy_game = TicTacToe()
        copy_game.board = self.board[:]
        copy_game.current_player = self.current_player
        return copy_game

def simulate_random_game(game:TicTacToe) -> int:
    while not game.is_terminal():
        mv = random.choice(game.available_moves())
        game.make_move(mv)
    if game.is_winner('X'):
        return 1
    if game.is_winner('O'):
        return -1
    return 0

def mcts(game:TicTacToe, simulations:int=100) -> int:
    moves = game.available_moves()
    stats = {mv:{'wins':0,'plays':0} for mv in moves}
    for mv in moves:
        for _ in range(simulations):
            sim = game.clone()
            sim.make_move(mv)
            result = simulate_random_game(sim)
            stats[mv]['plays'] += 1
            stats[mv]['wins'] += result
    # Elegir movimiento con mejor ratio
    return max(moves, key=lambda m: stats[m]['wins']/stats[m]['plays'])

# ────────────────────────────────────────────────────────────────────────────────
# Experimentos genéricos

def run_experiment(algo:str, param:int, starter:str, n_games:int=1000) -> Tuple[int,int,int,float,float]:
    wins = draws = losses = 0
    total_nodes = 0   # para MCTS aproximamos nodes = sims * moves
    total_time = 0.0

    for _ in range(n_games):
        game = TicTacToe()
        if starter == 'O':
            # O inicia aleatoriamente
            game.make_move(random.choice(game.available_moves()), 'O')

        t0 = time.perf_counter()
        while not game.is_terminal():
            if algo == 'plain':
                mv = game.get_best_plain(param)
                game.make_move(mv, 'X')
            elif algo == 'ab':
                mv = game.get_best_ab(param)
                game.make_move(mv, 'X')
            else:  # 'mcts'
                mv = mcts(game, simulations=param)
                total_nodes += param * len(game.available_moves())
                game.make_move(mv)

            # turno de O (aleatorio)
            if not game.is_terminal():
                omv = random.choice(game.available_moves())
                game.make_move(omv, 'O')

        total_time += time.perf_counter() - t0

        # contabilizar resultado
        if game.is_winner('X'): wins += 1
        elif game.is_winner('O'): losses += 1
        else: draws += 1

    avg_time = total_time / n_games
    avg_nodes = total_nodes / n_games if algo=='mcts' else 0.0
    return wins, draws, losses, avg_nodes, avg_time

# ────────────────────────────────────────────────────────────────────────────────
# Main

if __name__ == '__main__':
    random.seed(42)

    variants = [
        ('plain', 4),
        ('plain', 6),
        ('ab',    4),
        ('ab',    6),
        ('mcts', 100),
        ('mcts', 500),
    ]
    starters = ['X','O']
    icons    = {'plain':'⚔️','ab':'✂️','mcts':'🎲'}
    names    = {'plain':'Minimax puro','ab':'Minimax α–β','mcts':'MCTS'}

    header = "| Algoritmo      | Parámetro | Starter | Victorias | Empates | Derrotas | Nodos avg | Tiempo avg (s) |"
    sep    = "|" + "|".join(["-"*14,"-"*11,"-"*9,"-"*11,"-"*8,"-"*10,"-"*9,"-"*15]) + "|"

    print(Fore.MAGENTA + Style.BRIGHT + header)
    print(Fore.MAGENTA + sep)

    for algo,param in variants:
        for starter in starters:
            print(f"{Fore.CYAN}{icons[algo]} Ejecutando {names[algo]}({param}), Starter={starter}…{Style.RESET_ALL}", end="", flush=True)
            w,d,l,nodes,tm = run_experiment(algo, param, starter, n_games=1000)
            print(f"{Fore.GREEN} ✔️{Style.RESET_ALL}")
            print(
                f"| {names[algo]:<14} | {param:^9} | {starter:^7} |"
                f" {w:^9} | {d:^7} | {l:^8} |"
                f" {nodes:>9.2f} | {tm:>14.2f} |"
            )

    print(Fore.MAGENTA + Style.BRIGHT + "✔️ Todos los experimentos completados.")

# main.py

import random
import time
from typing import List, Tuple
from colorama import init, Fore, Style

init(autoreset=True)

# ────────────────────────────────────────────────────────────────────────────────
class TicTacToe:
    WIN_LINES = (
        (0,1,2),(3,4,5),(6,7,8),
        (0,3,6),(1,4,7),(2,5,8),
        (0,4,8),(2,4,6)
    )

    def __init__(self):
        self.board = [' '] * 9
        self.current_player = 'X'

    def reset(self):
        self.board = [' '] * 9
        self.current_player = 'X'

    def available_moves(self) -> List[int]:
        return [i for i,c in enumerate(self.board) if c==' ']

    def make_move(self, mv:int, p:str):
        self.board[mv] = p

    def undo_move(self, mv:int):
        self.board[mv] = ' '

    def is_winner(self,p:str) -> bool:
        return any(self.board[a]==self.board[b]==self.board[c]==p for a,b,c in TicTacToe.WIN_LINES)

    def is_draw(self) -> bool:
        return ' ' not in self.board and not self.is_winner('X') and not self.is_winner('O')

    def is_terminal(self) -> bool:
        return self.is_winner('X') or self.is_winner('O') or self.is_draw()

    def utility(self) -> int:
        if   self.is_winner('X'): return  1
        elif self.is_winner('O'): return -1
        else:                     return  0

    def heuristic(self) -> int:
        score = 0
        for a,b,c in TicTacToe.WIN_LINES:
            line = [self.board[a], self.board[b], self.board[c]]
            if 'O' not in line:
                score += line.count('X')
            if 'X' not in line:
                score -= line.count('O')
        return score

    # Minimax puro
    def _minimax(self, depth:int, maximizing:bool) -> Tuple[int,int]:
        if self.is_terminal() or depth==0:
            return (self.utility() if self.is_terminal() else self.heuristic(), -1)
        if maximizing:
            best_val, best_mv = -float('inf'), -1
            player = 'X'
        else:
            best_val, best_mv = float('inf'), -1
            player = 'O'
        for mv in self.available_moves():
            self.make_move(mv, player)
            val, _ = self._minimax(depth-1, not maximizing)
            self.undo_move(mv)
            if maximizing and val>best_val:
                best_val, best_mv = val, mv
            if not maximizing and val<best_val:
                best_val, best_mv = val, mv
        return best_val, best_mv

    def get_best_plain(self, k:int) -> int:
        _, mv = self._minimax(k, True)
        return mv if mv!=-1 else random.choice(self.available_moves())

    # Minimax α–β
    def _minimax_ab(self, depth:int, alpha:float, beta:float, maximizing:bool) -> Tuple[int,int]:
        if self.is_terminal() or depth==0:
            return (self.utility() if self.is_terminal() else self.heuristic(), -1)
        if maximizing:
            val, mv = -float('inf'), -1
            player = 'X'
            for m in self.available_moves():
                self.make_move(m, player)
                v,_ = self._minimax_ab(depth-1, alpha, beta, False)
                self.undo_move(m)
                if v>val:
                    val, mv = v, m
                alpha = max(alpha, val)
                if beta<=alpha:
                    break
        else:
            val, mv = float('inf'), -1
            player = 'O'
            for m in self.available_moves():
                self.make_move(m, player)
                v,_ = self._minimax_ab(depth-1, alpha, beta, True)
                self.undo_move(m)
                if v<val:
                    val, mv = v, m
                beta = min(beta, val)
                if beta<=alpha:
                    break
        return val, mv

    def get_best_ab(self, k:int) -> int:
        _, mv = self._minimax_ab(k, -float('inf'), float('inf'), True)
        return mv if mv!=-1 else random.choice(self.available_moves())

    # MCTS
    def clone(self) -> 'TicTacToe':
        g = TicTacToe()
        g.board = self.board[:]
        g.current_player = self.current_player
        return g

def simulate_random(game:TicTacToe) -> int:
    while not game.is_terminal():
        m = random.choice(game.available_moves())
        game.make_move(m, game.current_player)
        game.current_player = 'O' if game.current_player=='X' else 'X'
    if game.is_winner('X'): return 1
    if game.is_winner('O'): return -1
    return 0

def mcts(game:TicTacToe, sims:int) -> int:
    moves = game.available_moves()
    stats = {m:{'wins':0,'plays':0} for m in moves}
    for m in moves:
        for _ in range(sims):
            sim = game.clone()
            sim.make_move(m, sim.current_player)
            sim.current_player = 'O' if sim.current_player=='X' else 'X'
            res = simulate_random(sim)
            stats[m]['plays'] += 1
            stats[m]['wins']  += res
    return max(moves, key=lambda m: stats[m]['wins']/stats[m]['plays'])


# ────────────────────────────────────────────────────────────────────────────────
def run_experiment(algo:str, param:int, starter:str, n:int=1000) -> Tuple[int,int,int,float]:
    wins=draws=losses=0
    total_nodes=0  # solo para MCTS aproximado
    game = TicTacToe()

    for _ in range(n):
        game.reset()
        game.current_player = 'X'
        if starter=='O':
            # O inicia al azar
            mv0 = random.choice(game.available_moves())
            game.make_move(mv0, 'O')
            game.current_player = 'X'

        # jugar hasta terminal
        while not game.is_terminal():
            if algo=='plain':
                mv = game.get_best_plain(param)
                game.make_move(mv, 'X')
            elif algo=='ab':
                mv = game.get_best_ab(param)
                game.make_move(mv, 'X')
            else:  # mcts
                mv = mcts(game, param)
                total_nodes += param * len(game.available_moves())
                game.make_move(mv, 'X')

            # turno de O aleatorio
            if not game.is_terminal():
                mv_o = random.choice(game.available_moves())
                game.make_move(mv_o, 'O')

        # resultado
        if game.is_winner('X'): wins += 1
        elif game.is_winner('O'): losses += 1
        else: draws += 1

    avg_nodes = total_nodes/n if algo=='mcts' else 0.0
    return wins, draws, losses, avg_nodes


# ────────────────────────────────────────────────────────────────────────────────
if __name__=='__main__':

    experiments = [
        ('plain', 4), ('plain', 6),
        ('ab',    4), ('ab',    6),
        ('mcts',100), ('mcts',500),
    ]
    starters = ['X','O']
    icons = {'plain':'⚔️','ab':'✂️','mcts':'🎲'}
    names = {'plain':'Minimax puro','ab':'Minimax α–β','mcts':'MCTS'}

    header = "| Algoritmo      | Parámetro | Starter | Victorias | Empates | Derrotas | Nodos avg | Tiempo tot (s) |"
    sep    = "|" + "|".join(["-"*14,"-"*11,"-"*9,"-"*11,"-"*8,"-"*10,"-"*9,"-"*15]) + "|"

    print(Fore.MAGENTA + Style.BRIGHT + header)
    print(Fore.MAGENTA + sep)

    for algo,param in experiments:
        for st in starters:
            print(f"{Fore.CYAN}{icons[algo]} Ejecutando {names[algo]}({param}), Starter={st}...{Style.RESET_ALL}", end="", flush=True)
            t0 = time.perf_counter()
            w,d,l,nodes = run_experiment(algo, param, st, n=1000)
            ttot = time.perf_counter() - t0
            print(f"{Fore.GREEN} ✔️ {ttot:>6.2f}s{Style.RESET_ALL}")
            print(
                f"| {names[algo]:<14} | {param:^9} | {st:^7} |"
                f" {w:^9} | {d:^7} | {l:^8} |"
                f" {nodes:>9.2f} | {ttot:>14.2f} |"
            )

    print(Fore.MAGENTA + Style.BRIGHT + "✔️ Todos los experimentos completados.")

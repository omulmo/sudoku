#! /usr/bin/env python3

'''Sudoku puzzle solver'''

import argparse
import copy

class Cell:
    def __init__(self):
        self.value = 0
        self.candidates = {1,2,3,4,5,6,7,8,9}
        self.groups = []

    def eliminate(self, value):
        assert(self.value != value)
        if value in self.candidates:
            self.candidates.remove(value)
            assert(len(self.candidates)>0)

    def assign(self, value=None):
        if self.value==0:
            self.value = value if value else self.candidates.pop()
            self.candidates = set()

        for group in self.groups:
            for other in group:
                if other==self: continue
                other.eliminate(self.value)

    def __repr__(self):
        return str(self.value) if self.value>0 else '_'


class Board:
    def __init__(self, setup):
        self.cells = [ Cell() for _ in range(81) ]
        self.groups = []

        for i in range(9):
            self.groups.append( self.cells[i*9:i*9+9] )
            self.groups.append( self.cells[i:i+81:9] )

        for dx in range(3):
            for dy in range(3):
                array = [ self.cells[i+j*9] for i in range(dx*3,dx*3+3) for j in range(dy*3, dy*3+3)  ]
                self.groups.append( array )

        for cell in self.cells:
            for group in self.groups:
                if cell in group:
                    cell.groups.append(group)

        assert len(setup)==9, 'Malformed board, not 9 lines long'
        idx = 0
        for row in setup:
            assert len(row)==9, f'Malformed input, not 9 characters: {row}'
            for entry in row:
                if entry in '123456789':
                    self.cells[idx].assign(int(entry))
                idx += 1

    def __repr__(self):
        return '\n'.join([ ' '.join([str(self.cells[i+j*9]) for i in range(9)]) for j in range(9) ])

    def pretty(self):
        lines=[]
        for y in range(9):
            lines.append( '-' * 73 )
            for row in range(3):
                line=''
                for x in range(9):
                    line += '| '
                    cell = self.cells[x+y*9]
                    if cell.value!=0:
                        line += f' ({cell.value})  ' if row==1 else ' '*6
                    else:
                        for val in range(row*3,3+row*3):
                            line += f'{val+1} ' if val+1 in cell.candidates else '  '
                line += '|'
                lines.append(line)                    
        lines.append( '-' * 73 )
        return '\n'.join(lines)


class Solver:
    def __init__(self, board, depth=3):
        self.board = board
        self.depth = depth

    def solve(self, debug=False):
        counter=0
        cells = self.board.cells
        while any(map(lambda cell: cell.value==0, cells)):
            counter+=1
            if counter>3:
                return self.circuit_breaker()
            if debug:
                print(self.board.pretty())

            cell = next((x for x in cells if len(x.candidates)==1), None)
            if cell != None:
                cell.assign()
                counter=0

            for group in self.board.groups:
                self.find_single_candidates(group)
                self.find_tuples(group)

        return all(map(lambda cell: cell.value!=0, cells))

    def circuit_breaker(self):
        '''if stuck, then make a guess and recurse'''
        if self.depth==0: return False
        idx=0
        while len(self.board.cells[idx].candidates)<2:
            idx += 1
        cell = self.board.cells[idx]
        for value in cell.candidates:
            clone = copy.deepcopy(self.board)
            clone.cells[idx].assign(value)
            try:
                if Solver(clone, depth=self.depth-1).solve():
                    self.board.cells = clone.cells
                    self.board.groups = clone.groups
                    return True
            except:
                pass
        return False

    def find_single_candidates(self, group):
        '''find and assign values with only one candidate cell in a group'''
        for value in range(1,10):
            found = list(filter(lambda cell:value in cell.candidates, group))                
            if len(found)==1:
                cell = found[0]
                cell.assign(value)

    def find_tuples(self, group):
        ''' if N cells have the same N-tuple candidates, e.g. (4,7) in two cells,
            then no other cell in the group can have those candidate numbers
            (only supports N=2 right now)'''
        pairs = list(filter(lambda cell:len(cell.candidates)==2, group))
        for i in range(len(pairs)):
            values = pairs[i].candidates
            for j in range(i+1, len(pairs)):
                if pairs[j].candidates == values:
                    for cell in group:
                        if cell in [pairs[i], pairs[j]]: continue
                        for value in values:
                            cell.eliminate(value)


if __name__ == '__main__':
    parser = argparse.ArgumentParser('sudoku')
    parser.add_argument('--pretty', action='store_true', default=False,
                        help='Use large printout')
    parser.add_argument('--file', type=str,
                        help='Load puzzle from file (default: stdin)')
    parser.add_argument('--depth', type=int, default=3,
                        help='Max recursion depth when using a guessing strategy')
    args = parser.parse_args()

    setup=[]
    if args.file==None:
        print('Enter board (9x9 characters):')
        for i in range(9):
            setup.append(input())
    else:
        f = open(args.file)
        for line in f:
            setup.append(f.trim())

    try:
        board = Board(setup)
        success = Solver(board, depth=args.depth).solve()
        print(board.pretty() if args.pretty else str(board))
        print('OK' if success else 'FAILED')
    except Exception as e:
        print(e)

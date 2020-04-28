#! /usr/bin/env python3

'''Sudoku solver unit tests'''

import unittest
import os
from sudoku import Cell, Board, Solver

EASY = '''29_34____
7___9_265
5_1_2__9_
_5_91__72
4_26_7_51
9__2__6__
3_41_2___
12_____4_
____79_23'''.splitlines()

MEDIUM = '''1_7_32__6
3_67_____
_8_19__5_
_3_25__4_
__9______
6__9_4__1
_6_4___85
______3__
415_7____'''.splitlines()

HARD = '''4____68__
2__8____9
9_1__3_56
__968___2
_1____59_
__8__97__
_24_9____
1_____4__
__73_____'''.splitlines()

EXPERT = '''6_9751___
_____3__4
_________
2_____8__
__8_67___
_____9156
15_2__4__
________5
7______6_'''.splitlines()

debug = int(os.environ.get('DEBUG','0')) != 0

class TestCell(unittest.TestCase):
    def testEliminate(self):
        c = Cell()
        for x in '12345898458123458945':
            c.eliminate(int(x))
        self.assertEqual(0, c.value)
        self.assertIn(6, c.candidates)
        self.assertIn(7, c.candidates)

    def testAssign(self):
        c1 = Cell()
        c2 = Cell()
        c3 = Cell()
        g1 = [ Cell(), Cell(), c1 ]
        g2 = [ Cell(), Cell(), c2 ]
        g3 = [ c1, c2, c3 ]
        c1.groups= [ g1, g3 ]
        c2.groups= [ g3, g2 ]
        for g in g1, g2, g3:
            for c in g:
                c.candidates = {1,2,3}
        c1.assign(1)
        self.assertEqual(1, c1.value)
        self.assertSetEqual(set(), c1.candidates)
        self.assertNotIn(1, c2.candidates)
        self.assertNotIn(1, c3.candidates)
        self.assertSetEqual({2,3}, c3.candidates)
        c2.assign(2)
        self.assertEqual(1, c1.value)
        self.assertEqual(2, c2.value)
        self.assertNotIn(2, c3.candidates)
        self.assertSetEqual({3}, c3.candidates)

class TestBoard(unittest.TestCase):
    def test1(self):
        b = Board(EASY)
        self.assertEqual('\n'.join(EASY), str(b).replace(' ',''))
        
class TestSolver(unittest.TestCase):
    def test1_Easy(self):
        b = Board(EASY)
        self.assertTrue(Solver(b).solve())
        if debug: print(b)

    def test2_Medium(self):
        b = Board(MEDIUM)  
        self.assertTrue(Solver(b).solve())
        if debug: print(b)

    def test3_Hard(self):
        b = Board(HARD)
        self.assertTrue(Solver(b).solve())
        if debug:
            print(b.pretty())

    def test4_Expert(self):
        b = Board(EXPERT)
        self.assertTrue(Solver(b).solve())
        if debug:
            print(b.pretty())

if __name__=='__main__':
    unittest.main()

#!/usr/bin/env python
# Copyright (c) 2009, Andrew Brehaut, Steven Ashley
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, 
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice, 
#   this list of conditions and the following disclaimer in the documentation  
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.

if __name__ == '__main__':
    import sys
    from os import path
    sys.path.insert(0, path.abspath(path.join(path.dirname(sys.argv[0]), '..')))

import unittest

from picoparse import NoMatch, DefaultDiagnostics, BufferWalker
from picoparse import partial as p
from itertools import count

class TestDefaultDiagnostics(unittest.TestCase):
    """Checks some basic operations on the DefaultDiagnostics class
    Eventually this will report errors. For now, there isn't much to test.
    """
    def setUp(self):
        self.diag = DefaultDiagnostics()
        self.i = self.diag.wrap(range(1, 6))

    def test_wrap(self):
        for ((a, b), c) in zip(self.i, range(1, 6)):
             self.assertEqual(a, c)
             self.assertEqual(b, c)
    
    def test_wrap_len(self):
        self.assertEqual(len(list(self.i)), 5)
    
    def test_tokens(self):
        self.assertEqual(self.diag.tokens, [])
        for (a, b) in self.i:
             self.assertEqual(self.diag.tokens, list(zip(range(1, a+1),range(1, a+1))))
    
    def test_cut(self):
        next(self.i)
        next(self.i)
        c, p = next(self.i)
        self.diag.cut(p)
        self.assertEqual(self.diag.tokens, [(3,3)])


class TestBufferWalker(unittest.TestCase):
    """Checks all backend parser operations work as expected
    """
    def setUp(self):
        self.input = "abcdefghi"
        self.bw = BufferWalker(self.input, None)

    def test_next(self):
        for c in self.input[1:]:
            self.assertEqual(next(self.bw), c)
    
    def test_peek(self):
        for c in self.input:
            self.assertEqual(self.bw.peek(), c)
            next(self.bw)
    
    def test_current(self):
        for c, pos in zip(self.input, count(1)):
            self.assertEqual(self.bw.current(), (c, pos))
            next(self.bw)
    
    def test_pos(self):
        for c, pos in zip(self.input, count(1)):
            self.assertEqual(self.bw.pos(), pos)
            next(self.bw)
    
    def test_fail(self):
        self.assertRaises(NoMatch, self.bw.fail)
        self.assertEqual(self.bw.peek(), 'a')
    
    def test_tri_accept(self):
        self.bw.tri(self.bw.__next__)
        self.assertEqual(self.bw.peek(), 'b')
    
    def test_tri_fail(self):
        def fun():
            next(self.bw)
            self.bw.fail()
        self.assertRaises(NoMatch, p(self.bw.tri, fun))

    def test_commit_multiple(self):
        def multiple_commits():
            self.bw.commit()
            self.bw.commit()
        multiple_commits()
        self.bw.tri(multiple_commits)

    def test_commit_accept(self):
        def fun():
            next(self.bw)
            self.bw.commit()
        self.bw.tri(fun)
        self.assertEqual(self.bw.peek(), 'b')
    
    def test_commit_fail(self):
        def fun():
            next(self.bw)
            self.bw.commit()
            self.bw.fail()
        self.assertRaises(NoMatch, p(self.bw.tri, fun))
        self.assertEqual(self.bw.peek(), 'b')
    
    def test_choice_null(self):
        self.bw.choice()
    
    def test_choice_accept(self):
        self.bw.choice(self.bw.fail, self.bw.__next__)
        self.bw.choice(self.bw.__next__, self.bw.fail)
        self.bw.choice(self.bw.__next__, self.bw.__next__)
        self.assertEqual(self.bw.peek(), 'd')
    
    def test_choice_fail(self):
        self.assertRaises(NoMatch, p(self.bw.choice, self.bw.fail, self.bw.fail))
    
    def test_choice_commit_fail(self):
        def fun():
            next(self.bw)
            self.bw.commit()
            self.bw.fail()
        self.assertRaises(NoMatch, p(self.bw.choice, fun))
        self.assertEqual(self.bw.peek(), 'b')

if __name__ == '__main__':
    unittest.main()

__all__ = [cls.__name__ for name, cls in locals().items()
                        if isinstance(cls, type) 
                        and name.startswith('Test')]


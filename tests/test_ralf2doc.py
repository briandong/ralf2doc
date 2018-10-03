#!/usr/bin/env python
# -*- coding: utf-8 -*-

' the unit test '

__author__ = "Bo DONG"

import sys, os
import unittest

from context import ralf2doc

class Test_func(unittest.TestCase):
    def test_func(self):
        self.assertEqual(ralf2doc.func(), "Hello World!")

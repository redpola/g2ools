#!/usr/bin/env python2

import sys
from nord.g2.file import Pch2File, Prf2File

prog = sys.argv.pop(0)
while len(sys.argv):
  filename = sys.argv.pop(0)
  print(filename)
  if filename[-4:].lower() == 'prf2':
    prf2 = Prf2File(filename)
    for p in range(4):
      patch = prf2.performance.patches[p]
      patch.voice.shortencables()
      patch.fx.shortencables()
    prf2.write(filename)
  else:
    pch2 = Pch2File(filename)
    pch2.patch.voice.shortencables()
    pch2.patch.fx.shortencables()
    pch2.write(filename)

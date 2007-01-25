
#
# dxtable.py - DX7 convertion tables
#
# Copyright (c) 2006,2007 Matt Gerassimoff
#
# This file is part of g2ools.
#
# g2ools is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# g2ools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# FMAmod conversion table calculated by 3phase
# mod conversion table calculated by 3phase
# kbt conversion table calculated by 3phase 
amodsens = [ # [dxamod, g2mod]
  [  0,  0],  [  1,  2],  [  2,  3],  [  3,  4],
]

lfo = [ # [lforange,lforate,lfomod,lfoattack]
  [  1, 24, 55,  0], [  1, 36, 55,  0], [  1, 52, 55,  4], [  1, 58, 55,  7],
  [  1, 64, 55, 11], [  1, 67,  0, 14], [  1, 70,  0, 18], [  1, 74, 55, 21],
  [  1, 76, 55, 21], [  1, 78, 55, 23], [  1, 80, 55, 26], [  1, 80, 55, 28],
  [  1, 81, 55, 28], [  1, 82, 55, 29], [  1, 84, 55, 30], [  1, 85, 55, 31],
  [  1, 86, 55, 32], [  1, 87, 55, 33], [  1, 88, 55, 34], [  1, 90, 55, 35],
  [  1, 91, 55, 36], [  1, 92, 55, 37], [  1, 92, 55, 38], [  1, 93, 55, 39],
  [  1, 93, 55, 39], [  1, 94, 55, 40], [  1, 95, 55, 40], [  1, 96, 55, 41],
  [  1, 96, 55, 41], [  1, 97, 55, 42], [  1, 98, 55, 43], [  1, 98, 55, 43],
  [  1, 99, 55, 44], [  1, 99, 55, 44], [  1,100, 55, 45], [  1,100, 55, 45],
  [  1,101, 55, 46], [  1,101, 55, 46], [  1,102, 55, 47], [  1,102, 55, 48],
  [  1,103, 55, 48], [  1,103, 55, 49], [  1,104, 55, 50], [  1,104, 55, 50],
  [  1,104, 55, 51], [  1,104, 55, 52], [  1,105, 55, 52], [  1,105, 55, 53],
  [  1,105, 55, 53], [  1,106, 55, 54], [  1,106, 55, 56], [  1,106, 55, 57],
  [  1,106, 55, 58], [  1,107, 55, 59], [  1,107, 55, 61], [  1,107, 55, 62],
  [  1,107, 55, 63], [  1,108, 55, 63], [  1,108, 55, 64], [  1,109, 55, 65],
  [  1,109, 55, 65], [  1,109, 55, 66], [  1,110, 55, 67], [  1,110, 55, 68],
  [  1,111, 55, 69], [  1,111, 55, 69], [  1,111, 55, 70], [  1,112, 55, 71],
  [  1,112, 55, 71], [  1,113, 55, 71], [  1,114, 55, 72], [  2,115, 55, 72],
  [  2,115, 55, 72], [  2,116, 55, 73], [  2,117, 55, 73], [  2,117, 55, 73],
  [  2,118, 55, 73], [  2, 74, 55, 74], [  2, 74, 55, 74], [  2, 73, 55, 74],
  [  2, 72, 55, 75], [  2, 72, 55, 75], [  2, 71, 55, 76], [  2, 70, 55, 77],
  [  2, 69, 55, 78], [  2, 69, 55, 78], [  2, 68, 55, 79], [  2, 67, 55, 80],
  [  2, 67, 55, 80], [  2, 69, 55, 81], [  2, 70, 55, 81], [  2, 72, 55, 82],
  [  2, 74, 55, 83], [  2, 76, 55, 83], [  2, 77, 55, 84], [  2, 79, 55, 85],
  [  2, 81, 55, 86], [  2, 82, 55, 87], [  2, 84, 55, 87], [  2, 84, 55, 88],
]

pitcheg = [ # [lev,time]
  [  0,127], [  0,127], [  1,124], [  3,124],
  [  4,122], [  5,120], [  6,118], [  8,118],
  [  9,115], [ 10,113], [ 12,110], [ 13,108],
  [ 14,105], [ 15,105], [ 17,104], [ 18,103],
  [ 19,103], [ 21,102], [ 22,101], [ 23,100],
  [ 24, 99], [ 26, 99], [ 27, 98], [ 28, 97],
  [ 30, 97], [ 31, 96], [ 32, 96], [ 33, 95],
  [ 35, 94], [ 36, 94], [ 37, 93], [ 38, 92],
  [ 40, 91], [ 41, 91], [ 42, 90], [ 44, 90],
  [ 45, 90], [ 46, 89], [ 47, 89], [ 49, 88],
  [ 50, 88], [ 51, 87], [ 53, 87], [ 54, 86],
  [ 55, 86], [ 56, 85], [ 58, 85], [ 59, 84],
  [ 60, 83], [ 62, 83], [ 63, 82], [ 64, 81],
  [ 65, 81], [ 67, 80], [ 68, 79], [ 69, 79],
  [ 71, 78], [ 72, 77], [ 73, 77], [ 74, 77],
  [ 76, 76], [ 77, 76], [ 78, 75], [ 80, 75],
  [ 81, 75], [ 82, 74], [ 83, 74], [ 85, 73],
  [ 86, 73], [ 87, 73], [ 89, 73], [ 90, 72],
  [ 91, 72], [ 92, 71], [ 94, 71], [ 95, 70],
  [ 96, 70], [ 97, 69], [ 99, 69], [100, 68],
  [101, 68], [103, 68], [104, 67], [105, 67],
  [106, 66], [108, 66], [109, 65], [110, 65],
  [112, 64], [113, 64], [114, 63], [115, 63],
  [117, 62], [118, 61], [119, 61], [121, 60],
  [122, 59], [123, 59], [124, 59], [126, 58],
  [127, 58],
]

pmodsens = [ # [pmods, g2, lev1, lev2, moffset]
  [  0,  0, 11, 21, -5], [  1, 32, 11, 21, -5],
  [  2, 52, 11, 21, -5], [  3, 64, 11, 21, -5],
  [  4, 88, 11, 21, -5], [  5,108, 11, 24, -5],
  [  6,126, 15, 27, -5], [  7,127, 75, 47, -5],
]

#!/usr/bin/env python
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

import sys
from string import *
import re

class Module:
  pass

commentre=re.compile(';.*$')
modulere=re.compile('(\d+)\s+(\S+)')
remarkre=re.compile('remark\s+(\S+)')
namedblre=re.compile('(\w+)\s+(\d+.\d+)')
nameintre=re.compile('(\w+)\s+(\d+)')
parameterre=re.compile('(\d+)\s+"([^"]+)"\s+(\d+)\.\.(\d+)\s+"([^"]*)"')
inoutre=re.compile('(\d+)\s+"([^"]+)"\s+(\S+)')
customre=parameterre

entries=open('patch303.txt','r').read().split('----------\r\n')
entries.pop(0)
fromtype={}
fromname={}
modules=[]
for entry in entries:
  data=entry.split('\r\n')
  m=modulere.match(data.pop(0))
  if m:
    #print m.group(1), m.group(2)
    mod=Module()
    mod.type = m.group(1)
    mod.name = m.group(2)
    # remove remark
    data.pop(0)
    # get float attributes
    for i in range(2,8):
      mnd=namedblre.match(data.pop(0))
      if mnd:
        setattr(mod,mnd.group(1),float(mnd.group(2)))
        #print mnd.group(1), mnd.group(2)
    mni=nameintre.match(data.pop(0))
    if mni:
      setattr(mod,mni.group(1),int(mni.group(2)))
    # the rest is parameters, inputs, outpus, custom
    mod.parameters = []
    mod.inputs = []
    mod.outputs = []
    mod.custom = []
    while len(data):
      s=data.pop(0)
      if s == 'parameters':
        section = mod.parameters
        sectionre = parameterre
      elif s == 'inputs':
        section = mod.inputs
        sectionre = inoutre
      elif s == 'outputs':
        section = mod.outputs
        sectionre = inoutre
      elif s == 'custom':
        section = mod.custom
        sectionre = customre
      else:
        ms = sectionre.match(s)
        if ms:
          section.append(ms.groups()[:])
    fromtype[mod.type] = mod
    fromname[mod.name] = mod
    modules.append(mod)

out = open('../nord/nm1/modules.py','w')
out.write('''#!/usr/bin/env python

from nord.types import *
from nord.nm1.colors import nm1conncolors

class ParameterDef(Struct): pass

class ModuleMap(Struct): pass

audio,control,logic,slave = range(4)

modules = [
''')

for module in modules:
  s = '''  ModuleType(
    shortnm='%s',
    type=%s,
    height=%s,
''' % (module.name, module.type, module.height)
  if len(module.inputs):
    s += '''    inputs=[
%s
    ],\n''' % (
        '\n'.join(["      InputType(%-16snm1conncolors.%s)," % (
          "'%s'," %  nm.title().replace(' ',''),
          t.lower().replace(' ',''))
          for (n,nm,t) in module.inputs
        ])
    )
  else:
    s += '    inputs=[],\n'
  if len(module.outputs):
    s += '''    outputs=[
%s
    ],\n''' % (
        '\n'.join(["      OutputType(%-16snm1conncolors.%s)," % (
          "'%s'," %  nm.title().replace(' ',''),
          t.lower().replace(' ',''))
          for (n,nm,t) in module.outputs
        ])
    )
  else:
    s += '    outputs=[],\n'
  if len(module.parameters):
    s += '''    params=[
%s
    ],\n''' % (
        '\n'.join(
        ['''      ParameterType('%s',
        ParameterDef(  
          default=%s,
          low=%s,
          high=%s,
          comment='%s'
        ),
      ),''' % (
          nm.title().replace(' ',''), l, l, h, c)
          for (n,nm,l,h,c) in module.parameters
        ])
    )
  else:
    s += '    params=[],\n'
  if len(module.custom):
    s += '''    modes=[
%s
    ],\n''' % (
        '\n'.join(['''      ModeType('%s',
        ParameterDef(  
          low=%s,
          default=%s,
          high=%s,
          comment='%s'
        ),
      ),''' % (
          nm.title().replace(' ',''), l, l, h, c)
          for (n,nm,h,l,c) in module.custom
        ])
    )
  else:
    s += '    modes=[],\n'
  s += '  ),\n'

  print s
  out.write(s)

out.write(''']

fromtype = {}
fromname = {}
modulemap = Struct()
for module in modules:
  fromname[module.shortnm] = module
  fromtype[module.type] = module
  shortnm = module.shortnm.replace('-','_').replace('&','n').replace(' ','_')
  setattr(modulemap, shortnm, module)

if __name__ == '__main__':
  for module in modules:
    print '%s.type: %d(0x%02x)' % (module.shortnm, module.type, module.type)
    for i in range(len(module.inputs)):
      input = module.inputs[i]
      print ' .inputs[%d] .%s' % (i, input.name)
    for i in range(len(module.outputs)):
      output = module.outputs[i]
      print ' .outputs[%d] .%s' % (i, output.name)
    for i in range(len(module.params)):
      param = module.params[i]
      print ' .params[%d] .%s' % (i, param.name)
    for i in range(len(module.modes)):
      mode = module.modes[i]
      print ' .modes[%d] .%s' % (i, mode.name)
''')


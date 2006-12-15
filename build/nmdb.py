#!/usr/bin/env python

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

class Struct:
  def __init__(self, **kw):
    self.__dict__ = kw

class Module(Struct): pass
class Input(Struct): pass
class Output(Struct): pass
class Parameter(Struct): pass
class Custom(Struct): pass

class ModuleMap(Struct): pass

modules = [
''')

for module in modules:
  s = '''  Module(
    name='%s',
    type=%s,
    height=%s,
''' % (module.name, module.type, module.height)
  if len(module.inputs):
    s += '''    inputs=[
%s
    ],\n''' % (
        '\n'.join(["      Input(name=%-16stype='%s')," % (
          "'%s'," %  nm.title().replace(' ',''),
          t.title().replace(' ',''))
          for (n,nm,t) in module.inputs
        ])
    )
  else:
    s += '    inputs=[],\n'
  if len(module.outputs):
    s += '''    outputs=[
%s
    ],\n''' % (
        '\n'.join(["      Output(name=%-16stype='%s')," % (
          "'%s'," %  nm.title().replace(' ',''),
          t.title().replace(' ',''))
          for (n,nm,t) in module.outputs
        ])
    )
  else:
    s += '    outputs=[],\n'
  if len(module.parameters):
    s += '''    parameters=[
%s
    ],\n''' % (
        '\n'.join(
        ['''      Parameter(
        name='%s',
        low=%s,
        high=%s,
        comment='%s'
      ),''' % (
          nm.title().replace(' ',''), l, h, c)
          for (n,nm,l,h,c) in module.parameters
        ])
    )
  else:
    s += '    parameters=[],\n'
  if len(module.custom):
    s += '''    customs=[
%s
    ],\n''' % (
        '\n'.join(['''      Custom(
        name='%s',
        low=%s,
        high=%s,
        comment='%s'
      ),''' % (
          nm.title().replace(' ',''), l, h, c)
          for (n,nm,h,l,c) in module.custom
        ])
    )
  else:
    s += '    customs=[],\n'
  s += '  ),\n'

  print s
  out.write(s)

out.write(''']

fromtype = {}
fromname = {}
modulemap = Struct()
for module in modules:
  fromname[module.name] = module
  fromtype[module.type] = module
  name = module.name.replace('-','_').replace('&','n').replace(' ','_')
  setattr(modulemap, name, module)

''')

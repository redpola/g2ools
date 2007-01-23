#!/usr/bin/env python

import os,string,sys
from array import array
sys.path.append('.')
from nord.g2.file import Pch2File, MorphMap
from nord.g2.colors import g2modulecolors, g2cablecolors, g2conncolors

class DX7Converter: 
  def __init__(self):
    self.pch2 = Pch2File('dx7.pch2')
    self.dxrouter = self.modulebyname('DXRouter1')
    self.operators = [self.modulebyname('Operator%d'%i) for i in range(1,7)]
    self.lfo = self.modulebyname('LFO')
    self.lfosync = self.modulebyname('LFO Sync')
    self.lfodelay = self.modulebyname('LFO Delay')
    self.lfopitchmod = self.modulebyname('LFO PM')
    self.lfoam = self.modulebyname('LFO AM')
    self.pitcheg = self.modulebyname('PitchEG')

  def modulebyname(self, name):
    for module in self.pch2.patch.voice.modules:
      if module.name == name:
        return module
    return None

class Struct:
  def __init__(self, **kw):
    self.__dict__ = kw

class Operator:
  pass

class LFO:
  pass

class PitchEG:
  pass

class DX7Patch:
  def __init__(self):
    self.operators = [ Operator() for i in range(6) ]

def parsedx7(data):
  x = array('B',data)
  patch = DX7Patch()
  for i in range(6):
    op = patch.operators[5-i]
    op.R1,op.R2,op.R3,op.R4 = x[:4]; x = x[4:]
    op.L1,op.L2,op.L3,op.L4 = x[:4]; x = x[4:]
    op.BrPoint,op.LDepth,op.RDepth = x[:3]; x = x[3:]
    c = x.pop(0); op.RDepthMode,op.LDepthMode = (c>>2),c&3
    c = x.pop(0); op.FreqDetune,op.RateScale = c>>4,c&7
    c = x.pop(0); op.Vel,op.AMod = c>>2,c&3
    op.OutLevel = x.pop(0)
    c = x.pop(0); op.FreqCoarse,op.RatioFixed = c>>1,c&1
    op.FreqFine = x.pop(0)
  pitcheg = patch.pitcheg = PitchEG()
  pitcheg.R1,pitcheg.R2,pitcheg.R3,pitcheg.R4 = x[:4]; x = x[4:]
  pitcheg.L1,pitcheg.L2,pitcheg.L3,pitcheg.L4 = x[:4]; x = x[4:]
  patch.Algorithm = x.pop(0)
  c = x.pop(0); patch.OscKeySync,patch.Feedback = c>>3,c&7
  lfo = patch.lfo = LFO()
  lfo.Rate,lfo.Delay,lfo.PitchMod,lfo.AmMod = x[:4]; x = x[4:]
  c = x.pop(0); lfo.PitchModSens,lfo.Waveform,lfo.Sync = c>>4,(c>>1)&0x7,c&1
  patch.Transpose = x.pop(0)
  patch.Name = x.tostring()
  return patch
  
def convert(fname):
  f = open(fname,'rb')
  data = f.read()
  voice1 = '\xf0\x43\x00\x00\x01\x1b'
  voice32 = '\xf0\x43\x00\x09\x20\x00'
  patches = []
  while data:
    syx = data.find('\xf0')
    if syx < 0:
      break
    esx = data.find('\xf7',syx)
    if data[syx:syx+len(voice1)] == voice1:
      print fname, '1 voice'
    elif data[syx:syx+len(voice32)] == voice32:
      print fname, '32 voice'
      v32data = data[syx+len(voice32):esx]
      for i in range(len(v32data)/128):
        patch = parsedx7(v32data[i*128:i*128+128])
        patch.number = i+1
        patches.append(patch)
    data = data[esx+1:]
  outname = fname[:-4]
  groups = [ patches[i:i+8] for i in range(0,len(patches),8)]
  bank = 1
  opparamnms = [
    'R1','L1','R2','L2','R3','L3','R4','L4',
    'BrPoint','LDepth','RDepth','LDepthMode','RDepthMode',
    'FreqDetune','RateScale','Vel','AMod',
    'OutLevel','FreqCoarse','RatioFixed','FreqFine',
  ]
  for group in groups:
    dxconv = DX7Converter()
    for i in range(len(group)):
      dxpatch = group[i]
      nm = '%2d. %s' % (dxpatch.number, dxpatch.Name)
      print nm
      dxconv.pch2.patch.voice.addmodule('Name',name=nm,horiz=0,vert=i)
      # set DXRouter stuff
      dxconv.dxrouter.params.Algorithm.variations[i] = dxpatch.Algorithm
      dxconv.dxrouter.params.Feedback.variations[i] = dxpatch.Feedback
      # set all Operator's parameters
      for op in range(len(dxpatch.operators)):
        dxop = dxpatch.operators[op]
        g2op = dxconv.operators[op]
        for paramnm in opparamnms:
          g2param = getattr(g2op.params,paramnm)
          dxparam = getattr(dxop,paramnm)
          #print ' ',paramnm, dxparam
          g2param.variations[i] = dxparam
      # set LFO parameters
      lfop = dxconv.lfo.params
      lfop.Waveform.variations[i] = [1,2,2,3,0,4][dxpatch.lfo.Waveform]
      if dxpatch.lfo.Waveform == 2:
        lfop.OutputType.variations[i] = 5 # Bip
      else:
        lfop.OutputType.variations[i] = 4 # BipInv
      lfop.Rate.variations[i] = dxpatch.lfo.Rate
      lfop.PolyMono.variations[i] = dxpatch.lfo.Sync
      dxconv.lfodelay.params.Decay.variations[i] = dxpatch.lfo.Delay
      dxconv.lfopitchmod.params.Lev.variations[i] = dxpatch.lfo.PitchMod
      dxconv.lfoam.params.Level.variations[i] = dxpatch.lfo.AmMod
      # variations[i] = dxpatch.lfo.PitchModSens
      # set PitchEG parameters
      pitchegp = dxconv.pitcheg.params
      pitchegp.Time1.variations[i] = dxpatch.pitcheg.R1
      pitchegp.Level1.variations[i] = dxpatch.pitcheg.L1
      pitchegp.Time2.variations[i] = dxpatch.pitcheg.R2
      pitchegp.Level2.variations[i] = dxpatch.pitcheg.L2
      pitchegp.Time3.variations[i] = dxpatch.pitcheg.R3
      pitchegp.Level3.variations[i] = dxpatch.pitcheg.L3
      pitchegp.Time4.variations[i] = dxpatch.pitcheg.R4
      pitchegp.Level4.variations[i] = dxpatch.pitcheg.L4
      # set Transpose
      # setv(,dxpatch.Transpose
      # sync)
      morph = dxconv.pch2.patch.settings.morphs[7]
      if dxpatch.OscKeySync:
        morph.dials.variations[i] = 127
      else:
        morph.dials.variations[i] = 0
    #
    def addnamebars(pch2, lines, horiz, vert):
      for line in lines:
        m = pch2.patch.voice.addmodule('Name',name=line)
        m.horiz = horiz
        m.vert = vert
        vert += 1
      return vert

    lines = ['dx2g2 converter','by','Matt Gerassimoff']
    vert = 0
    for module in dxconv.pch2.patch.voice.modules:
      if module.horiz != 0:
        continue
      v = module.vert + module.type.height
      #print '',module.name, module.vert, module.type.height, v
      if v > vert:
        vert = v
    vert = addnamebars(dxconv.pch2,lines,0,vert+1)
    vert = addnamebars(dxconv.pch2,['All rights','reserved'],0,vert+1)


    dxconv.pch2.write(outname+'b%d.pch2' % bank)
    bank += 1

if __name__ == '__main__':
  prog = sys.argv.pop(0)
  fails = []
  for fname in sys.argv:
    if fname[-4:].lower() != '.syx':
      continue
    #try:
    #  convert(fname)
    #except:
    #  fails.append(fname)
    convert(fname)
  print 'Failures:'
  for fail in fails:
    print file

#
# audio.py - Audio tab conversion objects
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
from nord.utils import setv, getv
from nord.convert import Convert
from nord.convert.table import wavewrap, modtable

class ConvClip(Convert):
  maing2module = 'Clip'
  parammap = [['ClipLevMod', 'ClipMod'], ['ClipLev', 'Clip'], ['Shape', 'Sym']]
  inputmap = ['In', 'Mod']
  outputmap = ['Out']

class ConvOverdrive(Convert):
  maing2module = 'Clip'
  parammap = [None, None]
  inputmap = ['In', '']
  outputmap = ['']

  def __init__(self, nmarea, g2area, nmmodule, options):
    if options.g2overdrive:
      self.maing2module = 'Overdrive'
      self.parammap = [['AmountMod', 'Overdrive'], ['Amount', 'Overdrive']]
      self.inputmap[1] = 'Mod'
      self.outputmap[0] = 'Out'
    super(ConvOverdrive, self).__init__(nmarea, g2area, nmmodule, options)

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params

    if self.options.g2overdrive:
      setv(g2mp.Shape, 0) # Asym
      setv(g2mp.Type, 3)  # Heavy
      return

    setv(g2mp.Shape, 1) # Sym
    setv(g2mp.ClipLevMod, 91)

    if len(nmm.inputs.OverdriveMod.cables) != 0:
      modin = self.add_module('Mix1-1A', name='Mod In')
      setv(modin.params.On, 1)
      modin.params.On.labels = ['Mod']
      setv(modin.params.ExpLin, 1) # Lin
      setv(modin.params.Lev, getv(nmmp.OverdriveMod))
      self.params[0] = modin.params.Lev
      modout = modin.outputs.Out
      modlev = modin.params.Lev
      self.inputs[1] = modin.inputs.In
    else:
      modout = None
      modlev = None

    if not modout or getv(nmmp.Overdrive) != 0 or \
       nmmp.Overdrive.knob or nmmp.Overdrive.morph or nmmp.Overdrive.ctrl:
      overdrive = self.add_module('ConstSwT', name='Overdrive')
      setv(overdrive.params.On, 1)
      overdrive.params.On.labels = ['Drive']
      setv(overdrive.params.BipUni, 1) # Uni
      setv(overdrive.params.Lev, getv(nmmp.Overdrive))
      if modout:
        self.connect(overdrive.outputs.Out, modin.inputs.Chain)
      else:
        modout = overdrive.outputs.Out
      overdrivelev = overdrive.params.Lev
      self.params[1] = overdrive.params.Lev
    else:
      overdrivelev = None
    
    shpstatic = self.add_module('ShpStatic', name='')
    setv(shpstatic.params.Mode, 0) # Inv x3
    self.connect(modout, shpstatic.inputs.In)
    self.connect(shpstatic.outputs.Out, g2m.inputs.Mod)

    levmult = self.add_module('LevMult', name='')
    self.connect(shpstatic.outputs.Out, levmult.inputs.Mod)

    mix21b = self.add_module('Mix2-1B', name='')
    setv(mix21b.params.ExpLin, 0) # Exp
    setv(mix21b.params.Inv1, 1)
    setv(mix21b.params.Lev1, 53)
    setv(mix21b.params.Lev2, 120)
    self.connect(g2m.outputs.Out, mix21b.inputs.Chain)
    self.connect(levmult.outputs.Out, mix21b.inputs.In2)
    self.connect(mix21b.outputs.Out, levmult.inputs.In)

    mix11a = self.add_module('Mix1-1A', name='')
    setv(mix11a.params.ExpLin, 0) # Exp
    setv(mix11a.params.On, 1)
    setv(mix11a.params.Lev, 96)
    self.connect(mix21b.outputs.Out, mix11a.inputs.In)

    xfade = self.add_module('X-Fade', name='')
    setv(xfade.params.LogLin, 0) # Log
    setv(xfade.params.Mix, 0)
    setv(xfade.params.MixMod, 127)
    self.connect(levmult.inputs.Mod, xfade.inputs.Mod)
    self.connect(xfade.inputs.In1, g2m.inputs.In)
    self.connect(mix11a.outputs.Out, xfade.inputs.In2)

    shpstatic2 = self.add_module('ShpStatic', name='')
    setv(shpstatic2.params.Mode, 1) # Inv x2
    self.connect(xfade.outputs.Out, shpstatic2.inputs.In)

    mix21b2 = self.add_module('Mix2-1B', name='')
    setv(mix21b2.params.ExpLin, 0) # Exp
    setv(mix21b2.params.Lev1, 112)
    setv(mix21b2.params.Lev2, 106)
    self.connect(shpstatic2.outputs.Out, mix21b2.inputs.In1)
    self.connect(mix21b2.outputs.Out, mix21b.inputs.In1)
    self.connect(mix21b2.outputs.Out, mix21b2.inputs.In2)

    out = self.add_module('X-Fade', name='Out')
    setv(out.params.LogLin, 1) # Lin
    setv(out.params.Mix, 0)
    setv(out.params.MixMod, 127)
    self.connect(xfade.inputs.Mod, out.inputs.Mod)
    self.connect(xfade.inputs.In1, out.inputs.In1)
    self.connect(mix21b2.outputs.Out, out.inputs.In2)

    self.params = [ modlev, overdrivelev ]
    self.outputs[0] = out.outputs.Out

class ConvWaveWrap(Convert):
  maing2module = 'WaveWrap'
  parammap = [['AmountMod', 'WrapMod'], ['Amount', 'Wrap']]
  inputmap = ['In', 'Mod']
  outputmap = ['Out']

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params
    setv(g2mp.Amount, wavewrap[getv(nmmp.Wrap)])

class ConvQuantizer(Convert):
  maing2module = 'Digitizer'
  parammap = ['Bits']
  inputmap = ['In']
  outputmap = ['Out']

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params
    
    setv(g2mp.Rate, 127) # max sample rate

class ConvDelay(Convert):
  # no defaults because it's dependant on 2.64mS output.
  def __init__(self, nmarea, g2area, nmmodule, options):
    if not nmmodule.outputs.FixedDelay.net:
      self.maing2module = 'DlySingleB'
      self.parammap = [['TimeMod', 'Modulation'], ['Time', 'Time']]
      self.inputmap = ['In', 'Time']
      self.outputmap = ['', 'Out']
    else:
      self.maing2module = 'DelayDual'
      self.parammap = [['Time1Mod', 'Modulation'], ['Time1', 'Time']]
      self.inputmap = ['In', 'Time1']
      self.outputmap = ['Out2', 'Out1']
    super(ConvDelay, self).__init__(nmarea, g2area, nmmodule, options)

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params
    
    if self.maing2module == 'DelayDual':
      setv(g2mp.Time2, 63) # 2.64mS
      setv(g2mp.Time1, (getv(nmmp.Time)+1)/2)
      setv(g2mp.Time1Mod, (getv(nmmp.Modulation)+1)/2)
    else:
      setv(g2mp.Time, (getv(nmmp.Time)+1)/2)
      setv(g2mp.TimeMod, (getv(nmmp.Modulation)+1)/2)

class ConvSampleNHold(Convert):
  maing2module = 'S&H'
  inputmap = ['Ctrl', 'In']
  outputmap = ['Out']

class ConvDiode(Convert):
  maing2module = 'Rect'
  parammap = ['Mode']
  inputmap = ['In']
  outputmap = ['Out']

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params
    
    mode = getv(nmmp.Mode)
    setv(g2mp.Mode, [0, 0, 2][mode])
    if mode == 0:
      setv(g2mp.Active, 0)

class ConvStereoChorus(Convert):
  maing2module = 'StChorus'
  parammap = ['Detune', 'Amount', ['Active', 'Bypass']]
  inputmap = ['In']
  outputmap = ['OutL', 'OutR']

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params
    
    setv(g2mp.Active, 1-getv(nmmp.Bypass))

class ConvPhaser(Convert):
  maing2module = 'FltPhase'
  parammap = [None, None, ['PitchMod', 'FreqMod'], 'Freq', 'SpreadMod',
              ['FB', 'Feedback'], ['NotchCount', 'Peaks'], 'Spread', 'Level',
              ['Active', 'Bypass'], None]
  inputmap = ['In', '', 'Spr']
  outputmap = ['Out']

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params

    setv(g2mp.Active, 1-getv(nmmp.Bypass))
    setv(g2mp.FBMod, getv(nmmp.Depth))
    setv(g2mp.Type, 3)
    setv(g2mp.Level, modtable[getv(nmmp.Level)][0])
    
    if len(nmm.inputs.FreqMod.cables):
      # add mixer
      mix = self.add_module('Mix2-1B', name='FreqMod')
      self.connect(mix.outputs.Out, g2m.inputs.PitchVar)
      modinp = mix.inputs.In1
      self.inputs[1] = mix.inputs.In2
      setv(g2mp.PitchMod, 127)
      setv(mix.params.Lev1, getv(nmmp.FreqMod))
      depthparam = mix.params.Lev1
    else:
      modinp = g2m.inputs.PitchVar
      depthparam = g2mp.PitchMod
    lfo = self.add_module('LfoC')
    setv(lfo.params.Rate, getv(nmmp.Rate))
    self.params[0] = lfo.params.Rate
    setv(lfo.params.Active, getv(nmmp.Lfo))
    self.params[1] = lfo.params.Active
    self.connect(lfo.outputs.Out, modinp)
    setv(depthparam, getv(nmmp.Depth))
    self.params[9] = depthparam

class ConvInvLevShift(Convert):
  maing2module = 'LevConv'
  parammap = [['OutputType', 'Mode'], None]
  inputmap = ['In']
  outputmap = ['Out']

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params
    
    setv(g2mp.InputType, 0) # Pos
    mode = getv(nmmp.Mode)
    inv = getv(nmmp.Inv)
    setv(g2mp.OutputType, [4, 2, 0, 5, 3, 1][inv*3+mode])

class ConvShaper(Convert):
  maing2module = 'ShpStatic'
  parammap = ['Mode']
  inputmap = ['In']
  outputmap = ['Out']

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params
    
    mode = getv(nmmp.Mode)
    setv(g2mp.Mode, [0, 1, 0, 2, 3][mode])
    if mode == 2:
      setv(g2mp.Active, 0)
    
class ConvCompressor(Convert):
  maing2module = 'Compressor'
  parammap = ['Attack', 'Release', 'Threshold', 'Ratio', 'RefLevel', None,
              ['SideChain', 'Act'], ['SideChain', 'Mon'], ['Active', 'Bypass']]
  inputmap = ['InL', 'InR', 'SideChain']
  outputmap = ['OutL', 'OutR']

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params

    setv(g2mp.Active, 1-getv(nmmp.Bypass))
    setv(g2mp.SideChain, getv(nmmp.Act))
    
class ConvExpander(Convert):
  maing2module = 'Sw2-1'
  parammap = [None]*9
  inputmap = ['', '', 'In1'] # L, R
  outputmap = ['', ''] # L, R

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params

    g2mp.Sel.labels = ['In', 'SideAct']
    setv(g2mp.Sel, getv(nmmp.Act))
    self.params[6] = g2mp.Sel
    envfollow = self.add_module('EnvFollow')
    setv(envfollow.params.Attack, getv(nmmp.Attack))
    setv(envfollow.params.Release, getv(nmmp.Release))
    self.params[:2] = envfollow.params.Attack, envfollow.params.Release
    ratio = self.add_module('ShpExp', name='Ratio/Thresh')
    setv(ratio.params.Curve, 2) # x4
    setv(ratio.params.Amount, getv(nmmp.Ratio))
    self.params[3] = ratio.params.Amount
    left = self.add_module('LevMult', name='Left')
    right = self.add_module('LevMult', name='Right')
    # MISSING Gate, Hold, Mon, and Bypass  parameters

    self.connect(g2m.inputs.In1, left.inputs.In)
    self.connect(g2m.outputs.Out, envfollow.inputs.In)
    self.connect(envfollow.outputs.Out, ratio.inputs.In)
    self.connect(ratio.outputs.Out, left.inputs.Mod)
    self.connect(left.inputs.Mod, right.inputs.Mod)

    self.inputs[:] = left.inputs.In, right.inputs.In, g2m.inputs.In2
    self.outputs = left.outputs.Out, right.outputs.Out

class ConvDigitizer(Convert):
  maing2module = 'Digitizer'
  parammap = ['Bits', 'Rate', 'RateMod', ['Bits', 'QuantOff'],
              ['Active', 'SamplingOff']]
  inputmap = ['In', 'Rate']
  outputmap = ['Out']

  def domodule(self):
    nmm, g2m = self.nmmodule, self.g2module
    nmmp, g2mp = nmm.params, g2m.params

    setv(g2mp.Bits, getv(nmmp.Bits)) # becuase it's also used for QuantOff
    quantoff = getv(nmmp.QuantOff)
    if quantoff:
      setv(g2mp.Bits, 12)
    setv(g2mp.Active, 1-getv(nmmp.SamplingOff))

class ConvRingMod(Convert):
  maing2module = 'LevMod'
  parammap = ['ModDepth', ['ModType', 'RingmodDepth']]
  inputmap = ['In', 'Mod', 'ModDepth']
  outputmap = ['Out']


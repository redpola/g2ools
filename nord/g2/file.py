#!/usr/bin/env python2
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

import string, struct, sys

from nord import printf
from nord.module import Module
from nord.file import hexdump, binhexdump
from nord.g2.modules import fromname
from nord.file import Patch, Performance, Note, Cable, Knob, Ctrl, MorphMap
from nord.g2 import modules
from nord.g2.crc import crc
from nord.g2.bits import setbits, getbits

section_debug = 1 # outputs section debug 
title_section = 1 # replace end of section with section title

NVARIATIONS = 9 # 1-8, init
NMORPHS = 8     # 8 morphs
NKNOBS = 120    # 120 knob settings
NMORPHMAPS = 25 # max morphmaps per variation

FX, VOICE, SETTINGS = 0, 1, 2

class G2Error(Exception):
  '''G2Error - exception for throwing an unrecoverable error.'''
  def __init__(self, value):
    Exception.__init__(self)
    self.value = value
  def __str__(self):
    return repr(self.value)

def getbitsa(bit, sizes, data):
  '''getbitsa(bit, sizes, data) -> bit, [values]'''
  values = []
  for size in sizes:
    bit, value = getbits(bit, size, data)
    values.append(value)
  return bit, values

def setbitsa(bit, sizes, data, values):
  '''setbitsa(bit, sizes, data, values) -> bit'''
  for size, value in zip(sizes, values):
    bit = setbits(bit, size, data, value)
  return bit

class Section(object):
  '''Section abstract class that represents a section of .pch2 file.
  all sections objects have parse() and format() methods.
'''
  default = [0] * (2 << 10) # max 64k section size
  def __init__(self, **kw):
    self.__dict__ = kw
    self.data = bytearray(2<<10)

class Description(object):
  '''Description class for patch/performance description.'''
  pass

class PatchDescription(Section):
  '''PatchDescription Section subclass'''
  type = 0x21
  description_attrs = [
    ['reserved', 5], ['voices', 5], ['height', 14], ['unk2', 3],
    ['red', 1], ['blue', 1], ['yellow', 1], ['orange', 1],
    ['green', 1], ['purple', 1], ['white', 1],
    ['monopoly', 2], ['variation', 8], ['category', 8],
  ]
  def parse(self, patch, data):
    description = patch.description = Description()

    bit = 7*8
    for name, nbits in self.description_attrs:
      bit, val = getbits(bit, nbits, data)
      setattr(description, name, val)

  def format(self, patch):
    data = self.data
    description = patch.description

    bit = 7*8
    for name, nbits in self.description_attrs:
      bit = setbits(bit, nbits, data, getattr(description, name))
    bit = setbits(bit, 8, data, 0)

    last = (bit+7)>>3
    return str(data[:last])

class ModuleList(Section):
  '''ModuleList Section subclass'''
  type = 0x4a
  module_bit_sizes = [8, 7, 7, 8, 1, 1, 6]
  def parse(self, patch, data):
    bit, self.area = getbits(0, 2, data)
    bit, nmodules = getbits(bit, 8, data)

    area = [patch.fx, patch.voice][self.area]

    area.modules = [ None ] * nmodules
    for i in xrange(nmodules):
      bit, id = getbits(bit, 8, data)
      m = Module(modules.fromid(id), area)
      area.modules[i] = m

      bit, values = getbitsa(bit, self.module_bit_sizes, data)
      m.index, m.horiz, m.vert, m.color, m.uprate, m.leds, m.reserved = values
      bit, nmodes = getbits(bit, 4, data)
      # NOTE: .leds seems to related to a group of modules. i cannot
      #       see the relationship but I have got a list of modules
      #       that require this to be set.  This will probably be handled
      #       without this property but added to the module types that
      #       set it.
      self.fixleds(m)

      # mode data for module (if there is any)
      for mode in m.modes:
        bit, mode.value = getbits(bit, 6, data)

      # add missing mode data. some .pch2 versions didn't contain
      #   all the modes in version 23 BUILD 266
      mt = m.type
      if len(m.modes) < len(mt.modes):
        for mode in xrange(len(m.modes), len(mt.modes)):
          m.modes[mode].value = mt.modes[mode].type.default

  # make sure leds bit is set for specific modules
  # - some earlier generated .pch2 files where different
  #   these were emperically determined.
  ledtypes = [
    3, 4, 17, 38, 42, 48, 50, 57, 59, 60, 68, 69,
    71, 75, 76, 81, 82, 83, 85,
    105, 108, 112, 115, 141, 142, 143, 147, 148, 149, 150,
    156, 157, 170, 171, 178, 188, 189, 198, 199, 208,
  ]
  def fixleds(self, module):
    module.leds = 0
    return
    #if module.type.id in ModuleList.ledtypes:
    #  module.leds = 1
    #else:
    #  module.leds = 0

  def format(self, patch):
    data = self.data

    area = [patch.fx, patch.voice][self.area]

    bit  = setbits(0, 2, data, self.area)
    bit  = setbits(bit, 8, data, len(area.modules))

    for m in area.modules:
      bit = setbits(bit, 8, data, m.type.id)
      values = [m.index, m.horiz, m.vert, m.color, m.uprate, m.leds, 0]
      bit = setbitsa(bit, self.module_bit_sizes, data, values)
      # NOTE: .leds seems to related to a group of modules. i cannot
      #       see the relationship but I have got a list of modules
      #       that require this to be set.  This will probably be handled
      #       without this property.
      self.fixleds(m)

      nmodes = len(m.modes)
      bit = setbits(bit, 4, data, nmodes)
      for mode in m.modes:
        bit = setbits(bit, 6, data, mode.value)

    return str(data[:(bit+7)>>3])

class CurrentNote(Section):
  '''CurrentNote Section subclass'''
  type = 0x69
  def parse(self, patch, data):
    lastnote = patch.lastnote = Note()
    bit, values = getbitsa(0, [7, 7, 7], data)
    lastnote.note, lastnote.attack, lastnote.release = values
    bit, nnotes = getbits(bit, 5, data)
    notes = patch.notes = [ Note() for i in xrange(nnotes + 1) ]
    for i, note in enumerate(notes):
      bit, note.note    = getbits(bit, 7, data)
      bit, note.attack  = getbits(bit, 7, data)
      bit, note.release = getbits(bit, 7, data)

  def format(self, patch):
    data = self.data
    if len(patch.notes):
      bit = 0
      lastnote = patch.lastnote
      if not lastnote:
        values = [ 64, 0, 0 ]
      else:
        values = [ lastnote.note, lastnote.attack, lastnote.release ]
      bit = setbitsa(bit, [7, 7, 7], data, values)
      bit = setbits(bit, 5, data, len(patch.notes)-1)
      for note in patch.notes:
        bit = setbits(bit, 7, data, note.note)
        bit = setbits(bit, 7, data, note.attack)
        bit = setbits(bit, 7, data, note.release)
      return str(data[:(bit+7)>>3])
    else:
      return '\x80\x00\x00\x20\x00\x00'  # normal default

def invalidcable(smodule, sconn, direction, dmodule, dconn):
  '''invalidcable(area, smodule, sconn, direction, dmodule, dconn) -> bool
 if connection valid return 0, otherwise error.
'''
  if direction == 1:                  # verify from
    if sconn >= len(smodule.outputs): # out -> in
      return 1
  elif sconn >= len(smodule.inputs):  # in -> in
    return 2
  if dconn >= len(dmodule.inputs):    # verify to
    return 3

  return 0 # if we got here, everything's cool.

class CableList(Section):
  '''CableList Section subclass'''
  type = 0x52
  def parse(self, patch, data):

    bit, self.area = getbits(0, 2, data)
    bit, ncables   = getbits(8, 16, data)

    area = [patch.fx, patch.voice][self.area]

    area.cables = [ None ] * ncables 
    for i in xrange(ncables ):
      c = Cable(area)
      bit, c.color = getbits(bit, 3, data)
      bit, smod    = getbits(bit, 8, data)
      bit, sconn   = getbits(bit, 6, data)
      bit, dir     = getbits(bit, 1, data)
      bit, dmod    = getbits(bit, 8, data)
      bit, dconn   = getbits(bit, 6, data)

      smodule     = area.find_module(smod)
      dmodule     = area.find_module(dmod)

      if invalidcable(smodule, sconn, dir, dmodule, dconn):
        printf('Invalid cable %d: "%s"(%d,%d) -%d-> "%s"(%d,%d)\n',
            i, smodule.type.shortnm, smodule.index, sconn, dir,
            dmodule.type.shortnm, dmodule.index, dconn)
        continue

      if dir == 1:
        c.source = smodule.outputs[sconn]
      else:
        c.source = smodule.inputs[sconn]
      c.dest = dmodule.inputs[dconn]

      area.cables[i] = c
      c.source.cables.append(c)
      c.dest.cables.append(c)

      area.netlist.add(c.source, c.dest)

  def format(self, patch):
    data = self.data
    bit  = setbits(0, 2, data, self.area)

    area = [patch.fx, patch.voice][self.area]

    bit = setbits(8, 16, data, len(area.cables))

    for i, c in enumerate(area.cables):
      bit = setbits(bit, 3, data, c.color)
      bit = setbits(bit, 8, data, c.source.module.index)
      bit = setbits(bit, 6, data, c.source.index)
      bit = setbits(bit, 1, data, c.source.direction)
      bit = setbits(bit, 8, data, c.dest.module.index)
      bit = setbits(bit, 6, data, c.dest.index)

    return str(data[:(bit+7)>>3])

class Parameter(object):
  '''Parameter class for module parameters/settings.'''
  def __init__(self, index, param, default=0, name=''):
    self.index = index
    self.param = param
    self.variations = [default]*NVARIATIONS
    self.name = name
    self.knob = None
    self.mmap = None
    self.ctrl = None

class Morph(object):
  '''Morph class for morph settings.'''
  def __init__(self, index):
    self.dials = Parameter(0, 0, 0)
    self.modes = Parameter(0, 0, 1)
    self.maps = [[] for variation in xrange(NVARIATIONS) ]
    self.index = index
    self.ctrl = None
    self.name = 'morph%d' % (index+1)

class Settings(object):
  '''Settings class for patch settings.'''
  groups = [
    [ 'patchvol', 'activemuted' ],
    [ 'glide', 'glidetime' ],
    [ 'bend', 'semi' ],
    [ 'vibrato', 'cents', 'rate' ],
    [ 'arpeggiator', 'arptime', 'arptype', 'octaves' ],
    [ 'octaveshift', 'sustain' ],
  ]

  def __init__(self):
    for i, group in enumerate(self.groups):
      for j, name in enumerate(group):
        setattr(self, name, Parameter(i+2, j, name=name))
    self.morphs = [ Morph(morph) for morph in xrange(NMORPHS) ]
    self.morphmaps = [ [] for variation in xrange(NVARIATIONS) ]

class Parameters(Section):
  '''Parameters Section subclass'''
  type = 0x4d
  def parse_patch(self, patch, data, bit):
    settings = patch.settings = Settings()

    bit, self.area   = getbits(0, 2, data)
    bit, nsections   = getbits(bit, 8, data) # usually 7
    bit, nvariations = getbits(bit, 8, data) # usually 9

    bit, section  = getbits(bit, 8, data) # 1 for morph settings
    bit, nentries = getbits(bit, 7, data) # 16 parameters per variation
                                          # 8 dials, 8 modes 
    for i in xrange(nvariations): # morph groups
      bit, variation = getbits(bit, 8, data) # variation number
      for morph in xrange(NMORPHS):
        bit, dial = getbits(bit, 7, data)
        if variation < NVARIATIONS:
          settings.morphs[morph].dials.variations[variation] = dial

      for morph in xrange(NMORPHS):
        bit, mode = getbits(bit, 7, data)
        if variation < NVARIATIONS:
          settings.morphs[morph].modes.variations[variation] = mode

    for group in settings.groups:
      bit, section  = getbits(bit, 8, data)
      bit, nentries = getbits(bit, 7, data)
      for i in xrange(nvariations):
        bit, variation = getbits(bit, 8, data)
        for entry in xrange(nentries):
          bit, value = getbits(bit, 7, data)
          if variation < NVARIATIONS:
            getattr(settings, group[entry]).variations[variation] = value

  def format_patch(self, patch):
    data     = self.data
    settings = patch.settings

    bit = setbits(0, 2, data, self.area)
    bit = setbits(bit, 8, data, 7) # always 7 (number of sections?)
    bit = setbits(bit, 8, data, NVARIATIONS)
    
    bit = setbits(bit, 8, data, 1)  # 1 for morph settings
    bit = setbits(bit, 7, data, 16) # 16 parameters per variation

    for variation in xrange(NVARIATIONS): # morph groups
      bit = setbits(bit, 8, data, variation) # variation
      for morph in xrange(NMORPHS):
        dial = settings.morphs[morph].dials
        bit = setbits(bit, 7, data, dial.variations[variation])
      for morph in xrange(NMORPHS):
        mode = settings.morphs[morph].modes
        bit = setbits(bit, 7, data, mode.variations[variation])

    section = 2 # starts at 2 (above: morph is section 1)
    for group in settings.groups:
      nentries = len(group)
      bit = setbits(bit, 8, data, section)
      bit = setbits(bit, 7, data, nentries)
      for variation in xrange(NVARIATIONS):
        bit = setbits(bit, 8, data, variation)
        for entry in xrange(nentries):
          value = getattr(settings, group[entry]).variations[variation]
          bit = setbits(bit, 7, data, value)
      section += 1

    return str(data[:(bit+7)>>3])

  def parse_module(self, patch, data, bit):
    bit, nmodules    = getbits(bit, 8, data)
    bit, nvariations = getbits(bit, 8, data) # if any modules=9, otherwise=0

    area = [patch.fx, patch.voice][self.area]

    for i in xrange(nmodules):
      bit, index = getbits(bit, 8, data)
      bit, nparams = getbits(bit, 7, data)

      m = area.find_module(index)
      params = m.params
      for i in xrange(nvariations):
        bit, variation = getbits(bit, 8, data)
        for param in xrange(nparams):
          bit, value = getbits(bit, 7, data)
          if param < len(params) and variation < NVARIATIONS:
            params[param].variations[variation] = value
            
  def format_module(self, patch):
    data = self.data

    area = [patch.fx, patch.voice][self.area]

    modules = []
    for module in area.modules:
      if not hasattr(module, 'params'):
        continue
      elif not len(module.params):
        continue
      modules.append(module)
    modules.sort(lambda a, b: cmp(a.index, b.index))

    bit = setbits(0, 2, data, self.area)
    bit = setbits(bit, 8, data, len(modules))
    if not len(modules):
      bit = setbits(bit, 8, data, 0) # 0 variations
      return str(data[:(bit+7)>>3])
    bit = setbits(bit, 8, data, NVARIATIONS)

    for i, m in enumerate(modules):
      bit = setbits(bit, 8, data, m.index)

      params = m.params
      bit = setbits(bit, 7, data, len(params))
      for variation in xrange(NVARIATIONS):
        bit = setbits(bit, 8, data, variation)
        for param in params:
          bit = setbits(bit, 7, data, param.variations[variation])

    return str(data[:(bit+7)>>3])

  def parse(self, patch, data):
    bit, self.area = getbits(0, 2, data)
    if self.area < 2:
      self.parse_module(patch, data, bit)
    else:
      self.parse_patch(patch, data, bit)

  def format(self, patch):
    if self.area < 2:
      return self.format_module(patch)
    else:
      return self.format_patch(patch)

class MorphParameters(Section):
  '''MorphParameters Section subclass'''
  type = 0x65
  def parse(self, patch, data):
    bit, nvariations = getbits(0, 8, data)
    bit, nmorphs     = getbits(bit, 4, data)
    bit, reserved    = getbits(bit, 10, data) # always 0
    bit, reserved    = getbits(bit, 10, data) # always 0

    # variations seem to be 9 bytes with first nibble variation # from 0 ~ 8
    # number of morph parameters starts at byte 7-bit 0 for 5-bits
    morphs = patch.settings.morphs
    morphmaps = patch.settings.morphmaps

    for i in xrange(nvariations):
      bit, variation = getbits(bit, 4, data)
      bit += 4+(6*8)+4 # zeros

      bit, nmorphs = getbits(bit, 8, data)
      for i in xrange(nmorphs):
        mmap = MorphMap()
        bit, area       = getbits(bit, 2, data)
        bit, index      = getbits(bit, 8, data)
        bit, param      = getbits(bit, 7, data)
        bit, morph      = getbits(bit, 4, data)
        bit, mmap.range = getbits(bit, 8, data, 1)
        if area:
          mmap.param = patch.voice.find_module(index).params[param]
        else:
          mmap.param = patch.fx.find_module(index).params[param]
        mmap.variation = variation
        mmap.morph = morphs[morph]
        mmap.morph.maps[variation].append(mmap)
        morphmaps[variation].append(mmap)

      bit, reserved = getbits(bit, 4, data) # always 0

  def format(self, patch):
    data = self.data

    bit = setbits(0, 8, data, NVARIATIONS)
    bit = setbits(bit, 4, data, NMORPHS)
    bit = setbits(bit, 10, data, 0) # always 0
    bit = setbits(bit, 10, data, 0) # always 0

    # variations seem to be 9 bytes with first nibble variation # from 0 ~ 8
    # number of morph parameters starts at byte 7-bit 0 for 5-bits
    morphs = patch.settings.morphs

    for variation in xrange(NVARIATIONS):
      bit = setbits(bit, 4, data, variation)
      bit += 4+(6*8)+4 # zeros

      # collect all params of this variation into 1 array
      mparams = []
      for morph in morphs:
        mparams.extend(morph.maps[variation])
      mparams.sort(lambda a, b: cmp(a.param.module.index, b.param.module.index))

      bit = setbits(bit, 8, data, len(mparams))
      for mparam in mparams:
        bit = setbits(bit, 2, data, mparam.param.module.area.index)
        bit = setbits(bit, 8, data, mparam.param.module.index)
        bit = setbits(bit, 7, data, mparam.param.index)
        bit = setbits(bit, 4, data, mparam.morph.index)
        bit = setbits(bit, 8, data, mparam.range)

      bit = setbits(bit, 4, data, 0) # always 0

    bit -= 4
    return str(data[:(bit+7)>>3])

class KnobAssignments(Section):
  '''KnobAssignments Section subclass'''
  type = 0x62
  def parse(self, patch, data):
    bit, nknobs = getbits(0, 16, data)
    patch.knobs = [ Knob() for i in xrange(nknobs)]
    perf = patch

    for knob in perf.knobs:
      bit, knob.assigned = getbits(bit, 1, data)
      if knob.assigned:
        bit, area = getbits(bit, 2, data)
        bit, index = getbits(bit, 8, data)
        bit, knob.isled = getbits(bit, 2, data)
        bit, param = getbits(bit, 7, data)
        if type(perf) == Performance:
          bit, knob.slot = getbits(bit, 2, data)
          patch = perf.patches[knob.slot]
        else:
          knob.slot = 0

        if area == FX or area == VOICE:
          m = [patch.fx, patch.voice][area].find_module(index)
          if m:
            knob.param = m.params[param]
          else:
            knob.assigned = 0
            continue
        elif area == SETTINGS:
          knob.param = patch.settings.morphs[param]
        knob.param.knob = knob

  def format(self, patch):
    data = self.data
    perf = patch

    bit = setbits(0, 16, data, NKNOBS)
    for i in xrange(NKNOBS):
      k = perf.knobs[i]
      bit = setbits(bit, 1, data, k.assigned)
      if k.assigned:
        if hasattr(k.param, 'module'):
          mod = k.param.module
          area, index, param = mod.area.index, mod.index, k.param.index
        else:
          area, index, param = 2, 1, k.param.index
        bit = setbits(bit, 2, data, area)
        bit = setbits(bit, 8, data, index)
        bit = setbits(bit, 2, data, k.isled)
        bit = setbits(bit, 7, data, param)
        if type(perf) == Performance:
          bit = setbits(bit, 2, data, k.slot)

    return str(data[:(bit+7)>>3])

class CtrlAssignments(Section):
  '''CtrlAssignments Section subclass'''
  type = 0x60
  def parse(self, patch, data):
    bit, nctrls  = getbits(0, 7, data)
    patch.ctrls = [ Ctrl() for i in xrange(nctrls)]
    settings = patch.settings

    for m in patch.ctrls:
      bit, m.midicc = getbits(bit, 7, data)
      bit, m.type = getbits(bit, 2, data) # FX, VOICE, SETTINGS
      bit, index = getbits(bit, 8, data)
      bit, param = getbits(bit, 7, data)
      m.index = index
      if m.type == FX:
        m.param = patch.fx.find_module(index).params[param]
      elif m.type == VOICE:
        m.param = patch.voice.find_module(index).params[param]
      elif m.type == SETTINGS:
        if index < 2:
          m.param = settings.morphs[param]
        else:
          m.param = getattr(settings, settings.groups[index-2][param])
      m.param.ctrl = m

  def format(self, patch):
    data = self.data

    bit = setbits(0, 7, data, len(patch.ctrls))

    for m in patch.ctrls:
      bit = setbits(bit, 7, data, m.midicc)
      bit = setbits(bit, 2, data, m.type)
      if m.type < SETTINGS:
        index, param = m.param.module.index, m.param.index
      else:
        index, param = 1, m.param.index
      bit = setbits(bit, 8, data, index)
      bit = setbits(bit, 7, data, param)

    return str(data[:(bit+7)>>3])

class Labels(Section):
  '''Labels Section subclass'''
  type = 0x5b
  def parse_morph(self, patch, data, bit):
    bit, nentries = getbits(bit, 8, data)

    bit, (entry, length) = getbitsa(bit, [8, 8], data) # 1, 1, 0x50
    for i in xrange(NMORPHS):
      bit, (morph, morphlen, entry) = getbitsa(bit, [8, 8, 8], data)
      morphlen -= 1
      s = ''
      for l in xrange(morphlen):
        bit, c = getbits(bit, 8, data)
        if c != 0:
          s += chr(c&0xff)
      patch.settings.morphs[i].label = s

  def format_morph(self, patch):
    data = self.data

    bit = setbits(  0, 2, data, self.area)

    t = '\1\1\x50'
    for morph in xrange(NMORPHS):
      t += ''.join(map(chr, [1, 8, 8+morph]))
      s = patch.settings.morphs[morph].label[:7]
      s += '\0' * (7-len(s))
      for e in s:
        t += e

    for c in t:
      bit = setbits(bit, 8, data, ord(c))

    return str(data[:(bit+7)>>3])

  def parse_parameter(self, patch, data, bit):
    bit, nmodules = getbits(bit, 8, data)

    area = [patch.fx, patch.voice][self.area]

    for mod in xrange(nmodules):

      bit, index = getbits(bit, 8, data)
      bit, modlen = getbits(bit, 8, data)

      m = area.find_module(index)
      if m.type.id == 121: # SeqNote
        # extra editor parameters 
        # [0, 1, mag, 0, 1, octave]
        # mag: 0=3-octaves, 1=2-octaves, 2=1-octave
        # octave: 0-9 (c0-c9)
        m.editmodes = []
        for i in xrange(modlen):
          bit, c = getbits(bit, 8, data)
          m.editmodes.append(c)
        continue
      while modlen > 0:
        bit, (stri, paramlen, param) = getbitsa(bit, [8, 8, 8], data) 
        modlen -= 3

        p = m.params[param]
        p.labels = []

        paramlen -= 1 # decrease because we got param index
        if paramlen:
          for i in xrange(paramlen/7):
            s = ''
            for i in xrange(7):
              bit, c = getbits(bit, 8, data)
              s += chr(c)
            modlen -= 7
            null = s.find('\0')
            if null > -1:
              s = s[:null]
            p.labels.append(s)
        else:
          p.labels.append('')
        if section_debug:
          printf('%d %s %d %d %s\n', index, m.type.shortnm,
              paramlen, param, p.labels)

  def format_parameter(self, patch):
    data = self.data

    area = [patch.fx, patch.voice][self.area]

    modules = []
    # collect all modules with parameters that have labels
    for m in area.modules:
      if hasattr(m, 'params'):
        for param in m.params:
          if hasattr(param, 'labels'):
            modules.append(m)
            break
      if hasattr(m, 'editmodes'):
        modules.append(m)

    bit = setbits(0, 2, data, self.area)

    t = chr(len(modules))
    for m in modules:
      s = ''
      if m.type.id == 121: # SeqNote
        for ep in m.editmodes:
          s += chr(ep)
      else:
        # build up the labels and then write them
        for i, param in enumerate(m.params):
          if not hasattr(param, 'labels'):
            continue
          if section_debug:
            printf('%d %s %d %d %s\n', m.index, m.type.shortnm,
                7*len(param.labels), i, param.labels)
          ps = ''
          for nm in param.labels:
            ps += (nm+'\0'*7)[:7]
          ps = chr(i)+ps
          ps = chr(1)+chr(len(ps))+ps
          s += ps

      t += chr(m.index) + chr(len(s)) + s

    if section_debug:
      printf('paramlabels:\n')
      printf('%s\n', hexdump(t))

    for c in t:
      bit = setbits(bit, 8, data, ord(c))

    return str(data[:(bit+7)>>3])

  def parse(self, patch, data):
    bit, self.area = getbits(0, 2, data)
    if self.area < 2:
      self.parse_parameter(patch, data, bit)
    else:
      self.parse_morph(patch, data, bit)

  def format(self, patch):
    if self.area < 2:
      return self.format_parameter(patch)
    else:
      return self.format_morph(patch)

class ModuleNames(Section):
  '''ModuleNames Section subclass'''
  type = 0x5a
  def parse(self, patch, data):
    bit, self.area = getbits(0, 2, data)
    bit, self.unk1 = getbits(bit, 6, data)
    bit, nmodules = getbits(bit, 8, data)

    area = [patch.fx, patch.voice][self.area]

    names = data[bit/8:]
    for i in xrange(nmodules):
      null = names.find('\0')
      index = ord(names[0])
      if null < 0 or null > 17:
        name = names[1:17]
        null = 16
      else:
        name = names[1:null]
      m = area.find_module(index)
      m.name = name
      names = names[null+1:]

  def format(self, patch):
    data = self.data

    bit = setbits(0, 2, data, self.area)
    bit = setbits(bit, 6, data, self.area) # seems to be duplicate of area
    area = [patch.fx, patch.voice][self.area]

    bit = setbits(bit, 8, data, len(area.modules)) # unknown, see if zero works
    for module in area.modules:
      bit = setbits(bit, 8, data, module.index)
      nm = module.name[:16]
      if len(nm) < 16:
        nm += '\0'
      for c in nm:
        bit = setbits(bit, 8, data, ord(c))

    return str(data[:(bit+7)>>3])

class TextPad(Section):
  '''TextPad Section subclass'''
  type = 0x6f
  def parse(self, patch, data):
    patch.textpad = data

  def format(self, patch):
    return patch.textpad

class Pch2File(object):
  '''Pch2File(filename) - main reading/writing object for .pch2 files
   this may become generic G2 file for .pch2 and .prf2 files
   just by handling the performance sections (and perhaps others)
   and parsing all 4 patches within the .prf2 file.
'''
  section_map = {
      PatchDescription.type: PatchDescription,
      ModuleList.type:       ModuleList,
      CurrentNote.type:      CurrentNote,
      CableList.type:        CableList,
      Parameters.type:       Parameters,
      MorphParameters.type:  MorphParameters,
      KnobAssignments.type:  KnobAssignments,
      CtrlAssignments.type:  CtrlAssignments,
      Labels.type:           Labels,
      ModuleNames.type:      ModuleNames,
      TextPad.type:          TextPad,
  }
  patch_sections = [
    PatchDescription(),
    ModuleList(area=1),
    ModuleList(area=0),
    CurrentNote(),
    CableList(area=1),
    CableList(area=0),
    Parameters(area=2),
    Parameters(area=1),
    Parameters(area=0),
    MorphParameters(area=2),
    KnobAssignments(),
    CtrlAssignments(),
    Labels(area=2),
    Labels(area=1),
    Labels(area=0),
    ModuleNames(area=1),
    ModuleNames(area=0),
    TextPad(),
  ]
  standard_text_header = '''Version=Nord Modular G2 File Format 1\r
Type=%s\r
Version=%d\r
Info=BUILD %d\r
\0'''
  standard_binary_header = 23
  standard_build = 266
  def __init__(self, filename=None):
    self.type = 'Patch'
    self.binary_revision = 0
    self.patch = Patch(fromname)
    if filename:
      self.read(filename)

  def parse_patch(self, patch, data, off):
    while off < len(data):
      type, l = struct.unpack('>BH', data[off:off+3])
      off += 3
      section = Pch2File.section_map[type]()
      if section_debug:
        nm = section.__class__.__name__
        printf('0x%02x %-25s addr:0x%04x len:0x%04x\n', type, nm, off, l)
        printf('%s\n', binhexdump(data[off:off+l]))
      section.parse(patch, data[off:off+l])
      off += l
    return off

  def parse(self, data, off):
    return self.parse_patch(self.patch, data, off)

  # read - this is where the rubber meets the road.  it start here....
  def read(self, filename):
    self.filename = filename
    data = open(filename, 'rb').read()
    null = data.find('\0')
    if null < 0:
      raise G2Error('Invalid G2File "%s" missing null terminator.' % filename)
    self.txthdr = data[:null]
    off = null+1
    self.binhdr = struct.unpack('BB', data[off:off+2])
    if self.binhdr[0] != self.standard_binary_header:
      printf('Warning: %s version %d\n', filename, self.binhdr[0])
      printf('         version %d supported. it may fail to load.\n',
          self.standard_binary_header)
    off += 2
    off = self.parse(data[:-2], off)

    ecrc = struct.unpack('>H', data[-2:])[0]
    acrc = crc(data[null+1:-2])
    if ecrc != acrc:
      printf('Bad CRC 0x%x 0x%x\n' % (ecrc, acrc))

  def format_patch(self, patch):
    s = bytearray()
    for section in Pch2File.patch_sections:
      section.data = bytearray(4<<10)
      f = section.format(patch)

      if section_debug:
        nm = section.__class__.__name__
        printf('0x%02x %-25s len:0x%04x total: 0x%04x\n',
            section.type, nm, len(f), self.off+len(s))
        tbl = string.maketrans(string.ascii_lowercase, ' '*26)
        nm = nm.translate(tbl).replace(' ', '')
        printf('%s\n', nm)
        if title_section and len(nm) < len(f):
          f = nm+f[len(nm):]

      s += struct.pack('>BH', section.type, len(f)) + f
    return str(s)

  def format(self):
    return self.format_patch(self.patch)

  # write - this looks a lot easier then read ehhhh???
  def write(self, filename=None):
    out = open(filename, 'wb')
    hdr = Pch2File.standard_text_header % (self.type,
        self.standard_binary_header, self.standard_build)
    self.off = len(hdr)
    s = struct.pack('BB', self.standard_binary_header, self.binary_revision)
    self.off += len(s)
    s += self.format()
    out.write(hdr + s)
    out.write(struct.pack('>H', crc(s)))

class PerformanceDescription(Section):
  '''PerformanceDescription Section subclass'''
  type = 0x11
  description_attrs = [
    ['unk1', 8], ['hold', 1], ['unk2', 7], ['rangesel', 8], ['rate', 8],
    ['unk3', 8], ['clock', 8], ['unk4', 8], ['unk5', 8],
  ]
  patch_attrs = [
    ['unk1', 8], ['active', 8], ['keyboard', 8], ['keyhold', 8],
    ['unk2', 16], ['keylow', 8], ['keyhigh', 8], ['unk3', 8], ['unk4', 8],
  ]
  def parse_performance(self, perf, data):
    description = perf.description = Description()

    bit = 0
    for name, nbits in self.description_attrs:
      bit, value = getbits(bit, nbits, data)
      setattr(description, name, value)

    patches = description.patches = [ Description() for i in xrange(4) ] 
    for patch in patches:
      pdata = data[bit/8:]
      null = pdata.find('\0')
      if null < 0 or null > 16:
        null = 16
      else:
        null += 1
      patch.name = pdata[:null].replace('\0', '')
      bit += null*8

      for name, nbits in self.patch_attrs:
        bit, value = getbits(bit, nbits, data)
        setattr(patch, name, value)

  def format(self, perf):
    data = self.data
    description = perf.description

    bit = 0
    for name, nbits in self.description_attrs:
      bit = setbits(bit, nbits, data, getattr(description, name))

    patches = description.patches
    for patch in patches:
      nm = patch.name
      if len(nm) < 16:
        nm += '\0'
      for c in nm[:16]:
        bit = setbits(bit, 8, data, ord(c))

      for name, nbits in self.patch_attrs:
        bit = setbits(bit, nbits, data, getattr(patch, name))

    last = (bit+7)>>3
    return str(data[:last])

class GlobalKnobAssignments(KnobAssignments):
  '''GlobalKnobAssignments Section subclasss'''
  type = 0x5f

class Prf2File(Pch2File):
  '''Prf2File(filename) -> load a nord modular g2 performance.'''
  def __init__(self, filename=None):
    self.type = 'Performance'
    self.binary_revision = 1
    self.performance = Performance(fromname)
    self.performance_section = PerformanceDescription()
    self.global_section = GlobalKnobAssignments()
    if filename:
      self.read(filename)

  def parse_section(self, section, data, off):
    sid, l = struct.unpack('>BH', data[off:off+3])
    off += 3
    if section_debug:
      nm = section.__class__.__name__
      printf('0x%02x %-25s addr:0x%04x len:0x%04x\n', sid, nm, off, l)

    section.parse(self.performance, data[off:off+l])
    return off + l

  def parse(self, data, off):
    off = self.parse_section(self.performance_section, data, off)
    for patch in self.performance.patches:
      off = self.parse_patch(patch, data, off)
    return self.parse_section(self.global_section, data, off)

  def format_section(self, section, total=0):
    section.data = bytearray(4<<10)
    f = section.format(self.performance)
    if section_debug:
      nm = section.__class__.__name__
      printf('0x%02x %-25s             len:0x%04x total: 0x%04x\n',
          section.type, nm, len(f), total)
      if title_section:
        tbl = string.maketrans(string.ascii_lowercase, ' '*26)
        nm = nm.translate(tbl).replace(' ', '')
        l = len(nm)
        if l < len(f):
          f = f[:-len(nm)]+nm
    return struct.pack('>BH', section.type, len(f)) + f

  def format(self):
    s = self.format_section(self.performance_section)
    for patch in self.performance.patches:
      s += self.format_patch(patch)
    return s + self.format_section(self.global_section, len(s))

# this is what comes out the other end:
#   pch2 = Pch2File('test.pch2')
#   patch = pch2.patch
#
#   textpad = patch.textpad
#
#   desc = patch.description
#     desc.nvoices
#     desc.height
#     desc.unk2
#     desc.monopoly
#     desc.variation
#     desc.category
#     desc.red
#     desc.blue
#     desc.yellow
#     desc.orange
#     desc.green
#     desc.purple
#     desc.white
#
#   knob = patch.knobs[i] (i=0~119)
#     page = (i/8)%3 (1,2,3)
#     group = i/24   (A,B,C,D,E)
#     knobnum = i&7  (0 ~ 7)
#     knob.index
#     knob.paramindex
#     knob.area
#     knob.isled
#
#   ctrl = patch.ctrls[i]
#     ctrl.type (1=User,2=System)
#     ctrl.midicc
#     ctrl.index
#     ctrl.paramindex
#
#   settings = patch.settings
#     settings.morphdial[var][dial] (var=0~8, dial=0~7)
#   morphgroup = settings.morphgroup[var][group] (var=0~8, group=0~7)
#     - i may invert the composition so all variations just become arrays
#   variation = settings.variation[var]
#     - i may invert the composition so all variations just become arrays
#     - instead of settings.variation[var].activemuted, it would become
#       settings.activemuted which is a sequence of 9 integers.
#     variation.activemuted
#     variation.arpeggiator
#     variation.arptype
#     variation.bend
#     variation.cents
#     variation.glide
#     variation.octaves
#     variation.octaveshift
#     variation.patchvol
#     variation.rate
#     variation.semi
#     variation.sustain
#     variation.time
#     variation.vibrato
#
#   area = patch.voice
#   area = patch.fx
#
#   module = area.modules[i]
#     module.name
#     module.index
#     module.horiz
#     module.vert
#     module.color
#     module.uprate # increase rate of module i.e. control -> audio
#     module.led    # special parameter seems set for a group of modules
#                   # mostly led outputs for knobs but not always
#                   # i may handle it on a module type basis and remove it
#     module.modes[i]
#     module.params[i]
#     module.inputs[i]
#     module.outputs[i]
#   param = module.params[i]
#     param.variations
#     param.labels
#   type = module.type
#     type.longnm
#     type.shortnm
#     type.height
#     type.page
#     type.modes[i]
#     type.params[i]
#     type.inputs[i]
#     type.outputs[i]
#   page = type.page
#     page.name
#     page.index
#   input = module.inputs[i]
#     input.module
#     input.index
#     input.type
#     input.rate
#     input.cables[i]
#     input.net
#   output = module.outputs[i] # same members as input
#   param = module.params[i]
#     param.module
#     param.index
#     param.type
#     param.variations[i]
#     param.labels[i]
#   ptype = param.type
#     ptype.type
#     ptype.name
#     ptype.low
#     ptype.high
#     ptype.default
#     ptype.definitions
#     ptype.comments
#   mode = module.modes[i]
#     mode.module
#     mode.index
#     mode.type
#     mode.value
#   mtype = mode.type
#     mtype.name
#     mtype.low
#     mtype.high
#     mtype.default
#     mtype.definitions
#     mtype.comments
#
#   cable = area.cables[i]
#     cable.color
#     cable.source
#     cable.dest
#
#   source = cable.source # same as module.inputs[i] or module.outputs[i]
#   dest = cable.dest # same as module.inputs[i] only
#
#   morph = patch.morphs[i]
#     morph.label
#     morph.dial[variation]
#     morph.mode[variation] (0=knob,1=morph,2=wheel2)
#
#   param = morph.params[i]
#     param.area
#     param.index
#     param.paramindex
#     param.range
#   

if __name__ == '__main__':
  prog = sys.argv.pop(0)
  filename = sys.argv.pop(0)
  printf('"%s"\n', filename)
  pch2 = Pch2File(filename)
  #pch2.write(sys.argv.pop(0))


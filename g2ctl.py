#!/usr/bin/env python2
#
# g 2 c t l
#
import os, struct, sys
from nord import printf
from nord.g2.categories import g2categories
from nord.g2.file import Pch2File
from nord.g2.bits import BitStream
from array import array

# vim: set sw=2:

g2Message0x01                   = 0x01
g2QuerySynthSettings            = 0x02
g2SendSynthSettings             = 0x03
g2QueryAssignedVoices           = 0x04
g2RecvAssignedVoices            = 0x05
g2Message0x06                   = 0x06
g2Message0x07                   = 0x07
g2Message0x08                   = 0x08
g2SendSelectSlot                = 0x09
g2SendRetrieveBankPatch         = 0x0a
g2SendStoreBankPatch            = 0x0b
g2SendClearBankPatch            = 0x0c
g2RecvStoreBankPatch            = 0x0d
g2SendClearBank                 = 0x0e
g2Message0x0f                   = 0x0f
g2QueryPerformanceSettings      = 0x10
g2ChunkPerformanceSettings      = 0x11
g2RecvClearBank                 = 0x12
g2RecvListNames                 = 0x13
g2QueryBankPatchList            = 0x14
g2RecvClearBank                 = 0x15
g2RecvAddNames                  = 0x16 # partially known
g2SendPatchBankUpload           = 0x17
g2RecvPatchBankUpload           = 0x18
g2SendPatchBankData             = 0x19
g2Message0x1a                   = 0x1a
g2Message0x1b                   = 0x1b
g2SendGlobalKnobAssignment      = 0x1c
g2SendGlobalKnobDeassign        = 0x1d
g2SendSelectGlobalPage          = 0x1e
g2Message0x1f                   = 0x1f
g2Message0x20                   = 0x20
g2ChuckPatchDescription         = 0x21
g2SendMidiCCAssignement         = 0x22
g2SendMidiCCDeassign            = 0x23
g2Message0x24                   = 0x24
g2SendKnobAssignment            = 0x25
g2SendKnobDeassign              = 0x26
g2SendPatchName                 = 0x27
g2QueryPatchName                = 0x28
g2ChunkPerformanceName          = 0x29
g2SendSetModuleUprateMode       = 0x2a
g2SendSetModuleParameterMode    = 0x2b
g2Message0x2c                   = 0x2c
g2SendSelectParameterPage       = 0x2d
g2QuerySelectedParameter        = 0x2e
g2SendSelectParameter           = 0x2f
g2SendAddModule                 = 0x30
g2SendSetModuleColor            = 0x31
g2SendDeleteModule              = 0x32
g2SendSetModuleLabel            = 0x33
g2SendMoveModule                = 0x34
g2QuerySlotPatchVersion         = 0x35
g2Message0x36                   = 0x36
g2SendPatch                     = 0x37
g2RecvPatchVersionChanged       = 0x38
g2RecvLEDData                   = 0x39
g2RecvVolumeData                = 0x3a
g2QueryMasterClock              = 0x3b
g2QueryPatch                    = 0x3c
g2SendMidiDumpCommand           = 0x3d
g2SendSetPerformanceMode        = 0x3e
g2SendSetMasterClock            = 0x3f
g2SendSetParameterValue         = 0x40
g2Message0x41                   = 0x41
g2SendSetParameterLabel         = 0x42
g2SendSetMorphRange             = 0x43
g2SendCopyVariation             = 0x44
g2Message0x45                   = 0x45
g2Message0x46                   = 0x46
g2Message0x47                   = 0x47
g2Message0x48                   = 0x48
g2Message0x49                   = 0x49
g2ChunkModuleList               = 0x4a
g2Message0x4b                   = 0x4b
g2QueryParameterList            = 0x4c
g2ChunkParameterList            = 0x4d
g2Message0x4c                   = 0x4e
g2QueryParameterNames           = 0x4f
g2SendAddCable                  = 0x50
g2SendDeleteCable               = 0x51
g2ChunkCableList                = 0x52
g2Message0x53                   = 0x53
g2SendSetCableColor             = 0x54
g2SendMidiCCSnapshot            = 0x55
g2SendPlayNote                  = 0x56
g2Message0x57                   = 0x57
g2Message0x58                   = 0x58
g2Message0x59                   = 0x59
g2ChunkModuleNames              = 0x5a
g2ChunkParameterNames           = 0x5b
g2Message0x5c                   = 0x5c
g2RecvMasterClock               = 0x5d
g2QueryGlobalKnobs              = 0x5e
g2ChunkGlobalKnobs              = 0x5f
g2ChunkControllers              = 0x60
g2Message0x61                   = 0x61
g2ChunkKnobs                    = 0x62
g2Message0x63                   = 0x63
g2Message0x64                   = 0x64
g2ChunkMorphParamters           = 0x65
g2Message0x66                   = 0x66
g2Message0x67                   = 0x67
g2QueryCurrentNote              = 0x68 # partially known
g2ChunkCurrentNote              = 0x69 # partially known
g2SendSelectVariation           = 0x6a
g2Message0x6b                   = 0x6b
g2Message0x6c                   = 0x6c
g2Message0x6d                   = 0x6d
g2QueryPatchNotes               = 0x6e
g2ChunkPatchNotes               = 0x6f
g2Message0x70                   = 0x70
g2QueryResourcesUsed            = 0x71 # partially known
g2RecvResourcesUsed             = 0x72 # partially known
g2Message0x73                   = 0x73
g2Message0x74                   = 0x74
g2Message0x75                   = 0x75
g2Message0x76                   = 0x76
g2Message0x77                   = 0x77
g2Message0x78                   = 0x78
g2Message0x79                   = 0x79
g2Message0x7a                   = 0x7a
g2Message0x7b                   = 0x7b
g2Message0x7c                   = 0x7c
g2SendStartStopCommunication    = 0x7d
g2RecvErrorMessage              = 0x7e # partially known
g2RecvOK                        = 0x7f
g2RecvMidiCC                    = 0x80
g2Message0x81                   = 0x81
# ...

############################################################
# command processing
class Command:
  def __init__(self, name, params, description, func):
    self.name = name
    self.params = params
    self.description = description
    self.func = func

def debug(fmt, *a):
  if 0:
    printf(fmt, *a)

commands = {}
commandlist = []
def add_command(name, params, desc, func):
  command = Command(name, params, desc, func)
  commands[name] = command
  commandlist.append(command)

def run(name, args):
  error = -1
  if commands.has_key(name):
    command = commands[name]
    func = command.func
    l = len(command.params)
    a = args[:l]
    if len(a) < l:
      printf('error: %s missing %s\n', name,
          ' '.join([ '<%s>' % p for p in command.params[len(a):]]))
      error = -1
    else:
      args[:l] = []
      printf('%s %s\n', name, ' '.join(a))
      error = func(command, *a)
    if error:
       printf('usage: %s %s\n', name,
            ' '.join(['<%s>' % p for p in command.params ]))
    printf('\n')
  else:
    printf('error: bad command "%s"\n', name)
  return error

def process(args):
  error = 0
  while len(args):
    name = args.pop(0)
    error = run(name, args)
    if error:
      break
  return error

prog = ''
# default main
def main(argv):
  global prog
  prog = argv[0]
  try:
    args = argv[1:]
    rc = 0
    printf('\n')
    if len(args) == 0:
      process(['help'])
    rc = process(args)
    if rc:
      printf('use "help" command to see list of commands and arguments.\n')
      rc = -1
  except:
    import traceback
    printf('%s\n', traceback.format_exc())
    rc = -1
  sys.exit(rc)

def clean_line(line):
  cl = line.find('#')
  if cl > -1:
    line = line[:cl]
  return line.strip()

# default script command
def cmd_script(command, filename):
  lines = map(clean_line, open(filename, 'r').readlines())
  newargs = ' '.join(lines).split()
  return process(newargs)
add_command('script', ['file'], 'execute command from <file>', cmd_script)

def wrap_lines(s, maxlen=80):
  lines = []
  words = s.split()
  line = words.pop(0)
  while len(words):
    if len(line) + len(words[0]) + 1 > maxlen:
      lines.append(line)
      line = words.pop(0)
    else:
      line += ' ' + words.pop(0)
  lines.append(line)
  return lines

# default help system
def cmd_help(command):
  global prog
  printf('usage: %s [commands]*\n', prog)
  printf('  commands:\n')
  for command in commandlist:
    sep = ''
    if len(command.params):
      sep = ' '
    params = [ '<%s>' % p for p in command.params ]
    usage = '%s%s%s:' % (command.name, sep, ' '.join(params))
    desc = wrap_lines(command.description, 80-30)
    printf('    %-25s %s\n', usage, desc.pop(0))
    while len(desc):
      printf('    %-25s %s\n', '', desc.pop(0))
  printf('\n  multiple commands are executed consecutively\n')
  return 0
add_command('help', [], 'display list of commands', cmd_help)

######################## g2ctl functions ########################

import struct
import usb

def hexdump(bytes, addr=0, size=1):
  def out(x):
    if x < 32 or x >= 127:
      return '.'
    return chr(x)

  '''hexdump(bytes,addr,size) -> string
  return hex dump of size itmes using addr as address'''
  s = []
  if size == 4:
    type, fmt, l = 'I', '%08x', 17
  elif size == 2:
    type, fmt, l = 'H', '%04x', 19
  else:
    type, fmt, l = 'B', '%02x', 23
  a = array(type, str(bytes))
  ofmt = '%04x: %-*s  %-*s | %s'
  for off in range(0, len(bytes), 16):
    hex = [fmt % i for i in a[off/size:(off+16)/size]]
    s.append(ofmt % (addr+off,
      l, ' '.join(hex[:8/size]), l, ' '.join(hex[8/size:]),
      ''.join([out(byte) for byte in bytes[off:off+16]])))
  return '\n'.join(s)

def crc16(val, icrc):
  k = (((icrc>>8)^val)&0xff)<<8
  crc = 0
  for bits in range(8):
    if (crc^k)&0x8000 != 0:
      crc = (crc<<1)^0x1021
    else:
      crc <<= 1
    k <<= 1
  return (icrc<<8)^crc

def crc(s):
  return reduce(lambda a, b: crc16(b, a), s, 0) & 0xffff

CMD_A    = 0x08
CMD_B    = 0x09
CMD_C    = 0x0a
CMD_D    = 0x0b
CMD_SYS  = 0x0c
CMD_INIT = 0x80
CMD_MASK = 0xf0
CMD_REQ  = 0x20
CMD_SEND = 0x30
CMD_RESP = 0x00

class G2USBInterface:
  def __init__(self):
    vendorid, productid = 0xffc, 2 # clavia, g2

    # find g2 usb device
    g2dev = None
    for bus in usb.busses():
      for device in bus.devices:
        if device.idVendor == vendorid and device.idProduct == productid:
          g2dev = device
    if not g2dev:
      raise Exception('No g2 device found')
    self.g2dev = g2dev

    # get 3 endpoints
    g2conf = g2dev.configurations[0]
    g2intf = g2conf.interfaces[0][0]
    g2eps = g2intf.endpoints
    self.g2iin  = g2eps[0].address
    self.g2bin  = g2eps[1].address
    self.g2bout = g2eps[2].address

    self.g2h = g2dev.open()
    self.g2h.setConfiguration(g2conf)
    self.g2h.reset()

  def bwrite(self, addr, data):
    return self.g2h.bulkWrite(addr, data) # self.g2bout

  def bread(self, addr, len, timeout=100):
    try:
      data = self.g2h.bulkRead(addr, len, timeout) # self.g2bin
      return bytearray([ byte & 0xff for byte in data ])
    except:
      return []

  def iread(self, addr, len, timeout=100):
    data = self.g2h.interruptRead(addr, len, timeout) # self.g2iin
    return bytearray([ byte & 0xff for byte in data ])

  def read_message(self):
    try:
      diin = self.iread(self.g2iin, 16, 100)
      s =  hexdump(diin).replace('\n','\n       ')
      debug('<%d %s\n', self.g2iin & 0x7f, s)
    except:
      diin = None
    return diin

  def format_message(self, data, type):
    # handle 0x80 (init) messages specially
    if data[0] == CMD_INIT:
      # message 0x80 is just itself
      s = data
    else:
      # messages start with 0x01 0xRC 0xDD 0xDD .. 0xDD
      # C: command (usually just the lower nibble)
      # R: 0x2 when request, 0x0 for response
      #    0x3 ? maybe response-less request
      # DD: data for command
      s = bytearray([0x01]+[data[0]|type]+data[1:])

    # messages are sent formatted as bytes:
    # SS SS MM MM MM .. MM CC CC
    # SS: Big endian 16-bit size of message
    # MM: Message (variable length)
    # CC: Big endian 16-bit crc of MM MM .. MM
    l = len(s)+4  # length includes SS SS and CC CC (add 4 bytes)
    c = crc(s)    # calculate the crc
    # encode and send the message to be sent
    ns = bytearray(struct.pack('>H%dsH' % len(s), l, str(s), c))
    # max message len 4096, break message into 4096 byte chunks
    return [ ns[i:i+4096] for i in range(0, len(ns), 4096) ]

  def extended_message(self, din, data):
    sz = (din[1]<<8)|din[2]
    bin = []
    retries = 5 # the message has to return within 5 tries
    while retries != 0 and sz != len(bin):
      bin = self.bread(self.g2bin, sz)
      retries -= 1
    s = hexdump(bin).replace('\n','\n   ')
    debug('<%d %s\n', self.g2bin & 0x7f, s)
    if retries == 0:
      raise Exception('Could not get result')
    elif bin[0] == CMD_INIT: # special case
      pass
    elif bin[1] == data[0]: # if result is same as command we got message
      pass
    else:
      return None
    
    ecrc = crc(bin[:-2]) # expected crc
    acrc = (bin[-2]<<8)|bin[-1]     # actual crc
    if ecrc != acrc:
      printf('bad crc exp: 0x%04x act: 0x%04x\n', ecrc, acrc)
    return bin

  def embedded_message(self, din, data):
    dil = din.pop(0)>>4 # length encoded in upper nibble of header byte
    ecrc = crc(din[:dil-2]) # expected crc
    acrc = (din[dil-2]<<8)|din[dil-1]  # actual crc
    if ecrc != acrc:
      printf('bad crc exp: 0x%04x act: 0x%04x\n', ecrc, acrc)
    return din[:dil]

  def is_extended(self, data):
    return data[0] & 0xf == 1

  def is_embedded(self, data):
    return data[0] & 0xf == 2

  def send_message(self, data, type=CMD_REQ, timeout=100):

    packets = self.format_message(data, type)
    for packet in packets:
      self.bwrite(self.g2bout, packet)
      s = hexdump(packet).replace('\n','\n   ')
      debug('>%d %s\n', self.g2bout & 0x7f, s)

    if type != CMD_REQ:
      return ''

    # retry 5 times or til the correct reponse is returned
    # which is usually the command without the request bit (0x20) set
    result = None
    for retries in range(5):
      din = self.bread(self.g2iin, 16, timeout)
      if len(din) == 0:
        continue

      # result message first byte:
      #   0xLT 0xDD 0xDD .. 0xDD 0xCC 0xCC (16 0xDD bytes)
      #   T: message type (1=extended message, 2=embedded message)
      #   L: embedded message length (<=0xf, always zero for extended message)
      #   0xDD
      s = hexdump(din).replace('\n','\n   ')
      debug('<%d %s\n', self.g2iin & 0x7f, s)
      if self.is_extended(din):
        result = self.extended_message(din, data)
      elif self.is_embedded(din):
        result = self.embedded_message(din, data)

      if result:
        break

    return result

def parse_name(data):
  s = data[:16]
  if type(s) != type(''):
    s = str(s)
  null = s.find('\0')
  if null < 0:
    return s, data[16:]
  else:
    return s[:null], data[null+1:]

def format_name(name):
  if len(name) < 16:
    return name + '\0'
  else:
    return name[:16]

def parse_bank_patch(location):
  bank, patch = map(int, location.split(':'))
  if bank < 1 or bank > 32:
    printf('invalid bank %d, must be 1 to 32\n', bank)
    return -1, -1
  if patch < 1 or patch > 127:
    printf('invalid patch %d, must be 1 to 127\n', patch)
    return -1, -1
  return bank-1, patch-1

###################### commands ########################
class G2Interface(object):

  def __setattr__(self, name, value):
    if self.__dict__.get('usb', None) == None:
      self.__dict__['usb'] = G2USBInterface()
    setattr(self.usb, name, value)

  def __getattr__(self, name):
    if self.__dict__.get('usb', None) == None:
      self.__dict__['usb'] = G2USBInterface()
    return getattr(self.usb, name)

g2usb = G2Interface()

def cmd_list(command):
  JUMP, SKIP, BANK, MODE, CONTINUE = [1, 2, 3, 4, 5]
  LAST = CONTINUE
  PATCH_MODE, PERFORMANCE_MODE, END_MODE = range(3)
  modes = ['Pch2', 'Prf2']
  mode = PATCH_MODE
  bank = 0
  patch = 0
  while mode < END_MODE:
    cmd = [CMD_SYS, 0x41, g2QueryBankPatchList, mode, bank, patch]
    data = g2usb.send_message(cmd)
    data = str(data[9:-2])
    while len(data):
      c = ord(data[0])
      if c > LAST:
        name, data = parse_name(data)
        category, data = ord(data[0]), data[1:]
        printf('%s %-6s %-9s %s\n', modes[mode],
                '%d:%d' % (bank+1, patch+1), g2categories[category], name)
        patch += 1
      elif c == CONTINUE:
        data = data[1:]
      elif c == BANK:
        bank, patch, data = ord(data[1]), ord(data[2]), data[3:]
      elif c == JUMP:
        patch, data = ord(data[1]), data[2:]
      elif c == SKIP:
        patch, data = patch+1, data[1:]
      elif c == MODE:
        mode, bank, patch, data = mode+1, 0, 0, data[1:]
  return 0
add_command('list', [], 'list all patches and performances', cmd_list)

def read_g2_file(filename):
  data = open(filename).read()
  null = data.find('\0')
  if null < 0:
    printf('invalid pch2 %s\n', filename)
    return []
  return data[null:]

def cmd_loadslot(command, slot, filename):
  data = read_g2_file(filename)
  if len(data) == 0:
    return -1
  data = data[3:-2]
  patchname = format_name(os.path.splitext(os.path.basename(filename))[0])

  slot = 'abcd'.find(slot.lower())
  if slot < 0:
    return -1
  a = bytearray([CMD_A+slot, 0x53, 0x37, 0x00, 0x00, 0x00]) 
  a.fromstring(patchname)
  a.fromstring(data)
  g2usb.send_message(a.tolist())
  return 0
add_command('loadslot', ['slot', 'file'], 'load patch into a slot',
    cmd_loadslot)

def cmd_showslot(command, slot):
  slot = 'abcd'.find(slot.lower())
  if slot < 0:
    return -1
  version = g2usb.send_message([CMD_SYS, 0x41, 0x35, slot])[5]
  data = g2usb.send_message([CMD_A+slot, version, 0x3c])
  name = g2usb.send_message([CMD_A+slot, version, 0x28])
  name, junk = parse_name(name[4:])
  #printf("%s\n", hexdump(data[1:-2]))
  pch2 = Pch2File()
  data = data[0x03:0x15] + data[0x17:-2]
  pch2.parse(data.tostring(), 0)

  from pch2tog2 import print_patch
  printf('# %s\n', name)
  print print_patch(pch2.patch)
  return 0
add_command('showslot', ['slot'], 'show patch in a slot',
    cmd_showslot)

def cmd_store(command, location, filename):
  data = read_g2_file(filename)
  l = len(data)
  if l == 0:
    return -1
  bank, patch = parse_bank_patch(location)
  if bank < 0:
    return -1
  name, ext = os.path.splitext(os.path.basename(filename))
  name = format_name(name)
  printf('%s %s\n', name, ext)
  if ext.lower() == '.prf2':
    mode = 1
  else:
    mode = 0
  printf("%d:%d %s\n", bank, patch, name)
  a = bytearray([CMD_SYS, 0x41, 0x19, mode, bank-1, patch-1])
  a.fromstring(name)
  a.extend([ (l>>8)&0xff, l&0xff, 0x17 ])
  a.fromstring(data)
  g2usb.send_message(a.tolist())
  return 0
add_command('store', ['loc', 'file'], 'store file at location', cmd_store)

def cmd_clear(command, location):
  bank, patch = parse_bank_patch(location)
  if bank < 0:
    return -1
  g2usb.send_message([CMD_SYS, 0x41, 0x0c, 0x00, bank, patch, 0x00])
  return 0
add_command('clear', ['loc'], 'clear location', cmd_clear)

def cmd_dump(command, bank):
  bank, patch = parse_bank_patch(location)
  if bank < 1:
    return -1
  for patch in range(128):
    data = g2usb.send_message([CMD_SYS, 0x41, 0x17, 0x00, bank, patch])
    if data[3] == 0x18:
      continue
    data = data[5:]
    #bank, patch = data[:2]
    name, data = parse_name(data[2:])
    printf('%d:%d %s\n', bank+1, patch+1, name)
  #print hexdump(pch2)
  return 0
add_command('dump', ['loc'], 'dump location to .pch2 file', cmd_dump)

def cmd_mode(command, mode):
  modes = {'patch': 0, 'perf': 1}
  data = g2usb.send_message([CMD_SYS, 0x41, 0x3e, modes.get(mode, 0), 0x00])
  return 0
add_command('mode', ['mode'], 'set mode to patch or perf', cmd_mode)

def cmd_select(command, slot, loc):
  slot = 'abcdp'.find(slot.lower())
  print 'slot=', slot
  if slot < 0:
    return -1
  bank, patch = parse_bank_patch(loc)
  if bank < 0:
    return -1
  cmd = [CMD_SYS, 0x41, 0x0a, slot, bank, patch]
  data = g2usb.send_message(cmd, timeout=1000)
  return 0
add_command('select', ['slot', 'loc'], 'load a patch/performance into slot',
    cmd_select)

def cmd_settings(command):
  g2usb.send_message([CMD_SYS, 0x41, 0x35, 0x04])
  syst = g2usb.send_message([CMD_SYS, 0x41, 0x02])
  synthname, syst = parse_name(syst[4:])
  printf('%s:\n', synthname)
  bitstream = BitStream(syst)
  mode = bitstream.read_bits(1)
  bitstream.seek_bit(8*5)
  midis = bitstream.read_bitsa([8]*5)
  sysex, local, _, prgch = bitstream.read_bitsa([8, 1, 7, 8])
  _, clkse, clkre, _ = bitstream.read_bitsa([1, 1, 1, 5])
  _, tune_cent, _, tune_semi = bitstream.read_bitsa([8, 8, 16, 8])
  _, pedal_polarity, _, pedal_gain = bitstream.read_bitsa([8, 1, 7, 8])
  printf(' mode: %s\n', ['Patch', 'Performance'][mode])
  printf(' midi:\n')
  printf('  slots: a:%d b:%d c:%d d:%d glob:%d\n', *midis)
  printf('  sysex: %d\n', sysex+1)
  printf('  local: %s\n', ['off','on'][local])
  printf('  prgch: %s\n', ['off','send','recv','send/recv'][prgch])
  printf('  clkse: %s\n', ['on','off'][clkse])
  printf('  clkre: %s\n', ['on','off'][clkre])
  printf(' tune semi: %d\n', struct.unpack('b',chr(tune_semi))[0])
  printf(' tune cent: %d\n', struct.unpack('b',chr(tune_cent))[0])
  printf(' pedal polarity: %s\n', ['open','closed'][pedal_polarity])
  printf(' pedal gain: %.2f\n', 1.0 + 0.5*pedal_gain/32)
  sels = g2usb.send_message([CMD_SYS, 0x41, 0x81])
  data = g2usb.send_message([CMD_SYS, sels[2], 0x10])
  perfname, data = parse_name(data[4:])
  bitstream = BitStream(data, 8*4)
  if mode:
    printf('Performance: %s\n', perfname)
  else:
    printf('Patches: %s\n', perfname)
  _, focus, _ = bitstream.read_bitsa([4, 2, 2])
  range_enable, bpm, split, clock = bitstream.read_bitsa([8, 8, 8, 8])
  printf(' focus: %s\n', 'abcd'[focus])
  printf(' range enable: %s\n', ['off','on'][range_enable])
  printf(' master clock: %d BPM: %s\n', bpm, ['stop','run'][clock])
  printf(' kb split: %s\n', ['off','on'][split])
  data = data[11:]
  for slot in range(4):
    name, data = parse_name(data)
    active, key, hold, bank, patch, low, high = data[:7]
    printf(' slot %s: %d:%d "%-16s"\n', 'abcd'[slot], bank+1, patch+1, name)
    printf('  active: %-3s, ', ['off','on'][active])
    printf('key: %-3s, ', ['off','on'][key])
    printf('hold: %-3s, ', ['off','on'][hold])
    printf('range: %d-%d\n', low, high)
    data = data[10:]
  return 0
add_command('settings', [], 'print patch performance settings',
    cmd_settings)

def cmd_slot(command, slot):
  ion = g2usb.send_message([CMD_SYS, 0x41, 0x7d, 0x00])
  slot = 'abcd'.find(slot.lower())
  if slot < 0:
    return -1
  g2usb.send_message([CMD_SYS, ion[3], 0x07, 0x08>>slot, 0x0f, 0x08>>slot])
  g2usb.send_message([CMD_SYS, ion[3], 0x09, slot])
  g2usb.send_message([CMD_A+slot, 0x0a, 0x70])
  return 0
add_command('slot', ['slot'], 'select slot (A,B,C,D)', cmd_slot)

def cmd_variation(command, variation):
  variation = int(variation)
  if variation < 1 or 8 < variation:
    return -1
  slota = g2usb.send_message([CMD_SYS, 0x41, 0x35, 0x00])
  g2usb.send_message([CMD_A, slota[5], 0x6a, variation-1])
  return 0
add_command('variation', ['variation'], 'select variation', cmd_variation)
 
def cmd_parameterpage(command, page):
  row = 'abcde'.find(page[0].lower())
  if row < 0:
    printf('Invalid row %s\n', page[0].lower())
    return -1
  col = int(page[1]) - 1
  if col < 0 or 2 < col:
    printf('Invalid col %d\n', col)
    return -1
  slota = g2usb.send_message([CMD_SYS, 0x41, 0x35, 0x00])
  g2usb.send_message([0x08, slota[6], 0x2d, (row*3)+col])
  return 0
add_command('parameterpage', ['page'], 'select parameterpage',
    cmd_parameterpage)

def cmd_rename(command, slot, name):
  slot = 'abcd'.find(slot.lower())
  if slot < 0:
    return -1
  if len(name) < 16:
    name = name + '\0'
  version = g2usb.send_message([CMD_SYS, 0x41, 0x35, slot])[5]
  cmd = [ CMD_A + slot, version, 0x27 ] + \
        list(bytearray(name))
  data = g2usb.send_message(cmd)
  return 0
add_command('rename', ['slot', 'name'], 'rename current slots name',
    cmd_rename)

def cmd_sleep(command, seconds):
  import time
  seconds = float(seconds)
  time.sleep(seconds)
add_command('sleep', ['seconds'], 'sleep for seconds', cmd_sleep)
if __name__ == '__main__':
  main(sys.argv)


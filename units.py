#!/usr/bin/env python

from Numeric import *

def ts(x,ty):
  return (1-exp(x*ty))/(1-exp(ty))

x = array(range(0,127,8)+[127],typecode=Float)

print 'Nord Modular G2 Units'
print
print 'ts(x,ty) = (1-exp(x*ty))/(1-exp(ty))'
print 'Lfo Rate Lo:', 
print 'y[0]+y[-1]*ts(x[i]/127.,7.337)'
ylo = array([1/62.9,1/39.6,1/25.0,1/15.7,0.10,0.16,0.25,0.40,
           0.64,1.02,1.62,2.56,4.07,6.46,10.3,16.3,24.4],typecode=Float)
y = ylo
for i in range(len(x)):
  cy = y[0]+y[-1]*ts(x[i]/127.,7.337) # 7.34
  cy = int(cy*100)/100.
  if y[i] < 10.0:
    print '%3d %4.2f %4.2f' % (x[i], y[i], cy)
  else:
    print '%3d %4.1f %4.1f' % (x[i], y[i], cy)

print
print 'Lfo Rate Hi',
print 'y[0]+y[-1]*ts(x[i]/127.,7.337)'
yhi = array([0.26,0.41,0.64,1.02,1.62,2.58,4.09,6.49,10.3,16.4,
           26.0,41.2,65.4,104,165,262,392],typecode=Float)
y = yhi
for i in range(len(x)):
  cy = y[0]+y[-1]*ts(x[i]/127.,7.337) # 7.34
  cy = int(cy*100)/100.
  if y[i] < 10.0:
    print '%3d %4.2f %4.2f %10.6f' % (x[i], y[i], cy, cy)
  elif y[i] < 100.0:
    print '%3d %4.1f %4.1f %10.6f' % (x[i], y[i], cy, cy)
  else:
    print '%3d %4.0f %4.0f %10.6f' % (x[i], y[i], cy, cy)

print
print 'BPM 20 to 240'
print
print 'Lfo Rate Sub',
print '1/(x[i]*(1/y[-1]-1/y[0])/127.+1/y[0])'
ysub = array([699,77.7,41.1,28.0,21.2,17.1,14.3,12.3,10.8,
           9.58, 8.63,7.85,7.21,6.66,6.19,5.78,5.46],typecode=Float)
y = ysub
iy = 1/y
for i in range(len(x)):
  cy = x[i]*(iy[-1]-iy[0])/127.+iy[0]
  cy = 1/cy
  #cy = int(cy*100+0.5)/100.
  if y[i] < 10.0:
    print '%3d %4.2f %4.2f %10.6f' % (x[i], y[i], cy, cy)
  elif y[i] < 100.0:
    print '%3d %4.1f %4.1f %10.6f' % (x[i], y[i], cy, cy)
  else:
    print '%3d %4.0f %4.0f %10.6f' % (x[i], y[i], cy, cy)

print
print 'Env ADSR Time'
ytim = array([0.0005,0.0021,0.0073,0.0212,0.0543,0.126,0.269,0.540,1.02,
              1.85,3.21,5.37,8.72,13.8,21.2,32.0,45.0],typecode=Float)
y = ytim
for i in range(len(x)):
  cy = y[0]+y[-1]*ts(x[i]/127.,7.337) # 7.34
  if y[i] < 1.0:
    cym = cy*1000.
    ym = y[i]*1000.
    print '%3d %4.2fm %4.2fm %10.6fm' % (x[i], ym, cym, cym)
  elif y[i] < 10.0:
    print '%3d %4.2fs %4.2fs %10.6fs' % (x[i], y[i], cy, cy)
  else:
    print '%3d %4.1fs %4.1fs %10.6fs' % (x[i], y[i], cy, cy)


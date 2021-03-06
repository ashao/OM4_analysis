#!/usr/bin/env python
import sys
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt

def kahan_sum(a, axis=0):
    s = np.zeros(a.shape[:axis] + a.shape[axis+1:])
    c = np.zeros(s.shape)
    a.set_fill_value(0)
    for i in range(a.shape[axis]):
        # http://stackoverflow.com/a/42817610/353337
        y = a[(slice(None),) * axis + (i,)] - c
        t = s + y
        c = (t - s) - y
        s = t.copy()
    return s

def main():
  u_var = sys.argv[1]
  v_var = sys.argv[2]
  prefix = sys.argv[3]
  native_file = prefix + '.nc'
  z_file = prefix + '_z.nc'
  tidx = -1
  u = nc.Dataset(native_file).variables[u_var][tidx,:,:,:]
  v = nc.Dataset(native_file).variables[v_var][tidx,:,:,:]

  u.set_fill_value(1.e20)
  v.set_fill_value(1.e20)
#  u.mask = np.ma.nomask
#  v.mask = np.ma.nomask

  u_z = nc.Dataset(z_file).variables[u_var][tidx,:,:,:]
  v_z = nc.Dataset(z_file).variables[v_var][tidx,:,:,:]

  u_z.set_fill_value(1.e20)
  v_z.set_fill_value(1.e20)
#  u_z.mask = np.ma.nomask
#  v_z.mask = np.ma.nomask

  sum_u = u.sum(axis=0)
  sum_v = v.sum(axis=0)
  sum_u_z = u_z.sum(axis=0)
  sum_v_z = v_z.sum(axis=0)

  diff_u = np.abs(sum_u - sum_u_z).squeeze()
  diff_v = np.abs(sum_v - sum_v_z).squeeze()
  u_maxidx = np.unravel_index(diff_u.argmax(),diff_u.shape)
  v_maxidx = np.unravel_index(diff_v.argmax(),diff_v.shape)


  np.set_printoptions(precision=15)
  print('Max abs. difference in %s: %e at %d, %d' % (u_var,diff_u[u_maxidx],u_maxidx[0],u_maxidx[1]))
  print('\tNative:   ',sum_u[u_maxidx])
  print('\tRemapped: ',sum_u_z[u_maxidx])
  print('Max abs. difference in',v_var,diff_v[v_maxidx])
  print('\tNative:   ',sum_v[v_maxidx])
  print('\tRemapped: ',sum_v_z[v_maxidx])
  print('RMS difference in:',u_var,np.sum(np.sqrt(np.square(sum_u-sum_u_z))))
  print('RMS difference in:',v_var,np.sum(np.sqrt(np.square(sum_v-sum_v_z))))
  print('Total %s global integral difference: %.15e' % (u_var,sum_u.sum()-sum_u_z.sum()))
  print('Total %s global integral difference: %.15e' % (v_var,sum_v.sum()-sum_v_z.sum()))

  plt.figure()
  plt.subplot(2,3,1)
  plt.pcolormesh(sum_u.squeeze())
  plt.colorbar()
  plt.title('Native %s' % u_var)
  plt.subplot(2,3,2)
  plt.pcolormesh(sum_u_z.squeeze())
  plt.colorbar()
  plt.title('Remapped %s' % u_var)
  plt.subplot(2,3,3)
  plt.pcolormesh(sum_u.squeeze() - sum_u_z.squeeze())
  plt.colorbar()
  plt.title('Native-remapped')
  plt.subplot(2,3,4)
  plt.pcolormesh(sum_v.squeeze())
  plt.colorbar()
  plt.title('Native %s' % v_var)
  plt.subplot(2,3,5)
  plt.pcolormesh(sum_v_z.squeeze())
  plt.colorbar()
  plt.title('Remapped %s' %v_var)
  plt.subplot(2,3,6)
  plt.pcolormesh(sum_v.squeeze() - sum_v_z.squeeze())
  plt.colorbar()
  plt.title('Native-remapped')

  plt.show()

if __name__ == "__main__":
   main()

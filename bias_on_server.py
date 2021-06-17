#%%
import seafileapi
import h5py
import io
import os
import datetime as dt
import numpy as np
import config

client = seafileapi.connect(config.host_sea, config.user_sea, config.passwd_sea)
repo = client.repos.get_repo('f615e913-98d3-4bb3-8248-3608b496b991')
dir_seaf = '/data/'
dir_swh = '/swh_11_8_ 2041_4320/'
dir_result = '/final_result/'
seafdir = repo.get_dir(dir_seaf)
lst = seafdir.ls(force_refresh=True)
seafdir_swh = repo.get_dir(dir_swh)
lst_swh = seafdir_swh.ls(force_refresh=True)
seafdir_res = repo.get_dir(dir_result)
lst_res = seafdir_res.ls(force_refresh=True)

file_names_v2 = [dirent.name for dirent in lst]
swh_files = [dirent.name for dirent in lst_swh]
res_files = [d.name for d in lst_res]

def is_file(name_s):
    try:
        repo.get_file(dir_swh + name_s)
        return True
    except:
        return False

n = np.zeros((10,1))
bias_arr = np.zeros((10, 2041, 4320))

#%%

for f in swh_files:
    if is_file(f):
        ftr = repo.get_file(dir_swh + f)
        fr = h5py.File(io.BytesIO(ftr.get_content()),'r')
        if '0' in fr.keys():
            keys = [i for i in fr.keys()]
            keys.remove('time')
            keys.remove('0')
            print(f, keys)
            swh_r = fr['0']
            for i in keys:
                swh_p = fr[i]
                for j in range(8):
                    bias_arr[int(i)-1,:,:] += (swh_p[j, :, :]) - abs(swh_r[j, :, :])
                    n[int(i)-1] += 1
        else:
            print(f)
print('end')
for i in range(10):
    bias_arr[i, :, :] = bias_arr[i, :, :]/(n[i]*100)
file_np_b = io.BytesIO()
np.save(file_np_b, bias_arr)
file_np_b.seek(0)
seafdir_res.upload(file_np_b, 'bias_array_v2_at_' + (dt.datetime.now()).strftime('%Y_%m_%d_%H_%M') + '.npy')
print(n)
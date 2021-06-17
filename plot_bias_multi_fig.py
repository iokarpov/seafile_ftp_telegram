import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib as mpl

from mpl_toolkits.basemap import Basemap
import numpy as np

file_bias = 'D:/data_copernicus/final_results/bias_array_v2_at_2021_04_29_00_00.npy'

latlon = np.load('D:/data_copernicus/final_results/latlon.npz')
lon, lat = np.meshgrid(latlon['lon'], latlon['lat'])
bias_arr = np.load(file_bias)
fig = plt.figure(figsize=(12, 6))

for j in range(4):
    por = 1.1
    i = j*3

    img = bias_arr[i, :, :]
    img[abs(img)>=por] = 0
    ax_1 = fig.add_subplot(2, 2, j+1)
    m = Basemap(projection='mill',lon_0=180)
    m.pcolormesh(lon, lat, img,
                latlon=True, cmap = plt.get_cmap('bwr'))
    plt.clim(-(por), por)
    m.drawcoastlines()
    m.fillcontinents(color='coral')

    if i == 1:
        s1 = 'день'
    elif i > 1 and i < 5:
        s1 = 'дня'
    else:
        s1 = 'дней'
    plt.title('Для прогноза за ' + str(i) + ' ' + s1)
    
    print('Для прогноза за ' + str(i) + ' ' + s1)

norm = mpl.colors.Normalize(vmin = -(por), vmax = por)
cmap = plt.get_cmap('bwr')
sm = cm.ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([]) 

fig.subplots_adjust(right=0.8)
cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
fig.colorbar(sm, cax=cbar_ax)
fig.suptitle('Средняя ошибка прогноза.')

plt.savefig('D:/doc/work/py/images/'+'bias_all_v3.png', dpi=600)
plt.close(fig)
#plt.show()

#%%
import os
import tifffile as tif
import glob
import numpy as np
import matplotlib.pyplot as plt


import caiman as cm


#%% Directory of the datasets
initial_dir = '/Users/burakgur/Desktop/multisensory_data'

#%% Location of the data to analyze
experiment_name = '230724cf_fly1'
t_series_name = 'TSeries-07242023-1320-001'
t_series_path = os.path.join(initial_dir, experiment_name,t_series_name)
t_series_files = t_series_path + '/' + '*000001.ome.tif'
# t_series_files = t_series_path + '/' + '*.tif'
start_image = (glob.glob(t_series_files))

#%% Load data and save as single tif stack since CaImAn requires a single stack
data = tif.imread(start_image)
print('Loaded data of shape: ', data.shape)

tif_stack_name = f'{t_series_name}-stack.tif'
tif_stack_path = os.path.join(t_series_path,tif_stack_name)
tif.imsave(tif_stack_path, data)
print(f'Video saved: {tif_stack_name}')

#%% Caiman load
single_movie = cm.load(tif_stack_path)
print(single_movie.shape)

#%% Caiman play the movie
single_movie.play(magnification = 2, fr=30, q_min=0.1, q_max=99.75)


#%% Caiman motion correction
from caiman.motion_correction import MotionCorrect

# Set some parameters for motion correction
max_shifts = (50, 50)  # maximum allowed rigid shift in pixels (view the movie to get a sense of motion)
strides =  (48, 48)  # create a new patch every x pixels for pw-rigid correction
overlaps = (24, 24)  # overlap between pathes (size of patch strides+overlaps)
max_deviation_rigid = 3   # maximum deviation allowed for patch with respect to rigid shifts
pw_rigid = False  # flag for performing rigid or piecewise rigid motion correction
shifts_opencv = True  # flag for correcting motion using bicubic interpolation (otherwise FFT interpolation is used)
border_nan = 'copy'  # replicate values along the boundary (if True, fill in with NaN)



# create a motion correction object
mc = MotionCorrect(tif_stack_path, dview=None, max_shifts=max_shifts,
                  strides=strides, overlaps=overlaps,
                  max_deviation_rigid=max_deviation_rigid, 
                  shifts_opencv=shifts_opencv, nonneg_movie=True,
                  border_nan=border_nan)

mc.motion_correct(save_movie=True)


#%% load motion corrected movie
m_rig = cm.load(mc.mmap_file)
bord_px_rig = np.ceil(np.max(mc.shifts_rig)).astype(int)
plt.figure(figsize = (20,10))
plt.imshow(mc.total_template_rig, cmap = 'gray')


# %% Save movie
tif_corrected_stack_name = f'{t_series_name}-motionCorrected-stack.tif'
tif_corrected_stack_path = os.path.join(t_series_path,tif_corrected_stack_name)
tif.imsave(tif_corrected_stack_path, m_rig)
print(f'Video saved: {tif_corrected_stack_path}')


#%% TODO: Copy files to a new folder

# Your task is to copy the relevant files:
# Motion corrected and original video
# XML file (both imaging xml file and voltage output xml file)
# Optional: also copy to BOT csv file
# TIP: Use the os package. Ask in google how to create folders copy folders etc. Or even ask ChatGPT (easiest version)



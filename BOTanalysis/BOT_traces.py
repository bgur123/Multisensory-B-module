import os
import pandas as pd
import xml.etree.ElementTree as ET 
import numpy as np
import matplotlib.pyplot as plt
import xmlUtilities
def getoptostim(xml, fps, frames):
    tree = ET.parse(xml)
    root = tree.getroot()   
    for waveform in root.findall('Waveform'):
        if waveform.find('Enabled').text == 'true':
            # print(waveform.find('Name').text)
            for detail in waveform.findall('WaveformComponent_PulseTrain'):
                count = detail.find('PulseCount').text
                width = int(detail.find('PulseWidth').text)/1000*fps
                spacing = int(detail.find('PulseSpacing').text)/1000*fps
                pot_on =detail.find('PulsePotentialStart').text
                pot_off =detail.find('RestPotential').text
                pot_delta =detail.find('PulsePotentialDelta').text
                first_delay = int(detail.find('FirstPulseDelay').text)/1000*fps
    delay = np.zeros(int(first_delay),)
    width = np.ones(int(width),)
    isi = np.zeros(int(spacing),)
    protocoll = np.hstack((delay, width, isi))
    for repeat in range(int(count)-1):
        protocoll = np.hstack((protocoll, width, isi))
    protocoll = protocoll[:len(frames)]
    return protocoll, count
def plot_ROI(df, roi_n, fontsize, count, plot_path):
    fig, axes = plt.subplots(nrows=1, ncols=int(count)-1, figsize=(15,8), dpi=400) 
    axes = axes.ravel()
    count = range(0, int(count)-1, 1)
    for ax, count in zip(axes,count):
        ax.plot(df.loc[:,f'rel_pulse{count}'], df.loc[:,f'dff{count}'], label='ΔF/F')
        ax.plot(df.loc[:,f'rel_pulse{count}'], df.loc[:,f'prot_pulse{count}'], label='red LED (500mV)')
        if count == 0:
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['left'].set_visible(True)
        else: 
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.set_yticks([])
    fig.suptitle(roi_n, fontsize=fontsize+2)
    fig.supxlabel('time [s]', fontsize= fontsize)
    fig.tight_layout()
    plt.savefig(f'{plot_path}/{roi_n}.png', dpi=400, bbox_inches='tight')
    plt.close()

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------
os.chdir('U:/Christian_Felix_multisensory/Tseries') #tseries folder 
fly = '230724cf_fly1' #fly folder name 
tseries = 'TSeries-07242023-1320-001' #recording 

csv_path = f"{fly}/{tseries}/{tseries}_Cycle00001-botData.csv"
voltage_path = f"{fly}/{tseries}/{tseries}_Cycle00001_VoltageOutput_001.xml"
metadata_path = f"{fly}/{tseries}/{tseries}.xml"
plot_path = f'U:/Christian_Felix_multisensory/Tseries/{fly}/{tseries}'
csv_BOT = pd.read_csv(csv_path) #pandas frame with timestamp rows, + each BOT ROI as collumns
layerposition = xmlUtilities.getLayerPosition(metadata_path) #(x,y,z), list with len 3
frameperiod = xmlUtilities.getFramePeriod(metadata_path) #float, timebetween frames
rel_time = xmlUtilities.getMicRelativeTime(metadata_path) #np array (1556,)
fps = len(rel_time)/(frameperiod*len(rel_time)) # float
x_size, y_size, pixelArea = xmlUtilities.getPixelSize(metadata_path) # area in mircon square, x and y in micron per pixel, all floats
roi_bg = csv_BOT.iloc[:,1:].max().idxmin()
csv_bg = csv_BOT.loc[:,roi_bg]
protocoll, count = getoptostim(voltage_path, fps, rel_time)
on_i, off_i=[],[]
stim_on_stamp = np.where(protocoll[:-1] != protocoll[1:])[0]
for i in range(0, len(stim_on_stamp)):
    if i % 2:
        off_i.append(stim_on_stamp[i])
    else :
        on_i.append(stim_on_stamp[i])
for roi in csv_BOT.iloc[:,1:].columns:
    if roi == roi_bg:
        continue
    csv_ROI = csv_BOT.loc[:,roi]
    start_stim = int(on_i[0]-(15*fps))
    end_stim = int(on_i[0]+(20*fps))
    counter = 0
    ROI_frame = pd.DataFrame({})
    for repeat in range(int(count)-1):
        pulse_base = np.mean(csv_ROI[start_stim:(on_i[counter]-1)])
        pulse = csv_ROI[start_stim:end_stim]
        rel_pulse = rel_time[start_stim:end_stim]
        prot_pulse = protocoll[start_stim:end_stim]
        k = np.subtract(pulse, np.mean(csv_bg))
        df = np.subtract(k, pulse_base)
        dff = np.divide(df, pulse_base)#*(-1)
        pulse_frame = pd.DataFrame({f'dff{counter}': dff, f'rel_pulse{counter}': rel_pulse, f'prot_pulse{counter}': prot_pulse})
        pulse_frame.dropna(inplace=True)
        pulse_frame.reset_index(drop=True, inplace=True)
        ROI_frame = pd.concat([ROI_frame, pulse_frame], axis=1)
        counter+=1
        start_stim = end_stim
        end_stim = end_stim + int(35*fps)
    plot_ROI(ROI_frame, roi, 16, count, plot_path)

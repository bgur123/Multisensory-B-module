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
    return protocoll
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------
os.chdir('U:/Christian_Felix_multisensory/Tseries')
fly = '230724cf_fly1'
tseries = 'TSeries-07242023-1320-001'
csv_path = f"{fly}/{tseries}/{tseries}_Cycle00001-botData.csv"
voltage_path = f"{fly}/{tseries}/{tseries}_Cycle00001_VoltageOutput_001.xml"
metadata_path = f"{fly}/{tseries}/{tseries}.xml"

csv_BOT = pd.read_csv(csv_path) #pandas frame with timestamp rows, + each BOT ROI as collumns
layerposition = xmlUtilities.getLayerPosition(metadata_path) #(x,y,z), list with len 3
frameperiod = xmlUtilities.getFramePeriod(metadata_path) #float, timebetween frames
rel_time = xmlUtilities.getMicRelativeTime(metadata_path) #np array (1556,)
fps = len(rel_time)/(frameperiod*len(rel_time)) # float
x_size, y_size, pixelArea = xmlUtilities.getPixelSize(metadata_path) # area in mircon square, x and y in micron per pixel, all floats
roi_bg = csv_BOT.iloc[:,1:].max().idxmin()
csv_bg = csv_BOT.loc[:,roi_bg]
protocoll = getoptostim(voltage_path, fps, rel_time)

for roi in csv_BOT.iloc[:,1:].columns:
    if roi == roi_bg:
        continue
    csv_ROI = csv_BOT.loc[:,roi]
    k = np.subtract(csv_ROI, csv_bg)
    baseline = np.mean(csv_ROI[1:int(10*fps)])
    m = np.subtract(k, baseline)
    procentual = np.divide(m, baseline)#*(-1)
    plt.plot(rel_time, procentual, label='ΔF/F')
    plt.plot(rel_time, protocoll, label='red LED (500mV)') 
    plt.xlabel('time [s]')
    plt.title(roi)
    plt.legend()
    plt.show()
    plt.close()
## Create a tmp file containing only the lines containing "Bilayer Surface Tension" and the corresponding values

import os
import glob
import matplotlib.pyplot as plt
import numpy as np
from itertools import cycle
# Change the default pyplot parameters to put a readable size of text
params = {'legend.fontsize': 'xx-large',
          'figure.figsize': (15, 5),
         'axes.labelsize': 'xx-large',
         'axes.titlesize':'xx-large',
         'xtick.labelsize':'xx-large',
         'ytick.labelsize':'xx-large'}
plt.rcParams.update(params)


labels = []
files = glob.glob('*/dmpcas.*')
tmp_files = []
for i in range(len(files)):
    labels.append(str(files[i].strip().split('/')[0:1]).strip().split('_')[1][:-2])
    tmp_files.append(str(str(files[i].split('/')[0]) + '/' + str(files[i].split('.')[-1]) + '.tmp'))
    if os.path.exists(tmp_files[i]):
        os.system(f'rm { tmp_files[i] }')
    os.system('grep -A 1 "Bilayer Surface Tension" {} > {}'.format(files[i], tmp_files[i]))

labelValue = {}
for i in range(len(files)):
    with open(tmp_files[i], 'rt') as rf:
        localLines = []
        for line in rf:
            line = (line.strip().split())[0]
            localLines.append(line)
        goodLines = []
        for ind in range(1,60,3):
            goodLines.append(float(localLines[ind]))
        labelValue[labels[i]] = goodLines
            
x_axis = list(range(1000, 21000, 1000))

# Changes the line type for each lines
lines = ["-","--","-.",":"]
linecycler = cycle(lines)

plt.figure(figsize=(12,8))
for label in labels:
    plt.plot(x_axis[5:-1], labelValue[label][5:-1], next(linecycler), linewidth=3)
plt.legend(labels)
plt.grid()
plt.xlabel('Time')
plt.ylabel('Bilayer Surface Tension')

plt.show()

plt.figure(figsize=(12,8))
plt.plot(x_axis[5:-1],labelValue['1.125'][5:-1], 'k', x_axis[5:-1], labelValue['1.25'][5:-1], 'r')
plt.grid()
plt.legend(['1.125','1.25'])
plt.xlabel('Time')
plt.ylabel('Bilayer Surface Tension')
plt.show()
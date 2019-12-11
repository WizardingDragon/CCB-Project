## Create a tmp file containing only the lines containing "Bilayer Surface Tension" and the corresponding values

import os
import glob
import matplotlib.pyplot as plt
import numpy as np

labels = []
files = []
folderList = glob.glob('*/')
for folder in folderList:
    os.system('grep -A 1 "Bilayer Surface Tension" {}dmpcas.lp6_eq > {}lipid6.tmp'.format(folder, folder))
    labels.append(str(folder)[7:-1])
    files.append('{}lipid6.tmp'.format(folder))
# rangge(2,60,3)

labelValue = {}
for i in range(len(labels)):
    with open(files[i], 'rt') as rf:
        localLines = []
        for line in rf:
            line = (line.strip().split())[0]
            localLines.append(line)
        goodLines = []
        for ind in range(1,60,3):
            goodLines.append(float(localLines[ind]))
        labelValue[labels[i]] = goodLines
            
x_axis = list(range(1000, 21000, 1000))

for label in labels:
    plt.plot(x_axis[5:-1], labelValue[label][5:-1])
plt.legend(labels)
plt.show()
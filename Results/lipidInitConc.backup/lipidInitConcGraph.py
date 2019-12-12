## Create a tmp file containing only the lines containing "Bilayer Surface Tension" and the corresponding values

import os
import glob
import matplotlib.pyplot as plt
import numpy as np
from itertools import cycle
impo

labels = []
files = glob.glob('*/dmpcas.*')
for file in files:
    labels.append(str(file.strip().split('.')[1])[2:-3])
    if os.path.exists(file):
        os.system('rm {}'.fomat{file})
    os.system('grep -A 1 "Bilayer Surface Tension" {} > {}.tmp'.format(file, file))
    #labels.append(str(file)[-7:-1])
    #files.append('{}.tmp'.format(file))
print(files)
print(labels)

#labelValue = {}
#for i in range(len(labels)):
    #with open(files[i], 'rt') as rf:
        #localLines = []
        #for line in rf:
            #line = (line.strip().split())
            #localLines.append(line)
        #goodLines = []
        #for ind in range(1,60,3):
            #goodLines.append(float(localLines[ind]))
        #labelValue[labels[i]] = goodLines
            
#x_axis = list(range(1000, 21000, 1000))

#from itertools import cycle
#lines = ["-","--","-.",":"]
#linecycler = cycle(lines)

#for label in labels:
    #plt.plot(x_axis[5:-1], labelValue[label][5:-1], next(linecycler))
#plt.legend(labels)
#plt.show()

#### import the simple module from the paraview
import glob
folderList = glob.glob('*/')
VtkArray = []
timeList = range(3000, 33000, 3000)
for folder in folderList:
    fileList = []
    for time in timeList:
        basePath = '/home/archangel/Documents/EPFL/Computational Cell Biology/Project/stabilizeLipid4/*/{}dmpccs.ms_sim.con.{}.vtk'.format(folder, time)
        fileList.append(basePath)
    VtkArray.append(fileList)


with open('openVtkFile.py', 'wt') as wf:
    introLine = '#### import the simple module from the paraview\nfrom paraview.simple import *\n\n#### disable automatic camera reset on \'Show\'\nparaview.simple._DisableFirstRenderCameraReset()\n\n'
    wf.write(introLine)
    
    
    for i in range(len(VtkArray)):
        newVtkReader = '# create a new \'Legacy VTK Reader\'\ndmpccsms_simcon_{} = LegacyVTKReader(FileNames={})'.format(i, VtkArray[i])
        wf.write(newVtkReader + '\n')
    concLine = '#### uncomment the following to render all views\n# RenderAllViews()\n# alternatively, if you want to write images, you can use SaveScreenshot(...).\n'
    wf.write(concLine)
        

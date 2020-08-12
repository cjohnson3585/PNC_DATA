#
#               PNC_DATA--> Point and Click for data points
#                          2017.05.18
#                          Version 3.0
#
#prints out the x and y data of a plot interactively. Use for creating bright star cats
#
#
#
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
import photutils
from photutils import *
import sys
import math

print('')
print ('*************************************************************************************')
print ('                                      PNC_DATA.py                                    ')
print ('                                                                                     ')
print ('         (an interactive point-and-click routine for creating lists of stars)        ')
print ('                           Takes 1 argument: a fits file.                            ')
print ('    calling sequence: python PNC_DATA.py <path to .fits file> <"'"X"'"> (optional)   ') 
print ('*************************************************************************************')
print ('')
print ('   Use: one finger click expands your FOV to zoom in on stars. A two finger click    ')
print ('   will write the coordinates of that star to the log file. When using a mouse, the  ')
print ('   right click writes star coordinates to the log file. You can change the name      ')
print ('   of the logfile, the science enxtension of your .fits file, and the color of your  ')
print ('   .fits file image. For the latter, refer to the variable color choices online for  ')
print ('   the variable cmap on line 45 of this script.                                      ')
print ('         (see https://matplotlib.org/examples/color/colormaps_reference.html)        ')
print ('   You can pass an X after the fits file and the extensions of your fits file will   ')
print ('   be displayed for information purposes. This is optional. Red circles are added    ')
print ('   around stars that are selected and written to the log file. Aperture Photometry   ')
print ('   is performed on stars along with error using the flux and astropy.Photutils.      ')
print ('')

#which extension is the Sci extension?
sciext = 0
xs = [];ys = []

#Input the .fits file from the command line -> python PNC_DATA.py <path to .fits file> <X>
fitsfile = sys.argv[1]

#print out header extension info if key is set to X
try:
    key = sys.argv[2]
except:
    key = 'none'

if key == 'X':
    print ('')
    hdulist = fits.open(fitsfile,ignore_missing_end=True)
    print ('')
    print (hdulist.info())
    print ('')
    sys.exit()

#spot check for the correct Sci Ext
try:
    scidata1 = fits.getdata(fitsfile,ext=sciext,ignore_missing_end=True)
    print ('')
except:
    print ('')
    print ('*ERROR! USE CORRECT SCIENCE EXTENSION*')
    print ('TRY "'"python PNC_DATA.py <.fits file> X"'" ON THE COMMAND LINE '\
        'FOR EXTENSION INFO.')
    print ('')
    sys.exit()


#Change logfile name here
logfile = 'bright.test'

#open the plotting figure
fig = plt.figure(figsize=(10,8))
plt.imshow(scidata1,aspect='equal',cmap='gray_r',alpha=0.99,origin='lower')
plt.xlabel('X (pixel space)')
plt.ylabel('Y (pixel space)')
plt.title('File name: '+fitsfile)
plt.colorbar()

#add in opening and printing to a logfile
lf = open(logfile,'w')
lf.write("##Bright star log file. Using fits file: "+fitsfile+" ## \n")
lf.write("##-------------------------------## \n")
lf.write("## Xcenter Ycenter Inst_Mag Error## \n")
lf.write("##-------------------------------## \n")
lf.close()

#function to do the aperture photometry and phot_err
def phot(xcoord,ycoord):
    ap_rad = 6.0
    position = [(xcoord,ycoord)]
    apertures = CircularAperture(position,r = ap_rad)
    phot_table = photutils.aperture_photometry(scidata1,apertures,method='center')
    flux = float(phot_table[0][3]);flux_err = float(math.sqrt(flux))
    mag = -2.5*math.log10(flux); mag_err = flux_err*2.5/(flux*2.302)
    lf = open(logfile,'a')
    lf.write(str("%.4f" % xcoord).rjust(10)+''+str("%.4f" % ycoord).rjust(10)+''\
        +str("%.4f" % mag).rjust(10)+''\
        +str("%.4f" % mag_err).rjust(10)+'\n')
    lf.close()
        
#PNC function. Drag your FOV with one finger, use two finger click on a star to write coords to the logfile.
def onclick(event):
    if event.button == 1: 
        print('Wrote xdata=%f, ydata=%f' %
              (event.xdata, event.ydata)+' to logfile: '+logfile)
        xs.append(float(event.xdata));ys.append(float(event.ydata))
        plt.plot(xs,ys,'ro',fillstyle='none',ms=6.0)
        fig.canvas.draw()
        phot(event.xdata,event.ydata)

        
fig.canvas.mpl_connect('button_press_event', onclick)

plt.show()

#just close the plotting window when you are done

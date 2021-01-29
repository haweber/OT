import numpy as np
import time
import sys
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.backends.backend_pdf as pltpdf
import csv
import math
sys.path.append('MPA_Test/myScripts/') #python 2.7 ?                                                                              
from mpa_configurations import * # python 2.7 ?                                                                                   
import os.path
import glob
import re
import ROOT

def loadSCurvesFromCSV(csvfilename):
    values = []
    with open(csvfilename, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[0] == '':
                continue
            pixedid = int(row[0])
            #valuedict[pixedid] = value                                                                                        
            #values.append(value)                                                                                              
            value = [float(i) for i in row]
            value.pop(0)
            values.append(value)
    return values

class mpa_cal_utility():
    def __init__(self):
        self.conf = mpa_configurations()

    def errorf(self,x, *p):
        a, mu, sigma, offset = p
        return 0.5*a*(1.0+erf((x-mu)/sigma)) + offset #XXX added offset
    def line(self,x, *p):
        g, offset = p
        return  np.array(x) *g + offset
    def gauss(self,x, *p):
        A, mu, sigma = p
        return A*np.exp(-(x-mu)**2/(2.*sigma**2))
    def errorfc(self,x, *p):
        a, mu, sigma, offset = p
        return a*0.5*erfc((x-mu)/sigma) + offset #XXX added offset

    def plot_scurve(self,row, col, s_type, scurve, start, stop, chip, filename="../Results_MPATesting/"):

        plt.clf()

        if len(scurve.shape)!=2:
            print("Expect a 2D scurve array")
            return
        else:
            if scurve.shape[0]<1888:
                print("Data array is too short, expected 1888 pixels, found "+str(scurve.shape[0]))
                return
            if scurve.shape[0]==1888:
                data = scurve
            else:
                data = np.zeros(self.conf.npixsnom, ydim, dtype = np.int )#ensuring correct length of data array
                for p in range(self.conf.npixsnom):
                    pixel = self.conf.getnompix(p)
                    for y in range(ydim):
                        data[pixel,y] = scurve[p,y]            
            
        for r in row:
            for c in col:
                pixel = self.conf.pixelidnom(r,c)
                plt.plot(scurve[pixel,0:(stop-start)],'-')

        print("Plotting")
        if s_type == "THR":
            plot_xlabel = "Threshold DAC value"
        if s_type == "CAL":
            plot_xlabel = "Calibration DAC value"
        plot_ylabel = "Counter Value ("+chip+")"
        plt.title("SCurves")
        plt.xlabel(plot_xlabel)
        plt.ylabel(plot_ylabel)

        fig1 = plt.gcf()
        fig1.show()
        fig1.savefig(filename+"_curves.png")
        
        return 0

def RefitSCurvesOneChip(cal, mapsa, chip):
    moduleid = "mpa_test_"+mapsa
    thepath = "../Results_MPATesting/"+mapsa+"/"
    teststring = moduleid + "_"+chip+"_"
    bbstring = "_BumpBonding_SCurve_BadBump"
    calstring = "_CAL_CAL"

    #    filelist = glob.glob(thepath+teststring+"*"+bbstring+".csv")
    filelist = glob.glob(thepath+teststring+"*"+bbstring+".csv")
    maxstr = "" #string with highest number
    maxnbr = 0
    if len(filelist) == 0:
        print("No S Curve found.")
        return False
    for f in filelist:
        numbers_from_string = filter(str.isdigit, f)
        if numbers_from_string > maxnbr:
            maxnbr = numbers_from_string
            maxstr = f
    #print(maxstr)
    #print(maxstr[0:-4])
    csvfilename = maxstr

    data_array = loadSCurvesFromCSV(csvfilename)
    extract_val = int(250. * 95./218.)
    #print(np.array(cal.conf.rowsnom))
    cal.plot_scurve(row = np.array(cal.conf.rowsnom), col = np.array(cal.conf.colsnom), s_type = "CAL", scurve = np.array(data_array), start = 0, stop = 256, chip = chip, filename="../Results_MPATesting/"+mapsa+"/"+chip)
    return 0

def main():
    if len(sys.argv)<2:
        print("Give at least one MaPSA name to allow plotting.")

    cal = mpa_cal_utility()
    for i in range(1,17):
        print("Chip "+str(i))
        RefitSCurvesOneChip(cal,sys.argv[1],"Chip"+str(i))

if __name__ == "__main__":
    main()

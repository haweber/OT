import numpy as np
import time
import sys
#import matplotlib
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.special import erfc
from scipy.special import erf
#import matplotlib.cm as cm
#import matplotlib.backends.backend_pdf as pltpdf
#import seaborn as sns
import csv
import math
#sys.path.append('myScripts/') #python 2.7 ?
#from mpa_configurations import * # python 2.7 ?
from mpa_configurations import *
import os.path
import glob
import re
import ROOT

def loadValuesFromCSV(csvfilename, skip_edges):
    #print(csvfilename)
    #valuedict = dict()
    values = []
    with open(csvfilename, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if row[0] == '':
                continue
            pixedid = int(row[0])
            value = float(row[1])
            #valuedict[pixedid] = value
            if not skip_edges:
                values.append(value)
#            elif pixedid < 118 or pixedid > 1770:
#                # top or bottom row
#                continue
            elif pixedid%118 == 0 or pixedid%118 == 117:
                # left or right column
                continue
            else:
                values.append(value)

    #return valuedict
    return values

def AnalyzeBBallchips(modulename, show_plot=True, save_plot=True):
    moduleid = "mpa_test_"+modulename
    thepath = "../Results_MPATesting/"+modulename+"/"
    if not os.path.isdir(thepath):
        print("The directory  "+thepath+"  does not exist - cannot plot module maps.")
        return
    chipnames  = ['','','','','','','','','','','','','','','','']
    for i in range(0,16):
        teststring = moduleid + "_Chip" + str(i+1)+"_"
        filelist = glob.glob(thepath+teststring+"*.csv")
        #filelist = glob.glob(thepath+teststring+"*_refitted.csv")
        maxstr = "" #string with highest number
        maxnbr = 0
        for f in filelist:
            numbers_from_string = filter(str.isdigit, f)
            if numbers_from_string > maxnbr:
                maxnbr = numbers_from_string
                maxstr = f
        #print(maxstr)

        reducedmaxstr = maxstr[maxstr.find('Chip'):-4]#ensure that I don't make a mistake given that AEMTec have one number, and HPK have 2 numbers
        #print(reducedmaxstr)
        numberlist = re.findall('\d+', reducedmaxstr )
        if len(numberlist)>=7:#1 chip + 6 date
            chipstring = "Chip"+numberlist[0]
            for j in range(1,7):
                chipstring += "_" + numberlist[j]
            #print(chipstring)
            chipnames[i] = chipstring
        else:
            print("Could not find any csv file for chip "+ str(i+1)+" for the module "+modulename)
            return
    #print(chipnames)
    for chipname in chipnames:
        AnalyzeBBonechip(inpath=thepath,mapsaname=modulename,chip=chipname)

def AnalyzeBBonechip(inpath,mapsaname,chip):

    skip_edges = True

    moduleid = "mpa_test_"+mapsaname
    thepath = "../Results_MPATesting/"+mapsaname+"/"
    if not os.path.isdir(thepath):
        print("The directory  "+thepath+"  does not exist - cannot plot module maps.")
        return

    bbnoisecsv_thr = thepath + moduleid + "_" + chip + "_PostTrim_THR_THR_Mean.csv"
    bbnoisecsv_cal = thepath + moduleid + "_" + chip + "_PostTrim_CAL_CAL_Mean.csv"
    bbnoisecsv_bum = thepath + moduleid + "_" + chip + "_BumpBonding_Noise_BadBump.csv"

    chipshortname = chip[chip.find('Chip'):-20]
    
    hist_thr = ROOT.TH1F("h_noise_thr_"+chipshortname, "", 2560, 0, 256)
    hist_cal = ROOT.TH1F("h_noise_cal_"+chipshortname, "", 2560, 0, 256)
    hist_bum = ROOT.TH1F("h_noise_bum_"+chipshortname, "", 2560, 0, 256)
    if(os.path.isfile(bbnoisecsv_thr)):
        bbnoise_thr = loadValuesFromCSV(bbnoisecsv_thr,skip_edges)
        for n in bbnoise_thr:
            if n < 0: hist_thr.Fill(0.0000001)
            elif n>255: hist_thr.Fill(254.9999999)
            else: hist_thr.Fill(n)
    if(os.path.isfile(bbnoisecsv_cal)):
        bbnoise_cal = loadValuesFromCSV(bbnoisecsv_cal,skip_edges)
        for n in bbnoise_cal:
            if n < 0: hist_cal.Fill(0.0000001)
            elif n>255: hist_cal.Fill(254.9999999)
            else: hist_cal.Fill(n)
    if(os.path.isfile(bbnoisecsv_bum)):
        bbnoise_bum = loadValuesFromCSV(bbnoisecsv_bum,skip_edges)
        for n in bbnoise_bum:
            if n < 0: hist_bum.Fill(0.0000001)
            elif n>255: hist_bum.Fill(254.9999999)
            else: hist_bum.Fill(n)

    outfile = ROOT.TFile("BBnoisefiles/" + "BBstudy_"+mapsaname+".root","update")
    outfile.cd()
    hist_thr.Write(hist_thr.GetName(),ROOT.TH1F.kOverwrite);
    hist_cal.Write(hist_cal.GetName(),ROOT.TH1F.kOverwrite);
    hist_bum.Write(hist_bum.GetName(),ROOT.TH1F.kOverwrite);
    outfile.Close()

def main():
    if len(sys.argv)<2:
        print("Give at least one MaPSA name to allow plotting.")
    for i in range(1,len(sys.argv)):
        AnalyzeBBallchips(sys.argv[i])

if __name__ == "__main__":
    main()


'''from the official repository, function to get spectrum from the source_name
   example: python read_source_stevecat.py "1E 0317.0+1835"
'''
from astropy.table import Table,vstack
from scipy import constants
import pandas as pd
import sys
# E = h nu, and we want E in eV
h_eV_Hz = constants.h / constants.value("electron volt-joule relationship") #h is 6.63e-34 J/Hz, and 1 eV = 1.60e-19 J
eV2erg = constants.value("electron volt-joule relationship")/constants.erg #constants.erg is one erg in joule
SteVeCATPath = "/home/utente/Lavoro/CTA/Catalogs/STeVeCat/STeVECat/"
ref_table = Table.read(SteVeCATPath+"/table_spectra.csv")
ref_table.add_index("source_name") #indexing table by fileID
def read_source(source_name):
    outputsed = Table()
    sourceinfo = ref_table.loc[source_name] #access all references for this source in the STeVECat
    for ifile in range(len(sourceinfo)):
        filename = "filename"
        sourceref = "sourcereference" #NOT STEVECAT REFERENCE, which is "arXiv:2304.00835". This is the reference for the source
        if (isinstance(sourceinfo,Table)):
         filename = f"./{sourceinfo[ifile]['reference']}/{sourceinfo[ifile]['file_id']}.ecsv"
         sourceref = sourceinfo[ifile]['reference']
        else:
         filename = f"./{sourceinfo['reference']}/{sourceinfo['file_id']}.ecsv"
         sourceref = sourceinfo['reference']
        spectrum = Table.read(SteVeCATPath+filename)
        metaspectrum = spectrum.meta
        spectrum["start time"] = metaspectrum['mjd_start']
        spectrum["end time"] = metaspectrum['mjd_stop']
        spectrum["Catalog"] = "STEVECAT"
        spectrum["Frequency"] = spectrum["e_ref"]*1e+12/h_eV_Hz #from energy in TeV to frequency in Hz
        spectrum["Frequency"].unit = "Hz"
        spectrum["Reference"] = sourceref
        spectrum["Flag"] = "Det" #assuming detection for all data, no upper limits
        spectrum["e2dnde"] = spectrum["e_ref"] * spectrum["e_ref"] * spectrum["dnde"] * 1e+12 * eV2erg
        spectrum["e2dnde"].unit = "erg/(cm2s)"
        spectrum["e2dnde_errp"] = spectrum["e_ref"] * spectrum["e_ref"] * spectrum["dnde_errp"] * 1e+12 * eV2erg #assuming e_ref to be with negligible error
        spectrum["e2dnde_errp"].unit = "erg/(cm2s)"
        spectrum["e2dnde_errn"] = spectrum["e_ref"] * spectrum["e_ref"] * spectrum["dnde_errn"] * 1e+12 * eV2erg #assuming e_ref to be with negligible error
        spectrum["e2dnde_errn"].unit = "erg/(cm2s)"
        outputsed = vstack([outputsed,spectrum],metadata_conflicts='silent')
        if (isinstance(sourceinfo,Table)==False):
           break
    #final processing
    outputsed = outputsed["Frequency","e2dnde","e2dnde_errp","start time","end time","Flag","Catalog","Reference"]
    return outputsed

try:
 dfsourceinfo = pd.read_csv(sys.argv[1])
 dfsed = read_source(dfsourceinfo.loc[0]["source_name"])
 dfsed = dfsed.to_pandas()
 dfsed.dropna(inplace=True) #removing UL for now, to be treated at a later time
 dfsed.to_csv(sys.stdout,index=False,header=None) #ready to be appended to the other csv file!
except FileNotFoundError:
 exit    
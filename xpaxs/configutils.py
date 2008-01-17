"""
"""

#---------------------------------------------------------------------------
# Stdlib imports
#---------------------------------------------------------------------------

import os
import shutil

#---------------------------------------------------------------------------
# Extlib imports
#---------------------------------------------------------------------------

from PyMca import ConfigDict

#---------------------------------------------------------------------------
# xpaxs imports
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
# Normal code begins
#---------------------------------------------------------------------------

# TODO: much of this needs to go elsewhere, like in spec or spectromicroscopy

def getUserConfigDir():
    '''return the path to the user's spectromicroscopy config directory'''
    configDir = os.path.join(os.path.expanduser('~'), '.spectromicroscopy')
    if not os.path.exists(configDir): os.mkdir(configDir)
    return configDir

def getDefaultConfigDir():
    '''return the path to the default spectromicroscopy config directory'''
    import spectromicroscopy as smp
    return os.path.join(os.path.split(smp.__file__)[0], 'smp-data')

def getSmpConfigFile():
    return os.path.join(getUserConfigDir(), 'smp.conf')

def getDefaultPymcaConfigFile():
    configFile = os.path.join(getUserConfigDir(), 'pymca.cfg')
    if not os.path.isfile(configFile):
        defaultConfigFile = os.path.join(getDefaultConfigDir(), 'pymca.cfg')
        shutil.copyfile(defaultConfigFile, configFile)
    return configFile

def getPymcaConfig(configFile=None):
    '''return a ConfigDict containing the pymca config data'''
    if not configFile: configFile = getDefaultPymcaConfigFile()
    return ConfigDict.ConfigDict(filelist=configFile)

def getSpecMacro(filename):
    if not os.path.isfile(filename):
        filename = os.path.join(getDefaultConfigDir(), filename)
    return open(filename).read()

def getSpecClientLogFile():
    return os.path.join(getUserConfigDir(), 'specclient.log')
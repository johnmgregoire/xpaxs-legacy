"""
"""

#---------------------------------------------------------------------------
# Stdlib imports
#---------------------------------------------------------------------------

import os
import sys

#---------------------------------------------------------------------------
# Extlib imports
#---------------------------------------------------------------------------

from PyQt4 import QtCore

#---------------------------------------------------------------------------
# SMP imports
#---------------------------------------------------------------------------

from spectromicroscopy.external.SpecClient import SpecMotor

#---------------------------------------------------------------------------
# Normal code begins
#---------------------------------------------------------------------------

DEBUG = 1

# TODO: This needs to emit signals that we can use to change state of motor 
# widgets
class QtSpecMotorA(SpecMotor.SpecMotorA, QtCore.QObject):
    
    __state_strings__ = ['NOTINITIALIZED',
                         'UNUSABLE',
                         'READY',
                         'MOVESTARTED',
                         'MOVING',
                         'ONLIMIT']
    
    def __init__(self, specName=None, specVersion=None):
        QtCore.QObject.__init__(self)
        SpecMotor.SpecMotorA.__init__(self, specName, specVersion)
        self.getPosition()

    def connected(self):
        self.__connected__ = True
        if DEBUG: print'Motor %s connected'%self.specName
    
    def disconnected(self):
        self.__connected__ = False
        if DEBUG: print 'Motor %s disconnected'%self.specName

    def isConnected(self):
        if DEBUG: return (self.__connected__ != None) and (self.__connected__)

    def motorLimitsChanged(self):
        limits = self.getLimits()
        self.emit(QtCore.SIGNAL("motorLimitsChanged(PyQt_PyObject)"),
                  limits)
        if DEBUG:
            limitString = "(" + str(limits[0])+", "+ str(limits[1]) + ")"
            print "Motor %s limits changed to %s"%(self.specName,limitString)
    
    def motorPositionChanged(self, absolutePosition):
        self.emit(QtCore.SIGNAL("motorPositionChanged(PyQt_PyObject)"),
                  absolutePosition)
        if DEBUG: print "Motor %s position changed to %s"%(self.specName,
                                                           absolutePosition)
    
    def syncQuestionAnswer(self, specSteps, controllerSteps):
        if DEBUG: print "Motor %s syncing"%self.specName
    
    def motorStateChanged(self, state):
        state = self.__state_strings__[state]
        self.emit(QtCore.SIGNAL("motorStateChanged(PyQt_PyObject)"),
                  state)
        if DEBUG: print "Motor %s state changed to %s"%(self.specName, state)
    
    def getState(self):
        state = SpecMotor.SpecMotorA.getState()
        return self.__state_strings__[state]
    
    def motor_name(self):
        if DEBUG: return self.specName
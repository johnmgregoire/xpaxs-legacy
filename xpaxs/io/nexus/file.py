"""
Wrappers around the pytables interface to the hdf5 file.

"""

#---------------------------------------------------------------------------
# Stdlib imports
#---------------------------------------------------------------------------

import sys
import time

#---------------------------------------------------------------------------
# Extlib imports
#---------------------------------------------------------------------------

from PyQt4 import QtCore
import tables

#---------------------------------------------------------------------------
# xpaxs imports
#---------------------------------------------------------------------------

from xpaxs.io.nexus.attrs import NXattrs

#---------------------------------------------------------------------------
# Normal code begins
#---------------------------------------------------------------------------


def get_local_time():
    # TODO: format according to nexus
    return time.localtime()


class NXfile(QtCore.QObject):

    """
    """

    _readonly = ()

    def __init__(self, file_name, mode='r+', parent=None):
        super(NXFile, self).__init__(parent)

        self.__mutex = QtCore.QMutex()

        self.__attrs = NXattrs(self)

        try:
            self.__h5file = tables.openFile(file_name, mode)
            self.__h5Node = self.__h5File.root
        except IOError, err:
            if mode == 'r+':
                self.__h5file = tables.openFile(file_name, 'w')
                self.__h5Node = self.__h5File.root
            else:
                raise err
            now = get_local_time
            self.attrs.file_name = file_name
            self.attrs.file_time = now
            self.attrs.file_update_time = now
            self.attrs.creator = sys.argv[0]
            self.attrs.NeXus_version = ''

    def __getattr__(self, name):
        try:
            self.mutex.lock()
            return self.__h5Node._v_children[name]
        finally:
            self.mutex.unlock()

    def __iter__(self):
        try:
            self.mutex.lock()
            return self.__h5File.walkNodes('/')
        finally:
            self.mutex.unlock()

    def create_array(self, where, name):
        try:
            self.mutex.lock()
            self.__h5File.createArray(where, name)
        finally:
            self.mutex.unlock()

    def create_carray(self, where, name):
        try:
            self.mutex.lock()
            self.__h5File.createCArray(where, name)
        finally:
            self.mutex.unlock()

    def create_earray(self, where, name):
        try:
            self.mutex.lock()
            self.__h5File.createEArray(where, name)
        finally:
            self.mutex.unlock()

    def create_entry(self, where, name):
        try:
            self.mutex.lock()
            self.__h5File.createGroup(where, name)
        finally:
            self.mutex.unlock()

    def close(self):
        try:
            self.mutex.lock()
            self.__h5File.close()
        finally:
            self.mutex.unlock()

    def flush(self):
        try:
            self.mutex.lock()
            self.__h5File.flush()
        finally:
            self.mutex.unlock()

        self.file_update_time = get_local_time()

    mutex = property(lambda self: self.__mutex)

    nxFile = property(lambda self: self)

    path = property(lambda self: '/')
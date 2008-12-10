"""
Wrappers around the pytables interface to the hdf5 file.

"""

from __future__ import absolute_import

#---------------------------------------------------------------------------
# Stdlib imports
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
# Extlib imports
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
# xpaxs imports
#---------------------------------------------------------------------------

from .group import NXgroup
from .registry import registry

#---------------------------------------------------------------------------
# Normal code begins
#---------------------------------------------------------------------------


class NXdata(NXgroup):

    """
    """

registry['NXdata'] = NXdata


class NXevent_data(NXgroup):

    """
    """

registry['NXevent_data'] = NXevent_data


class NXmonitor(NXgroup):

    """
    """

registry['NXmonitor'] = NXmonitor

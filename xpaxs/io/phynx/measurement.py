"""
"""

from __future__ import absolute_import, with_statement

#---------------------------------------------------------------------------
# Stdlib imports
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
# Extlib imports
#---------------------------------------------------------------------------



#---------------------------------------------------------------------------
# xpaxs imports
#---------------------------------------------------------------------------

from .group import Group
from .registry import registry

#---------------------------------------------------------------------------
# Normal code begins
#---------------------------------------------------------------------------


class Measurement(Group):

    """
    A group to contain all the information reported by the measurement. This
    group provides a link between standard tabular data formats (like spec)
    and the emerging hierarchical NeXus format.
    """

    @property
    def version(self):
        # TODO: use attrs.get() with h5py-1.1
        if 'version' in self.attrs:
            return self.attrs['version']
        else:
            return 0

registry.register(Measurement)


class ScalarData(Group):

    """
    A group containing all the scanned scalar data in the measurement,
    including:

    * positions of motors or other axes
    * counters
    * timers
    * single channel analyzers
    * etc.

    """

registry.register(ScalarData)


class Positioners(Group):

    """
    A group containing the reference positions of the various axes in the
    measurement.
    """

registry.register(Positioners)
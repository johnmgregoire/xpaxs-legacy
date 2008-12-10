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


class NXgeometry(NXgroup):

    """
    """

    def create_translation(self, name, **data):
        return NXtranslation(self, name, **data)

    def require_translation(self, name, **data):
        if not name in self:
            return self.create_translation(name, **data)
        else:
            item = self[name]
            if not isinstance(item, NXtranslation):
                raise NameError(
                    "Incompatible object (%s) already exists" % \
                    item.__class__.__name__
                )
            if data:
                raise RuntimeError(
                    "Can not define data for existing %s object" % \
                    item.__class__.__name__
                )
            return item

    def create_shape(self, name, **data):
        return NXshape(self, name, **data)

    def require_shape(self, name, **data):
        if not name in self:
            return self.create_shape(name, **data)
        else:
            item = self[name]
            if not isinstance(item, NXshape):
                raise NameError(
                    "Incompatible object (%s) already exists" % \
                    item.__class__.__name__
                )
            if data:
                raise RuntimeError(
                    "Can not define data for existing %s object" % \
                    item.__class__.__name__
                )
            return item

    def create_orientation(self, name, **data):
        return NXorientation(self, name, **data)

    def require_orientation(self, name, **data):
        if not name in self:
            return self.create_orientation(name, **data)
        else:
            item = self[name]
            if not isinstance(item, NXorientation):
                raise NameError(
                    "Incompatible object (%s) already exists" % \
                    item.__class__.__name__
                )
            if data:
                raise RuntimeError(
                    "Can not define data for existing %s object" % \
                    item.__class__.__name__
                )
            return item

registry['NXgeometry'] = NXgeometry


class NXtranslation(NXgroup):

    """
    """

registry['NXtranslation'] = NXtranslation


class NXshape(NXgroup):

    """
    """

registry['NXshape'] = NXshape


class NXorientation(NXgroup):

    """
    """

registry['NXorientation'] = NXorientation

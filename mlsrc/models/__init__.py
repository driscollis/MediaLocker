# -*- coding: utf-8 -*-#
#!/usr/bin/env python
"""SQLAlchemy model for the application"""

import sys
if not hasattr(sys, 'frozen'):
    # needed when having multiple versions of SA installed
    import pkg_resources
    pkg_resources.require("sqlalchemy>=0.6") # get latest version

import sqlalchemy as sa
import sqlalchemy.orm as sao
import sqlalchemy.ext.declarative as sad
from sqlalchemy.ext.hybrid import hybrid_property

maker = sao.sessionmaker(autoflush=True, autocommit=False)
DBSession = sao.scoped_session(maker)

class Base(object):
    """Extend the base class

    - Provides a nicer representation when a class instance is printed.
        Found on the SA wiki, not included with TG
    """
    def __repr__(self):
        return "%s(%s)" % (
                 (self.__class__.__name__),
                 ', '.join(["%s=%r" % (key, getattr(self, key))
                            for key in sorted(self.__dict__.keys())
                            if not key.startswith('_')]))

DeclarativeBase = sad.declarative_base(cls=Base)
metadata = DeclarativeBase.metadata

def init_model(engine):
    """Call me before using any of the tables or classes in the model."""
    DBSession.configure(bind=engine)

# you could have your models defined within this module, for larger applications
# it is probably nicer to work with to have them in separate modules and
# import them as shown below.
#
# remember to define __ALL__ in each module

# Import your model modules here.
from mlsrc.models.m_profiles import *
from mlsrc.models.m_book import *
from mlsrc.models.m_olvlist import *

# -*- coding: utf-8 -*-#
#!/usr/bin/env python

"""Profile type models are in here"""

import sys

if not hasattr(sys, 'frozen'):
    import pkg_resources
    pkg_resources.require("sqlalchemy") # get latest version

import sqlalchemy as sa
import sqlalchemy.orm as sao
import sqlalchemy.sql as sasql
import sqlalchemy.ext.declarative as sad
from sqlalchemy.ext.hybrid import hybrid_property

from mlsrc.models import DeclarativeBase, metadata, Base

__all__ = ['Person', 'Publisher']


########################################################################
class Person(DeclarativeBase):
    """"""
    __tablename__ = "person"

    id = sa.Column(sa.Integer, primary_key=True)
    first_name = sa.Column(sa.Unicode(25), index=True)
    last_name = sa.Column(sa.Unicode(25), index=True)

    @hybrid_property
    def full_name(self):
        """Either of them can be Null, need to account for that"""
        fn = u''
        ln = u''
        if self.first_name:
            fn = self.first_name
        if self.last_name:
            ln = self.last_name
        return (fn + u" " + ln)


########################################################################
class Publisher(DeclarativeBase):
    """"""
    __tablename__ = "publisher"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.Unicode(50), index=True)

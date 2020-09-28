# -*- coding: utf-8 -*-#
#!/usr/bin/env python

"""Olvlist model"""

import sys

if not hasattr(sys, 'frozen'):
    import pkg_resources
    pkg_resources.require("sqlalchemy") # get latest version

import sqlalchemy as sa
import sqlalchemy.orm as sao
import sqlalchemy.sql as sasql
import sqlalchemy.ext.declarative as sad

from mlsrc.models import DeclarativeBase, metadata, Base

__all__ = ['Olvlist']

class Olvlist(DeclarativeBase):
    __tablename__ = u'olvlist'

    id = sa.Column(sa.Integer, primary_key=True)
    tablename = sa.Column(sa.Unicode(length=50), index=True)
    colname = sa.Column(sa.Unicode(length=50))
    colno = sa.Column(sa.Integer())
    colshow = sa.Column(sa.BOOLEAN, default=True)
    colgroup = sa.Column(sa.BOOLEAN, default=False)
    align = sa.Column(sa.Unicode(length=6), default=u'left')
    width = sa.Column(sa.Integer(), default=20)
    minwidth = sa.Column(sa.Integer(), default=-1)
    isfilling = sa.Column(sa.BOOLEAN, default=False)
    valuecol = sa.Column(sa.Unicode(length=50), default=None)
    valuerel = sa.Column(sa.Unicode(length=50), default=None)
    groupkeyg = sa.Column(sa.Unicode(length=50), default=None)
    imageg = sa.Column(sa.Unicode(length=50), default=None)
    checkstatrel = sa.Column(sa.Unicode(length=50), default=None)
    checkstatcol = sa.Column(sa.Unicode(length=50), default=None)
    stringconv = sa.Column(sa.Unicode(length=50), default=None)



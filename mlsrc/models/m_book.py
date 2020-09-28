# -*- coding: utf-8 -*-#
#!/usr/bin/env python

"""Book model is"""

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

__all__ = ['Book']


########################################################################
class Book(DeclarativeBase):
    """"""
    __tablename__ = "book"

    id = sa.Column(sa.Integer, primary_key=True)
    author_id = sa.Column(sa.Integer, sa.ForeignKey("person.id"))
    publisher_id = sa.Column(sa.Integer, sa.ForeignKey("publisher.id"))
    title = sa.Column(sa.Unicode(50))
    isbn = sa.Column(sa.Unicode(16))
    person = sao.relationship("Person", backref="books",
                              cascade_backrefs=False)
    publisher = sao.relationship("Publisher", backref="books",
                                 cascade_backrefs=False)

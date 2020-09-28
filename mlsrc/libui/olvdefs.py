# -*- coding: utf-8 -*-#
#!/usr/bin/env python
"""A method per table for some definitions for the OLV listctrls

the def name should match the model name"""

# just to prevent exception, needs to be changed for true I18N
import wx
_ = wx.GetTranslation


def Book():
    """Column descriptions, list heading and klass name for the table"""
    coldesc = {'publisher': _("Publisher"),
               'title': _("Title"),
               'author': _("Author"),
               'isbn': _("ISBN"),}
    heading = _("Books")
    klass = 'Book'

    return heading, coldesc, klass

def Person():
    """Column descriptions, list heading and klass name for the table"""
    coldesc = {'first_name': _("First name"),
               'last_name': _("Last name")}
    heading = _("Authors")
    klass = 'Person'

    return heading, coldesc, klass

def Publisher():
    """Column descriptions, list heading and klass name for the table"""
    coldesc = {'name': _("Name"),}
    heading = _("Publishers")
    klass = 'Publisher'

    return heading, coldesc, klass

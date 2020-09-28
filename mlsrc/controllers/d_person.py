# -*- coding: utf-8 -*-#
#!/usr/bin/env python
"""The person controller"""
import logging

import wx

from base_addedit import BaseAE
import validators as validators

import mlsrc.libui.textctrl as tcs

import mlsrc.models as db

from mlsrc.app_constants import *

# needs to be changed to fully support i18n
_ = wx.GetTranslation

########################################################################
class Person(BaseAE):
    def __init__(self, parent, row=None, title="Add", addModus=True, **kwds):
        """Constructor

        :param parent: caller
        :param row: a sa db instance or None to default add
        :param title: the title for the dialog
        :param addRecord: True = add, False = edit
        """
        self.view = wx.Dialog(parent, wx.ID_ANY,
              style=wx.DEFAULT_DIALOG_STYLE,
              title="%s Record" % title)
        self.view.SetName("dlgPerson")
        super(Person, self).__init__(parent, view=self.view, model="Person",
                                     row=None, title="Add", addModus=True,
                                     **kwds)

        self.baseTitle = "Person"
        self.modusTitle = title

        self._AddModus = addModus
        self.dbItem = row

        # create some widgets
        lbl = wx.StaticText(self.view, label="%s Record" % title)
        lbl.SetFont(wx.Font(dlgFontHeader, dlgFontFam, wx.NORMAL, wx.BOLD))
        self.dlgSizer.Add(lbl, 0, wx.CENTER)

        stFont = wx.Font(dlgFontSt, dlgFontFam, wx.NORMAL, wx.BOLD)

        firstLbl = wx.StaticText(self.view, label="First name:")#, size=size)
        firstLbl.SetFont(stFont)
        self.firstTxt = tcs.TextCtrl(self.view)
        self.firstTxt.dbParent = self
        self.firstTxt.dbColName = "first_name"
        self.firstTxt.dbRelName = None
        self.firstTxt.dbItemName = "dbItem"
        self.firstTxt.SetValidator(validators.ValTC())
        self.rowBuilder([firstLbl, self.firstTxt])

        lastLbl = wx.StaticText(self.view, label="Last name:")#, size=size)
        lastLbl.SetFont(stFont)
        self.lastTxt = tcs.TextCtrl(self.view)
        self.lastTxt.dbParent = self
        self.lastTxt.dbColName = "last_name"
        self.lastTxt.dbRelName = None
        self.lastTxt.dbItemName = "dbItem"
        self.lastTxt.SetValidator(validators.ValTC())
        self.rowBuilder([lastLbl, self.lastTxt])

        self.focusCtrl = self.firstTxt
        self.initDlgBase()

#----------------------------------------------------------------------
if __name__ == '__main__':
    import mlsrc.base_app as base_app

    app = base_app.BaseApp(redirect=False)

    dlg = Person(None).view
    try:
        dlg.ShowModal()
    finally:

        dlg.Destroy()
    app.MainLoop()
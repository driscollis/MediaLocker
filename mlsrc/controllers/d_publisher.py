# -*- coding: utf-8 -*-#
#!/usr/bin/env python
"""The publisher controller"""
import logging

import wx

from base_addedit import BaseAE
import validators as validators

import mlsrc.libui.textctrl as tcs

from mlsrc.app_constants import *

# needs to be changed to fully support i18n
_ = wx.GetTranslation

########################################################################
class Publisher(BaseAE):
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
        self.view.SetName("dlgPublisher")
        super(Publisher, self).__init__(parent, view=self.view,
                                        model="Publisher",
                                        row=None, title="Add",
                                        addModus=True, **kwds)

        self.baseTitle = "Publisher"
        self.modusTitle = title
        
        self._AddModus = addModus
        self.dbItem = row

        # create some widgets
        lbl = wx.StaticText(self.view, label="%s Record" % title)
        lbl.SetFont(wx.Font(dlgFontHeader, dlgFontFam, wx.NORMAL, wx.BOLD))
        self.dlgSizer.Add(lbl, 0, wx.CENTER)

        stFont = wx.Font(dlgFontSt, dlgFontFam, wx.NORMAL, wx.BOLD)

        nameLbl = wx.StaticText(self.view, label="Name:")
        nameLbl.SetFont(stFont)
        self.nameTxt = tcs.TextCtrl(self.view)
        self.nameTxt.dbParent = self
        self.nameTxt.dbColName = "name"
        self.nameTxt.dbRelName = None
        self.nameTxt.dbItemName = "dbItem"
        self.nameTxt.SetValidator(validators.ValTC())
        self.rowBuilder([nameLbl, self.nameTxt])

        self.focusCtrl = self.nameTxt
        self.initDlgBase()

#----------------------------------------------------------------------
if __name__ == '__main__':
    import mlsrc.base_app as base_app

    app = base_app.BaseApp(redirect=False)

    dlg = Publisher(None).view
    try:
        dlg.ShowModal()
    finally:

        dlg.Destroy()
    app.MainLoop()
# -*- coding: utf-8 -*-#
#!/usr/bin/env python
"""The book controller"""
import logging

import wx

from base_addedit import BaseAE
import validators as validators

import mlsrc.libui.uiutils as uiutils
import mlsrc.libui.textctrl as tcs

import d_person as dlgPerson
import d_publisher as dlgPublisher

from mlsrc.app_constants import *

import mlsrc.models as db

# needs to be changed to fully support i18n
_ = wx.GetTranslation


########################################################################
class Book(BaseAE):
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
        self.view.SetName("dlgBook")
        super(Book, self).__init__(parent, view=self.view, model="Book",
                                     row=None, title="Add", addModus=True,
                                     **kwds)

        self.baseTitle = "Book"
        self.modusTitle = title

        self._AddModus = addModus
        self.dbItem = row

        # create some widgets
        lbl = wx.StaticText(self.view, label="%s Record" % title)
        lbl.SetFont(wx.Font(dlgFontHeader, dlgFontFam, wx.NORMAL, wx.BOLD))
        self.dlgSizer.Add(lbl, 0, wx.CENTER)

        stFont = wx.Font(dlgFontSt, dlgFontFam, wx.NORMAL, wx.BOLD)

        titleLbl = wx.StaticText(self.view, label="Title:")
        titleLbl.SetFont(stFont)
        self.titleTxt = tcs.TextCtrl(self.view)
        self.titleTxt.dbParent = self
        self.titleTxt.dbColName = "title"
        self.titleTxt.dbRelName = None
        self.titleTxt.dbItemName = "dbItem"
        self.titleTxt.SetValidator(validators.ValTC())
        self.rowBuilder([titleLbl, self.titleTxt])

        authorLbl = wx.StaticText(self.view, label="Author:")
        authorLbl.SetFont(stFont)

        ctrls = [{'cType': 'sc', 'desc': _(u"Author"),
                        'dbColName': 'full_name',
                        'dbRelName': 'person',
                        'dbLength': 50,
                        'dbItemName': 'dbItem',
                        'cName': 'eAuthorName',
                        'sTableName': 'Person',
                        'sFkColName': 'author_id',
                        'sRelName': 'person',
                        'sMaintDlg': dlgPerson.Person,
                        'emptyInvalid': True,
                        'formatcodes': "_S>",},
                ]
        ctrlsU = uiutils.defaultCtrlDict(ctrls)
        ctrl = ctrlsU[0]
        self.authorSc = uiutils.doCreateSearchControl(self, self.view, ctrl)
        self.authorSc.Enable(True)
        self.rowBuilder([authorLbl, self.authorSc])

        isbnLbl = wx.StaticText(self.view, label="ISBN:")
        isbnLbl.SetFont(stFont)
        self.isbnTxt = tcs.TextCtrl(self.view)
        self.isbnTxt.dbParent = self
        self.isbnTxt.dbColName = "isbn"
        self.isbnTxt.dbRelName = None
        self.isbnTxt.dbItemName = "dbItem"
        self.isbnTxt.SetValidator(validators.ValTC())
        self.rowBuilder([isbnLbl, self.isbnTxt])

        publisherLbl = wx.StaticText(self.view, label="Publisher:")
        publisherLbl.SetFont(stFont)
        ctrls = [{'cType': 'sc', 'desc': _(u"Publisher"),
                        'dbColName': 'name',
                        'dbRelName': 'publisher',
                        'dbLength': 50,
                        'dbItemName': 'dbItem',
                        'cName': 'ePublisherName',
                        'sTableName': 'Publisher',
                        'sFkColName': 'publisher_id',
                        'sRelName': 'publisher',
                        'sMaintDlg': dlgPublisher.Publisher,
                        'emptyInvalid': True,
                        'formatcodes': "_S>",},
                ]
        ctrlsU = uiutils.defaultCtrlDict(ctrls)
        ctrl = ctrlsU[0]
        self.publisherSc = uiutils.doCreateSearchControl(self, self.view, ctrl)
        self.publisherSc.Enable(True)
        self.rowBuilder([publisherLbl, self.publisherSc])

        self.focusCtrl = self.titleTxt
        self.initDlgBase()

#----------------------------------------------------------------------
if __name__ == '__main__':
    import mlsrc.base_app as base_app

    app = base_app.BaseApp(redirect=False)

    dlg = Book(None).view
    try:
        dlg.ShowModal()
    finally:

        dlg.Destroy()
    app.MainLoop()
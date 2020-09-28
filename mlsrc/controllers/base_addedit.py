# -*- coding: utf-8 -*-#
#!/usr/bin/env python
"""A base controller with add/modify buttons,
e.g. for dialogs, see e.g. d_book

"""
import logging

import wx

import base as cBase
import validators as validators

import mlsrc.libui.uiutils as uiutils
import mlsrc.libui.textctrl as tcs
import mlsrc.libui.commonDlgs as commonDlgs

import mlsrc.models as db

from mlsrc.mypub import pub, pTopics

# needs to be changed to fully support i18n
_ = wx.GetTranslation

########################################################################
class BaseAE(cBase.BaseController):
    def __init__(self, parent, view=None, model=None,
                 row=None, title="Add", addModus=True, **kwds):
        """Constructor

        :param parent: caller
        :param view: the view
        :param model: the model name
        :param row: a sa db instance or None to default add
        :param title: the title for the dialog
        :param addRecord: True = add, False = edit
        """
        super(BaseAE, self).__init__(view=view, model=model, **kwds)

        self.baseTitle = "Base"
        self.modusTitle = title
        self.dbItem = row
        self._AddModus = addModus
        self.focusCtrl = None

        # create the sizers
        self.dlgSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer = wx.FlexGridSizer(cols=2)

    def initDlgBase(self):
        """Add common buttons and layout"""
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)

        okBtn = wx.Button(self.view, label="%s - %s" % (self.modusTitle,
                                                        self.baseTitle))
        okBtn.Bind(wx.EVT_BUTTON, self.onRecord)
        btnSizer.Add(okBtn, 0, wx.ALL, 5)
        cancelBtn = wx.Button(self.view, label="Close")
        cancelBtn.Bind(wx.EVT_BUTTON, self.onCloseButton)
        btnSizer.Add(cancelBtn, 0, wx.ALL, 5)

        self.dlgSizer.Add(self.mainSizer, 0, wx.CENTER)
        self.dlgSizer.Add(btnSizer, 0, wx.CENTER)
        self.view.SetSizer(self.dlgSizer)
        self.view.Fit()

    #----------------------------------------------------------------------
    def onAdd(self):
        """
        Add the record to the database
        """
        self.createNewDbItem()
        self.view.TransferDataFromWindow()
        if not self.validateControls():
            return False
        self.addRecord(self.dbItem)
        logging.debug(self)
        pub.sendMessage(pTopics.data.itemAdded, dbparent=self,
                                                dbitem=self.dbItem)
        # reset db item and clear controls
        self.dbItem = None
        self.view.TransferDataToWindow()

    #----------------------------------------------------------------------
    def onEdit(self):
        """
        Updated the modified record in the database
        """
        self.view.TransferDataFromWindow()
        if not self.validateControls():
            return False
        logging.debug(self.dbItem)
        pub.sendMessage(pTopics.data.itemModified, dbparent=self,
                                                   dbitem=self.dbItem)
        self.editRecord()
        self.view.Close()

    #----------------------------------------------------------------------
    def createNewDbItem(self):
        """
        Create a new empty dbItem
        """
        self.dbItem = getattr(db, self.modelName) ()

    #----------------------------------------------------------------------
    def onCloseButton(self, event):
        """
        onClose is defined in base, therefor use onCloseButton here
        otherwise we get a max recursion error
        
        Cancel the dialog
        """
        self.view.Close()

    #----------------------------------------------------------------------
    def onRecord(self, event):
        """
        Either do "ADD" or "Edit"
        """
        if self._AddModus:
            self.onAdd()
        else:
            self.onEdit()
        if self.focusCtrl:
            self.focusCtrl.SetFocus()

    #----------------------------------------------------------------------
    def rowBuilder(self, widgets):
        """
        Build a row with the statictext and txt/search control

        :param widgets: list with the two controls
        """
        lbl, txt = widgets
        self.mainSizer.Add(lbl, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
        self.mainSizer.Add(txt, 1, wx.EXPAND|wx.ALL, 5)


# -*- coding: utf-8 -*-#
#!/usr/bin/env python
"""A base controller with list and add/edit/delete support,
see e.g. d_persons.py
"""

import logging

import functools

import wx

import base as cBase

import mlsrc.libui.commonDlgs as commonDlgs
import mlsrc.libui.olvgroup as olvg
import mlsrc.libui.olvdefs as olvd

import mlsrc.models as db

from mlsrc.mypub import pub, pTopics

########################################################################
class BaseList(cBase.BaseController):
    def __init__(self, view=None, model=None, **kwds):
        """Constructur for base dialog with list controller """

        super(BaseList, self).__init__(view=view, model=model, **kwds)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        searchSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)

        # create the search related widgets
        cat = ["Default", ]
        searchByLbl = wx.StaticText(self.view, label="Search By:")
        searchByLbl.SetFont(font)
        searchSizer.Add(searchByLbl, 0, wx.ALL, 5)

        self.categories = wx.ComboBox(self.view, value="Default", choices=cat)
        searchSizer.Add(self.categories, 0, wx.ALL, 5)

        self.search = wx.SearchCtrl(self.view, style=wx.TE_PROCESS_ENTER)
        self.search.Bind(wx.EVT_TEXT_ENTER, self.onSearch)
        searchSizer.Add(self.search, 0, wx.ALL, 5)

        self.theOlv = olvg.OlvGroup(id=wx.ID_ANY, name=u'olvList',
                                       parent=self.view, style=wx.TAB_TRAVERSAL)

        # create the button row
        addRecordBtn = wx.Button(self.view, label="Add")
        addRecordBtn.Bind(wx.EVT_BUTTON, self.onAddRecord)
        btnSizer.Add(addRecordBtn, 0, wx.ALL, 5)

        editRecordBtn = wx.Button(self.view, label="Edit")
        editRecordBtn.Bind(wx.EVT_BUTTON, self.onEditRecord)
        btnSizer.Add(editRecordBtn, 0, wx.ALL, 5)

        deleteRecordBtn = wx.Button(self.view, label="Delete")
        deleteRecordBtn.Bind(wx.EVT_BUTTON, self.onDelete)
        btnSizer.Add(deleteRecordBtn, 0, wx.ALL, 5)

        showAllBtn = wx.Button(self.view, label="Show All")
        showAllBtn.Bind(wx.EVT_BUTTON, self.onShowAllRecord)
        btnSizer.Add(showAllBtn, 0, wx.ALL, 5)

        mainSizer.Add(searchSizer)
        mainSizer.Add(self.theOlv, 1, wx.ALL|wx.EXPAND, 5)
        mainSizer.Add(btnSizer, 0, wx.CENTER)
        self.view.SetSizer(mainSizer)

        pub.subscribe(self.onItemAdded, pTopics.data.itemAdded)
        pub.subscribe(self.onItemModified, pTopics.data.itemModified)

    #----------------------------------------------------------------------
    def initDlgListBase(self, scats):
        """Initionalize list and search categories
        
        :param scats: list of search categories
        """
        self.categories.Clear()
        self.categories.AppendItems(scats)
        self.categories.SetSelection(0)
        
        # setup list and load list objects
        self.setUpOlv()
        self.listObjects = self.getAllRecords()
        self.setObjects()

    #----------------------------------------------------------------------
    def onItemAdded(self, dbparent, dbitem):
        """
        Update list if a db.Person item was added
        """
        # protect from PyDeadObjectError
        if self:
            if isinstance(dbitem, getattr(db, self.modelName)):
                self.theOlv.getList().AddObject(dbitem)

    #----------------------------------------------------------------------
    def onItemModified(self, dbparent, dbitem):
        """
        Update list if a db.Book item was modified
        """
        # protect from PyDeadObjectError
        if self:
            if isinstance(dbitem, getattr(db, self.modelName)):
                self.theOlv.getList().RefreshObject(dbitem)

    #----------------------------------------------------------------------
    def onAddRecord(self, event):
        """
        Needs to be overriden
        """
        logging.error("Not implement - onAddRecord")

    #----------------------------------------------------------------------
    def onEditRecord(self, event):
        """
        Needs to be overriden
        """
        logging.error("Not implement - onEditRecord")

    #----------------------------------------------------------------------
    def onDelete(self, event):
        """
        Delete a record
        """
        selectedRow = self.theOlv.getList().GetSelectedObject()
        if selectedRow == None:
            commonDlgs.showMessageDlg("No row selected!", "Error")
            return
        self.theOlv.getList().RemoveObject(selectedRow)
        self.deleteRecord(selectedRow.id)

    #----------------------------------------------------------------------
    def onSearch(self, event):
        """
        Searches database based on the user's filter choice and keyword
        """
        filterChoice = self.categories.GetValue()
        keyword = self.search.GetValue()
        logging.debug("%s %s" % (filterChoice, keyword))
        self.listObjects = self.searchRecords(filterChoice, keyword)
        self.setObjects()

    #----------------------------------------------------------------------
    def onShowAllRecord(self, event):
        """
        Updates the record list to show all of them
        """
        self.showAllRecords()

    #----------------------------------------------------------------------
    def setUpOlv(self):
        header, coldesc, table = getattr(olvd, self.modelName)()
        self.theOlv.initOLV(header, coldesc, table)
        self.theOlv.ignoreDataDirty = True

    #----------------------------------------------------------------------
    def setObjects(self):
        logging.debug(self.listObjects)
        self.theOlv.getList().SetObjects(self.listObjects)

    #----------------------------------------------------------------------
    def showAllRecords(self):
        """
        Show all records in the object list view control
        """
        self.listObjects = self.getAllRecords()
        self.setObjects()

    #----------------------------------------------------------------------
    def searchRecords(self, filterChoice, keyword):
        """
        Needs to be overriden
        """
        logging.error("Not implement - searchRecords")


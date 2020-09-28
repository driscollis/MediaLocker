# -*- coding: utf-8 -*-#
#!/usr/bin/env python
"""The books controller"""

import logging

import functools

import wx

import ObjectListView as olv

import base as cBase
import d_book as dBook

import mlsrc.libui.commonDlgs as commonDlgs

import mlsrc.models as db

from mlsrc.mypub import pub, pTopics

########################################################################
class Books(cBase.BaseController):
    def __init__(self, parent, **kwds):
        """The controller for books"""

        self.view = wx.Panel(parent, wx.ID_ANY)
        self.view.SetName("pBook")
        super(Books, self).__init__(view=self.view, model="Book", **kwds)

        self.view.Bind(wx.EVT_CLOSE, self.onClose)
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        searchSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        font = wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD)

        # create the search related widgets
        cat = ["Author", "Title", "ISBN", "Publisher"]
        searchByLbl = wx.StaticText(self.view, label="Search By:")
        searchByLbl.SetFont(font)
        searchSizer.Add(searchByLbl, 0, wx.ALL, 5)

        self.categories = wx.ComboBox(self.view, value="Author", choices=cat)
        searchSizer.Add(self.categories, 0, wx.ALL, 5)

        self.search = wx.SearchCtrl(self.view, style=wx.TE_PROCESS_ENTER)
        self.search.Bind(wx.EVT_TEXT_ENTER, self.onSearch)
        searchSizer.Add(self.search, 0, wx.ALL, 5)

        self.bookResultsOlv = olv.GroupListView(self.view, style=wx.LC_REPORT
                                                        |wx.SUNKEN_BORDER)
        self.bookResultsOlv.SetEmptyListMsg("No Records Found")
        self.setUpOlv()
        self.bookResults = self.getAllRecords()
        self.setBooks()

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
        mainSizer.Add(self.bookResultsOlv, 1, wx.ALL|wx.EXPAND, 5)
        mainSizer.Add(btnSizer, 0, wx.CENTER)
        self.view.SetSizer(mainSizer)

        pub.subscribe(self.onItemAdded, pTopics.data.itemAdded)
        pub.subscribe(self.onItemModified, pTopics.data.itemModified)

    #----------------------------------------------------------------------
    def onItemAdded(self, dbparent, dbitem):
        """
        Update list if a db.Book item was added
        """
        # protect from PyDeadObjectError
        if self:
            if isinstance(dbitem, db.Book):
                self.bookResultsOlv.AddObject(dbitem)

    def onItemModified(self, dbparent, dbitem):
        """
        Update list if a db.Book item was modified
        """
        # protect from PyDeadObjectError
        if self:
            if isinstance(dbitem, db.Book):
                self.bookResultsOlv.RefreshObject(dbitem)

    #----------------------------------------------------------------------
    def onClose(self, evt):
        """Close actions
        
        - unsubscribe pubsub
        """
        pub.unsubAll()
        evt.Skip()

    #----------------------------------------------------------------------
    def onAddRecord(self, event):
        """
        Add a record to the database
        """
        dbItem = getattr(db, self.modelName) ()
        person = db.Person()
        publisher = db.Publisher()
        dbItem.person = person
        dbItem.publisher = publisher
        dlg = dBook.Book(self.view, dbItem).view
        dlg.ShowModal()
        dlg.Destroy()

    #----------------------------------------------------------------------
    def onEditRecord(self, event):
        """
        Edit a record
        """
        selectedRow = self.bookResultsOlv.GetSelectedObject()
        if selectedRow == None:
            commonDlgs.showMessageDlg("No row selected!", "Error")
            return
        dlg = dBook.Book(self.view, selectedRow, title="Modify",
                                                 addModus=False).view
        dlg.ShowModal()
        dlg.Destroy()

    #----------------------------------------------------------------------
    def onDelete(self, event):
        """
        Delete a record
        """
        selectedRow = self.bookResultsOlv.GetSelectedObject()
        if selectedRow == None:
            commonDlgs.showMessageDlg("No row selected!", "Error")
            return
        self.bookResultsOlv.RemoveObject(selectedRow)
        self.deleteRecord(selectedRow.id)

    #----------------------------------------------------------------------
    def onSearch(self, event):
        """
        Searches database based on the user's filter choice and keyword
        """
        filterChoice = self.categories.GetValue()
        keyword = self.search.GetValue()
        logging.debug("%s %s" % (filterChoice, keyword))
        self.bookResults = self.searchRecords(filterChoice, keyword)
        self.setBooks()

    #----------------------------------------------------------------------
    def onShowAllRecord(self, event):
        """
        Updates the record list to show all of them
        """
        self.showAllRecords()

    #----------------------------------------------------------------------
    def setUpOlv(self):
        self.bookResultsOlv.SetColumns([
            olv.ColumnDefn("Publisher", "left", 150,
                           valueGetter=functools.partial(self.getRelInfo,
                               relation="publisher", colname="name")),
            olv.ColumnDefn("Title", "left", 250,
                           valueGetter=functools.partial(self.getRelInfo,
                               relation=None, colname="title")),
            olv.ColumnDefn("Author", "left", 150,
                           valueGetter=functools.partial(self.getRelInfo,
                               relation="person", colname="full_name")),
            olv.ColumnDefn("ISBN", "right", 150,
                           valueGetter=functools.partial(self.getRelInfo,
                               relation=None, colname="isbn")),
        ])

        lcSize = 30
        for col in self.bookResultsOlv.columns:
            lcSize += col.width
        # set the list size
        self.bookResultsOlv.SetMinSize((lcSize, 100))
        self.view.Layout()

    #----------------------------------------------------------------------
    def setBooks(self):
        logging.debug(self.bookResults)
        self.bookResultsOlv.SetObjects(self.bookResults)

    #----------------------------------------------------------------------
    def showAllRecords(self):
        """
        Show all records in the object list view control
        """
        self.bookResults = self.getAllRecords()
        self.setBooks()

    #----------------------------------------------------------------------
    def searchRecords(self, filterChoice, keyword):
        """
        Searches the database based on the filter chosen and the keyword
        given by the user
        """
        session = wx.GetApp().session
        model = getattr(db, self.modelName)

        if filterChoice == "Author":
            qry = session.query(model).join(db.Person)
            logging.debug(qry)
            result = qry.filter(db.Person.full_name.contains(u'%s' % keyword))

            logging.debug(result)
            result = result.all()
        elif filterChoice == "Title":
            qry = session.query(model)
            result = qry.filter(model.title.contains(u'%s' % keyword)).all()
        elif filterChoice == "ISBN":
            qry = session.query(model)
            result = qry.filter(model.isbn.contains(u'%s' % keyword)).all()
        else:
            qry = session.query(model).join(db.Publisher)
            result = qry.filter(db.Publisher.name.contains(
                                                    u'%s' % keyword)).all()

        logging.debug(result)
        return result


    def getRel(self, data, relation):
        """Resolve dotted relation entry"""
        baseAttr = data
        if not relation == None:
            comp = relation.split('.')
            for arel in comp:
                if baseAttr:
                    baseAttr = getattr(baseAttr, arel)
        return baseAttr

    def getRelInfo(self, data, relation, colname):
        """return value or blank"""
        try:
            baseAttr = self.getRel(data, relation)

            if baseAttr:
                return getattr(baseAttr, colname)
            else:
                return ''
        except:
            # don't raise otherwise it takes a long time,
            # and one might have to kill app
            msg = "Parent: %s, Grand Parent: %s\n" % (self.view.GetParent(),
                                                    self.view.GetGrandParent())
            msgR = "relation: %s, colname: %s, data: %s\n" % (relation,
                                                            colname,
                                                            data)
            logging.error(msg)
            logging.exception(msgR)

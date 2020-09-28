# -*- coding: utf-8 -*-#
#!/usr/bin/env python
"""ObjectListView based GroupList

Note that column definitions are defined in the table olvlist
"""

import logging

import sys
import traceback

import ObjectListView as olvLib
import olvbase as olvB
from ObjectListView import Filter

import wx
import wx.lib.art.flagart as flags

# needs to be changed to fully support i18n
_ = wx.GetTranslation

import mlsrc.models as db
from mlsrc.models.sautils import no_autoflush as no_autoflush


class OlvGroup(wx.Panel, olvB.OlvBase):
    def __init__(self, *args, **kwds):
        """An OLV based group listctrl"""
        super(OlvGroup, self).__init__(*args, **kwds)
        olvB.OlvBase.__init__(self, *args, **kwds)

        self.initWidget()
        self.Layout()

    def setOlvQuery(self, query):
        """Setting of the base SQLAlchemy query"""
        self.saQuery = query

    def initWidget(self):
        """Initialize the listctrl"""
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer_1)

        self.myOlv = olvLib.GroupListView(self, -1,
                        style=wx.LC_REPORT|wx.SUNKEN_BORDER|wx.LC_SINGLE_SEL)
        self.myOlv.SetEmptyListMsg(self.EmptyListMsg)
        self.myOlv.SetEmptyListMsgFont(wx.FFont(24, wx.DEFAULT, face="Tekton"))

        sizer_1.Add(self.myOlv, 1, wx.ALL|wx.EXPAND)
        self.Layout()

        self.myOlv.currentItem = None
        self.myOlv.currentItemPkeys = None
        self.myOlv.Bind(wx.EVT_LIST_COL_CLICK, self.onOLVColClick)
        self.myOlv.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onOLVItemSelected)

        self.myOlv.Bind(wx.EVT_CONTEXT_MENU, self.onListContextMenu)

    def initModel(self):
        """Initiallize the OLV model and load items to the listctrl"""
        if not self.saQuery:
            logging.error("a query needs to be set")
            return
        else:
            self.listObjects = self.saQuery.autoflush(False)

        if self.sqljoin:
            self.listObjects = self.listObjects.join(self.sqljoin)

        if self.sqljoinSA:
            for ajoin in self.sqljoinSA:
                self.listObjects = self.listObjects.join(ajoin)

        if self.filter:
            self.listObjects = self.listObjects.filter(self.filter)

        if self.order_by:
            self.listObjects = self.listObjects.order_by(self.order_by)

        if self.saJoinOption:
#            logging.debug(self.saJoinOption)
            for opt in self.saJoinOption:
                self.listObjects = self.listObjects.options(opt)

        logging.debug(self.listObjects)
        self.listObjects.all()

    def initOLV(self, desc, coldesc, table, distinct=None):
        """
        :param desc: the list title, e.g. _('Countries')
        :param coldesc: a dict of column name and column description
        :param table: the table name as a string e.g. 'Country_LV'
        :param distinct: a list of joins, e.g.
        [db.Recipeit, (db.Recipe, db.Recipe.recipeid==db.Recipeit.fk_recipeid)]
        """

        self.EmptyListMsg = (_('No %s are found for the entered search criteria') % desc)
        self.listMinMenuDesc = (_('Preview - %s List - minimal') % desc)
        self.listNormMenuDesc = (_('Preview - %s List - normal') % desc)
        self.listMinReportDesc = (_('%s - list') % desc)
        self.listNormReportDesc = (_('%s - list') % desc)

        self.tableName = table
        ds = wx.GetApp().session
        with no_autoflush(ds):
            if distinct:
                joinedQuery = ds.query(getattr(db, self.tableName))
                for item in distinct:
                    joinedQuery = joinedQuery.join(item)

                self.setOlvQuery(joinedQuery.distinct())
            else:
                self.setOlvQuery(ds.query(getattr(db, self.tableName)))

        cols = self.setColumnDef(coldesc, self.tableName)
        self.initObjectListView(None, cols)
        self.setGroupCols(0)

        xCols = len(cols)
        olvList = self.getList()
        olvList.SetFilter(Filter.TextSearch(olvList, olvList.columns[0:xCols]))

    def searchItems(self, where):
        """Search items in database and load items to listctrl"""
        self.filter = where
        self.InitModel()
        self.getList().SetSortColumn(0)
        self.setGroupCols(0)

        self.getList().SetObjects(self.listObjects)

    def onOLVColClick(self, event):
        """Handle listctrl column header click"""
        col = event.m_col
        self.setGroupCols(col)
        event.Skip()

    def setGroupCols(self, col):
        """Handle groupable"""
        if col in self.nonGroupCols:
            self.getList().SetShowGroups(False)
        else:
            self.getList().SetShowGroups(True)


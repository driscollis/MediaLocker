# -*- coding: utf-8 -*-#
#!/usr/bin/env python

"""ObjectListView base mixin, provides common methods used by
olvgroup and olvvirt, e.g. printing
"""
import logging
import sys
import traceback

import decimal

import wx
import wx.lib.art.flagart as flags

import ObjectListView as olvLib
import functools

import mlsrc.models as db
from mlsrc.models.sautils import no_autoflush as no_autoflush

# needs to be changed to fully support i18n
_ = wx.GetTranslation

class OlvBase(object):
    def __init__(self, *args, **kwds):

        self.saQuery = None
        self.filter = None
        self.sqljoin = None
        self.sqljoinSA = []
        self.saJoinOption = []
        self.order_by = None
        self.nonGroupCols = []

        # override the following if you have e.g. multi keys or a different
        # column name, e.g for drinks
        self.itemPkeysCols = ('id', )

        self.ignoreDataDirty = False

        self.EmptyListMsg = _('Nothing found for the entered search criteria')

        # minimal reports
        self.listMinMenuDesc = _('Preview - List - minimal')
        self.listNormMenuDesc = _('Preview - List - normal')
        self.listMinReportDesc = _('List minimal')
        self.listNormReportDesc = _('List normal')

        self.singleItemText = _("%(title)s [only %(count)d item]")
        self.pluralItemsText = _("%(title)s [%(count)d items]")

    def getRel(self, data, relation):
        """Resolve dotted relation entry"""
        baseAttr = data
        if not relation == None:
            comp = relation.split('.')
            for arel in comp:
                if baseAttr:
                    with no_autoflush(wx.GetApp().session):
                        baseAttr = getattr(baseAttr, arel)
        return baseAttr

    def getRelInfo(self, data, relation, colname):
        """return value or blank"""
        try:
            baseAttr = self.getRel(data, relation)

            if baseAttr:
                with no_autoflush(wx.GetApp().session):
                    return getattr(baseAttr, colname)
            else:
                return ''
        except:
            # don't raise otherwise it takes a long time, might have to kill app
            msg = "Parent: %s, Grand Parent: %s\n" % (self.GetParent(),
                                                    self.GetGrandParent())
            msgR = "relation: %s, colname: %s, data: %s\n" % (relation,
                                                            colname,
                                                            data)
            logging.error(msg)
            logging.exception(msgR)

    def getColumnDefFromTable(self, table):
        """Get the column definition from the Olvlist table"""
        listFilter = "tablename = '%s'" % table
        cols = []
        ds = wx.GetApp().session
        with no_autoflush(ds):
            cols = ds.query(db.Olvlist).filter(listFilter
                                    ).order_by('colno').all()

        return cols

    def setColumnDef(self, coldesc, table):
        """get the column definitions from olvlist table"""
        self.includedColumns = {}
        coldef = []
        listFilter = "tablename = '%s'" % table

        cols = self.getColumnDefFromTable(table)
        if cols:
            for col in cols:
                if col.colshow:
                    coldef.append(self.createColDef(col, coldesc))
                    # adjust as column count of list is zero based
                    x = len(coldef)-1
                    if not col.colgroup:
                        self.nonGroupCols.append(x)
                    self.includedColumns[col.colname] = x

        else:
            logging.error("no entry in Olvlist table for: %s" % table)

        return coldef

    def createColDef(self, col, coldesc):
        coldef = []
        try:
            if col.colname in coldesc:
                desc = coldesc[col.colname]
            else:
                desc = col.colname
            if col.groupkeyg:
                groupKeyGetter = getattr(self, col.groupkeyg)
            else:
                groupKeyGetter = None
            if col.imageg:
                imageGetter = getattr(self, col.imageg)
            else:
                imageGetter = None
            if col.stringconv:
                stringConverter = getattr(self, col.stringconv)
            else:
                stringConverter = None

            if col.checkstatcol:
                coldef = olvLib.ColumnDefn(desc, col.align, col.width,
                            valueGetter=functools.partial(self.getRelInfo,
                               relation=col.valuerel, colname=col.valuecol),
                            isSpaceFilling=col.isfilling,
                            minimumWidth=col.minwidth,
                            groupKeyGetter=groupKeyGetter,
                            imageGetter=imageGetter,
                            checkStateGetter=functools.partial(self.getRelInfo,
                                relation=col.checkstatrel,
                                colname=col.checkstatcol),
                            checkStateSetter=lambda x,y:0,
                            stringConverter=lambda x: '',
                            isEditable=False,
                            groupTitleSingleItem=self.singleItemText,
                            groupTitlePluralItems=self.pluralItemsText)
            else:
                coldef = olvLib.ColumnDefn(desc, col.align, col.width,
                            valueGetter=functools.partial(self.getRelInfo,
                                relation=col.valuerel, colname=col.valuecol),
                            isSpaceFilling=col.isfilling,
                            minimumWidth=col.minwidth,
                            groupKeyGetter=groupKeyGetter,
                            imageGetter=imageGetter,
                            stringConverter=stringConverter,
                            groupTitleSingleItem=self.singleItemText,
                            groupTitlePluralItems=self.pluralItemsText)

        except:
            msg = "Parent: %s, Grand Parent: %s" % (self.GetParent(),
                                                    self.GetGrandParent())
            msgC = "col: %s, coldesc: %s" % (col,
                                             coldesc)
            logging.error(msg)
            logging.exception(msgC)
        return coldef

    def onListContextMenu(self, event):
        """Contect menu for printing a list"""
        if not hasattr(self, "previewListID"):
            self.previewListMinID = wx.NewId()
            self.previewListNormID = wx.NewId()
            self.saveColumConfigID = wx.NewId()

            self.Bind(wx.EVT_MENU, self.onPreviewListMinimal,
                      id=self.previewListMinID)
            self.Bind(wx.EVT_MENU, self.onPreviewListNormal,
                      id=self.previewListNormID)
            self.Bind(wx.EVT_MENU, self.onSaveColumnConfig,
                      id=self.saveColumConfigID)

        # make a menu
        menu = wx.Menu()
        # Show how to put an icon in the menu
        item = wx.MenuItem(menu, self.previewListMinID, self.listMinMenuDesc)
        menu.AppendItem(item)
        item = wx.MenuItem(menu, self.previewListNormID, self.listNormMenuDesc)
        menu.AppendItem(item)
        item = wx.MenuItem(menu, self.saveColumConfigID,
                           _("Save the current column settings."))
        menu.AppendItem(item)

        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.PopupMenu(menu)
        menu.Destroy()

    def onSaveColumnConfig(self, event):
        logging.debug("did save")
        colNo = 0
        # TODO: wait for next 2.9.3,
        # as per Robin will have at least MSW support for this
        for column in self.myOlv.columns:
            logging.debug("column: %s, %s, %s, %s, %s, %s" % (column.title,
                                                      column.width,
                                    self.myOlv.GetColumnWidth(colNo),
                                    colNo,
                                    self.myOlv.GetColumn(3).GetWidth(),
                                    self.myOlv.GetColumn(3).GetColumn(),))
            colNo += 1

        for col in xrange(self.myOlv.GetColumnCount()):
            logging.debug("%s, %s" % (col, self.myOlv.GetColumnWidth(col)))

    def onPreviewListMinimal(self, event):
        printer = olvLib.ListCtrlPrinter(self.myOlv, '')
        # basic format
        printer.ReportFormat = self.fmtMinimal()

        # adapt the format
        printer.ReportFormat.IncludeImages = True

        printer.SetPageHeader(self.listMinReportDesc, '', wx.GetApp().GetPrefs().owner.strip())
        printer.SetPageFooter("%(date)s", '', "%(currentPage)d of %(totalPages)d")

        # set printData
        printer.GetPrintData().SetOrientation(wx.LANDSCAPE)

        printer.PrintPreview()

    def onPreviewListNormal(self, event):
        printer = olvLib.ListCtrlPrinter(self.myOlv, '')
        # basic format
        printer.ReportFormat = self.fmtNormal()

        # adapt the format
        printer.ReportFormat.IncludeImages = True

        printer.SetPageHeader(self.listNormReportDesc, '', wx.GetApp().GetPrefs().owner.strip())
        printer.SetPageFooter("%(date)s", '', "%(currentPage)d of %(totalPages)d")

        # set printData
        printer.GetPrintData().SetOrientation(wx.LANDSCAPE)

        printer.PrintPreview()

    def getList(self):
        return self.myOlv

    def initObjectListView(self, checkstatecol=None, columnDef=None):
        # put expansion in 1st data column and not use a separate column
        # this way clicking the header always sorts the correct column
        tList = self.getList()
        tList.useExpansionColumn = False
        tList.SetColumns(columnDef)

        if checkstatecol != None:
            tList.CreateCheckStateColumn(checkstatecol)

        # suppress blank line
        tList.putBlankLineBetweenGroups = False

        # set size of list and panel based on column width
        # start value to deal with left blank space and a bit
        lcSize = 30
        for col in tList.columns:
            lcSize += col.width
        # set the list size
        tList.SetMinSize((lcSize, 100))
        # set the panel containing the list
        self.SetMinSize((lcSize, 100))

    def initModel(self):
        """needs to be implemented in olvgroup or olvvirtual"""
        raise NotImplementedError("initModel needs to be overidden")

    def onOLVItemSelected(self, event):
        if not self.ignoreDataDirty:
            # do we ignore dirty state
            if wx.GetApp().dataCheckDirty():
                return
        tList = self.getList()
        tList.currentItem = event.GetIndex()
        # we only allow single selection
        sel = event.GetEventObject().GetSelectedObjects()
        if sel:
            item = sel[0]
        else:
            item = None

        if item:
            tList.currentItemPkeys = ()
            for key in self.itemPkeysCols:
                tList.currentItemPkeys += self.getKeyValue(item, key)
        else:
            tList.currentItemPkeys = ()
            for x in range(len(self.itemPkeysCols)):
                tList.currentItemPkeys += (None, )
        event.Skip()

    def getKeyValue(self, item, key):
        keyValue = item
        if key.find('.') == -1:
            # no relation in key
            colname = key
        else:
            rel, colname = key.rsplit('.', 1)
            comp = rel.split('.')
            for arel in comp:
                if keyValue:
                    with no_autoflush(wx.GetApp().session):
                        keyValue = getattr(keyValue, arel)

        if keyValue:
            with no_autoflush(wx.GetApp().session):
                return (getattr(keyValue, colname), )
        else:
            return (None, )

    def refreshData(self):
        self.initModel()
        self.getList().SetObjects(self.listObjects)

    def selectItem(self, keys):
        filter = '%s = %i' % (self.itemPkeysCols[0], keys[0])
        if len(keys) > 1:
            if keys[1]:
                filter += ' AND '
                filter += "%s = %i" % (self.itemPkeysCols[1], keys[1])
            if keys[2]:
                filter += ' AND '
                filter += "%s = %i" % (self.itemPkeysCols[2], keys[2])
        items = self.saQuery.filter(filter).all()

        if items:
            self.getList().SelectObject(items[0], deselectOthers=True,
                                        ensureVisible=True)

    def updatedItem(self):
        curItemKeys = self.getList().currentItemPkeys
        if curItemKeys:
            if curItemKeys[0]:
                filter = '%s = %i' % (self.itemPkeysCols[0], curItemKeys[0])
                items = self.saQuery.filter(filter).all()
                self.getList().RefreshObjects(items)

    def deletedItem(self, keys):
        filter = '%s = %i' % (self.itemPkeysCols[0], keys[0])
        if len(keys) > 1:
            if keys[1]:
                filter += ' AND '
                filter += "%s = %i" % (self.itemPkeysCols[1], keys[1])
            if keys[2]:
                filter += ' AND '
                filter += "%s = %i" % (self.itemPkeysCols[2], keys[2])
        items = self.saQuery.filter(filter).all()
        self.getList().RemoveObjects(items)

    def addedItem(self, keys):
        filter = '%s = %i' % (self.itemPkeysCols[0], keys[0])
        if len(keys) > 1:
            if keys[1]:
                filter += ' AND '
                filter += "%s = %i" % (self.itemPkeysCols[1], keys[1])
            if keys[2]:
                filter += ' AND '
                filter += "%s = %i" % (self.itemPkeysCols[2], keys[2])
        items = self.saQuery.filter(filter).all()
        if items:
            self.getList().AddObject(items[0])

            self.GetList().SelectObject(items[0], deselectOthers=True, ensureVisible=True)

    # a couple of formats for printing
    def fmtMinimal(self, headerFontName="Arial", rowFontName="Times New Roman"):
        """
        Return a minimal format for a report
        """
        fmt = olvLib.ReportFormat()
        fmt.AlwaysCenterColumnHeader = True
        fmt.IsShrinkToFit = True
        fmt.CanCellsWrap = True

        fmt.PageHeader.Font = wx.FFont(12, wx.FONTFAMILY_DEFAULT, face=headerFontName)
        fmt.PageHeader.Line(wx.BOTTOM, wx.BLACK, 1, space=5)
        fmt.PageHeader.Padding = (0, 0, 0, 12)

        fmt.ListHeader.Font = wx.FFont(18, wx.FONTFAMILY_DEFAULT, face=headerFontName)
        fmt.ListHeader.Padding = (0, 12, 0, 12)
        fmt.ListHeader.Line(wx.BOTTOM, wx.BLACK, 1, space=5)

        fmt.GroupTitle.Font = wx.FFont(12, wx.FONTFAMILY_DEFAULT, face=headerFontName)
        fmt.GroupTitle.Padding = (0, 12, 0, 12)
        fmt.GroupTitle.Line(wx.BOTTOM, wx.BLACK, 1, space=5)

        fmt.PageFooter.Font = wx.FFont(10, wx.FONTFAMILY_DEFAULT, face=headerFontName)
        fmt.PageFooter.Line(wx.TOP, wx.BLACK, 1, space=3)
        fmt.PageFooter.Padding = (0, 16, 0, 0)

        fmt.ColumnHeader.Font = wx.FFont(14, wx.FONTFAMILY_DEFAULT, wx.FONTFLAG_BOLD, face=headerFontName)
        fmt.ColumnHeader.Padding = (0, 12, 0, 12)
        fmt.ColumnHeader.CellPadding = 5
        fmt.ColumnHeader.Line(wx.BOTTOM, wx.Colour(192, 192, 192), 1, space=3)

        fmt.Row.Font = wx.FFont(10, wx.FONTFAMILY_DEFAULT, face=rowFontName)
        fmt.Row.CellPadding = 5
        fmt.Row.Line(wx.BOTTOM, wx.Colour(192, 192, 192), 1, space=3)

        return fmt

    def fmtNormal(self, headerFontName="Gill Sans", rowFontName="Times New Roman"):
        """
        Return a reasonable default format for a report
        """
        fmt = olvLib.ReportFormat()
        fmt.AlwaysCenterColumnHeader = False
        fmt.IsShrinkToFit = True
        fmt.CanCellsWrap = False

        fmt.PageHeader.Font = wx.FFont(12, wx.FONTFAMILY_DEFAULT, face=headerFontName)
        fmt.PageHeader.Line(wx.BOTTOM, wx.BLUE, 2, space=5)
        fmt.PageHeader.Padding = (0, 0, 0, 12)

        fmt.ListHeader.Font = wx.FFont(26, wx.FONTFAMILY_SWISS, wx.FONTFLAG_BOLD, face=headerFontName)
        fmt.ListHeader.TextColor = wx.WHITE
        fmt.ListHeader.Padding = (0, 12, 0, 12)
        fmt.ListHeader.TextAlignment = wx.ALIGN_LEFT
        fmt.ListHeader.Background(wx.BLUE, wx.WHITE, space=(16, 4, 0, 4))

        fmt.GroupTitle.Font = wx.FFont(14, wx.FONTFAMILY_DEFAULT, face=headerFontName)
        fmt.GroupTitle.Padding = (0, 12, 0, 12)
        fmt.GroupTitle.Line(wx.BOTTOM, wx.BLUE, 4, toColor=wx.WHITE, space=5)

        fmt.PageFooter.Font = wx.FFont(10, wx.FONTFAMILY_DEFAULT, face=headerFontName)
        fmt.PageFooter.Background(wx.WHITE, wx.BLUE, space=(0, 4, 0, 4))

        fmt.ColumnHeader.Font = wx.FFont(14, wx.FONTFAMILY_DEFAULT, wx.FONTFLAG_BOLD, face=headerFontName)
        fmt.ColumnHeader.CellPadding = 2
        fmt.ColumnHeader.Background(wx.Colour(192, 192, 192))
        fmt.ColumnHeader.GridPen = wx.Pen(wx.WHITE, 1)
        fmt.ColumnHeader.Padding = (0, 0, 0, 12)

        fmt.Row.Font = wx.FFont(12, wx.FONTFAMILY_DEFAULT, face=rowFontName)
        fmt.Row.CellPadding = 2
        fmt.Row.Line(wx.BOTTOM, pen=wx.Pen(wx.BLUE, 1, wx.DOT), space=3)

        return fmt

    def addListImages(self):
        # add flag images to imagelist
        for flag in flags.catalog:
            # resize to
            fImg = flags.catalog[flag].GetImage().Resize((16, 16), (0, 0))
            self.GetList().AddNamedImages(flag, fImg.ConvertToBitmap())

    def flagImageGetterAlt(self, data):
        retVal = -1
        if data.is2code:
            if data.is2code in flags.catalog:
                retVal = data.is2code
        return retVal

    def moneyConverter(self, value):
        if value:
            if type(value) == str:
                value = decimal.Decimal(value)
            return '%.2f' % value
        else:
            return ''
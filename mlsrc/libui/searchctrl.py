# -*- coding: utf-8 -*-#
#!/usr/bin/env python
"""A search control which is used instead of a simple combobox.

The popup is a ObjectListView with search and optional buttons to
call up a dialog to edit/add items.

Sample use in e.g. controllers.d_book:

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


One can also set it up that content is filtered based on another control.

              {'cType': 'sc', 'desc': _(u"Country name"),
                    'helpt': _(u"Select the country."),
                    'toolt': _(u"Select the country."),
                    'dbColName': 'name', 'dbLength': 50,
                    'cName': 'sCountryName',
                    'sTableName': 'Country_LV',
                    'sFkColName': 'fk_country_id',
                    'sRelName': 'country'},
              {'cType': 'sc', 'desc': _(u"Region name"),
                    'helpt': _(u"Select the region."),
                    'toolt': _(u"Select the region."),
                    'dbColName': 'name', 'dbLength': 70,
                    'cName': 'sRegionName',
                    'sTableName': 'Region_LV',
                    'sFkColName': 'fk_region_id',
                    'sRelName': 'region',
                    'sFilterCtrls': ['sCountryName', ]},

The code snippet above shows a country and a region control and if e.g. the
country control has "France" selected then the region control will only show
french regions.
"""

import logging

import wx
import wx.lib.sized_controls as sc

# needs to be changed to fully support i18n
_ = wx.GetTranslation

import ObjectListView as olvLib
import olvgroup as olvg

from mlsrc.mypub import pub, pTopics

import cpopupctrl as pop

from mixins import *
import uiutils

import mlsrc.controllers.validators as validators

import mlsrc.models as db

class SearchCtrl(pop.PopupControl, DbMixin):
    def __init__(self, *args, **kwds):
        """Generic search control using the PopupControl

        call ctrl.InitSC to do the setup
        """
        super(SearchCtrl, self).__init__(*args, **kwds)
        DbMixin.__init__(self)

        # NOTE: need to see if these events are causing an issue
        wx.UpdateUIEvent.SetUpdateInterval(500)
        self.Bind(wx.EVT_UPDATE_UI, self.onUpdateUI)
        
        self.Bind(wx.EVT_CLOSE, self.onClose)

        self.name = 'sControl'
        self._IsModified = False
        self._ctrlInit = False
        self._typedChar = False
        self._dbItemSelected = None
        self._dbItemSelectedPkey = None
        # no dbItem is to be updated
        self._searchOnly = False

        self.getTc().Bind(wx.EVT_CHAR, self.doChar)

        # some additional db stuff, other see DbMixin
        self.dbScFkColName = ''
        self.dbScRelName = ''
        self.dbScJoinSA = []
        self.dbScTable = None

        self.scMaintDlg = None
        # following are needed for the filtering based on another controls
        # value setting, look at sample above and code in SetDependen*
        self._dbScFilterCtrls = [None, ]
        self._dbScDependency = []

        self.createPopUp()

        pub.subscribe(self.onItemAdded, pTopics.data.itemAdded)
        pub.subscribe(self.onItemModified, pTopics.data.itemModified)

    def onItemAdded(self, dbparent, dbitem):
        """
        Update list if dbitem instance matches dbScTable
        """
        # protect from PyDeadObjectError
        if self:
            if self.dbScTable:
                cInst = getattr(db, self.dbScTable)
                if isinstance(dbitem, cInst):
                    self.olvList.getList().AddObject(dbitem)

    def onItemModified(self, dbparent, dbitem):
        """
        Update list if dbitem instance matches dbScTable
        """
        # protect from PyDeadObjectError
        if self:
            logging.debug(dbitem)
            if self.dbScTable:
                cInst = getattr(db, self.dbScTable)
                if isinstance(dbitem, cInst):
                    tList = self.olvList.getList()
                    tList.RefreshObject(dbitem)
                    tList.SelectObject(dbitem, deselectOthers=True,
                                        ensureVisible=True)

    def onClose(self, evt):
        """Close actions
        
        - unsubscribe pubsub
        """
        pub.unsubAll()
        evt.Skip()
        
    def createPopUp(self):
        # create the popup window content
        self.win = wx.Window(self, wx.ID_ANY, pos = (0,0), style = 0,
                             name='swin')
        winSizer = wx.BoxSizer()
        cPanel = sc.SizedPanel(self.win, wx.ID_ANY, name='cPanel')
        winSizer.Add(cPanel, 1, wx.EXPAND)
        self.win.SetSizer(winSizer)

        cPanel.SetSizerType('grid', {'cols': 1,})

        self.stSearchCtrl = wx.StaticText(cPanel, wx.ID_ANY,
                                    _('Use double left mouse click to select'))
        self.stSearchCtrl.SetSizerProps(halign='centre')

        bPanel = sc.SizedPanel(cPanel, wx.ID_ANY)
        bPanel.SetSizerType('grid', {'rows': 1,})
        self.searchCtrl = wx.SearchCtrl(bPanel, wx.ID_ANY)
        self.searchCtrl.SetSizerProps(valign='centre')

        blist = [
         ['select', wx.ID_ANY, _("Select"), _("Select first item and close."),
                               _("Select first item and close."),
                               self.onSelectButton,
                               "apply.png"],
         ['clear', wx.ID_ANY, _("Clear"), _("Close and clear selection."),
                                  _("Close and clear selection."),
                                  self.onClearButton,
                                  "clear.png"],
         ['cancel', wx.ID_ANY, _("Cancel"), _("Cancel and keep old value."),
                              _("Cancel and keep old value."),
                              self.onCancelButton,
                              "stop.png"],
         ['add', wx.ID_ANY, _("Add"), _("Create a new item."),
                               _("Create a new item."),
                               self.onAddButton,
                               "add.png"],
         ['edit', wx.ID_ANY, _("Edit"), _("Edit selected item."),
                                  _("Edit selected item."),
                                  self.onEditButton,
                                  "edit.png"],
        ]

        uiutils.doCreateButtons(self, bPanel, blist)

        self.olvList = olvg.OlvGroup(id=wx.ID_ANY, name=u'olvList',
                                       parent=cPanel, style=wx.TAB_TRAVERSAL)
        self.olvList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onOLVItemSelected)
        self.olvList.getList().Bind(wx.EVT_LEFT_DCLICK,
                                    self.onOLVItemDoubleClicked)

        self.olvList.SetSizerProps(expand=True, proportion=1)
        cPanel.SetSizerProps({'growable_row': (2, 1),
                              'growable_col': (0, 1),})

        self.searchCtrl.Bind(wx.EVT_TEXT, self.onTextSearchCtrl)
        self.searchCtrl.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN,
                             self.onCancelSearchCtrl)

        # hard code as we don't want it too big
        self.olvList.SetMinSize(wx.Size(300, 300))
        # following two are needed other wise popup is not correctly sized!
        cPanel.Fit()
        self.win.Fit()
        # This method is needed to set the contents that will be displayed
        # in the popup
        self.setPopupContent(self.win)

    def doChar(self, evt):
        # if tab then navigate, otherwise
        # send keycode to searchCtrl
        self._typedChar = None
        keycode = evt.KeyCode
        if keycode == wx.WXK_TAB:
            self.getTc().Navigate()
        else:
            if keycode < 256:
                if keycode > 27:
                    self._typedChar = keycode
            self.doPop()

    def initSC(self, heading=None, coldesc=None, table=None, distinct=None,
               searchOnly=False):
        self.createOLVList(heading, coldesc, table, distinct=distinct)

        self._searchOnly = searchOnly
        self._ctrlInit = True
        self.dbScTable = table

        self.olvList.getList().Layout()
        
        if not self.scMaintDlg:
            self.add.Hide()
            self.edit.Hide()
        self.Layout()
        self.Fit()

    def createOLVList(self, *args, **kwds):
        """Initialize the OLV list control
        see InitOLV for valid call signature
        """
        self.olvList.initOLV(*args, **kwds)
        # if caller set it to dirty we don't care,
        # we will just check our own flag or check self.save state
        self.olvList.ignoreDataDirty = True

    def onTextSearchCtrl(self, event):
        searchCtrl = event.GetEventObject()
        olv = self.olvList.getList()
        searchCtrl.ShowCancelButton(len(searchCtrl.GetValue()))
        olv.GetFilter().SetText(searchCtrl.GetValue())
        if isinstance(olv, olvLib.GroupListView):
            olv.RebuildGroups()
        else:
            olv.RepopulateList()

    def onCancelSearchCtrl(self, event):
        searchCtrl = event.GetEventObject()
        searchCtrl.SetValue("")
        self.onTextSearchCtrl(event)

    def onCancelButton(self, evt):
        """pop down and leave old value"""
        self.popDown()

        if self._searchOnly:
            return

    def onClearButton(self, evt):
        """Clear the control and the currently set value"""
        self.popDown()
        self.doSetDbItem(None)
        self.searchCtrl.ChangeValue('')
        self._typedChar = None

    def onSelectButton(self, evt):
        self.popDown()
        # close and select first item if present
        try:
            fItems = self.olvList.getList().GetFilteredObjects()
        except:
            fItems = None
        logging.debug(fItems)
        if fItems:
            if len(fItems) > 0:
                self.doSetDbItem(fItems[0])
        else:
            # if no filter then get all objects
            items = self.olvList.getList().GetObjects()
            if len(items) > 0:
                self.doSetDbItem(items[0])

        self.MarkDirty()
        pub.sendMessage(pTopics.data.needsSaving, dbparent=self.dbParent)

    def onAddButton(self, evt):
        dlg = self.scMaintDlg (None).view
        dlg.ShowModal()
        dlg.Destroy()
        # TODO: error handling

    def onEditButton(self, evt):
        logging.debug("edit item: %s\n" % self._dbItemSelected)
        dlg = self.scMaintDlg (None, self._dbItemSelected,
                               title="Modify",
                               addModus=False).view
        dlg.ShowModal()
        dlg.Destroy()
        # TODO: error handling

    def onOLVItemSelected(self, evt):
        ctrl = evt.GetEventObject()
        selObj = ctrl.GetSelectedObject()
        logging.debug('selObj: %s\n' % selObj)
        if selObj:
            self.doSetDbItem(selObj)
            self.MarkDirty()
            pub.sendMessage(pTopics.data.needsSaving, dbparent=self.dbParent)
            self.resetDependency(selObj)
        evt.Skip()

    def onOLVItemDoubleClicked(self, evt):
        logging.debug("double click: %s \n" % self._dbItemSelected)
        self.popDown()

    def onUpdateUI(self, evt):
        """Set button states, override if controller uses non
        standard buttons and/or toolbar
        """
        if self._dbItemSelected:
            if evt.GetId() == self.edit.GetId():
                evt.Enable(True)
        else:
            if evt.GetId() == self.edit.GetId():
                evt.Enable(False)

    def doSetDbItem(self, item):
        # set the variables we return
        if item:
            self._dbItemSelectedPkey = getattr(item, 'id')
        else:
            self._dbItemSelectedPkey = None

        self._dbItemSelected = item

        self.MarkDirty()

        # only set the search control
        if self._searchOnly:
            self.ClearValueAlt()
            if item:
                newAttr = getattr(item, self.dbColName)#.strip()
                self.ChangeValue(newAttr)
            self.Refresh()
            return

        else:
            self.ClearValueAlt()
            logging.debug(self.GetValue())
            if item:
                newAttr = getattr(item, self.dbColName)#.strip()
                self.ChangeValue(newAttr)
                self.setDependendControl(item)
            else:
                self.setDependendControl(None)
            logging.debug("searchCtrl value: %s\n" % self.GetValue())
            self.Refresh()
            return

    def setDependendControl(self, dbitem):
        """set controls we depend on"""
        for dctrl in self.dbScFilterCtrls:
            if dctrl:
                tctrl = getattr(self.dbParent, dctrl)
                if dbitem:
                    relDbItem = getattr(dbitem, tctrl.dbScRelName)
                else:
                    relDbItem = None
                tctrl.doSetDbItem(relDbItem)
                logging.debug(relDbItem)
                logging.debug(tctrl)

    @property
    def selectedDbItemPk(self):
        """return the Primary Key of the selected item"""
        return self._dbItemSelectedPkey

    @property
    def selectedDbItem(self):
        """return the selected dbItem"""
        return self._dbItemSelected

    @selectedDbItem.setter
    def selectedDbItem(self, item):
        """Set a dbItem"""
        if item:
            val = getattr(item, self.dbColName)
        else:
            val = ''
        pKey = getattr(item, 'id')

        logging.debug(val)
        logging.debug(item)
        self.ChangeValue(val.ljust(self.getTc()._masklength).strip())
        self._dbItemSelectedItem = item
        self._dbItemSelectedPkey = pKey

    def IsModified(self):
        return self._IsModified

    def IsValid(self):
        return self.getTc().IsValid()

    def MarkDirty(self):
        self._IsModified = True

    @property
    def dbScFilterCtrls(self):
        """Controls to use as filter criteria for this one"""
        return self._dbScFilterCtrls

    @dbScFilterCtrls.setter
    def dbScFilterCtrls(self, ctrls):
        """:param ctrls: list of controls to filter on and to set dependency"""
        self._dbScFilterCtrls = ctrls
        for item in ctrls:
            if item:
                # dependency uses the same dbParent as this controls!
                logging.debug('dbScFilter: %s' % item)
                dCtrl = getattr(self.dbParent, item)
                dCtrl.setDependency(self.Name)

    def setDependency(self, ctrl):
        """:param ctrl: a control dependend on this one, they share the
        same dbParent
        """
        self._dbScDependency += [ctrl, ]

    def resetDependency(self, dbitem):
        """Reset the dependent control's selected item to None"""
        for item in self._dbScDependency:
            ctrl = getattr(self.dbParent, item)
            ctrl.doSetDbItem(None)

    # Method overridden from PopupControl
    # This method is called just before the popup is displayed
    # Use this method to format any controls in the popup
    def formatContent(self):
        if self._ctrlInit:
            # are we depended on another control
            filter = ''
            for dctrl in self.dbScFilterCtrls:
                if dctrl:
                    tctrl = getattr(self.dbParent, dctrl)
                    if tctrl.selectedDbItemPk:
                        f = "%s.%s = '%s'" % (self.dbScTable,
                                              tctrl.dbScFkColName,
                                              tctrl.selectedDbItemPk)
                        if not filter == u'':
                            filter += ' AND '
                        filter += f
                    logging.debug('Filter: %s' % filter)
            self.olvList.filter = filter

            # Reload the OLV
            self.olvList.refreshData()
            self.olvList.setGroupCols(0)
            self.olvList.getList().SetSortColumn(0, True)
            if self._typedChar:
                self.searchCtrl.SetValue(chr(self._typedChar))
                self.searchCtrl.SetInsertionPointEnd()
            self.searchCtrl.SetFocus()

        else:
            print 'Search control is not initialized'

if __name__ == '__main__':
    #change working dir for translation files to be found, if running test
    import os
    os.chdir("..")
    import mlsrc.base_app as base_app
    import mlsrc.libui.olvdefs as olvd

    app = base_app.BaseApp(redirect=False)

    frame = wx.Frame(None, -1)
    fsizer = wx.FlexGridSizer(vgap=5, hgap=5)
    popupctrl = SearchCtrl(frame, -1)

    h, c, t = olvd.Person()
    popupctrl.InitSC(heading=h, coldesc=c, table=t, distinct=None,
                     searchOnly=True)
    popupctrl.dbColName = 'full_name'
    popupctrl.dbRelName = None
    popupctrl.dbItemName = None
    popupctrl.dbScTable = 'Person'
    popupctrl.dbScFkColName = 'fk_person_id'

    fsizer.Add(popupctrl, 1, wx.EXPAND|wx.ALL)
    fsizer.AddGrowableCol(0)

    popupctrl2 = SearchCtrl(frame, -1)
    h, c, t = olvd.Publisher()
    popupctrl2.InitSC(heading=h, coldesc=c, table=t, distinct=None,
                     searchOnly=True)
    popupctrl2.dbColName = 'name'
    popupctrl2.dbRelName = None
    popupctrl2.dbItemName = None
    popupctrl2.dbScTable = 'Publisher'
    popupctrl2.dbScFkColName = 'fk_publisher_id'

    fsizer.Add(popupctrl2, 1, wx.ALL)
    frame.SetSizer(fsizer)
    frame.Fit()
    frame.SetMinSize(frame.GetSize())
    frame.Show()
    app.SetTopWindow(frame)
    app.MainLoop()
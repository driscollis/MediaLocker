# -*- coding: utf-8 -*-#
#!/usr/bin/env python
"""The publishers controller"""

import logging

import functools

import wx

import base_list as bList
import d_publisher as dPublisher

import mlsrc.libui.commonDlgs as commonDlgs
import mlsrc.libui.olvgroup as olvg
import mlsrc.libui.olvdefs as olvd

import mlsrc.models as db

from mlsrc.mypub import pub, pTopics

########################################################################
class Publishers(bList.BaseList):
    def __init__(self, parent, **kwds):
        """The controller for publishers"""

        self.view = wx.Dialog(parent, wx.ID_ANY,
              style=wx.DEFAULT_DIALOG_STYLE,
              title="Maintain publisher information")
        self.view.SetName("dPublishers")
        super(Publishers, self).__init__(view=self.view, model="Publisher",
                                         **kwds)

        scats = ["Publisher", ]
        self.initDlgListBase(scats)

    #----------------------------------------------------------------------
    def onAddRecord(self, event):
        """
        Add a record to the database
        """
        dbItem = getattr(db, self.modelName) ()
        dlg = dPublisher.Publisher(self.view, dbItem).view
        dlg.ShowModal()
        dlg.Destroy()

    #----------------------------------------------------------------------
    def onEditRecord(self, event):
        """
        Edit a record
        """
        selectedRow = self.theOlv.getList().GetSelectedObject()
        if selectedRow == None:
            commonDlgs.showMessageDlg("No row selected!", "Error")
            return
        dlg = dPublisher.Publisher(self.view, selectedRow, title="Modify",
                                                 addModus=False).view
        dlg.ShowModal()
        dlg.Destroy()

    #----------------------------------------------------------------------
    def searchRecords(self, filterChoice, keyword):
        """
        Searches the database based on the filter chosen and the keyword
        given by the user
        """
        session = wx.GetApp().session
        model = getattr(db, self.modelName)

        result = None
        if filterChoice == "Publisher":
            qry = session.query(model)
            logging.debug(qry)
            result = qry.filter(db.Publisher.name.contains('%s' % keyword))

            result = result.all()

        logging.debug(result)
        return result


#----------------------------------------------------------------------
if __name__ == '__main__':
    import mlsrc.base_app as base_app

    app = base_app.BaseApp(redirect=False)

    dlg = Publishers(None).view
    try:
        dlg.ShowModal()
    finally:

        dlg.Destroy()
    app.MainLoop()
    

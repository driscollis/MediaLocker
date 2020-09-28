# -*- coding: utf-8 -*-#
#!/usr/bin/env python
"""The base controller, all other controllers will inherit from this"""

import logging

import wx
# needs to be changed to fully support i18n
_ = wx.GetTranslation

import mlsrc.models as db

from mlsrc.mypub import pub, pTopics

__all__ = ['BaseController', '_', 'db']

class BaseController(wx.EvtHandler):
    def __init__(self, view=None, model=None, **kwds):
        """Base controller doing all the setup of controls, handling the default
        button events, and persistance of the dialog/frame.
        """

        self.view = view
        # mainly for debugging, e.g. with WIT
        self.view._Controller = self
        
        self.view.Bind(wx.EVT_CLOSE, self.onClose)

        self.dbParent = self
        self.initModel(model)

        self._InvalidControls = []

        pub.subscribe(self.trackInvalidControls, pTopics.validateControl)

    #----------------------------------------------------------------------
    def onClose(self, evt):
        """Close actions
        
        - unsubscribe pubsub
        """
        pub.unsubAll()
        evt.Skip()

    #----------------------------------------------------------------------
    def initModel(self, model):
        """Initialize the model, some variables and the dbItem

        :param model: model name, e.g. "Book"
        """

        self.modelName = model
        self.dbItem = None

    #----------------------------------------------------------------------
    def addRecord(self, dbitem):
        """Add a record

        :param dbitem: an SA db model instance
        """
        # commit data to database
        session = wx.GetApp().session
        session.add(dbitem)
        session.commit()

    #----------------------------------------------------------------------
    def deleteRecord(self, pkey):
        """
        Delete a record from the database

        :param pkey: Primary key of item to delete
        """
        session = wx.GetApp().session
        record = session.query(getattr(db, self.modelName)).get(pkey)
        session.delete(record)
        session.commit()

    #----------------------------------------------------------------------
    def editRecord(self):
        """
        Commit changed record to database
        """
        session = wx.GetApp().session
        session.commit()

    #----------------------------------------------------------------------
    def getAllRecords(self):
        """
        Get all records and return them
        """
        session = wx.GetApp().session
        result = session.query(getattr(db, self.modelName)).all()
        return result

    #----------------------------------------------------------------------
    def trackInvalidControls(self, dbparent, ctrl, msg=None):
        """Track controls which are not valid"""
        if self.dbParent == dbparent:
            self._InvalidControls.append(ctrl.MyLabel)
        logging.debug('controls are invalid: %s' % self._InvalidControls)

    #----------------------------------------------------------------------
    def validateControls(self):
        """Validate all controls and display an error if any don't pass"""
        pub.sendMessage(pTopics.statusText, msg='')
        self._InvalidControls = []

        self.view.Validate()

        if self._InvalidControls > []:
            ctrls = u''
            for ctrl in self._InvalidControls:
                ctrls += ctrl
                ctrls += u', '

            msg = (_(u'Following fields are not valid: %s') % ctrls.rstrip(', '))
            wx.Bell()
            pub.sendMessage(pTopics.statusText, msg=msg)
        else:
            return True

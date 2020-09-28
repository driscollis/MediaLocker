# -*- coding: utf-8 -*-#
#!/usr/bin/env python
"""base_app for MediaLocker"""

import logging
format = '%(name)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s'
logging.basicConfig(format=format, level=logging.DEBUG)

import os

import wxversion
try:
    wxversion.ensureMinimal('2.8')
except wxversion.AlreadyImportedError:
    # should only happen during testing, i.e. when not running main script
    pass

import wx
import wx.lib.mixins.inspection as wit

import mlsrc.controllers.base as cBase
import mlsrc.models as db

class BaseApp(wx.App, wit.InspectionMixin):
    def OnInit(self):
        self.Init() # WIT
        
        self._dataNeedsSaving = False
        self.baseDir, f = os.path.split(__file__)
        # data folder is one level up
        pPath, pFolder = os.path.split(self.baseDir)
        dbFolder = os.path.join(pPath, 'data')
        # define the name you want to use for your db here or get it
        # from some configuration file
        dbFile = os.path.abspath(os.path.join(dbFolder, 'devdata.sqlite'))
        # define the db driver name here or get it from a configuration file
        dbDriver = "sqlite"
        dbUrl = db.sa.engine.url.URL(dbDriver, database=dbFile)
        logging.debug(dbUrl)

        self.session = self.connectToDatabase(dbUrl)

        return True

    #----------------------------------------------------------------------
    def connectToDatabase(self, dburl):
        """
        Connect to our database and return a Session object

        :param dburl: a valid SQLAlchemy URL string
        """

        engine = db.sa.create_engine(dburl, echo=False)
        db.init_model(engine)
        session = db.DBSession()
        self.setupDatabase(session, engine)
        return session

    #----------------------------------------------------------------------
    def setupDatabase(self, session, engine):
        """Setup the db, note that this will not upgrade already existing tables"""
        db.metadata.create_all(engine)
        logging.debug("db created")

        result = session.query(db.Olvlist).first()
        if not result:
            self.createOLVEntries(session)
            logging.debug('olv entries created')

    #----------------------------------------------------------------------
    def createOLVEntries(self, session):
        """Create entires in Olvlist table for olv.ColumnDefn"""
        olvEntries = {}
        olvEntries[u'Book'] = [
            [u'publisher', 0, 150, u'publisher', u'name',
                    None, None, False, u'', u'left', u'', u''],
            [u'title', 0, 150, None, u'title',
                    None, None, False, u'', u'left', u'', u''],
            [u'author', 1, 150, u'person', u'full_name',
                    None, None, False, u'', u'left', u'', u''],
            [u'isbn', 2, 40, None, u'isbn',
                    None, None, False, u'', u'left', u'', u'']]

        olvEntries[u'Person'] = [
            [u'first_name', 0, 150, None, u'first_name',
                    None, None, False, u'', u'left', u'', u''],
            [u'last_name', 0, 150, None, u'last_name',
                    None, None, False, u'', u'left', u'', u'']]

        olvEntries[u'Publisher'] = [
            [u'name', 0, 150, None, u'name',
                    None, None, False, u'', u'left', u'', u'']]

        for k in olvEntries:
            self.doCreateOLVEntry(session, k, olvEntries[k])

    #----------------------------------------------------------------------
    def doCreateOLVEntry(self, session, table, cols):
        """Do the actual creation in the database"""
        for col in cols:
            olve = db.Olvlist(tablename=table, colname=col[0],
                           colno=col[1], width=col[2], valuerel=col[3],
                           valuecol=col[4],
                           checkstatrel=col[5], checkstatcol=col[6],
                           colgroup=col[7], groupkeyg=col[8],
                           align=col[9],
                           stringconv=col[10],
                           imageg=col[11])
            if col[2] == 0:
                olve.colshow = False

            session.add(olve)
        session.commit()

    def dataCheckDirty(self):
        """Check if there is unsaved data.

        This should be called by e.g. the tool bar buttons which load new data
        or by the objectlistview before loading a new item.

        Return value:
        True if data needs saving
        False if there is no data to save, or if user selected to loose
        the changes they made
        """
        if self._dataNeedsSaving:
            msg = _(u'You entered data which is not saved!\n\nClick on "No" to return and save it\n\nor on "Yes" to quit and lose it!')
            caption = _(u'Unsaved data warning!')
            dlg = wx.MessageDialog(None, msg, caption,
                                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
            try:

                result = dlg.ShowModal()
                if result == wx.ID_NO:
                    # caller needs to do necessary action to allow user to save data
                    return True
                else:
                    self.ds.rollback()
                    # need to reset the flag
                    pub.sendMessage(pub.topics.data.commitDone,
                                    dbparent=self.db)
                    pub.sendMessage(pub.topics.data.data.rollbackDone)
                    # we rolled back, caller can continue
                    return False
            finally:
                dlg.Destroy()
        else:
            return False

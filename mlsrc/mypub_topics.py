# -*- coding: utf-8 -*-#
# Copyright:   see cr_and_license.txt in the doc folder
# License:     see cr_and_license.txt in the doc folder
#-----------------------------------------------------------------------------
#!/usr/bin/env python
"""The topic tree for The Wine Cellar Book version 4"""

class data:
    """To flag about state of data"""

    class needsSaving:
        """there is un-saved data

        :param dbparent: parent holding the dbItem
        """

        def msgDataSpec(dbparent):
            """params doc on class above"""

    class commitDone:
        """all data is commited

        :param dbparent: parent holding the dbItem
        """

        def msgDataSpec(dbparent):
            """params doc on class above"""

    class rollbackDone:
        """all data is rolled back

        :param dbparent: parent holding the dbItem
        """

        def msgDataSpec(dbparent):
            """params doc on class above"""

    class itemAdded:
        """an item was added

        :param dbparent: parent holding the dbItem
        :param dbitem: the item added
        """

        def msgDataSpec(dbparent, dbitem):
            """params doc on class above"""

    class itemModified:
        """an item was added

        :param dbparent: parent holding the dbItem
        :param dbitem: the item added
        """

        def msgDataSpec(dbparent, dbitem):
            """params doc on class above"""

    class itemDeleted:
        """an item was added

        :param dbparent: parent holding the dbItem
        :param dbitem: the item added
        """

        def msgDataSpec(dbparent, dbitem):
            """params doc on class above"""


class statusText:
    """a status text needs to be shown

    :param msg: the msg to be shown
    :param flag: wx.ICON_something, it is assumed that the listing handler
        will default to wx.ICON_INFORMATION, depending on where the statusText
        is shown it could also ignore this flag (e.g. when using wx.StatusText)
    """

    def msgDataSpec(msg, flag=None):
        """params doc defined on class above"""

class searchControl:
    """search controls, a sophisticated replacement for combobox,
    for e.g. masterdata
    """

    class updated:
        """database table was updated

        :param table: the database table name, use base table for localized
        """

        def msgDataSpec(tablename):
            """params doc defined on class above"""

class validateControl:
    """a control did not pass validation

    :param dbparent: parent holding the dbItem
    :param ctrl: control
    :param msg: an optional message
    """

    def msgDataSpec(dbparent, ctrl, msg=None):
        """params doc defined on class above"""

#--------------------------------------------------------
# Following topics are just here for the test in mypub.py
#--------------------------------------------------------
class topic_1:
    """
    Explain when topic_1 should be used
    """

    def msgDataSpec(msg):
        """
        - msg: a text string message for recipient
        """

    class subtopic_11:
        """
        Explain when subtopic_11 should be used
        """

        def msgDataSpec(msg, msg2, extra=None):
            """
            - extra: something optional
            - msg2: a text string message #2 for recipient"""


class topic_2:
    """
    Some something useful about topic2
    """

    def msgDataSpec(msg=None):
        """
        - msg: a text string
        """

    class subtopic_21:
        """
        description for subtopic 21
        """

        def msgDataSpec(msg, arg1=None):
            """
            - arg1: UNDOCUMENTED
            """
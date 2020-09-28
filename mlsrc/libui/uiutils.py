# -*- coding: utf-8 -*-#
#!/usr/bin/env python
"""UI utilities"""
import logging

import os

import wx
import wx.lib.agw.aui as aui

# needs to be changed to fully support i18n
_ = wx.GetTranslation

import buttons
import searchctrl
import mlsrc.controllers.validators as validators

import olvdefs as olvd

from mlsrc.mypub import pub, pTopics

# the definition of all possible keys used for a control
# TODO: document what goes into each!!!
ctrlDefaultDict = {'cType': 'tc', 'desc': '',
                   'helpt': '',
                   'toolt': '',
                   'dbColName': '',
                   'dbLength': '',
                   'emptyInvalid': False,
                   'allowNegative': False,
                   'integerWidth': None,
                   'fractionWidth': None,
                   'readOnly': False,
                   'dbRelName': None,
                   'dbItemName': None,
                   'localize': False,
                   'cName': '',
                   'sTableName': None,
                   'sFkColName': None,
                   'sRelName': None,
                   'sFilterCtrls': [None, ],
                   'sDistinct': None,
                   'sJoinSA': [],
                   'sMaintDlg': None,
                   'expand': False,
                   'proportion': 0,
                   'autoformat': None,
                   'mask': '',
                   'formatcodes': "F_S>",
                   'cbChoices': [u'', ],
                  }

def defaultCtrlDict(ctrls):
    """Fill ctrl dict with any missing keys and default values"""
    ctrlsU = []
    for item in ctrls:
        bd = dict(ctrlDefaultDict)
        bd.update(item)
        ctrlsU += [bd, ]
    return ctrlsU

def doCreateButtons(parent, pane, blist):
    """Create buttons based on definition in blist

    :param parent: parent, see setattr below
    :param pane: pane to hold buttons
    :param blist: list of buttons to create

    blist = [['btnname', wx.ID_ (ANY or a Stock ID),
             'btnlabel',
             'btnhelptext',
             'btntooltip',
             'btnevthandler',
             'bitmap],
             ]
    """
    bStyle = "bmp"
    for b in blist:
        if b[6]:
            bmp = getImage(b[6])
        else:
            bmp = wx.NullBitmap

        if bStyle == "aqua":
            btn = buttons.AquaButton(parent=pane, id=b[1], bitmap=bmp,
                            label=b[2], name=b[0])
        elif bStyle == "std":
            btn = buttons.Button(parent=pane, id=b[1],
                            label=b[2], name=b[0])
            btn.SetBitmap(bmp, wx.RIGHT)
        elif bStyle == "bmp":
            btn = buttons.BitmapButton(parent=pane, id=b[1], bitmap=bmp,
                            name=b[0])

        btn.SetHelpText(b[3])
        btn.SetToolTipString(b[4])
        btn.Bind(wx.EVT_BUTTON, b[5])
        setattr(parent, b[0], btn)


def getImage(imgstr, imgfld=False, asicon=False):
    """Get image as Bitmap or as Icon

    "icons" folder contains non application specific stuff
    "images" folder contains TWCB specific images

    :param imgstr: image name as a string, inclusive extension
    :param imgfld: True, get from images folder,
     False, get from icons folder
    :param asicon: True return wx.Icon, False scalled bitmap
    """
    if imgfld:
        bDir = os.path.join(wx.GetApp().baseDir, "images")
    else:
        bDir = os.path.join(wx.GetApp().baseDir, "icons")
    imgFile = os.path.join(bDir, imgstr)
    if os.path.isfile(imgFile):
        if asicon:
            bmpTmp = wx.Image(imgFile, wx.BITMAP_TYPE_ANY)
            if "wxMSW" in wx.PlatformInfo:
                bmpTmp = bmpTmp.Scale(16, 16)
            elif "wxGTK" in wx.PlatformInfo:
                bmpTmp = bmpTmp.Scale(22, 22)
            # wxMac can be any size upto 128x128,
            # so leave the source img alone....
            myicon = wx.IconFromBitmap(bmpTmp.ConvertToBitmap() )
            return myicon
        else:
            return wx.Image(imgFile,
                wx.BITMAP_TYPE_ANY).Rescale(16, 16).ConvertToBitmap()
    else:
        logging.error("image not found: %s" % imgFile)


def doCreateSearchControl(parent, tpane, ctrl, searchonly=False):
    """Create a SearchControl

    :param parent: parent for control, see setattr below
    :param tpane: the pane for the control
    :param ctrl: a dict with definitions for the control, see defaultCtrlDict
    :param searchonly: True only use for search/filtering do not update dbItem
    """
    tctrl = searchctrl.SearchCtrl(tpane, wx.ID_ANY, name=ctrl['cName'])
    tctrl.Disable()

    if ctrl['dbItemName']:
        tctrl.SetValidator(validators.ValSC())

    tctrl.getTc().SetCtrlParameters(mask = u"*{%i}" % ctrl['dbLength'],
                            formatcodes = ctrl['formatcodes'],
                            includeChars = u'-',
                            emptyInvalid = ctrl['emptyInvalid'])

    tctrl.SetName(ctrl['cName'])
    tctrl.MyLabel = ctrl['desc']
    tt = _(u"Click on the down arrow to select entry.")
    he = _(u"Click on the down arrow to select entry or \
start typing to initiate the selection.")
    if ctrl['toolt'] > '':
        tt = ctrl['toolt']
    if ctrl['helpt'] > '':
        he = ctrl['helpt']

    tctrl.SetToolTipString(tt)
    tctrl.getTc().SetToolTipString(tt)
    tctrl.SetHelpText(he)
    # following requires that pane is a sized_controls.sized_panel
#    tctrl.SetSizerProps(valign='center', border=(['all'], 0))
    tctrl.dbParent = parent.dbParent
    tctrl.dbColName = ctrl['dbColName']
    tctrl.dbRelName = ctrl['dbRelName']
    tctrl.dbItemName = ctrl['dbItemName']
    tctrl.dbScTable = ctrl['sTableName']
    tctrl.dbScFkColName = ctrl['sFkColName']
    tctrl.dbScRelName = ctrl['sRelName']
    tctrl.dbScFilterCtrls = ctrl['sFilterCtrls']
    tctrl.dbScJoinSA = ctrl['sJoinSA']
    tctrl.scMaintDlg = ctrl['sMaintDlg']

    h, c, t = getattr(olvd, ctrl['sTableName'])()
    tctrl.initSC(heading=h, coldesc=c, table=t, distinct=ctrl['sDistinct'],
                 searchOnly=searchonly)

    # save a variable
    setattr(parent, ctrl['cName'], tctrl)

    return tctrl

def doCreateToolbarItems(parent, tb, tools):
    """Create tool bar items"""
    for b in tools:
        if b[6]:
            bmp = getImage(b[6])
        else:
            bmp = wx.NullBitmap

        if b[7] == aui.ITEM_SPACER:
            tb.AddSpacer(10)
        elif b[7] == aui.ITEM_SEPARATOR:
            tb.AddSeparator()
        else:
            setattr(parent, b[0], b[1])
            parent.Bind(wx.EVT_TOOL, b[5], id=b[1])
            tb.AddTool(b[1], b[2], bmp, disabled_bitmap=wx.NullBitmap,
                    kind=b[7],
                    short_help_string=b[4], long_help_string=b[4],
                    client_data=None, target=None)

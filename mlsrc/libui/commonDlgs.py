# -*- coding: utf-8 -*-#
#!/usr/bin/env python
# commonDlgs.py

import wx

#----------------------------------------------------------------------
def showMessageDlg(message, caption, flag=wx.ICON_ERROR|wx.OK):
    """"""
    msg = wx.MessageDialog(None, message=message,
                           caption=caption, style=flag)
    msg.ShowModal()
    msg.Destroy()
# -*- coding: utf-8 -*-#
#!/usr/bin/env python
"""A view constants"""
import wx

__ALL__ = ['dlgFontFam', 'dlgFontHeader', 'dlgFontSt']

# can not create the font here directly as wx.APP has to be instantiated first
dlgFontFam = wx.SWISS
dlgFontHeader = 12
dlgFontSt = 10
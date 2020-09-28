# -*- coding: utf-8 -*-#
#!/usr/bin/env python
"""the custom textctrl's we use"""
import logging

import wx
import wx.lib.masked.maskededit

import mixins as mix

class TextCtrl(wx.TextCtrl, mix.DbMixin, mix.LabelMixin):
    """TextCtrl with some db variables mixed in"""
    def __init__(self, parent, **kwds):
        super(TextCtrl, self).__init__(parent, **kwds)
        mix.DbMixin.__init__(self)
        mix.LabelMixin.__init__(self)


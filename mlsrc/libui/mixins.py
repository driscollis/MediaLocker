# -*- coding: utf-8 -*-#
#!/usr/bin/env python
"""Mixin's for different ui controls, e.g. textctrl, checkbox etc"""

class DbMixin:

    def __init__(self, **kwds):
        """Mixin to initialize db related variables"""

        # db enabling, but they need to be set correctly when using ctrl
        self.dbParent = self
        self.dbColName = ''
        self.dbRelName = ''
        self.dbItemName = ''


class LabelMixin:

    def __init__(self, **kwds):
        """Mixin to provide a MyLabel property"""
        self._myLabel = u""

    @property
    def MyLabel(self):
        """wx.Windows has a Label, but its usage is different based on
        control, as we use it in exception we want to be able to set our
        own independent of the controls usage
        """
        if self._myLabel == u"":
            self._myLabel = self.GetLabel()
        return self._myLabel

    @MyLabel.setter
    def MyLabel(self, label):
        self._myLabel = label
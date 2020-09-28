# -*- coding: utf-8 -*-#
#!/usr/bin/env python
"""A button based on Aquabutton, at least for the moment???"""
import logging

import wx
import wx.lib.agw.aquabutton as AB

class AquaButton(AB.AquaButton):
    """AquaButton"""
    def __init__(self, **kwargs):
        super(AquaButton, self).__init__(**kwargs)

        bgColour = wx.Colour(128, 0, 64)
        self.SetBackgroundColour(bgColour)
        self.SetHoverColour(self.LightColour(bgColour, 30))
        self.SetDisabledColour(self.LightColour(bgColour, 70))
        self.SetForegroundColour(wx.BLACK)

        # TODO: any other option to show has focus???!!!
        self.SetPulseOnFocus(True)


class Button(wx.Button):
    """Standard wx.Button"""
    def __init__(self, **kwargs):
        super(Button, self).__init__(**kwargs)


class BitmapButton(wx.BitmapButton):
    """Standard wx.Button"""
    def __init__(self, **kwargs):
        super(BitmapButton, self).__init__(**kwargs)

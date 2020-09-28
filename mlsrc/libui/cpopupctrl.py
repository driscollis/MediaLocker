# -*- coding: utf-8 -*-#
# A popup control based on code from the wxPython demo
#
# but we use wx.lib.sized_controls, which does nicer sizing handling
#-----------------------------------------------------------------------------
#!/usr/bin/env python
import logging

import wx
import wx.lib.masked
import wx.lib.sized_controls as sc
from wx.lib.buttons import GenButtonEvent

from mixins import LabelMixin

class PopButton(wx.PyControl):
    def __init__(self, *args, **kwds):
        super(PopButton, self).__init__(*args, **kwds)

        self._up = True
        self._didDown = False

        self.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.onLeftUp)
        self.Bind(wx.EVT_MOTION, self.onMotion)
        self.Bind(wx.EVT_PAINT, self.onPaint)

        self.myMinSize = wx.Size(20, 23)
        self.SetMinSize(self.myMinSize)

    def notify(self):
        evt = GenButtonEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.GetId())
        evt.SetIsDown(not self._up)
        evt.SetButtonObj(self)
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

    def OnEraseBackground(self, event):
        pass

    def onLeftDown(self, event):
        if not self.IsEnabled():
            return
        self._didDown = True
        self._up = False
        self.CaptureMouse()
        self.GetGrandParent().textCtrl.SetFocus()
        self.Refresh()
        event.Skip()

    def onLeftUp(self, event):
        if not self.IsEnabled():
            return
        if self._didDown:
            self.ReleaseMouse()
            if not self._up:
                self.notify()
            self._up = True
            self.Refresh()
            self._didDown = False
        event.Skip()

    def onMotion(self, event):
        if not self.IsEnabled():
            return
        if event.LeftIsDown():
            if self._didDown:
                x,y = event.GetPosition()
                w,h = self.GetClientSize()
                if self._up and x<w and x>=0 and y<h and y>=0:
                    self._up = False
                    self.Refresh()
                    return
                if not self._up and (x<0 or y<0 or x>=w or y>=h):
                    self._up = True
                    self.Refresh()
                    return
        event.Skip()

    def onPaint(self, event):
        dc = wx.BufferedPaintDC(self)
        if self._up:
            flag = wx.CONTROL_CURRENT
        else:
            flag = wx.CONTROL_PRESSED
        wx.RendererNative.Get().DrawComboBoxDropButton(self, dc,
                                            self.GetClientRect(), flag)

    def DoGetBestSize(self):
        # TODO: probably should calculate this no????
        # best size for the button
        return self.myMinSize


#---------------------------------------------------------------------------


# Tried to use wxPopupWindow but the control misbehaves on MSW
# lets see if SizedDialog will work
# needs testing on e.g. nix?
class PopupDialog(sc.SizedDialog, LabelMixin):
    def __init__(self, *args, **kwds):
        if 'content' in kwds:
            content = kwds.pop('content')
        else:
            content = None
        if 'style' in kwds:
            kwds['style'] |= wx.BORDER_SIMPLE|wx.TAB_TRAVERSAL|wx.STAY_ON_TOP
        else:
            kwds['style'] = wx.BORDER_SIMPLE|wx.TAB_TRAVERSAL|wx.STAY_ON_TOP

        super(PopupDialog, self).__init__(*args, **kwds)
        LabelMixin.__init__(self)

        self.pane = self.GetContentsPane()

        self.popCtrl = self.GetParent()
        self.win = wx.Window(self.pane, id=wx.ID_ANY, name='win')
        self.win.SetSizerProps(expand=True, proportion=1)

        if content:
            self.setContent(content)

        self.Layout()
        self.Fit()

    def setContent(self, content):
        self.content = content
        self.content.Reparent(self.win)
        self.win.SetClientSize(self.content.GetSize())
        self.SetSize(self.win.GetSize())

        self.content.Show(True)

    def display(self):
        """position popup control depending on where we are on the screen"""
        logging.debug('do display')
        pos = self.popCtrl.ClientToScreen( (0,0) )
        dSize = wx.GetDisplaySize()
        selfSize = self.GetSize()
        tcSize = self.popCtrl.GetSize()

        pos.x -= (selfSize.width - tcSize.width) / 2
        if pos.x + selfSize.width > dSize.width:
            pos.x = dSize.width - selfSize.width
        if pos.x < 0:
            pos.x = 0

        pos.y += tcSize.height
        if pos.y + selfSize.height > dSize.height:
            pos.y = dSize.height - selfSize.height
        if pos.y < 0:
            pos.y = 0

        self.Move(pos)

        self.popCtrl.formatContent()

        self.ShowModal()


#---------------------------------------------------------------------------

class PopupControl(wx.PyControl, LabelMixin):
    def __init__(self, *args, **kwds):
        if 'style' in kwds:
            kwds['style'] |= wx.BORDER_NONE
        else:
            kwds['style'] = wx.BORDER_NONE

        super(PopupControl, self).__init__(*args, **kwds)
        LabelMixin.__init__(self)

        cSizer = wx.BoxSizer()
        self.cPanel = sc.SizedPanel(self, wx.ID_ANY)
        cSizer.Add(self.cPanel, 1, wx.EXPAND)
        self.SetSizer(cSizer)

        self.cPanel.SetSizerType('grid', {'cols': 2,})
        self.textCtrl = wx.lib.masked.TextCtrl(self.cPanel, wx.ID_ANY,
                                               useFixedWidthFont=False)
        self.textCtrl.SetCtrlParameters(mask = u"*{%i}" % 20,
                                formatcodes = "F_S>",
                                includeChars = u'-',
                                emptyInvalid = False)
        # expand and prop grow it in height!!!!????
        self.textCtrl.SetSizerProps(proportion=1, expand=True,
                                    valign="centre", border=('all', 0))
        self.bCtrl = PopButton(self.cPanel, wx.ID_ANY, style=wx.BORDER_NONE)
        # NOTE: bug in sized controls, below gives wx.ALL border
        self.bCtrl.SetSizerProps(border=(['left', ], 3))
        self.cPanel.SetSizerProps({'growable_col': (0, 1),})

        self.pop = None
        self.content = None

        self.bCtrl.Bind(wx.EVT_BUTTON, self.onButton, self.bCtrl)
        self.Bind(wx.EVT_SET_FOCUS, self.onFocus)
        self.Bind(wx.EVT_SIZE, self.onSize)

        self.cPanel.Layout()
        self.Layout()
        self.Fit()

    def DoGetBestSize(self):
        self.cPanel.Layout()
        self.Layout()
        bSize = self.cPanel.GetBestSize()
        return bSize

    def onSize(self, evt):
        self.cPanel.Layout()
        self.Layout()

    def onFocus(self, evt):
        # embedded control should get focus on TAB keypress
        self.textCtrl.SetFocus()
        evt.Skip()

    def onButton(self, evt):
        logging.debug('button')
        self.doPop()

    def doPop(self):
        logging.debug('dopop')
        if not self.pop:
            if self.content:
                self.pop = PopupDialog(self, content=self.content)
                del self.content
            else:
                print 'No Content to pop'
        if self.pop:
            self.pop.display()

    def Enable(self, flag):
        self.textCtrl.Enable(flag)
        self.bCtrl.Enable(flag)

    def getTc(self):
        return self.textCtrl

    def setPopupContent(self, content):
        if not self.pop:
            self.content = content
            self.content.Show(False)
        else:
            self.pop.setContent(content)

    def formatContent(self):
        raise NotImplementedError("FormatContent needs to be overiden")

    def popDown(self):
        if self.pop:
            self.pop.EndModal(True)

    def SetValue(self, value):
        """Just do it on the textCtrl"""
        tc = self.textCtrl
        if value:
            tc.SetValue(value.ljust(tc._masklength).strip())
        else:
            tc.ClearValue()

    def ChangeValue(self, value):
        """Just do it on the textCtrl"""
        tc = self.textCtrl
        if value:
            tc.ChangeValue(value.ljust(tc._masklength).strip())
        else:
            tc.ClearValue()

    def ClearValue(self):
        """Just do it on the textCtrl"""
        self.textCtrl.ClearValue()

    def ClearValueAlt(self):
        """Just do it on the textCtrl"""
        self.textCtrl.ClearValueAlt()

    def GetValue(self):
        """Just do it on the textCtrl"""
        return self.textCtrl.GetValue()

    def SetFont(self, font):
        """Just do it on the textCtrl"""
        self.textCtrl.SetFont(font)

    def GetFont(self):
        """Just do it on the textCtrl"""
        return self.textCtrl.GetFont()

    def Refresh(self):
        """Just do it on the textCtrl"""
        self.textCtrl.Refresh()
        
# an alias
PopupCtrl = PopupControl


if __name__ == '__main__':
    #change working dir for translation files to be found, if running test
    import os
    os.chdir("..")
    import mlsrc.base_app as base_app
    app = base_app.BaseApp(redirect=False)

    frame = wx.Frame(None, -1)
    fsizer = wx.BoxSizer()
    popupctrl = PopupControl(frame, -1)
    fsizer.Add(popupctrl, 1, wx.EXPAND|wx.ALL)
    frame.SetSizer(fsizer)
    frame.Fit()
    frame.SetMinSize(frame.GetSize())
    frame.Show()
    app.SetTopWindow(frame)
    app.MainLoop()


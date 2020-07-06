#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

"""utility classes for the Builder
"""

from __future__ import absolute_import, division, print_function

import os
from builtins import object

from wx.lib.agw.aui.aui_constants import *
from wx.lib.agw.aui.aui_utilities import IndentPressedBitmap, ChopText, TakeScreenShot
import sys
import wx
import wx.lib.agw.aui as aui
from wx.lib import platebtn
from psychopy import logging
from . import pavlovia_ui
from .icons import combineImageEmblem
from .themes import ThemeMixin
from psychopy.tools.versionchooser import _translate


class FileDropTarget(wx.FileDropTarget):
    """On Mac simply setting a handler for the EVT_DROP_FILES isn't enough.
    Need this too.
    """

    def __init__(self, targetFrame):
        wx.FileDropTarget.__init__(self)
        self.target = targetFrame

    def OnDropFiles(self, x, y, filenames):
        logging.debug(
            'PsychoPyBuilder: received dropped files: %s' % filenames)
        for fname in filenames:
            if fname.endswith('.psyexp') or fname.lower().endswith('.py'):
                self.target.fileOpen(filename=fname)
            else:
                logging.warning(
                    'dropped file ignored: did not end in .psyexp or .py')
        return True


class WindowFrozen(object):
    """
    Equivalent to wxWindowUpdateLocker.

    Usage::

        with WindowFrozen(wxControl):
            update multiple things
        # will automatically thaw here

    """

    def __init__(self, ctrl):
        self.ctrl = ctrl

    def __enter__(self):  # started the with... statement
        # Freeze should not be called if platform is win32.
        if sys.platform == 'win32':
            return self.ctrl

        # check it hasn't been deleted
        #
        # Don't use StrictVersion() here, as `wx` doesn't follow the required
        # numbering scheme.
        if self.ctrl is not None and wx.__version__[:3] <= '2.8':
            self.ctrl.Freeze()
        return self.ctrl

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Thaw should not be called if platform is win32.
        if sys.platform == 'win32':
            return
        # check it hasn't been deleted
        if self.ctrl is not None and self.ctrl.IsFrozen():
            self.ctrl.Thaw()


def getSystemFonts(encoding='system', fixedWidthOnly=False):
    """Get a list of installed system fonts.

    Parameters
    ----------
    encoding : str
        Get fonts with matching encodings.
    fixedWidthOnly : bool
        Return on fixed width fonts.

    Returns
    -------
    list
        List of font facenames.

    """
    fontEnum = wx.FontEnumerator()

    encoding = "FONTENCODING_" + encoding.upper()
    if hasattr(wx, encoding):
        encoding = getattr(wx, encoding)

    return fontEnum.GetFacenames(encoding, fixedWidthOnly=fixedWidthOnly)


class PsychopyToolbar(wx.ToolBar, ThemeMixin):
    """Toolbar for the Builder/Coder Frame"""
    def __init__(self, frame):
        wx.ToolBar.__init__(self, frame)
        self.frame = frame
        # Configure toolbar appearance
        self.SetWindowStyle(wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT | wx.TB_NODIVIDER)
        #self.SetBackgroundColour(ThemeMixin.appColors['frame_bg'])
        # Set icon size (16 for win/linux small mode, 32 for everything else
        if (sys.platform == 'win32' or sys.platform.startswith('linux')) \
                and not self.frame.appPrefs['largeIcons']:
            self.iconSize = 16
        else:
            self.iconSize = 32  # mac: 16 either doesn't work, or looks bad
        self.SetToolBitmapSize((self.iconSize, self.iconSize))
        # OS-dependent tool-tips
        ctrlKey = 'Ctrl+'
        if sys.platform == 'darwin':
            ctrlKey = 'Cmd+'
        # keys are the keyboard keys, not the keys of the dict
        self.keys = {k: self.frame.app.keys[k].replace('Ctrl+', ctrlKey)
                for k in self.frame.app.keys}
        self.keys['none'] = ''
        self.makeTools()

    def makeTools(self):
        frame = self.frame
        # Create tools
        cl = frame.__class__.__name__
        pavButtons = pavlovia_ui.toolbar.PavloviaButtons(frame, toolbar=self, tbSize=self.iconSize)
        if frame.__class__.__name__ == 'BuilderFrame':
            self.AddPsychopyTool('filenew', 'New', 'new',
                            "Create new experiment file",
                            self.frame.app.newBuilderFrame) # New
            self.AddPsychopyTool('fileopen', 'Open', 'open',
                                 "Open an existing experiment file",
                                 self.frame.fileOpen)  # Open
            self.frame.bldrBtnSave = \
                self.AddPsychopyTool('filesave', 'Save', 'save',
                                 "Save current experiment file",
                                 self.frame.fileSave)  # Save
            self.AddPsychopyTool('filesaveas', 'Save As...', 'saveAs',
                                 "Save current experiment file as...",
                                 self.frame.fileSaveAs)  # SaveAs
            self.frame.bldrBtnUndo = \
                self.AddPsychopyTool('undo', 'Undo', 'undo',
                                 "Undo last action",
                                 self.frame.undo)  # Undo
            self.frame.bldrBtnRedo = \
                self.AddPsychopyTool('redo', 'Redo', 'redo',
                                 "Redo last action",
                                 self.frame.redo)  # Redo
            self.AddSeparator() # Seperator
            self.AddPsychopyTool('monitors', 'Monitor Center', 'none',
                                 "Monitor settings and calibration",
                                 self.frame.app.openMonitorCenter)  # Monitor Center
            self.AddPsychopyTool('cogwindow', 'Experiment Settings', 'none',
                                 "Edit experiment settings",
                                 self.frame.setExperimentSettings)  # Settings
            self.AddSeparator()
            self.AddPsychopyTool('compile', 'Compile Script', 'compileScript',
                                 "Compile to script",
                                 self.frame.compileScript)  # Compile
            self.frame.bldrBtnRun = self.AddPsychopyTool(('run', 'runner'), 'Run', 'runScript',
                                 "Run experiment",
                                 self.frame.runFile)  # Run
            pavButtons.addPavloviaTools()
        elif frame.__class__.__name__ == 'CoderFrame':
            self.AddPsychopyTool('filenew', 'New', 'new',
                                 "Create new experiment file",
                                 self.frame.app.newBuilderFrame)  # New
            self.AddPsychopyTool('fileopen', 'Open', 'open',
                                 "Open an existing experiment file",
                                 self.frame.fileOpen)  # Open
            self.frame.cdrBtnSave = \
                self.AddPsychopyTool('filesave', 'Save', 'save',
                                     "Save current experiment file",
                                     self.frame.fileSave)  # Save
            self.AddPsychopyTool('filesaveas', 'Save As...', 'saveAs',
                                 "Save current experiment file as...",
                                 self.frame.fileSaveAs)  # SaveAs
            self.frame.cdrBtnUndo = \
                self.AddPsychopyTool('undo', 'Undo', 'undo',
                                     "Undo last action",
                                     self.frame.undo)  # Undo
            self.frame.cdrBtnRedo = \
                self.AddPsychopyTool('redo', 'Redo', 'redo',
                                     "Redo last action",
                                     self.frame.redo)  # Redo
            self.AddSeparator()  # Seperator
            self.AddPsychopyTool('monitors', 'Monitor Center', 'none',
                                 "Monitor settings and calibration",
                                 self.frame.app.openMonitorCenter)  # Monitor Center
            self.AddPsychopyTool('color', 'Color Picker', 'none',
                                 "Color Picker -> clipboard",
                                 self.frame.app.colorPicker)
            self.AddSeparator()
            self.frame.cdrBtnRun = self.AddPsychopyTool(('run', 'runner'), 'Run', 'runScript',
                                                         "Run experiment",
                                                         self.frame.runFile)  # Run
            self.AddSeparator()
            pavButtons.addPavloviaTools(
                buttons=['pavloviaSync', 'pavloviaSearch', 'pavloviaUser'])
        frame.btnHandles.update(pavButtons.btnHandles)

        # Finished setup. Make it happen
        frame.SetToolBar(self)
        self.Realize()


    def AddPsychopyTool(self, fName, label, shortcut, tooltip, func):
        # Load in graphic resource
        rc = self.frame.app.prefs.paths['icons']
        if isinstance(fName, str):
            # If one stimulus is supplied, read bitmap
            bmp = wx.Bitmap(os.path.join(
                rc, fName+'%i.png' % self.iconSize
            ), wx.BITMAP_TYPE_PNG)
        elif isinstance(fName, tuple) and len(fName) == 2:
            # If two are supplied, create combined bitmap
            bmp = combineImageEmblem(os.path.join(rc, fName[0]+'%i.png' % self.iconSize),
                               os.path.join(rc, fName[1]+'16.png'),
                               pos='bottom_right')
        else:
            return
        # Create tool object
        if 'phoenix' in wx.PlatformInfo:
            item = self.AddTool(wx.ID_ANY,
                              _translate(label + " [%s]") % self.keys[shortcut],
                              bmp,
                              _translate(tooltip))
        else:
            item = self.AddSimpleTool(wx.ID_ANY,
                                    bmp,
                                    _translate(label + " [%s]") % self.keys[shortcut],
                                    _translate(tooltip))
        # Bind function
        self.Bind(wx.EVT_TOOL, func, item)
        return item

class PsychopyPlateBtn(platebtn.PlateButton, ThemeMixin):
    def __init__(self, parent, id=wx.ID_ANY, label='', bmp=None,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=1, name=wx.ButtonNameStr):
        platebtn.PlateButton.__init__(self, parent, id, label, bmp, pos, size, style, name)
        self.parent = parent
        self.__InitColors()
        self._applyAppTheme()


    def _applyAppTheme(self):
        cs = ThemeMixin.appColors
        self.__InitColors()
        self.SetBackgroundColour(wx.Colour(self.parent.GetBackgroundColour()))
        self.SetPressColor(cs['txtbutton_bg_hover'])
        self.SetLabelColor(cs['text'],
                           cs['txtbutton_fg_hover'])

    def __InitColors(self):
        cs = ThemeMixin.appColors
        """Initialize the default colors"""
        colors = dict(default=True,
                      hlight=cs['txtbutton_bg_hover'],
                      press=cs['txtbutton_bg_hover'],
                      htxt=cs['text'])
        return colors

class PsychopyScrollbar(wx.ScrollBar):
    def __init__(self, parent, ori=wx.VERTICAL):
        wx.ScrollBar.__init__(self)
        if ori == wx.HORIZONTAL:
            style = wx.SB_HORIZONTAL
        else:
            style = wx.SB_VERTICAL
        self.Create(parent, style=style)
        self.ori = ori
        self.parent = parent
        self.Bind(wx.EVT_SCROLL, self.DoScroll)
        self.Resize()

    def DoScroll(self, event):
        if self.ori == wx.HORIZONTAL:
            w = event.GetPosition()
            h = self.parent.GetScrollPos(wx.VERTICAL)
        elif self.ori == wx.VERTICAL:
            w = self.parent.GetScrollPos(wx.HORIZONTAL)
            h = event.GetPosition()
        else:
            return
        self.parent.Scroll(w, h)
        self.Resize()

    def Resize(self):
        sz = self.parent.GetSize()
        vsz = self.parent.GetVirtualSize()
        start = self.parent.GetViewStart()
        if self.ori == wx.HORIZONTAL:
            sz = (sz.GetWidth(), 20)
            vsz = vsz.GetWidth()
        elif self.ori == wx.VERTICAL:
            sz = (20, sz.GetHeight())
            vsz = vsz.GetHeight()
        self.SetDimensions(start[0], start[1], sz[0], sz[1])
        self.SetScrollbar(
            position=self.GetScrollPos(self.ori),
            thumbSize=10,
            range=1,
            pageSize=vsz
        )

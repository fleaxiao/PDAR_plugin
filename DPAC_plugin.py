import pcbnew
import wx
import os
import numpy as np
import pandas as pd
from .function import *

class DPAC_plugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Design PCB Action Recorder"
        self.category = "Export PCB actions"
        self.description = "Record the actions when designing PCB"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'icon.png')

    def start_record(self, event):
        self.text2.SetLabel('Recording...')
        pcb_init()
        self.df = record_pcb_design()

    def end_record(self, event):
        self.text2.SetLabel('Reocrd is finished!')
        self.df.to_csv('pcb_design.csv', index = False)

    def abandon_record(self, event):
        self.text2.SetLabel('Reocrd is abandoned!')
        board: pcbnew.BOARD = pcbnew.GetBoard()
        for item in list(board.GetDrawings()):
            if isinstance(item, pcbnew.PCB_SHAPE) and item.GetLayer() == pcbnew.Edge_Cuts:
                board.Remove(item)
        for module in board.GetFootprints():
            board.RemoveNative(module)
  
        pcbnew.Refresh()
        
    def Run(self):
        board = pcbnew.GetBoard()
        work_dir, in_pcb_file = os.path.split(board.GetFileName())
        os.chdir(work_dir) # Change the working directory to the directory of the PCB file

        self.frame = wx.Frame(None, -1, 'Design PCB Action Recorder')
        self.frame.SetSize(0,0,500,220)
        self.frame.SetBackgroundColour(wx.WHITE)

        # Set the icon
        icon = wx.Icon(os.path.join(os.path.dirname(__file__), 'icon.ico'), wx.BITMAP_TYPE_ICO)
        self.frame.SetIcon(icon)

        # Load the image
        image = wx.Image(os.path.join(os.path.dirname(__file__), 'tue.png'), wx.BITMAP_TYPE_ANY)

        # Scale the image
        image = image.Scale(100, 100, wx.IMAGE_QUALITY_HIGH)
        bitmap = wx.Bitmap(image)

        # Create a StaticBitmap with the bitmap
        wx.StaticBitmap(self.frame, -1, bitmap, (50, 20))
        self.text1 = wx.StaticText(self.frame, label = 'Copyright \u00A9 fleaxiao', pos = (190,150))
        self.text1.SetFont(wx.Font(7, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.text1.SetForegroundColour(wx.LIGHT_GREY)

        self.text2 = wx.StaticText(self.frame, label = 'Record is ready', pos = (270,110))
        self.text2.SetFont(wx.Font(7, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.text2.SetForegroundColour(wx.LIGHT_GREY)
        self.text2.SetWindowStyle(wx.ALIGN_CENTER) 

        # Create first button
        self.button1 = wx.Button(self.frame, label = 'Start Record', pos = (180,30), size=(260, 30))
        self.button1.Bind(wx.EVT_BUTTON, self.start_record)

        self.button2 = wx.Button(self.frame, label = 'End Record', pos = (180,70), size=(130, 30))
        self.button2.Bind(wx.EVT_BUTTON, self.end_record)

        self.button3 = wx.Button(self.frame, label = 'Abandon Record', pos = (310,70), size=(130, 30))
        self.button3.Bind(wx.EVT_BUTTON, self.abandon_record)

        self.frame.Show()

        return


import pcbnew
import wx
import os
import numpy as np
import pandas as pd
import time
import threading
import json
from .function import *
from .tool import *

class PDAC_plugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "PCB Design Action Recorder"
        self.category = "Export PCB actions"
        self.description = "Record the actions when designing PCB"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'icon.png')

    def record_loop(self):
        global FLAG_RECORD
        global RECORD_DESIGN

        FLAG_RECORD = True
        prev_df = pd.DataFrame()

        while FLAG_RECORD:
            time.sleep(0.1)
            new_df = pcb_record()

            if not new_df.equals(prev_df):
                if not is_component_selected():
                    data_dict = new_df.to_dict('records')

                    for record in data_dict:
                        module_ref = record.get('Module Reference')

                        if module_ref not in RECORD_DESIGN:
                            RECORD_DESIGN[module_ref] = {'Position X': [], 'Position Y': [], 'Angle': []}

                        pos_x = record.get('Position X')
                        pos_y = record.get('Position Y')
                        angle = record.get('Angle')

                        RECORD_DESIGN[module_ref]['Position X'].append(pos_x)
                        RECORD_DESIGN[module_ref]['Position Y'].append(pos_y)
                        RECORD_DESIGN[module_ref]['Angle'].append(angle)

                    prev_df = new_df
    
    def initialization(self, event):
        self.text2.SetLabel('Environment is ready.')
        
        pcb_init()
        # random_placement()

    def start_record(self, event):
        self.text2.SetLabel('Recording...')

        random_placement()
        
        global RECORD_DESIGN

        RECORD_DESIGN = {}
        thread = threading.Thread(target = self.record_loop).start()


    def end_record(self, event):
        self.text2.SetLabel('Reocrd is finished!')
        
        global FLAG_RECORD
        global RECORD_DESIGN

        FLAG_RECORD = False
        record_data = json.dumps(RECORD_DESIGN, indent=4)
        with open('pcb_record.json', 'w') as file:
            file.write(record_data)
        
        RECORD_DESIGN = {}

    def abandon_record(self, event):
        self.text2.SetLabel('Reocrd is abandoned!')
        
        global FLAG_RECORD
        global RECORD_DESIGN

        FLAG_RECORD = False
        RECORD_DESIGN = {}
        # board: pcbnew.BOARD = pcbnew.GetBoard()
        # for item in list(board.GetDrawings()):
        #     if isinstance(item, pcbnew.PCB_SHAPE) and item.GetLayer() == pcbnew.Edge_Cuts:
        #         board.Remove(item)
        # for module in board.GetFootprints():
        #     board.RemoveNative(module)
  
        pcbnew.Refresh()
        
    def Run(self):
        board = pcbnew.GetBoard()
        work_dir, in_pcb_file = os.path.split(board.GetFileName())
        os.chdir(work_dir) # Change the working directory to the directory of the PCB file

        self.frame = wx.Frame(None, -1, style=wx.STAY_ON_TOP)
        self.frame.SetTitle("Design PCB Action Recorder")
        self.frame.SetSize(0,0,500,170)
        self.frame.SetBackgroundColour(wx.WHITE)

        displaySize = wx.DisplaySize()
        self.frame.SetPosition((10, displaySize[1] - self.frame.GetSize()[1]-100))

        # Set the icon
        icon = wx.Icon(os.path.join(os.path.dirname(__file__), 'icon.ico'), wx.BITMAP_TYPE_ICO)
        self.frame.SetIcon(icon)

        # Set the image
        image = wx.Image(os.path.join(os.path.dirname(__file__), 'tue.png'), wx.BITMAP_TYPE_ANY)
        image = image.Scale(100, 100, wx.IMAGE_QUALITY_HIGH)
        bitmap = wx.Bitmap(image)
        wx.StaticBitmap(self.frame, -1, bitmap, (50, 20))

        # Create a StaticBitmap with the bitmap
        self.text1 = wx.StaticText(self.frame, label = 'PCB Design Action Recorder   Copyright \u00A9 fleaxiao', pos = (130,150))
        self.text1.SetFont(wx.Font(6, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.text1.SetForegroundColour(wx.LIGHT_GREY)

        self.text2 = wx.StaticText(self.frame, label = 'Record is ready', pos = (20,125), size = (140,10), style=wx.ALIGN_CENTER)
        self.text2.SetFont(wx.Font(7, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.text2.SetForegroundColour(wx.RED)
        # self.text2.SetForegroundColour(wx.LIGHT_GREY)
        self.text2.SetWindowStyle(wx.ALIGN_CENTER) 

        # Create first button
        self.button1 = wx.Button(self.frame, label = 'Initialization', pos = (180,15), size=(260, 30))
        self.button1.Bind(wx.EVT_BUTTON, self.initialization)

        self.line1 = wx.StaticLine(self.frame, pos=(185, 50), size=(240,1), style=wx.LI_HORIZONTAL)

        self.button2 = wx.Button(self.frame, label = 'Start Record', pos = (180,55), size=(260, 30))
        self.button2.Bind(wx.EVT_BUTTON, self.start_record)

        self.button3 = wx.Button(self.frame, label = 'End Record', pos = (180,90), size=(130, 30))
        self.button3.Bind(wx.EVT_BUTTON, self.end_record)

        self.button4 = wx.Button(self.frame, label = 'Abandon Record', pos = (310,90), size=(130, 30))
        self.button4.Bind(wx.EVT_BUTTON, self.abandon_record)

        self.line2 = wx.StaticLine(self.frame, pos=(40, 142), size=(120,1), style=wx.LI_HORIZONTAL)
        self.line3 = wx.StaticLine(self.frame, pos=(185, 142), size=(240,1), style=wx.LI_HORIZONTAL)

        self.frame.Show()

        return


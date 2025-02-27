import pcbnew
import wx
import os
import numpy as np
import pandas as pd
import time
from datetime import datetime
import threading
import json

from .function import *
from .tool import *
from .PositionInit import position_init
from .constant import *


class PDAR_plugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "PCB Design Action Recorder"
        self.category = "Export PCB actions"
        self.description = "Record the actions when designing PCB"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'images/icon.png')

    def record_loop(self):
        global FLAG_RECORD
        global RECORD_DESIGN

        FLAG_RECORD = True
        self.prev_module_status = []
        self.prev_track_status = []
        self.prev_via_status = []

        while FLAG_RECORD:
            time.sleep(0.1)
            footprint, new_module_status, new_track_status, new_via_status = pcb_record(self.x1, self.y1, self.x2, self.y2)

            if len(self.prev_module_status) == 0:
                data_dict = footprint.to_dict('records')
                for record in data_dict:
                    module_ref = record.get('Module Reference')
                    if module_ref not in RECORD_DESIGN['Record']['Module']:
                        RECORD_DESIGN['Footprint'][module_ref] = {'Width': record.get('Footprint Width'), 'Height': record.get('Footprint Height'), 'Pad': record.get('Pad Info')}

                data_dict = new_module_status.to_dict('records')
                for record in data_dict:
                    module_ref = record.get('Module Reference')
                    if module_ref not in RECORD_DESIGN['Record']['Module']:
                        RECORD_DESIGN['Record']['Module'][module_ref] = {'Position X': [], 'Position Y': [], 'Angle': []}

                    pos_x = record.get('Position X')
                    pos_y = record.get('Position Y')
                    angle = record.get('Angle')

                    RECORD_DESIGN['Record']['Module'][module_ref]['Position X'].append(pos_x)
                    RECORD_DESIGN['Record']['Module'][module_ref]['Position Y'].append(pos_y)
                    RECORD_DESIGN['Record']['Module'][module_ref]['Angle'].append(angle)
                
                RECORD_DESIGN['Record']['Track']['Net'].append(new_track_status['Net'].tolist())
                RECORD_DESIGN['Record']['Track']['Start X'].append(new_track_status['Start X'].tolist())
                RECORD_DESIGN['Record']['Track']['Start Y'].append(new_track_status['Start Y'].tolist())
                RECORD_DESIGN['Record']['Track']['End X'].append(new_track_status['End X'].tolist())
                RECORD_DESIGN['Record']['Track']['End Y'].append(new_track_status['End Y'].tolist())
                RECORD_DESIGN['Record']['Track']['Width'].append(new_track_status['Width'].tolist())
                RECORD_DESIGN['Record']['Track']['Layer'].append(new_track_status['Layer'].tolist())

                RECORD_DESIGN['Record']['Via']['Net'].append(new_via_status['Net'].tolist())
                RECORD_DESIGN['Record']['Via']['Position X'].append(new_via_status['Position X'].tolist())
                RECORD_DESIGN['Record']['Via']['Position Y'].append(new_via_status['Position Y'].tolist())
                RECORD_DESIGN['Record']['Via']['Diameter'].append(new_via_status['Diameter'].tolist())

                self.prev_module_status.append(new_module_status)
                self.prev_track_status.append(new_track_status)
                self.prev_via_status.append(new_via_status)

            else:
                if not new_module_status.equals(self.prev_module_status[-1]) or not new_track_status.equals(self.prev_track_status[-1]) or not new_via_status.equals(self.prev_via_status[-1]):
                    if not is_module_selected() and not is_track_selected():
                        data_dict = new_module_status.to_dict('records')

                        for record in data_dict:
                            module_ref = record.get('Module Reference')

                            if module_ref not in RECORD_DESIGN['Record']['Module']:
                                RECORD_DESIGN['Record']['Module'][module_ref] = {'Position X': [], 'Position Y': [], 'Angle': []}

                            pos_x = record.get('Position X')
                            pos_y = record.get('Position Y')
                            angle = record.get('Angle')

                            RECORD_DESIGN['Record']['Module'][module_ref]['Position X'].append(pos_x)
                            RECORD_DESIGN['Record']['Module'][module_ref]['Position Y'].append(pos_y)
                            RECORD_DESIGN['Record']['Module'][module_ref]['Angle'].append(angle)
                        
                        RECORD_DESIGN['Record']['Track']['Net'].append(new_track_status['Net'].tolist())
                        RECORD_DESIGN['Record']['Track']['Start X'].append(new_track_status['Start X'].tolist())
                        RECORD_DESIGN['Record']['Track']['Start Y'].append(new_track_status['Start Y'].tolist())
                        RECORD_DESIGN['Record']['Track']['End X'].append(new_track_status['End X'].tolist())
                        RECORD_DESIGN['Record']['Track']['End Y'].append(new_track_status['End Y'].tolist())
                        RECORD_DESIGN['Record']['Track']['Width'].append(new_track_status['Width'].tolist())
                        RECORD_DESIGN['Record']['Track']['Layer'].append(new_track_status['Layer'].tolist())

                        RECORD_DESIGN['Record']['Via']['Net'].append(new_via_status['Net'].tolist())
                        RECORD_DESIGN['Record']['Via']['Position X'].append(new_via_status['Position X'].tolist())
                        RECORD_DESIGN['Record']['Via']['Position Y'].append(new_via_status['Position Y'].tolist())
                        RECORD_DESIGN['Record']['Via']['Diameter'].append(new_via_status['Diameter'].tolist())

                        self.prev_module_status.append(new_module_status)
                        self.prev_track_status.append(new_track_status)
                        self.prev_via_status.append(new_via_status)
    
    def initialization(self, event):
        pcb_init(self.x1, self.y1, self.x2, self.y2)

        self.text2.SetLabel('Environment is ready.')

    def start_record(self, event):
        global RECORD_DESIGN

        position_init().Run()
        module_init(self.x1, self.y1, self.x2, self.y2)

        RECORD_DESIGN = {'Footprint':{},
                         'Constraint':{
                            'Power Module': [],
                            'Sensitive Module': []
                         },
                         'Record':{
                            'Module':{},
                            'Track':{'Net':[], 'Start X': [], 'Start Y': [], 'End X': [], 'End Y': [], 'Width': [], 'Layer': []},
                            'Via':{'Net':[], 'Position X': [], 'Position Y': [], 'Diameter': []}
                            }
                        }
        if not str(self.text3.GetValue()) == 'Power Module':
            RECORD_DESIGN['Constraint']['Power Module'] = str(self.text3.GetValue()).split()
        if not str(self.text4.GetValue()) == 'Sensitive Module':
            RECORD_DESIGN['Constraint']['Sensitive Module'] = str(self.text4.GetValue()).split()
        thread = threading.Thread(target = self.record_loop).start()

        self.text2.SetLabel('Recording...')
    
    def undo(self, event):
        global RECORD_DESIGN

        RECORD_DESIGN['Record'] = delete_last_action(RECORD_DESIGN['Record'])
        play_last_action(RECORD_DESIGN['Record'])
        self.prev_module_status = self.prev_module_status[0:-1]
        self.prev_track_status = self.prev_track_status[0:-1]
        self.prev_via_status = self.prev_via_status[0:-1]


    def end_record(self, event):
        global FLAG_RECORD
        global RECORD_DESIGN

        FLAG_RECORD = False
        OUTPUT_DESIGN = RECORD_DESIGN
        OUTPUT_DESIGN['Record'] = extract_last_action(RECORD_DESIGN['Record'])

        record_data = json.dumps(RECORD_DESIGN, indent=4)
        output_data = json.dumps(OUTPUT_DESIGN, indent=4)

        board = pcbnew.GetBoard()
        now = datetime.now()
        _, pcb_file = os.path.split(board.GetFileName())
        pcb_file_name = os.path.splitext(pcb_file)[0]
        time_string = now.strftime("%Y%m%d_%H%M%S")

        record_filename = pcb_file_name + '_' + time_string + '_record' + '.json' #? Add the current time to the filename
        # record_filename = pcb_file_name + '_record' + '.json' #? Keep the filename unchanged
        with open(record_filename, 'w') as file:
            file.write(record_data)
        output_filename = pcb_file_name + '_' + time_string + '_output' + '.json' #? Add the current time to the filename
        # output_filename = pcb_file_name + '_output' + '.json' #? Keep the filename unchanged
        with open(output_filename, 'w') as file:
            file.write(output_data)
        
        RECORD_DESIGN = {}

        self.text2.SetLabel('Reocrd is finished!')

    def abandon_record(self, event):
        global FLAG_RECORD
        global RECORD_DESIGN

        FLAG_RECORD = False
        RECORD_DESIGN = {}
        pcbnew.Refresh()

        self.text2.SetLabel('Reocrd is abandoned!')
        
    def Run(self):
        board = pcbnew.GetBoard()
        work_dir, _ = os.path.split(board.GetFileName())
        os.chdir(work_dir) # Change the working directory to the directory of the PCB file

        # Set pcb board frame
        self.x1 = START_X
        self.y1 = START_Y
        self.x2 = END_X
        self.y2 = END_Y

        self.frame = wx.Frame(None, -1, style=wx.STAY_ON_TOP)
        self.frame.SetTitle("Design PCB Action Recorder")
        self.frame.SetSize(0,0,500,170)
        self.frame.SetBackgroundColour(wx.WHITE)

        displaySize = wx.DisplaySize()
        self.frame.SetPosition((10, displaySize[1] - self.frame.GetSize()[1]-100))

        # Set icon
        icon = wx.Icon(os.path.join(os.path.dirname(__file__), 'images/icon.ico'), wx.BITMAP_TYPE_ICO)
        self.frame.SetIcon(icon)

        # Set image
        image = wx.Image(os.path.join(os.path.dirname(__file__), 'images/tue.png'), wx.BITMAP_TYPE_ANY)
        image = image.Scale(100, 100, wx.IMAGE_QUALITY_HIGH)
        bitmap = wx.Bitmap(image)
        wx.StaticBitmap(self.frame, -1, bitmap, (50, 20))

        # Create text
        self.text1 = wx.StaticText(self.frame, label = 'PCB Design Action Recorder   Copyright \u00A9 fleaxiao', pos = (130,150))
        self.text1.SetFont(wx.Font(6, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.text1.SetForegroundColour(wx.LIGHT_GREY)

        self.text2 = wx.StaticText(self.frame, label = 'PDAR is ready', pos = (40,125), size = (120,10), style=wx.ALIGN_CENTER)
        self.text2.SetFont(wx.Font(7, wx.DECORATIVE, wx.NORMAL, wx.BOLD))
        self.text2.SetForegroundColour(wx.RED)
        self.text2.SetWindowStyle(wx.ALIGN_CENTER) 

        self.text3 = wx.TextCtrl(self.frame, value="Power Module", pos = (180,52), size = (128, 25), style = wx.TE_CENTRE)

        self.text4 = wx.TextCtrl(self.frame, value="Sensitive Module", pos = (310,52), size = (128, 25), style = wx.TE_CENTRE)

        # Create button
        self.button1 = wx.Button(self.frame, label = 'Initialization', pos = (180,15), size=(260, 25))
        self.button1.Bind(wx.EVT_BUTTON, self.initialization)

        self.button2 = wx.Button(self.frame, label = 'Start Record', pos = (180,80), size=(260, 25))
        self.button2.Bind(wx.EVT_BUTTON, self.start_record)

        self.button3 = wx.Button(self.frame, label = 'Undo', pos = (180,108), size=(80, 25))
        self.button3.Bind(wx.EVT_BUTTON, self.undo)

        self.button4 = wx.Button(self.frame, label = 'End', pos = (262,108), size=(96, 25))
        self.button4.Bind(wx.EVT_BUTTON, self.end_record)

        self.button5 = wx.Button(self.frame, label = 'Abandon', pos = (360,108), size=(80, 25))
        self.button5.Bind(wx.EVT_BUTTON, self.abandon_record)

        # Create line
        self.line1 = wx.StaticLine(self.frame, pos=(188, 45), size=(240,1), style=wx.LI_HORIZONTAL)
        self.line2 = wx.StaticLine(self.frame, pos=(40, 142), size=(120,1), style=wx.LI_HORIZONTAL)
        self.line3 = wx.StaticLine(self.frame, pos=(188, 142), size=(240,1), style=wx.LI_HORIZONTAL)

        self.frame.Show()

        return
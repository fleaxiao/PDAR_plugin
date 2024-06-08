import pcbnew
import os
import numpy as np
import pandas as pd
import wx
import random
import pyautogui
import pygetwindow as gw
import time
from .tool import *

def pcb_init():
    board: pcbnew.BOARD = pcbnew.GetBoard()

    x1 = 40
    y1 = 40
    x2 = 100
    y2 = 100
    margin = 5
    originX = pcbnew.FromMM(x1-margin)  
    originY = pcbnew.FromMM(y1-margin)  
    endX = pcbnew.FromMM(x2+margin) 
    endY = pcbnew.FromMM(y2+margin)

    # Initialize the board
    for item in list(board.GetDrawings()):
        if isinstance(item, pcbnew.PCB_SHAPE) and item.GetLayer() == pcbnew.Edge_Cuts:
            board.Remove(item)
    rectangle = pcbnew.PCB_SHAPE(board)
    rectangle.SetShape(pcbnew.SHAPE_T_RECT)
    rectangle.SetStartX(originX)
    rectangle.SetStartY(originY)
    rectangle.SetEndX(endX)
    rectangle.SetEndY(endY)
    rectangle.SetLayer(pcbnew.Edge_Cuts)
    board.Add(rectangle)

    # Initialize the components
    ## Import the footprints from the schematic
    windows = gw.getWindowsWithTitle('PCB Editor')
    pcb_editor_window = None
    for window in windows:
        if window.title.endswith('PCB Editor'):
            pcb_editor_window = window
            break
    if pcb_editor_window:
        pcb_editor_window.activate()
    else:
        wx.MessageBox('Window is not found', 'Error', wx.OK | wx.ICON_ERROR)
    time.sleep(0.1)
    pyautogui.press('f8')
    time.sleep(0.1)
    pyautogui.press('enter')
    time.sleep(0.1)
    pyautogui.press('enter')
    time.sleep(0.1)
    pyautogui.press('enter')
    time.sleep(0.1)
    pyautogui.press('esc')

    ## Import the footprints from the predefinition
    # KICAD_VERSION = pcbnew.Version().split(".")[0]
    # fp_path = os.getenv("KICAD" + KICAD_VERSION + "_FOOTPRINT_DIR", default=None)
    # create_component(board, fp_path, "Capacitor_THT.pretty", "CP_Axial_L37.0mm_D20.0mm_P43.00mm_Horizontal", "C1", "47uF", x1, y1, x2, y2)
    # create_component(board, fp_path, "Capacitor_THT.pretty", "CP_Axial_L37.0mm_D16.0mm_P43.00mm_Horizontal", "C2", "47uF", x1, y1, x2, y2)
    # create_component(board, fp_path, "Diode_THT.pretty", "D_DO-201AE_P15.24mm_Horizontal", "D1", "Diode", x1, y1, x2, y2)
    # create_component(board, fp_path, "inductor_THT.pretty", "L_Radial_D21.0mm_P15.00mm_Vishay_IHB-2", "L1", "110uH", x1, y1, x2, y2)
    # create_component(board, fp_path, "Package_TO_SOT_THT.pretty", "TO-247-3_Vertical", "S1", "TO-247-3", x1, y1, x2, y2)
    # create_component(board, fp_path, "Connector_PinSocket_2.54mm.pretty", "PinSocket_1x05_P2.54mm_Vertical", "P1", "Signal", x1, y1, x2, y2)
    # create_component(board, fp_path, "Connector_Phoenix_GMSTB.pretty", "PhoenixContact_GMSTBVA_2,5_2-G_1x02_P7.50mm_Vertical", "P2", "Power Input", x1, y1, x2, y2)
    # create_component(board, fp_path, "Connector_Phoenix_GMSTB.pretty", "PhoenixContact_GMSTBVA_2,5_2-G_1x02_P7.50mm_Vertical", "P3", "Power Output", x1, y1, x2, y2)

    pcbnew.Refresh()

def random_placement():
    board: pcbnew.BOARD = pcbnew.GetBoard()

    x1 = 40
    y1 = 40
    x2 = 100
    y2 = 100

    for module in board.GetFootprints():
        place_component(board, module, x1, y1, x2, y2)

    pcbnew.Refresh()

def pcb_record():
    board: pcbnew.BOARD = pcbnew.GetBoard()

    module_ref = list()
    pos_x = np.array([]).reshape(-1, 1)
    pos_y = np.array([]).reshape(-1, 1)
    angle = np.array([]).reshape(-1, 1)
    for module in board.GetFootprints():
        
        module_ref_i, pos_x_i, pos_y_i, angle_degrees_i, _, _ = get_status(module)
        
        module_ref.append(module_ref_i)
        pos_x = np.append(pos_x, pos_x_i)
        pos_y = np.append(pos_y, pos_y_i)
        angle = np.append(angle, angle_degrees_i)

    data = {'Module Reference': module_ref, 'Position X': pos_x, 'Position Y': pos_y, 'Angle': angle}
    new_df = pd.DataFrame(data)
    new_df = new_df.sort_values(by = ['Module Reference'])

    return new_df
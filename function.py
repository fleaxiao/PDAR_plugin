import pcbnew
import os
import numpy as np
import pandas as pd
import wx
import random

def get_courtyard_size(module):
    courtyard_bbox = None

    for graphic in module.GraphicalItems():
        if graphic.GetLayer() == pcbnew.F_CrtYd or graphic.GetLayer() == pcbnew.B_CrtYd:
            if courtyard_bbox is None:
                courtyard_bbox = graphic.GetBoundingBox()
            else:
                courtyard_bbox.Merge(graphic.GetBoundingBox())

    if courtyard_bbox is not None:
        # x = pcbnew.ToMM(courtyard_bbox.GetLeft () + courtyard_bbox.GetRight() / 2)
        # y = pcbnew.ToMM(courtyard_bbox.GetTop () + courtyard_bbox.GetBottom() / 2)
        w = pcbnew.ToMM(courtyard_bbox.GetWidth())
        h = pcbnew.ToMM(courtyard_bbox.GetHeight())
        return w, h
    else:
        return None

def get_status(module):
    module_ref = module.GetReference()
    pos_x = pcbnew.ToMM(module.GetPosition())[0]
    pos_y = pcbnew.ToMM(module.GetPosition())[1]
    angle_degrees = module.GetOrientationDegrees()
    w, h = get_courtyard_size(module)

    return module_ref, pos_x, pos_y, angle_degrees, w, h

def place_component(board, fp_path, fp_lib, fp, ref, value, x1, y1, x2, y2):
    fp_lib = fp_path + fp_lib
    module = pcbnew.FootprintLoad(fp_lib, fp)
    # module.Reference().SetPosition(pcbnew.VECTOR2I(module.GetPosition()))
    w, h = get_courtyard_size(module)

    # Overlap detection
    for _ in range(1000):
        FLAG = False
        x = random.uniform(x1 + w/2, x2 - w/2)
        y = random.uniform(y1 + h/2, y2 - h/2)
        for module_existing in board.GetFootprints():
            _ , pos_existing_x, pos_existing_y, _, w_existing, h_existing = get_status(module_existing)
            if ((pos_existing_x - w_existing/2 <= x - w/2 <= pos_existing_x + w_existing/2 and 
                 pos_existing_y - h_existing/2 <= y - h/2 <= pos_existing_y + h_existing/2) or
                (pos_existing_x - w_existing/2 <= x + w/2 <= pos_existing_x + w_existing/2 and 
                 pos_existing_y - h_existing/2 <= y + h/2 <= pos_existing_y + h_existing/2) or
                (pos_existing_x - w_existing/2 <= x - w/2 <= pos_existing_x + w_existing/2 and 
                 pos_existing_y - h_existing/2 <= y + h/2 <= pos_existing_y + h_existing/2) or
                (pos_existing_x - w_existing/2 <= x + w/2 <= pos_existing_x + w_existing/2 and 
                 pos_existing_y - h_existing/2 <= y - h/2 <= pos_existing_y + h_existing/2)):
                print('Overlap detected')
                FLAG = True
                break
            if (( x - w/2 <= pos_existing_x + w_existing/2 and
                  x + w/2 >= pos_existing_x - w_existing/2 and
                  y - h/2 <= pos_existing_y + h_existing/2 and
                  y + h/2 >= pos_existing_y - h_existing/2)):
                print('Overlap detected')
                FLAG = True
                break

        if FLAG == False:
            break

    if FLAG == True:
        wx.MessageBox(f'No space available for {ref}', 'Error')
    else:
        module.SetPosition(pcbnew.VECTOR2I(pcbnew.wxPointMM(x, y)))
        board.Add(module)
        module.SetReference(ref) # when mutiple components are placed with same reference, there is a bug of the overlap detction
        module.SetValue(value) # when the value is set to empty, there is a bug of the overlap detction

def pcb_init():
    board: pcbnew.BOARD = pcbnew.GetBoard()
    x1 = 40
    y1 = 40
    x2 = 200
    y2 = 140
    margin = 5
    originX = pcbnew.FromMM(x1-margin)  
    originY = pcbnew.FromMM(y1-margin)  
    endX = pcbnew.FromMM(x2+margin) 
    endY = pcbnew.FromMM(y2+margin)

    # Initialize the board
    rectangle = pcbnew.PCB_SHAPE(board)
    rectangle.SetShape(pcbnew.SHAPE_T_RECT)
    rectangle.SetStartX(originX)
    rectangle.SetStartY(originY)
    rectangle.SetEndX(endX)
    rectangle.SetEndY(endY)
    rectangle.SetLayer(pcbnew.Edge_Cuts)
    board.Add(rectangle)

    # Initialize the components
    KICAD_VERSION = pcbnew.Version().split(".")[0]
    fp_path = os.getenv("KICAD" + KICAD_VERSION + "_FOOTPRINT_DIR", default=None)
    place_component(board, fp_path, "Capacitor_THT.pretty", "CP_Axial_L37.0mm_D20.0mm_P43.00mm_Horizontal", "C1", "47uF", x1, y1, x2, y2)
    place_component(board, fp_path, "Capacitor_THT.pretty", "CP_Axial_L37.0mm_D16.0mm_P43.00mm_Horizontal", "C2", "47uF", x1, y1, x2, y2)
    place_component(board, fp_path, "Diode_THT.pretty", "D_DO-201AE_P15.24mm_Horizontal", "D1", "Diode", x1, y1, x2, y2)
    place_component(board, fp_path, "inductor_THT.pretty", "L_Radial_D21.0mm_P15.00mm_Vishay_IHB-2", "L1", "110uH", x1, y1, x2, y2)
    place_component(board, fp_path, "Package_TO_SOT_THT.pretty", "TO-247-3_Vertical", "S1", "TO-247-3", x1, y1, x2, y2)
    place_component(board, fp_path, "Connector_PinSocket_2.54mm.pretty", "PinSocket_1x05_P2.54mm_Vertical", "P1", "Signal", x1, y1, x2, y2)
    place_component(board, fp_path, "Connector_Phoenix_GMSTB.pretty", "PhoenixContact_GMSTBVA_2,5_2-G_1x02_P7.50mm_Vertical", "P2", "Power Input", x1, y1, x2, y2)
    place_component(board, fp_path, "Connector_Phoenix_GMSTB.pretty", "PhoenixContact_GMSTBVA_2,5_2-G_1x02_P7.50mm_Vertical", "P3", "Power Output", x1, y1, x2, y2)

    pcbnew.Refresh()

def record_pcb_design():
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
    df = pd.DataFrame(data)
    df = df.sort_values(by = ['Module Reference'])

    return df
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

def is_component_selected():
    pcb = pcbnew.GetBoard()
    for module in pcb.GetFootprints():
        if module.IsSelected():
            return True
    return False

def create_component(board, fp_path, fp_lib, fp, ref, value, x1, y1, x2, y2):
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

def place_component(board, module, x1, y1, x2, y2):

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
        wx.MessageBox(f'No space available for component', 'Error')
    else:
        module.SetPosition(pcbnew.VECTOR2I(pcbnew.wxPointMM(x, y)))
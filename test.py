import pandas as pd
import numpy as np
import json


data = {
    'Column1': ['Value1', 'Value2', 'Value3'],
    'Column2': ['Value4', 'Value5', 'Value6'],
    'Column3': ['Value7', 'Value8', 'Value9']
}
data = pd.DataFrame(data)
a = []
a.append(data)
a.append(data)
print(data.equals(a[-1]))
print(a[-1])
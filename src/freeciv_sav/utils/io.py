# Copyright (C) 2023  The Freeciv-sav project
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import pandas as pd
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
    
class IOManager(object):

    @staticmethod
    def save_csv_from_df(df:pd.DataFrame):
        return
    
    @staticmethod
    def save_csv_from_dict(dic:dict, filename:str):
        data = pd.DataFrame(dic)
        data.to_csv(filename, index=False, encoding="utf-8")
        return
    
    @staticmethod
    def get_handler(filename):
        return open(filename, "w", encoding="utf-8")
    
    @staticmethod
    def save_json(dic:dict, filename:str):
        res = json.dumps(dic, cls=NumpyEncoder)
        with open(filename, 'w') as f:
            f.write(res)        
        return
    

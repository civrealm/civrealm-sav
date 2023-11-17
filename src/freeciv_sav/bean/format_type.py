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

import pandas as pd
from freeciv_sav.bean.parse_type import ParseTypeBean

class FormatTypeBean(object):
    
    @staticmethod
    def line_from_dict(dic: dict, sep=""):
        """
        Data structure: {k1: list}
        """
        _dic = dict()
        for key, value in dic.items():
            if key not in _dic:
                _dic[key] = dict()
            _dic[key] = key + '="' + sep.join(value) + '"'
        return _dic
    
    @staticmethod
    def line_from_list(lis: list):
        """
        Data structure: {k1: list}
        """
        _lis = "{"
        for value in lis:
            _lis += value + "\n"
        _lis += "}"
        return _lis

    @staticmethod
    def line_from_kv_parse_type(dic: dict):
        """
        Data structure: {k1: {k2: line}}
        """
        _dic = dict()
        for key, value in dic.items():
            if key not in _dic:
                _dic[key] = dict()
            for _key, _value in value.items():
                _dic[key][_key] = _key+"="+ParseTypeBean.get_value(_value)
        return _dic
    
    @staticmethod
    def line_from_kv_parse_type_first_level(dic: dict):
        """
        Data structure: {k1: {k2: line}}
        """
        _dic = dict()
        for key, value in dic.items():
            _dic[key] = key+"="+str(ParseTypeBean.get_value(value))
        return _dic

    @staticmethod
    def line_from_dataframe(df: pd.DataFrame, key: str):
        columns = df.columns
        first_row = "{"+",".join(['"'+col+'"' for col in df.columns])
        immediate_rows = list()
        _rows = df.to_dict(orient='split')['data']
        for _row in _rows:
            print(_row)
            immediate_rows.append(",".join([str(ParseTypeBean.set_format(i)) for i in _row]))
        last_row = "}"
        
        return [key+first_row]+immediate_rows+[last_row]
    
    @staticmethod
    def player_id_format(uid):
        if isinstance(uid, int):
            return "player"+str(uid)
        return uid

if __name__ == "__main__":
    print(FormatTypeBean.line_from_dataframe(pd.DataFrame({"id": [1, 2], "x": [1, 2], "y": [3, 4]})))

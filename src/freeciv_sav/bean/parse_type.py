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

import numpy as np

class ParseTypeBean(object):

    """
    Define data structure: [score, {property, terrain, resource, location, terrain_property, resource_property}]
    -- Score is used to sort array.
    """

    @staticmethod
    def adapt_to_parser(row):
        """Adapt the base data structure of sav parser to get the real value.
        The base data structure of sav parser: 
            [('"', 'asdfc')]]
        """
        if isinstance(row, list):
            return row[0][1]
        return row

    @staticmethod
    def exchange(old_value, new_value):
        if old_value.startswith('"'):
            return '"'+new_value+'"'
        return new_value

    @staticmethod
    def set_value(dic, key, value):
        if isinstance(dic[key][0], tuple):
            dic[key] = [dic[key][0][0], value]
        else:
            dic[key] = [dic[key][0], value]
        return 

    @staticmethod
    def get_value(value, format_value="str"):
        if isinstance(value[0], tuple):
            if value[0][0].startswith('"'):
                return '"'+value[0][1]+'"'
            if format_value == "int":
                return int(value[0][1])
            return value[0][1]
        if value[0].startswith('"'):
            return '"'+value[1]+'"'
        return value[1]
    
    @staticmethod
    def get_realvalue(value):
        if isinstance(value[0], tuple):
            if value[0][0].startswith('"'):
                return value[0][1]
            return value[0][1]
        if value[0].startswith('"'):
            return value[1]
        return value[1]
    
    @staticmethod
    def set_format(value):
        output = list()
        for v in value:
            if isinstance(v, str):
                output.append('"'+v+'"')
            elif v == np.nan:
                output.append('""')
        return output
    
    @staticmethod
    def set_format(value):
        if isinstance(value, str):
            return '"'+value+'"'
        elif str(value) == "nan":
            return '""'
        return value
    
    @staticmethod
    def set_event(value):
        if_flag = False
        output = ""
        for s in value:
            tmp = s
            if s == '"':
                if if_flag:
                    if_flag = False
                else:
                    if_flag = True
            if if_flag:
                if s == ',':
                    tmp = '@'
            output += tmp
        return output
    
    @staticmethod
    def recover_event(value):
        output = ""
        for s in value:
            tmp = s
            if s == '@':
                tmp = ','
            output += tmp
        return output

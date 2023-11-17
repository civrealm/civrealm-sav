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

import copy

__all__ = ['recursive_dict', 'search_dict']

def _recursive_dict(dic:dict, fetch_key:str=None):
    if fetch_key is None:
        return dic
    if isinstance(dic, dict):
        for key in dic:
            if isinstance(dic[key], dict):
                if fetch_key in dic[key]:
                    dic[key] = dic[key][fetch_key]
                    _recursive_dict(dic[key], fetch_key)
    return 

def recursive_dict(keys:list, dic:dict, fetch_key:str=None):
    if fetch_key in dic:
        return dic[fetch_key]
    else:
        if not isinstance(dic, dict):
            return dic
    if len(keys) == 0:
        _dic = copy.deepcopy(dic)
        _recursive_dict(_dic, fetch_key)
        return _dic
    if keys[0] in dic:
        return recursive_dict(keys[1:], dic[keys[0]], fetch_key)
    return

def recursive_dict_out(key:str, dic:dict, output:list):
    if key not in dic:
        output.append([key])
    else:
        if not isinstance(dic[key], dict):
            output.append(dic[key])
        for _key in dic[key]:
            recursive_dict_out(_key, dic, output)
    return

def _search_dict(key:str, dic:dict, _dic:dict, output:dict, keys:str, fetch_key:str=None):
    if not isinstance(dic, dict):
        return 
    for _key in dic:
        if key in _key:
            _keys = keys+'.'+_key
            if isinstance(output, dict):
                output[_keys] = recursive_dict(_keys.split('.')[1:], _dic, fetch_key)
            elif isinstance(output, list):
                output.append(recursive_dict(_keys.split('.')[1:], _dic, fetch_key))
        else:
            _search_dict(key, dic[_key], _dic, output, keys+'.'+_key, fetch_key)
    return

def search_dict(key:str, dic:dict, fetch_key:str=None, output=None):
    if output is None:
        output = dict()
    _search_dict(key, dic, dic, output, "", fetch_key)
    return output

def exchange_key(dic, meta_dic):
    output = dict()
    for key, value in dic.items():
        if key in meta_dic:
            output[meta_dic[key]] = value
    return output

def exchange_key_value(dic, meta_dic):
    """ dict(list) structure """
    output = dict()
    for key, value in dic.items():
        new_key = key
        if key in meta_dic:
            new_key = meta_dic[key]
            output[new_key] = value
        else:
            output[new_key] = value
        for _key, _value in enumerate(value):
            if _value in meta_dic:
                output[new_key][_key] = meta_dic[_value]
    return output

def dict_sum_by_list(lis):
    property = None
    for _property in lis:
        if _property is None:
            continue
        if property is None:
            property = copy_dict_by_key(_property)
        for key, value in property.items():
            property[key] = float(property[key])+float(_property[key])
    return property

def dict_minus_by_list(lis):
    property = None
    for i, _property in enumerate(lis):
        if _property is None:
            continue
        if property is None:
            property = copy_dict_by_key(_property)
        for key, value in property.items():
            property[key] = float(property[key])+float(_property[key]) * (1 if i == 0 else -1)
    return property

def dict_mean(dic):
    output = 0
    cnt = 0
    for key, value in dic.items():
        output += value
        cnt += 1
    output /= cnt
    return output

def dict_sum(dic, weight:dict=None):
    output = 0
    for key, value in dic.items():
        if weight is None:
            output += value
        else:
            output += float(value) * float(weight[key])
    return round(output, 6)

def copy_dict_by_key(dic, init=0):
    output = dict()
    for key, _ in dic.items():
        output[key] = init
    return output

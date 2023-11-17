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
import random

CITY_SCOPE_DEPTH = 2
EMPTY_SIGNAL = "-"

class CityTool(object):

    def __init__(self, player_city_data, global_owner_data=None, global_eowner_data=None, global_source_data=None, global_worked_data=None):
        self._player_city_data = player_city_data
        self._global_owner_data = {"map": [], "key": []}
        self._global_source_data = {"map": [], "key": []}
        self._global_eowner_data = {"map": [], "key": []}
        self._global_worked_data = {"map": [], "key": []}
        self._parse_data(global_owner_data, self._global_owner_data)
        self._parse_data(global_source_data, self._global_source_data)
        self._parse_data(global_eowner_data, self._global_eowner_data)
        self._parse_data(global_worked_data, self._global_worked_data)
        self.xsize, self.ysize = self._cal_size()
    
    def _parse_data(self, data, store):
        if data is None:
            store["map"] = [[]]
            store["key"] = [[]]
            return
        for key, map in data.items():
            store["map"].append(map)
            store["key"].append(key)
        return

    def _cal_size(self):
        return len(self._global_eowner_data["map"][0]), len(self._global_eowner_data["map"])
    
    def get_player_city_data(self):
        return self._player_city_data
    
    def get_city_map_data(self):
        output = dict()
        for _data in [self._global_owner_data, self._global_source_data, self._global_eowner_data, self._global_worked_data]:
            for index, row in enumerate(_data["map"]):
                output[_data["key"][index]] = row
        return output

    def rotation_location(self, rotation_angle):
        center_x = int(self.xsize/2) - 1
        center_y = int(self.ysize/2) - 1
        for index, player_id in enumerate(self._player_city_data):
            if "c" in self._player_city_data[player_id]:
                c_df = self._player_city_data[player_id]["c"]
                city_uid_list = list()
                x_list = list()
                y_list = list()
                for city_i, city_raw in self._player_city_data[player_id]["c"].iterrows():
                    x = city_raw['x']
                    y = city_raw['y']
                    _x = round(float(x-center_x) * np.cos(rotation_angle) - float(y-center_y) * np.sin(rotation_angle) + center_x) % self.xsize
                    _y = round(float(x-center_x) * np.sin(rotation_angle) + float(y-center_y) * np.cos(rotation_angle) + center_y)
                    c_df.loc[city_i, "x"] = _x
                    c_df.loc[city_i, "y"] = _y
                    city_uid = c_df.loc[city_i, "id"]
                    player_uid = c_df.loc[city_i, "original"]
                    city_uid_list.append(str(city_uid))
                    x_list.append(_x)
                    y_list.append(_y)
                self.set_titles_from_cities(str(player_uid), city_uid_list, x_list, y_list)
                self._player_city_data[player_id]["c"] = c_df
        return

    def set_location_with_cluster(self, clusters, 
                                  unit_locations):
        """ Change city location by clustering. 
        """
        print("clusters: ", clusters)
        for index, player_id in enumerate(self._player_city_data):
            print("CITY INDEX: ", index, player_id)
            if "c" in self._player_city_data[player_id]:
                c_df = self._player_city_data[player_id]["c"]
                cluster = clusters[index]["candidate"]
                city_i = 0
                while city_i < self._player_city_data[player_id]["c"].shape[0]:
                    _clu = cluster.pop()
                    c_df.loc[city_i, "x"] = _clu[0]
                    c_df.loc[city_i, "y"] = _clu[1]
                    self._player_city_data[player_id]["c"] = c_df
                    player_uid = c_df.loc[city_i, "original"]
                    city_uid = c_df.loc[city_i, "id"]
                    self.set_titles(str(player_uid), str(city_uid), _clu[0], _clu[1])
                    city_i += 1
        return 

    def set_size(self, worked_cnt):
        """
        size [6] != (workers [3] - free worked tiles [1]) + specialists [0]
        """
        for index, player_id in enumerate(self._player_city_data):
            if "c" in self._player_city_data[player_id]:
                c_df = self._player_city_data[player_id]["c"]
                for city_i, _ in self._player_city_data[player_id]["c"].iterrows():
                    city_uid = str(c_df.loc[city_i, "id"])
                    if city_uid in worked_cnt:
                        c_df.loc[city_i, "size"] = worked_cnt[city_uid] - 1
                self._player_city_data[player_id]["c"] = c_df
        return 
    
    def set_titles(self, player_uid, city_uid, x, y):
        scope_yx_list = self.cal_city_scope_with_loop(x, y, self.xsize, self.ysize)
        source_uid = None
        worked_cnt = 0
        print(player_uid, city_uid, self._global_worked_data["map"])
        for i in range(len(self._global_eowner_data["map"])):
            for j in range(len(self._global_eowner_data["map"][0])):
                ## eowner mask
                if self._global_eowner_data["map"][i][j] == player_uid:
                    self._global_eowner_data["map"][i][j] = EMPTY_SIGNAL
                    source_uid = self._global_source_data["map"][i][j]

                ## owner mask
                if self._global_owner_data["map"][i][j] == player_uid:
                    self._global_owner_data["map"][i][j] = EMPTY_SIGNAL

                ## worked mask
                if self._global_worked_data["map"][i][j] == city_uid:
                    print("WORKED MASK: ", i, j, self._global_worked_data["map"][i][j])
                    self._global_worked_data["map"][i][j] = EMPTY_SIGNAL
                    worked_cnt += 1

        for i in range(len(self._global_eowner_data["map"])):
            for j in range(len(self._global_eowner_data["map"][0])):
                ## source mask
                if self._global_source_data["map"][i][j] == source_uid:
                    self._global_source_data["map"][i][j] = EMPTY_SIGNAL

                # eowner setting
                if j == x and i == y:
                    self._global_eowner_data["map"][i][j] = player_uid

                ## owner & source setting
                if [i, j] in scope_yx_list:
                    self._global_owner_data["map"][i][j] = player_uid
                    self._global_source_data["map"][i][j] = source_uid

        ## worked setting
        self._global_worked_data["map"][y][x] = city_uid
        while worked_cnt > 1:
            random.shuffle(scope_yx_list)
            yx = scope_yx_list.pop()
            if yx != [y, x]:
                self._global_worked_data["map"][yx[0]][yx[1]] = city_uid
                worked_cnt -= 1

        return
    
    def set_titles_from_cities(self, player_uid, city_uid_list, xlist, ylist):
        print("city_uid_list: ", city_uid_list)
        source_uid = {}
        worked_cnt = {}
        print("player_uid: ", player_uid)
        for index, city_uid in enumerate(city_uid_list):
            print(player_uid, city_uid, self._global_source_data["map"])
            for i in range(len(self._global_eowner_data["map"])):
                for j in range(len(self._global_eowner_data["map"][0])):
                    ## eowner mask
                    if self._global_eowner_data["map"][i][j] == player_uid:
                        self._global_eowner_data["map"][i][j] = EMPTY_SIGNAL
                    
                    ## set source uid
                    if self._global_worked_data["map"][i][j] == city_uid:
                        if (_sid := self._global_source_data["map"][i][j]) != "-":
                            source_uid[city_uid] = _sid

                    ## owner mask
                    if self._global_owner_data["map"][i][j] == player_uid:
                        self._global_owner_data["map"][i][j] = EMPTY_SIGNAL

                    ## worked mask
                    if self._global_worked_data["map"][i][j] == city_uid:
                        self._global_worked_data["map"][i][j] = EMPTY_SIGNAL
                        if city_uid not in worked_cnt:
                            worked_cnt[city_uid] = 0
                        worked_cnt[city_uid] += 1

        #self.set_size(worked_cnt)
        print("bef worked_cnt: ", worked_cnt)

        worked_list = list()
        for index, city_uid in enumerate(city_uid_list):
            print(city_uid)
            x, y = xlist[index], ylist[index]
            scope_yx_list = self.cal_city_scope_with_half_loop(x, y, self.xsize, self.ysize)
            for i in range(len(self._global_eowner_data["map"])):
                for j in range(len(self._global_eowner_data["map"][0])):
                    ## source mask
                    if self._global_source_data["map"][i][j] == source_uid[city_uid]:
                        self._global_source_data["map"][i][j] = EMPTY_SIGNAL

                    # eowner setting
                    if j == x and i == y:
                        self._global_eowner_data["map"][i][j] = player_uid

                    ## owner & source setting
                    if [i, j] in scope_yx_list:
                        self._global_owner_data["map"][i][j] = player_uid
                        self._global_source_data["map"][i][j] = source_uid[city_uid]

            ## worked setting
            self._global_worked_data["map"][y][x] = city_uid
            while worked_cnt[city_uid] > 1:
                random.shuffle(scope_yx_list)
                yx = scope_yx_list.pop()
                if yx != [y, x] and yx not in worked_list:
                    print(yx, worked_list)
                    self._global_worked_data["map"][yx[0]][yx[1]] = city_uid
                    worked_list.append(yx)
                    worked_cnt[city_uid] -= 1
        print("aft worked_cnt: ", worked_cnt)

        return
    
    @staticmethod
    def cal_city_scope(x, y):
        row_len = CITY_SCOPE_DEPTH * 2 + 1
        vision_list = [(-CITY_SCOPE_DEPTH+j, -CITY_SCOPE_DEPTH+i) for j in range(row_len) for i in range(row_len) 
                       if abs(-CITY_SCOPE_DEPTH+j)+abs(-CITY_SCOPE_DEPTH+i) != 2*CITY_SCOPE_DEPTH]
        location_list = []
        for i, vision in enumerate(vision_list):
            location_list.append([y+vision[0], x+vision[1]])
        return location_list
    
    @staticmethod
    def cal_city_scope_with_half_loop(x, y, xsize, ysize):
        row_len = CITY_SCOPE_DEPTH * 2 + 1
        vision_list = [(-CITY_SCOPE_DEPTH+j, -CITY_SCOPE_DEPTH+i) for j in range(row_len) for i in range(row_len) 
                       if abs(-CITY_SCOPE_DEPTH+j)+abs(-CITY_SCOPE_DEPTH+i) != 2*CITY_SCOPE_DEPTH]
        location_list = []
        for i, vision in enumerate(vision_list):
            if xsize is not None and ysize is not None:
                _y = (y+vision[0])
                _x = (x+vision[1]) % xsize
            else:
                _y, _x = y+vision[0], x+vision[1]
            if _y >= 0 and _y < ysize:
                location_list.append([_y, _x])
        return location_list

    @staticmethod
    def cal_city_scope_with_loop(x, y, xsize, ysize):
        row_len = CITY_SCOPE_DEPTH * 2 + 1
        vision_list = [(-CITY_SCOPE_DEPTH+j, -CITY_SCOPE_DEPTH+i) for j in range(row_len) for i in range(row_len) 
                       if abs(-CITY_SCOPE_DEPTH+j)+abs(-CITY_SCOPE_DEPTH+i) != 2*CITY_SCOPE_DEPTH]
        location_list = []
        for i, vision in enumerate(vision_list):
            if xsize is not None and ysize is not None:
                _y = (y+vision[0]) % ysize
                _x = (x+vision[1]) % xsize
            else:
                _y, _x = y+vision[0], x+vision[1]
            location_list.append([_y, _x])
        return location_list

    def get_location(self):
        output = dict()
        for player_id in self._player_city_data:
            if "c" in self._player_city_data[player_id]:
                c_df = self._player_city_data[player_id]["c"]
                output[player_id] = dict()
                for i in range(c_df.shape[0]):
                    output[player_id].update({c_df.iloc[i]["id"]: {"location": [c_df.iloc[i]["x"], c_df.iloc[i]["y"]]}})
        return output

    def get_citizens_cnt(self):
        output = dict()
        for index, player_id in enumerate(self._player_city_data):
            output[player_id] = 0
            if "c" in self._player_city_data[player_id]:
                c_df = self._player_city_data[player_id]["c"]
                for i, _ in c_df.iterrows():
                    output[player_id] += c_df.iloc[i]["size"]
        return output

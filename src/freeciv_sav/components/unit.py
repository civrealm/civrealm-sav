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
import copy

OCEAN_SIGNAL_LIST = [" ", ":", "a"]

UNIT_SCOPE_DEPTH = {2: 2, 8: 3}

UNIT_COMBAT_STATIS = {
    "warriors":[1,1,10],
    "phalanx":[1,2,10],
    "archers":[3,2,10],
    "legion":[4,2,10],
    "pikemen":[1,2,10],
    "musketeers":[3,3,20],
    "partisan":[4,4,20],
    "alpine troops":[5,5,20],
    "riflemen":[5,4,20],
    "marines":[8,5,20],
    "paratroopers":[6,4,20],
    "mech. inf.":[6,6,30],
    "horsemen":[2,1,10],
    "chariot":[3,1,10],
    "knights":[4,2,10],
    "dragoons":[5,2,20],
    "cavalry":[8,3,20],
    "armor":[10,5,30],
    "catapult":[6,1,10],
    "cannon":[8,1,20],
    "artillery":[10,1,20],
    "howitzer":[12,2,30],
    "fighter":[4,3,20],
    "bomber":[12,1,20],
    "helicopter":[10,3,20],
    "stealth fighter":[8,4,20],
    "stealth bomber":[18,5,20],
    "trireme":[1,1,10],
    "caravel":[2,1,10],
    "galleon":[0,2,20],
    "frigate":[4,2,20],
    "ironclad":[4,4,30],
    "destroyer":[4,4,30],
    "cruiser":[6,6,30],
    "aegis cruiser":[8,8,30],
    "battleship":[12,12,40],
    "submarine":[12,2,30],
    "carrier":[1,9,40],
    "transport":[0,3,30],
    "cruise missile":[18,0,10],
    "nuclear":[99,0,10],
    "diplomat":[0,0,10],
    "spy":[0,0,10],
    "caravan":[0,1,10],
    "freight":[0,1,10],
    "explorer":[0,1,10],
    "leader":[0,2,20],
    "barbarian leader":[0,0,10],
    "awacs":[0,1,20],
}


VISUAL_RANGE = {
    "settlers":2,
    "workers":2,
    "engineers":2,
    "warriors":2,
    "phalanx":2,
    "archers":2,
    "legion":2,
    "pikemen":2,
    "musketeers":2,
    "partisan":2,
    "alpine troops":2,
    "riflemen":2,
    "marines":2,
    "paratroopers":2,
    "mech. inf.":2,
    "horsemen":2,
    "chariot":2,
    "knights":2,
    "dragoons":2,
    "cavalry":2,
    "armor":2,
    "catapult":2,
    "cannon":2,
    "artillery":2,
    "howitzer":2,
    "fighter":8,
    "bomber":8,
    "helicopter":8,
    "stealth fighter":8,
    "stealth bomber":8,
    "trireme":2,
    "caravel":2,
    "galleon":2,
    "frigate":2,
    "ironclad":2,
    "destroyer":8,
    "cruiser":8,
    "aegis cruiser":8,
    "battleship":8,
    "submarine":8,
    "carrier":8,
    "transport":8,
    "cruise missile":2,
    "nuclear":2,
    "diplomat":2,
    "spy":8,
    "caravan":2,
    "freight":2,
    "explorer":2,
    "leader":8,
    "barbarian leader":2,
    "awacs":26
}

OCEAN_UNITS = ["aegis cruiser", "trireme", "caravel", "galleon", "frigate", "ironclad", "transport", 
               "destroyer", "cruiser", "battleship", "submarine", "carrier"]

class UnitTool(object):

    def __init__(self, raw_data, unit_obsolete_conf):
        self._raw_data = copy.deepcopy(raw_data)
        self._data = raw_data
        self.unit_obsolete_conf = unit_obsolete_conf

    def remove_unit(self, keep_unit_id:int):
        return
    
    def _random_choice_location(self, map_data):
        return
    
    def get_max_id(self):
        max_id = -1
        for player_id in self._raw_data:
            u_df = self._raw_data[player_id]["u"]
            for _, row in u_df.iterrows():
                max_id = max(max_id, row['id'])
        return max_id

    def get_unit_number(self):
        output = dict()
        for player_id in self._raw_data:
            output[player_id] = self._raw_data[player_id]["u"].shape[0]
        return output
    
    def set_unit_type(self, max_walks_rate=0.5, rate=0.1):
        for player_id in self._raw_data:
            u_df = self._raw_data[player_id]["u"]
            indics = list(u_df[u_df['type_by_name'] != 'Leader'].index)
            max_walks = int(len(indics)*max_walks_rate)
            walk = 0
            while walk < max_walks:
                index = random.choice(indics)
                if random.random() < rate:
                    print("change---->", index, u_df.loc[index, "type_by_name"])
                    choice_type = u_df.loc[index, "type_by_name"].lower()
                    new_type = "none"
                    if random.random() < 0.5:
                        if choice_type in self.unit_obsolete_conf["pro"]:
                            new_type = random.choice(self.unit_obsolete_conf["pro"][choice_type.lower()])
                    else:
                        if choice_type in self.unit_obsolete_conf["req"]:
                            new_type = random.choice(self.unit_obsolete_conf["req"][choice_type.lower()])
                    if new_type != "none":
                        u_df.loc[index, "type_by_name"] = new_type
                walk += 1
        return

    def set_unit_number(self, lower=0.5, upper=2, limit=2, rate=[]):
        cnt_base = None
        max_id = self.get_max_id()
        for player_id in self._raw_data:
            print('-------------- start -------------------', player_id)

            u_df = self._raw_data[player_id]["u"]
            records = u_df[u_df['type_by_name'] != 'Leader'].to_dict(orient='record')
            indexes = list(u_df[u_df['type_by_name'] != 'Leader'].index)

            cnt = u_df.shape[0]
            # find bound
            if player_id == 'player0': 
                cnt_base = cnt
            else:
                upper = rate[1]
                lower = rate[0]

            lower_bound = min(max(int(cnt_base * lower), limit), 29)
            upper_bound = min(max(int(cnt_base * upper), lower_bound+1), 30)
            # random choice number
            rand_cnt = random.randint(lower_bound, upper_bound)

            if player_id == 'player0': cnt_base = rand_cnt

            if cnt > 30 or rand_cnt > 30:
                raise ValueError(f"Too much units as {rand_cnt}, original cnt is {cnt}!")

            while rand_cnt - cnt != 0:
                print("loop: ", max_id, rand_cnt, cnt)
                if rand_cnt > cnt:
                    # add id
                    _record = random.choice(records)
                    max_id = max_id + 1
                    _record['id'] = max_id
                    u_df = u_df.append([_record])
                elif rand_cnt < cnt:
                    # pop id
                    random.shuffle(indexes)
                    _index = indexes.pop()
                    u_df = u_df.drop(_index)
                cnt = u_df.shape[0]
            print('-------------- finished -------------------')
            u_df.reset_index(inplace=True)
            del u_df['index']
            self._raw_data[player_id]["u"] = u_df

        return

    def set_location_random(self, map_locations:list):
        """ Change unit location randomly. """
        for player_id in self._raw_data:
            u_df = self._raw_data[player_id]["u"]
            for i, _ in u_df.iterrows():
                x, y = random.choice(map_locations)
                u_df.loc[i, "x"] = x
                u_df.loc[i, "y"] = y
            self._raw_data[player_id]["u"] = u_df
        return self._raw_data

    def rotation_location(self, rotation_angle, xsize, ysize):
        center_x = int(xsize/2) - 1
        center_y = int(ysize/2) - 1
        for player_id in self._raw_data:
            u_df = self._raw_data[player_id]["u"]
            for i, _ in u_df.iterrows():
                x = u_df.loc[i, "x"]
                y = u_df.loc[i, "y"]
                _x = round(float(x-center_x) * np.cos(rotation_angle) - float(y-center_y) * np.sin(rotation_angle) + center_x) % xsize
                _y = round(float(x-center_x) * np.sin(rotation_angle) + float(y-center_y) * np.cos(rotation_angle) + center_y)
                u_df.loc[i, "x"] = _x
                u_df.loc[i, "y"] = _y
            self._raw_data[player_id]["u"] = u_df
        return 

    def reset(self):
        self._raw_data = copy.deepcopy(self._data)
        return

    def set_location_with_cluster(self, cluster_func, 
                                  land_locations:list, 
                                  radius:int=2, 
                                  distance:list=[5, 20],
                                  ocean_locations:list=list(),
                                  extra:int=0):
        """ Change unit location by clustering. 
        :parameter radius: list, [min, max], the radius of cluster
        :parameter distance: list, the distance between two clusters
        """
        # find the reasonable clusters for multi-player to satisfy radius and units count
        clusters = cluster_func(land_locations, self.get_unit_cluster_cnt(), radius, distance, self._get_player_has_unit_cnt(), extra=extra, ocean_locations=ocean_locations)

        print("clusters ori: ", clusters)
        if len(clusters) < self._get_player_has_unit_cnt():
            return list()
        
        for index, player_id in enumerate(self._raw_data):
            print(f"SETTING PLAYER ID: {player_id}")
            if "u" not in self._raw_data[player_id]:
                continue
            u_df = self._raw_data[player_id]["u"]
            if "land" in clusters[index]:
                land_cluster = clusters[index]["land"]
                ocean_cluster = clusters[index]["ocean"]
                for i, _ in u_df.iterrows():
                    a = u_df.loc[i, "type_by_name"].lower()
                    if u_df.loc[i, "type_by_name"].lower() in OCEAN_UNITS:
                        x, y = ocean_cluster[random.randrange(len(ocean_cluster))]
                        print(f"insert to ocean {x}, {y}, {a}")
                    else:
                        x, y = land_cluster[random.randrange(len(land_cluster))]
                        print(f"insert to land {x}, {y}, {a}")

                    u_df.loc[i, "x"] = x
                    u_df.loc[i, "y"] = y
            else:
                cluster = clusters[index]["candidate"]
                for i, _ in u_df.iterrows():
                    x, y = cluster[random.randrange(len(cluster))]
                    a = u_df.loc[i, "type_by_name"].lower()
                    print(f"insert to candidate {x}, {y}, {a}")
                    u_df.loc[i, "x"] = x
                    u_df.loc[i, "y"] = y
            self._raw_data[player_id]["u"] = u_df
        return clusters
    
    def get_conf(self):
        return self._raw_data

    def get_location(self):
        output = dict()
        for player_id in self._raw_data:
            if "u" not in self._raw_data[player_id]:
                continue
            u_df = self._raw_data[player_id]["u"]
            output[player_id] = dict()
            for i in range(u_df.shape[0]):
                output[player_id].update({u_df.iloc[i]["id"]: {"location": [u_df.iloc[i]["x"], u_df.iloc[i]["y"]], "name": u_df.iloc[i]["type_by_name"]}})
        return output

    def get_unit_cnt(self):
        output = dict()
        for player_id in self._raw_data:
            if "u" in self._raw_data[player_id]:
                output[player_id] = self._raw_data[player_id]["u"].shape[0]
            else:
                output[player_id] = 0
        return output
    
    def get_combat_unit_cnt(self):
        output = dict()
        for player_id in self._raw_data:
            output[player_id] = 0
            if "u" in self._raw_data[player_id]:
                u_df = self._raw_data[player_id]["u"]
                for i in range(u_df.shape[0]):
                    if u_df.iloc[i]["type_by_name"].lower() in UNIT_COMBAT_STATIS:
                        output[player_id] += 1
        return output

    def get_unit_cluster_cnt(self):
        output = dict()
        for player_id in self._raw_data:
            land_cnt = 0
            ocean_cnt = 0
            if "u" in self._raw_data[player_id]:
                for _, row in self._raw_data[player_id]["u"].iterrows():
                    if row["type_by_name"].lower() in OCEAN_UNITS:
                        ocean_cnt += 1
                    else:
                        land_cnt += 1
            output[player_id] = {"land": land_cnt, "ocean": ocean_cnt}
        return output

    def _get_player_has_unit_cnt(self):
        cnt = 0
        for player_id in self._raw_data:
            if "u" in self._raw_data[player_id]:
                cnt +=  1
        return cnt

    @staticmethod
    def cal_unit_scope(unit_name, x, y, xsize=None, ysize=None):
        visual_range = VISUAL_RANGE[unit_name.lower()]
        depth = UNIT_SCOPE_DEPTH[visual_range]
        vision_list = [(-depth+j, -depth+i) for j in range(depth * 2 + 1) for i in range(depth * 2 + 1) 
                       if abs(-depth+j)+abs(-depth+i) != 2*depth]
        location_list = []
        for _, vision in enumerate(vision_list):
            _y = y+vision[0]
            _x = x+vision[1]
            if xsize is not None and ysize is not None:
                _y = _y % ysize
                _x = _x % xsize
            location_list.append([_y, _x])
        return location_list
    
    @staticmethod
    def cal_unit_max_scope(x, y, max_turns=10):
        return [[-max_turns+j+y, -max_turns+i+x] for j in range(2*max_turns+1) for i in range(2*max_turns+1)]

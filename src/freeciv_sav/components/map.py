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

import random
import copy
import pandas as pd
import numpy as np
from collections import OrderedDict
from freeciv_sav.utils.dic_tools import exchange_key, dict_sum, exchange_key_value, dict_sum_by_list, dict_minus_by_list
from freeciv_sav.components.city import CityTool, CITY_SCOPE_DEPTH
from freeciv_sav.bean.property import PropertyBean
from freeciv_sav.components.unit import UnitTool
from freeciv_sav.components.terrain import TerrainTool

# terrain signal
UNSEEN_SIGNAL = "u"
LAKE_SIGNAL = "+"
INACCESSION_SIGNAL = "i"
LOCATION_NEGSIGNAL_LIST = ["i", " ", ":", "a", "+"]
FPT_ZERO_SIGNAL_LIST = ["i", " ", ":", "a"]
OCEAN_TERRAIN_LIST = [" ", ":"]
PLAYER_TERRAIN_SIGNAL = "map_t"

# format of map
FORMAT_MAP_LINE_KEY = "line"
FORMAT_MAP_LINE_PATTERN = "{key}="+"\"{line}\""

# method of scope
SCOPE_METHOD_ALL = "all"
SCOPE_METHOD_TOP = "topk"

# proba of land modification
WAIT_PROBA = 0.3
OCEAN_PROBA = 0.3
UNCHANGE_PROBA = 0.4
LAND_TO_OCEAN_PROBA = 0.2
OCEAN_TO_LAND_PROBA = 0.2

__all__ = ["MapTool"]

class MapTool(object):
    """
    Sav Map Operation Interface.
    :parameter raw_data: dict<str, str>, original row map data.
    :parameter map_abbr_conf: dict<str, str>, the mapping of total name(key) and abbr name, design for bidirection communication.
    :attribute _global_map: list<list<str>>, built (y,x), convert raw_data to 2-d array.
    }
    """
    strides = 3
    resource_prob = 0.15
    valid_steps = [[i-1, j-1] for i in range(3) for j in range(3) if abs(i-1)+abs(j-1) != 0]
    total_steps = [[i-1, j-1] for i in range(3) for j in range(3)]

    def __init__(self, raw_data:dict=None, 
                 seen_map:dict=None,
                 player_map_data:dict=None,
                 player_resource_data:dict=None,
                 terrain_fpt_conf:dict=None,
                 resource_fpt_conf:dict=None,
                 terrain_resource_conf:dict=None,
                 extra_resources:dict=None
                 ):
        if raw_data is None:
            raise ValueError("Please input raw_data for global map!")
        self._raw_data = raw_data
        self._seen_data = seen_map
        self._player_map_data = player_map_data
        self._player_resource_data = player_resource_data
        self._raw_resources = extra_resources

        self.terrain_fpt_conf = terrain_fpt_conf
        self.resource_fpt_conf = resource_fpt_conf
        self.terrain_resource_conf = terrain_resource_conf

        self.terrain_keys = list(terrain_fpt_conf.keys())

        self._global_map = list()
        self._global_keys = list()
        self._players_map = dict()
        self._players_resource = dict()
        self._extra_resources = dict()
        self._seen_map = list()
        self._seen_keys = list()
        self._layers = dict()

        self._parse_map()
        self.xsize, self.ysize = self.cal_size()

    @staticmethod
    def parse_map(map_data, extra_data):
        _map = list()
        _extra = dict()
        for _, map in map_data.items():
            _map.append(map)
        for key, extra in extra_data.items():
            _extra[key] = list()
            for _e, _v in extra.items():
                _extra[key].append(_v)
        return _map, _extra

    def _parse_map(self):
        # global map data
        for key, map in self._raw_data.items():
            self._global_keys.append(key)
            self._global_map.append(map)
        
        self._layers["connectivity"] = copy.deepcopy(self._global_map)

        # global seen map data
        for key, map in self._seen_data.items():
            self._seen_map.append(map)
            self._seen_keys.append(key)

        # player maps data
        for key, data in self._player_map_data.items():
            self._players_map[key] = dict()
            self._players_map[key]["key"] = list()
            self._players_map[key]["map"] = list()
            for _key, map in data.items():
                self._players_map[key]["key"].append(_key)
                self._players_map[key]["map"].append(map)

        # player resource data
        for player, player_data in self._player_resource_data.items():
            self._players_resource[player] = dict()
            for eid, e_data in player_data.items():
                self._players_resource[player][eid] = dict()
                self._players_resource[player][eid]["key"] = list()
                self._players_resource[player][eid]["map"] = list()
                for _key, map in e_data.items():
                    self._players_resource[player][eid]["key"].append(_key)
                    self._players_resource[player][eid]["map"].append(map)

        # global resource data
        for key, data in self._raw_resources.items():
            self._extra_resources[key] = dict()
            self._extra_resources[key]["key"] = list()
            self._extra_resources[key]["map"] = list()
            for _key, map in data.items():
                self._extra_resources[key]["key"].append(_key)
                self._extra_resources[key]["map"].append(map)
        return

    def _search_extra_map(self, extra_map:dict, x:int, y:int):
        if extra_map is None:
            return list()
        resource_list = list()
        for _, data in extra_map.items():
            if not data["map"][y][x].endswith("0"):
                resource_list.append(data["map"][y][x])
        return resource_list
    
    def _get_resource_fpt_conf(self, resource):
        if resource in self.resource_fpt_conf:
            return self.resource_fpt_conf[resource]
        return {"food": 0, "shield": 0, "trade": 0}
    
    def _cal_resource_fpt(self, resource_list):
        fpt = {"food": 0, "shield": 0, "trade": 0}
        for _resource in resource_list:
            if _resource in self.resource_fpt_conf:
                fpt = dict_sum_by_list([fpt, self._get_resource_fpt_conf(_resource)])
        return fpt
    
    def _calulate_map_properties(self, location_list:list, 
                                         weight:dict=None, 
                                         input_map=None, 
                                         extra_resources=None):
        if input_map is None:
            input_map = self._global_map
        if extra_resources is None:
            extra_resources = self._extra_resources

        property_list = list()
        for location in location_list:
            try:
                terrain = input_map[location[0]][location[1]]
            except Exception as ex:
                raise ValueError(f"{ex}\n{location[0]},{location[1]}")
            resource_list = self._search_extra_map(extra_resources, location[1], location[0])
            _properties_terrain = copy.deepcopy(self.terrain_fpt_conf[terrain])
            _properties_resource = self._cal_resource_fpt(resource_list)
            _properties = dict_sum_by_list([_properties_terrain, _properties_resource])
            property_list.append([round(dict_sum(_properties, weight), 3), 
                                  round(dict_sum(_properties_terrain, weight), 3), 
                                  round(dict_sum(_properties_resource, weight), 3), 
                                  {"property": _properties, 
                                    "terrain_property": _properties_terrain, 
                                    "resource_property": _properties_resource, 
                                    "location": location, 
                                    "terrain": terrain,
                                    "resource": resource_list}])
        return property_list

    def calulate_map_properties_by_total(self, location_list:list, 
                                         weight:dict=None, 
                                         input_map=None, 
                                         extra_resources=None):
        """
        Calulating food.
        :parameter location_list: the list of locations (y,x) of terrain.
        """
        property_list = self._calulate_map_properties(location_list, 
                                         weight, 
                                         input_map, 
                                         extra_resources)
        total_property = dict_sum_by_list([PropertyBean.get_prop(property, "property") for property in property_list])
        return total_property

    def calulate_map_properties_by_order(self, location_list:list, 
                                         topk:int=6, 
                                         weight:dict=None, 
                                         input_map=None, 
                                         keep_ocean=None,
                                         extra_resources=None):
        """
        Calulating properties.
        :parameter location_list: the list of locations (y,x) of terrain.
        """
        property_list = self._calulate_map_properties(location_list, 
                                         weight, 
                                         input_map, 
                                         extra_resources)

        # reorder
        property_list = self._reorder_terrains(property_list, keep_ocean, topk)

        topk_property = None
        for i in range(topk):
            topk_property = dict_sum_by_list([topk_property, PropertyBean.get_prop(property_list[i], "property")])
        return topk_property, property_list

    def _reorder_terrains(self, properties: list, keep_ocean:bool, topk:int):
        properties = sorted(properties, key=lambda row: row[0], reverse=True)
        if keep_ocean:
            topk_list = list()
            tail_list = list()
            index = 0
            while len(topk_list) < topk and index < len(properties):
                if PropertyBean.get_prop(properties[index], "terrain") not in FPT_ZERO_SIGNAL_LIST:
                    topk_list.append(properties[index])
                else:
                    tail_list.append(properties[index])
                index += 1
            tail_list += properties[index:]
            return sorted(topk_list, key=lambda row: row[0], reverse=True)+\
                    sorted(tail_list, key=lambda row: row[0], reverse=True)
        return properties

    def cal_size(self):
        """Get map size.
        :return xsize: int
        :return ysize: int
        """
        ysize = len(self._global_map)
        xsize = len(self._global_map[0])
        return xsize, ysize
    
    def _terrain_random_change(self):
        while True:
            rand_terrain = random.choice(self.terrain_keys)
            if rand_terrain != INACCESSION_SIGNAL:
                return rand_terrain
        return 
    
    def _resource_random_change(self, terrain:str):
        if terrain == INACCESSION_SIGNAL or terrain not in self.terrain_resource_conf:
            return 
        if random.random() < self.resource_prob:
            rand_resource = random.choice(self.terrain_resource_conf[terrain])
            return rand_resource
        return 

    @staticmethod
    def _convert_format(gen_map, key_list, format_type:str):
        """ Convert map to the special format
        :parameter format: str, support "line"
        """
        output = dict()
        if format_type == FORMAT_MAP_LINE_KEY:
            for index, key in enumerate(key_list):
                line = FORMAT_MAP_LINE_PATTERN.format(key=key, line="".join(gen_map[index]))
                output[key] = line
        else:
            raise ValueError(f"Please note that the format only supported {FORMAT_MAP_LINE_KEY}, but you use {format_type}!")
        return output
    
    def _align_extras_map(self, resource_map, format_type):
        """ Align the external map with global resource map. """
        extra_output = dict()
        for eid in self._extra_resources:
            extra_map = copy.deepcopy(self._extra_resources[eid]["map"])
            extra_output.update(self._convert_format(MapTool.align_to_extra(eid, extra_map, resource_map),
                                                    self._extra_resources[eid]["key"], format_type))

        return extra_output

    def _align_players_map(self, global_map, format_type):
        """ Align players map with global map. """
        players_map = dict()
        for player in self._player_map_data:
            player_map = copy.deepcopy(self._players_map[player]["map"])
            players_map[player] = self._convert_format(MapTool.align_to_map(player_map, global_map),
                                                    self._players_map[player]["key"], format_type)
        return players_map

    def _align_players_resource(self, global_resource, format_type):
        """ Align players map with global map. """
        players_resource = dict()
        for player in self._player_resource_data:
            players_resource[player] = dict()
            for eid in self._player_resource_data[player]:
                player_resource = copy.deepcopy(self._players_resource[player][eid]["map"])
                players_resource[player].update(self._convert_format(MapTool.align_to_resource(player_resource, global_resource[eid]["map"]),
                                                        self._players_resource[player][eid]["key"], format_type))
        return players_resource

    def gen_random_map(self, format_type:str):
        """ Generate a random map."""
        # terrain randomly
        terrain_rand_map = [[self._terrain_random_change() if i not in [self.ysize-1, 0] else x for x in y] 
                    for i, y in enumerate(self._global_map)]
        terrain_players_map = self._align_players_map(terrain_rand_map, format_type)
        terrain_output = {"global": MapTool._convert_format(terrain_rand_map, self._global_keys, format_type)}
        terrain_output.update(terrain_players_map)
        # resource randomly
        resource_map = [[self._resource_random_change(x) for x in y] for y in terrain_rand_map]
        resource_output = self._align_extras_map(resource_map, format_type)
        return terrain_output, resource_output

    def _is_accessible(self, x, y, input_map=None, margin=1, is_ocean=False):
        if input_map is None:
            input_map = self._global_map
        if x >= margin and x <= self.xsize-margin-1 and y >= margin and y <= self.ysize-margin-1:
            if not is_ocean and input_map[y][x] not in LOCATION_NEGSIGNAL_LIST:
                return True
            elif is_ocean and input_map[y][x] in OCEAN_TERRAIN_LIST:
                return True
        return False

    @staticmethod
    def _if_accessible(x, y, input_map=None, margin=1, is_ocean=False):
        xsize = len(input_map[0])
        ysize = len(input_map[1])
        if x >= margin and x <= xsize-margin-1 and y >= margin and y <= ysize-margin-1:
            if not is_ocean and input_map[y][x] not in LOCATION_NEGSIGNAL_LIST:
                return True
            elif is_ocean and input_map[y][x] in OCEAN_TERRAIN_LIST:
                return True
        return False

    def _is_wide_accessible(self, x, y):
        if x >= 0 and x <= self.xsize-1 and y >= 0 and y <= self.ysize-1:
            return True
        return False
    
    def _check_locations(self, locations):
        _locations = list()
        for loc in locations:
            if self._is_wide_accessible(loc[0], loc[1]):
                _locations.append(loc)
        return _locations
    
    def _check_loop_locations(self, locations):
        _locations = list()
        for loc in locations:
            x, y = loc[0], loc[1]
            if x < 0: x += self.xsize
            if y < 0: y += self.ysize
            if x >= self.xsize: x %= self.xsize
            if y >= self.ysize: y %= self.ysize
            _locations.append([x, y])
        return _locations

    def get_map_accessible_location(self):
        x, y = random.choice(list(range(self.xsize))), \
                random.choice(list(range(self.ysize)))
        return [x, y]

    def get_city_accessible_location(self, input_map=None):
        while True:
            x, y = random.choice(list(range(CITY_SCOPE_DEPTH, self.xsize-CITY_SCOPE_DEPTH))), \
                    random.choice(list(range(CITY_SCOPE_DEPTH, self.ysize-CITY_SCOPE_DEPTH)))
            if self._is_accessible(x, y, input_map):
                return x, y

    def get_unit_accessible_locations(self, input_map=None, is_ocean=False, connectivity=False):
        output = list()

        best_locations = set()
        if connectivity:
            metrics = self.cal_connectivity_layer(input_map)
            best_locations = metrics["best_locations"]

        for x in list(range(CITY_SCOPE_DEPTH, self.xsize-CITY_SCOPE_DEPTH)):
            for y in list(range(CITY_SCOPE_DEPTH, self.ysize-CITY_SCOPE_DEPTH)):
                if self._is_accessible(x, y, input_map, is_ocean=is_ocean):
                    if connectivity:
                       if (y, x) not in best_locations:
                        continue
                    output.append([x, y])
        return output

    def _sampling_step(self, x, y, input_map=None, margin=2):
        random.shuffle(self.valid_steps)
        for action in self.valid_steps:
            _x, _y = x+action[0]*self.strides, y+action[1]*self.strides
            if self._is_accessible(_x, _y, input_map, margin):
                return _x, _y
        return -1, -1

    def _sampling_step_by_proba(self, steps, proba):
        action_id = np.random.choice(list(range(len(steps))), p=proba)
        return steps[action_id][0], steps[action_id][1]

    def _beyond_limit(self, properties_list:list, terrain:str, limit=0.2):
        terrain_cnt = 0
        for property in properties_list:
            if PropertyBean.get_prop(property, "terrain") == terrain:
                terrain_cnt += 1
        terrain_rate = terrain_cnt/len(properties_list)
        return terrain_rate > limit
    
    def _cal_terrain_scores(self, keep_ocean, weight):
        """ Calculate terrain scores.
        Don't put the terrain with zero fpt into list.
        """
        terrain_product = dict()
        for terrain, terrain_pro in self.terrain_fpt_conf.items():
            if keep_ocean and terrain in FPT_ZERO_SIGNAL_LIST:
                continue
            weight_score = round(dict_sum(terrain_pro, weight), 3)
            if weight_score == 0:
                continue
            if weight_score not in terrain_product:
                terrain_product[weight_score] = list()
            terrain_product[weight_score].append(terrain)
        terrain_keys = sorted(list(terrain_product.keys()))
        return terrain_product, terrain_keys
    
    def _remove_resource_with_terrain(self, choice_prop, new_terrain, extra_map, weight, _y, _x):
        choice_resource_score, new_resource_score = 0, 0
        if len(PropertyBean.get_prop(choice_prop, "resource")) > 0:
            choice_resource = PropertyBean.get_prop(choice_prop, "resource")
            pop_choice_resource = list()
            for resource in choice_resource:
                if new_terrain in self.terrain_resource_conf and \
                    resource not in self.terrain_resource_conf[new_terrain]:
                    pop_choice_resource.append(resource)
            if len(pop_choice_resource) > 0:
                new_resource = [c for c in choice_resource if c not in pop_choice_resource]
                PropertyBean.set_prop(choice_prop, "resource", new_resource)
                for _resource in pop_choice_resource:
                    PropertyBean.set_prop(choice_prop, "resource_property", dict_minus_by_list(
                        [PropertyBean.get_prop(choice_prop, "resource_property"), self._get_resource_fpt_conf(_resource)]))
                    eid = _resource.split("_")[0]
                    extra_map[eid]["map"][_y][_x] = eid+"_0"
                new_resource_score = dict_sum(PropertyBean.get_prop(choice_prop, "resource_property"), weight)
                choice_resource_score = PropertyBean.get_prop(choice_prop, "resource_score")
                PropertyBean.set_prop(choice_prop, "resource_score", new_resource_score)
                _y, _x = PropertyBean.get_prop(choice_prop, "location")
                #print(f"RESOURCE REMOVE: {choice_resource}, {choice_resource_score} -> {new_resource}, {new_resource_score}!")
        return choice_resource_score, new_resource_score
    
    def _clean_resource(self, extra_map, _y, _x):
        for eid in extra_map:
            extra_map[eid]["map"][_y][_x] = eid+"_0"
        return 
    
    def _remove_resource(self, choice_prop, extra_map, weight, _y, _x):
        choice_resource_score = PropertyBean.get_prop(choice_prop, "resource_score")
        if len(choice_prop[-1]["resource"]) == 0:
            return 0, 0
        choice_resource = choice_prop[-1]["resource"].pop()
        PropertyBean.set_prop(choice_prop, "resource_property", dict_minus_by_list(
            [PropertyBean.get_prop(choice_prop, "resource_property"), self._get_resource_fpt_conf(choice_resource)]))
        new_resource_score = dict_sum(PropertyBean.get_prop(choice_prop, "resource_property"), weight)
        PropertyBean.set_prop(choice_prop, "resource_score", new_resource_score)
        new_resource = PropertyBean.get_prop(choice_prop, "resource")
        _y, _x = PropertyBean.get_prop(choice_prop, "location")
        eid = choice_resource.split("_")[0]
        extra_map[eid]["map"][_y][_x] = eid+"_0"
        #print(f"RESOURCE REMOVE: {choice_resource}, {choice_resource_score} -> {new_resource}, {new_resource_score}!")
        return choice_resource_score, new_resource_score

    def _add_resource(self, choice_prop, extra_map, weight, _y, _x):
        terrain = PropertyBean.get_prop(choice_prop, "terrain")
        if terrain not in self.terrain_resource_conf:
            return 0, 0
        choice_resource = random.choice(self.terrain_resource_conf[terrain])
        if choice_resource not in self.resource_fpt_conf:
            return 0, 0
        choice_resource_score = PropertyBean.get_prop(choice_prop, "resource_score")
        PropertyBean.set_prop(choice_prop, "resource_property", dict_sum_by_list(
            [PropertyBean.get_prop(choice_prop, "resource_property"), self._get_resource_fpt_conf(choice_resource)]))
        new_resource_score = dict_sum(PropertyBean.get_prop(choice_prop, "resource_property"), weight)
        PropertyBean.set_prop(choice_prop, "resource_score", new_resource_score)
        new_resource = PropertyBean.get_prop(choice_prop, "resource")
        _y, _x = PropertyBean.get_prop(choice_prop, "location")
        eid = choice_resource.split("_")[0]
        extra_map[eid]["map"][_y][_x] = choice_resource
        #print(f"RESOURCE ADD: {choice_resource}, {choice_resource_score} -> {new_resource}, {new_resource_score}!")
        return choice_resource_score, new_resource_score

    def _random_gen(self, properties_list, terrain_product, extra_map, rand_map, weight):
        choice_prop = random.choice(properties_list)
        if PropertyBean.get_prop(choice_prop, "terrain") not in FPT_ZERO_SIGNAL_LIST:
            target_terrain = terrain_product[PropertyBean.get_prop(choice_prop, "terrain_score")]

            if self._beyond_limit(properties_list, LAKE_SIGNAL) and LAKE_SIGNAL in target_terrain:
                prob = [1/(len(target_terrain)-1) if _ != LAKE_SIGNAL else 0 for _ in target_terrain]
                new_terrain = np.random.choice(target_terrain, p=prob)
            else:
                new_terrain = random.choice(target_terrain)

            PropertyBean.set_prop(choice_prop, "terrain", new_terrain)
            PropertyBean.set_prop(choice_prop, "terrain_property", self.terrain_fpt_conf[new_terrain])
            _y, _x = PropertyBean.get_prop(choice_prop, "location")
            #print(f"RANDOM CHANGE: {rand_map[_y][_x]} -> {new_terrain}!")
            rand_map[_y][_x] = new_terrain
            # remove unconsistent resource
            self._remove_resource_with_terrain(choice_prop, new_terrain, extra_map, weight, _y, _x)

            if random.random() < self.resource_prob:
                if random.random() < 0.5:
                    # add
                    self._add_resource(choice_prop, extra_map, weight, _y, _x)
                else:
                    # remove
                    self._remove_resource(choice_prop, extra_map, weight, _y, _x)

            PropertyBean.set_prop(choice_prop, "property", dict_sum_by_list([
                PropertyBean.get_prop(choice_prop, "terrain_property"), PropertyBean.get_prop(choice_prop, "resource_property")]))
            PropertyBean.set_prop(choice_prop, "score", dict_sum(PropertyBean.get_prop(choice_prop, "property"), weight))

        return 

    def _change_terrain(self, choice_prop, terrain_keys, terrain_product, properties_list, move, rand_map, _y, _x):
        # choice_score = PropertyBean.get_prop(choice_prop, "score")
        choice_terrain_score = PropertyBean.get_prop(choice_prop, "terrain_score")
        if choice_terrain_score < 1e-5:
            return 0, 0, PropertyBean.get_prop(choice_prop, "terrain")
        # select the target terrain
        new_terrain_score = terrain_keys[terrain_keys.index(choice_terrain_score)+int(move)]
        target_terrain= terrain_product[new_terrain_score]
        if self._beyond_limit(properties_list, LAKE_SIGNAL) and LAKE_SIGNAL in target_terrain:
            prob = [1/(len(target_terrain)-1) if _ != LAKE_SIGNAL else 0 for _ in target_terrain]
            new_terrain = np.random.choice(target_terrain, p=prob)
        else:
            new_terrain = random.choice(target_terrain)
        PropertyBean.set_prop(choice_prop, "terrain", new_terrain)
        PropertyBean.set_prop(choice_prop, "terrain_property", self.terrain_fpt_conf[new_terrain])
        PropertyBean.set_prop(choice_prop, "terrain_score", new_terrain_score)
        #print(f"TERRAIN CHANGE: {rand_map[_y][_x]}, {choice_terrain_score} -> {new_terrain}, {new_terrain_score}!")
        rand_map[_y][_x] = new_terrain
        return choice_terrain_score, new_terrain_score, new_terrain
    
    def _close_to_ocean(self, x, y, rand_map):
        close_list = list()
        accessible_list = list()
        for step in self.total_steps:
            _x, _y = x+step[0], y+step[1]
            if self._is_wide_accessible(_x, _y):
                if rand_map[_y][_x] in OCEAN_TERRAIN_LIST:
                    close_list.append([_x, _y])
                accessible_list.append([_x, _y])
        return close_list, accessible_list

    def _cal_distance_with_loop(self, loc1, loc2):
        return min(abs(loc1[0]-loc2[0]), abs(self.xsize-loc1[0]+loc2[0])), min(abs(loc1[1]-loc2[1]), abs(self.ysize-loc1[1]+loc2[1]))

    def _is_less_than_distance(self, center, locations, dist_lower, dist_upper):
        for location in locations:
            xdist, ydist = self._cal_distance_with_loop(center, location)
            if not (xdist >= dist_lower and xdist <= dist_upper \
                and ydist >= dist_lower and ydist <= dist_upper):
                return True
        return False

    def _get_center_recent_locations(self, land_locations, center, radius, known_list, ocean_locations=list()):
        req_land_locations = list()
        req_ocean_locations = list()

        for _location in land_locations:
            xdist, ydist = self._cal_distance_with_loop(center, _location)
            if xdist <= radius and ydist <= radius and _location not in known_list:
                req_land_locations.append(_location)
                known_list += _location

        for _location in ocean_locations:
            xdist, ydist = self._cal_distance_with_loop(center, _location)
            if xdist <= radius and ydist <= radius and _location not in known_list:
                req_ocean_locations.append(_location)
                known_list += _location

        return req_land_locations, req_ocean_locations

    def get_unit_clusters(self, land_locations, unit_cnt, radius, distance, max_step=100, extra=0, ocean_locations=list()):
        step = 0
        clusters = 0

        unit_clusters = list()
        center_list = list()
        known_list = list()
        cluster_cnt = 0
        for player, unit_c in unit_cnt.items():
            if isinstance(unit_c, dict):
                if unit_c["land"]+unit_c["ocean"] > 0:
                    cluster_cnt += 1
            else:
                if unit_c > 0:
                    cluster_cnt += 1
        while clusters < cluster_cnt and step < 100:
            if isinstance(unit_cnt[list(unit_cnt.keys())[0]], dict):
                center = random.choice(land_locations+ocean_locations)
                req_land_locations, req_ocean_locations = self._get_center_recent_locations(land_locations, 
                                                                                        center, 
                                                                                        radius, 
                                                                                        known_list, 
                                                                                        ocean_locations=ocean_locations)

                if len(req_land_locations) >= min(unit_cnt[list(unit_cnt.keys())[clusters]]["land"]+extra, 3) \
                    and len(req_ocean_locations) >= min(unit_cnt[list(unit_cnt.keys())[clusters]]["ocean"], 3) \
                    and center not in center_list \
                    and not self._is_less_than_distance(center, center_list, distance[0], distance[1]):
                    unit_clusters.append({"center": center, "candidate": req_land_locations, "land": req_land_locations, "ocean": req_ocean_locations})
                    center_list.append(center)
                    clusters += 1
            else:
                center = random.choice(land_locations)
                req_land_locations, req_ocean_locations = self._get_center_recent_locations(land_locations, 
                                                                                        center, 
                                                                                        radius, 
                                                                                        known_list, 
                                                                                        ocean_locations=ocean_locations)

                if len(req_land_locations) >= unit_cnt[list(unit_cnt.keys())[clusters]]+extra \
                    and center not in center_list \
                    and not self._is_less_than_distance(center, center_list, distance[0], distance[1]):
                    unit_clusters.append({"center": center, "candidate": req_land_locations})
                    center_list.append(center)
                    clusters += 1
            step += 1
        return unit_clusters

    def _modify_land(self, rand_map, extra_map, land_center):
        """
        Randomly modify the shape of land
        """
        # whether the location is close to ocean
        # if close to ocean, make it randomly walking or wait on current location
        # if wait on current location, make it change to ocean given probability
        # if walk to ocean, make it change to land given probability

        x, y = self.get_map_accessible_location()

        close_ocean_list, accessible_list = self._close_to_ocean(x, y, rand_map)

        if len(close_ocean_list) == 0:
            return

        proba = list()
        for step in accessible_list:
            if step in close_ocean_list:
                _proba = 0.4/len(close_ocean_list)
            else:
                _proba = 0.6/(len(accessible_list)-len(close_ocean_list))
            proba.append(_proba)
        proba = [p/sum(proba) for p in proba]

        location = self._sampling_step_by_proba(accessible_list, proba)
        _x, _y = location[0], location[1]

        distance = abs(_y-land_center[1])+abs(_x-land_center[0])
        new_terrain = None
        if rand_map[_y][_x] in FPT_ZERO_SIGNAL_LIST:
            if random.random() > 1.5 * distance/(self.xsize+self.ysize):
                rand_map[_y][_x] = random.choice(TerrainTool.get_land())
                new_terrain = rand_map[_y][_x]
        else:
            if random.random() < distance/(self.xsize+self.ysize):
                rand_map[_y][_x] = " "
                new_terrain = rand_map[_y][_x]

        # remove resource
        if new_terrain is not None:
            self._clean_resource(extra_map, _y, _x)
        return

    def _rotation_map(self, rotation_angle=90, is_isotropy=True):
        # terrain rotation
        input_map = self._global_map
        rotation_terrain_map = [[' ' for _ in range(self.xsize)] for _ in range(self.ysize)]
        center_x = int(self.xsize/2) - 1
        center_y = int(self.ysize/2) - 1
        for y in range(len(input_map)):
            for x in range(len(input_map[0])):
                terrain = input_map[y][x]
                _x = round(float(x-center_x) * np.cos(rotation_angle) - float(y-center_y) * np.sin(rotation_angle) + center_x) % self.xsize
                _y = round(float(x-center_y) * np.sin(rotation_angle) + float(y-center_y) * np.cos(rotation_angle) + center_y) # % self.ysize
                if _y >= 0 and _y < self.ysize:
                    rotation_terrain_map[_y][_x] = terrain
        self._global_map = rotation_terrain_map

        # resource rotation
        rotation_extra_map = [[None for _ in range(self.xsize)] for _ in range(self.ysize)]
        for eid, data in self._extra_resources.items():
            for y, l in enumerate(data["map"]):
                for x, r in enumerate(l):
                    _x = round(float(x-center_x) * np.cos(rotation_angle) - float(y-center_y) * np.sin(rotation_angle) + center_x) % self.xsize
                    _y = round(float(x-center_x) * np.sin(rotation_angle) + float(y-center_y) * np.cos(rotation_angle) + center_y) % self.ysize
                    self._extra_resources[eid]["map"][_y][_x] = self._extra_resources[eid]["map"][y][x]
                    if not r.endswith("0"):
                        rotation_extra_map[y][x] = r
        return rotation_terrain_map, rotation_extra_map

    def _shift_map(self, windows):
        return

    def gen_rotation_shift_map(self, format_type:str, rotation:int):
        rotation_terrain_map, rotation_extra_map = self._rotation_map(rotation_angle=rotation)
        terrain_output = {"__raw__": self._global_map, "global": MapTool._convert_format(rotation_terrain_map, self._global_keys, format_type)}
        resource_output = self._align_extras_map(rotation_extra_map, format_type)
        resource_output["__raw__"] = copy.deepcopy(self._extra_resources)
        return terrain_output, resource_output, None

    def gen_random_walk_map(self, format_type:str, 
                            max_steps:int=1000000, 
                            topk:int=6, 
                            weight:dict=None,
                            score_bound:float=None,
                            max_walks:int=100,
                            margin:int=2,
                            keep_ocean:bool=True,
                            change_rate:float=0.5,
                            extra_optimal:bool=False
                            ):
        """ Generate a map by random walk. 
        terrain product:
            {0.8: ['+', 'g', 'p'], 0.4: ['d', 'h', 'j', 'm', 's', 't'], 1.2: ['f'], 0.0: ['a']}
        """
        # Calculate the scores of terrain
        terrain_product, terrain_keys = self._cal_terrain_scores(keep_ocean, weight)

        # score bound info
        score_lower_bound_conf = score_bound[0]
        score_upper_bound_conf = score_bound[1]

        # get land center
        land_center = self.get_map_accessible_location()

        rand_map = copy.deepcopy(self._global_map)
        extra_map = copy.deepcopy(self._extra_resources)
        record_covergence = list()
        step = 0
        while step < max_steps:

            #print(f"===========step: {step}============")

            # initial location
            x, y = self.get_city_accessible_location(rand_map)

            # random walk
            walk = 0
            record_covergence.append(list())
            while walk < max_walks:

                # scope
                scope = CityTool.cal_city_scope(x, y)

                # score
                total_property_dict, properties_list = self.calulate_map_properties_by_order(scope, 
                                                                                             topk=topk, 
                                                                                             weight=weight,
                                                                                             input_map=rand_map,
                                                                                             extra_resources=extra_map,
                                                                                             keep_ocean=keep_ocean)
                # change terrain
                score = dict_sum(total_property_dict, weight)
                #print(f"=====walk: {walk}, score: {score}=====")
                if score_bound is not None:
                    lower_cond = score - score_lower_bound_conf
                    upper_cond = score - score_upper_bound_conf

                    choice_terrain_space = list()
                    choice_resource_reduce_space = list()
                    choice_resource_boost_space = list()
                    topk_list = list()

                    while lower_cond < 0 or upper_cond > 0:

                        # reorder
                        properties_list = self._reorder_terrains(properties_list, keep_ocean, topk)
                        topk_list = properties_list[:topk]

                        # get effect terrain list
                        for p in topk_list:
                            if (PropertyBean.get_prop(p, "terrain_score") < terrain_keys[-1] and lower_cond < 0) or \
                                (PropertyBean.get_prop(p, "terrain_score") > terrain_keys[0] and upper_cond > 0):
                                choice_terrain_space.append(p)

                        for p in topk_list:
                            if len(PropertyBean.get_prop(p, "resource")) > 0:
                                choice_resource_reduce_space.append(p)
                            else:
                                choice_resource_boost_space.append(p)

                        new_resource_score = 0
                        choice_resource_score = 0
                        new_terrain_score = 0
                        choice_terrain_score = 0
                        move = -1 if upper_cond > 0 else 1

                        if len(choice_terrain_space) > 0:
                            # select the random terrain
                            choice_prop = random.choice(choice_terrain_space)
                            _y, _x = PropertyBean.get_prop(choice_prop, "location")
                            # change terrain
                            choice_terrain_score, new_terrain_score, new_terrain = self._change_terrain(choice_prop, terrain_keys, 
                                                                                                        terrain_product, properties_list, move, rand_map, _y, _x)
                            # remove unconsistent resource
                            choice_resource_score, new_resource_score = self._remove_resource_with_terrain(choice_prop, new_terrain, extra_map, weight, _y, _x)
                            record_covergence[step].append("terrain_change")
                        elif len(choice_resource_reduce_space) > 0 and move == -1:
                            choice_prop = random.choice(choice_resource_reduce_space)
                            _y, _x = PropertyBean.get_prop(choice_prop, "location")
                            choice_resource_score, new_resource_score = self._remove_resource(choice_prop, extra_map, weight, _y, _x)
                            record_covergence[step].append("resource_reduce")
                        elif len(choice_resource_boost_space) > 0 and move == 1:
                            choice_prop = random.choice(choice_resource_boost_space)
                            _y, _x = PropertyBean.get_prop(choice_prop, "location")
                            choice_resource_score, new_resource_score = self._add_resource(choice_prop, extra_map, weight, _y, _x)
                            record_covergence[step].append("resource_boost")
                        else:
                            raise ValueError(f"No valid action! move={move}, properties={properties_list}, boost={choice_resource_boost_space}")

                        # update scores
                        choice_score = choice_terrain_score + choice_resource_score
                        new_score = new_terrain_score + new_resource_score
                        lower_cond += round(new_score - choice_score, 3)
                        upper_cond += round(new_score - choice_score, 3)

                        # update map & properties
                        PropertyBean.set_prop(choice_prop, "property", 
                              dict_sum_by_list([PropertyBean.get_prop(choice_prop, "terrain_property"), 
                                                PropertyBean.get_prop(choice_prop, "resource_property")]))
                        PropertyBean.set_prop(choice_prop, "score", new_score-choice_score+PropertyBean.get_prop(choice_prop, "score"))

                        choice_terrain_space.clear()
                        choice_resource_reduce_space.clear()
                        choice_resource_boost_space.clear()
                        topk_list.clear()

                if step < 0.6 * max_steps:
                    # randomly change terrain and resource in the same fpt level
                    self._random_gen(properties_list, terrain_product, extra_map, rand_map, weight)

                if step < 0.5 * max_steps:
                    # randomly change land shape
                    self._modify_land(rand_map, extra_map, land_center)

                # randomly walk
                x, y = self._sampling_step(x, y, rand_map, margin)
                if x < 0 or y < 0:
                    break
                walk += 1
            step += 1

        terrain_output = {"__raw__": rand_map, "global": MapTool._convert_format(rand_map, self._global_keys, format_type)}

        # optimal extra: todo
        if extra_optimal:
            resource_conf = ResourceTool.get_resource_conf()
            for ind_y, y in enumerate(rand_map):
                for ind_x, x in enumerate(y):
                    terrain = rand_map[ind_y][ind_x]
                    if terrain in self.terrain_optimal_extra_conf:
                        self.terrain_optimal_extra_conf[terrain]

        # resource randomly
        resource_map = [[None for x in y] for y in rand_map]
        for eid, data in extra_map.items():
            for i, y in enumerate(data["map"]):
                for j, x in enumerate(y):
                    if not x.endswith("0"):
                        if resource_map[i][j] is not None:
                            resource_map[i][j] = resource_map[i][j] + "," + x
                        else:
                            resource_map[i][j] = x
        resource_output = self._align_extras_map(resource_map, format_type)
        resource_output["__raw__"] = copy.deepcopy(extra_map)

        covergence = [len(step) for step in record_covergence]
        report = {"covergence": covergence, "land_center": land_center}

        return terrain_output, resource_output, report

    def gen_other_map(self, terrain_conf, resource_conf, unit_locations, city_locations={}, format_type=None):
        # recalcuate the player map of unseen part, default a

        for player_id in unit_locations:
            unit_location = unit_locations[player_id]
            city_location = city_locations[player_id] if player_id in city_locations else {}

            # init map & resouce
            seen_locations = list()
            for _unit_id, _unit_msg in unit_location.items():
                _unit_location = _unit_msg["location"]
                _unit_name = _unit_msg["name"]
                seen_locations += UnitTool.cal_unit_scope(_unit_name, _unit_location[0], _unit_location[1], self.xsize, self.ysize)

            for _city_id, _city_msg in city_location.items():
                _city_location = _city_msg["location"]
                seen_locations += CityTool.cal_city_scope_with_loop(_city_location[0], _city_location[1], self.xsize, self.ysize)

            # player map
            player_map = self._players_map[player_id]["map"]
            for y in range(len(player_map)):
                for x in range(len(player_map[0])):
                    if int(player_id[-1]) == 0:
                        self._seen_map[y][x] = "0"
                    if [y, x] in seen_locations:
                        player_map[y][x] = "a"
                        if self._seen_map[y][x] == "0":
                            self._seen_map[y][x] = str(int(player_id[-1])+1)
                    else:
                        player_map[y][x] = "u"

            # player resource
            for eid in self._players_resource[player_id]:
                resource_map = self._players_resource[player_id][eid]["map"]
                for y in range(len(resource_map)):
                    for x in range(len(resource_map[0])):
                        if [y, x] in seen_locations:
                            resource_map[y][x] = "a"
                        else:
                            resource_map[y][x] = "0"

        # align players_map
        players_map = self._align_players_map(terrain_conf["__raw__"], format_type)
        players_resource = self._align_players_resource(resource_conf["__raw__"], format_type)

        terrain_conf.update(players_map)
        terrain_conf.update({"seen": self._convert_format(copy.deepcopy(self._seen_map), self._seen_keys, format_type)})

        resource_conf.update(players_resource)

        return terrain_conf, resource_conf
    
    def statis_city_scope(self, method:str, max_steps:int=1000000, topk:int=6, weight:dict=None):
        """ Statistic map by sampling. """
        step = 0
        output = []
        while step < max_steps:

            # initial location
            x, y = self.get_city_accessible_location()

            # scope
            scope = CityTool.cal_city_scope(x, y)
            if method == SCOPE_METHOD_ALL:
                score = self.calulate_map_properties_by_total(scope)
            elif method == SCOPE_METHOD_TOP:
                score, _ = self.calulate_map_properties_by_order(scope, topk=topk, weight=weight)
            output.append(score)
            step += 1
        return output

    @staticmethod
    def statis_map_topk(x, y, terrain_map, extra_map, terrain_conf, extra_conf, weight:dict=None, topk:int=6):
        """ Statistic map by sampling. """        
        if not MapTool._if_accessible(x, y, terrain_map):
            return
        
        # scope
        scope = CityTool.cal_city_scope_with_loop(x, y, len(terrain_map[0]), len(terrain_map))
        total_score, terrain_score, extra_score = MapTool.calulate_cri(scope, weight, terrain_map, extra_map, terrain_conf, extra_conf, topk)
        return total_score, terrain_score, extra_score

    @staticmethod
    def statis_map_properties(terrain_map, extra_map, terrain_conf, extra_conf):
        statis_terrain = dict()
        statis_extra = dict()
        for y in range(len(terrain_map)):
            for x in range(len(terrain_map[y])):
                if not MapTool._if_accessible(x, y, terrain_map):
                    continue
                    
                scope = CityTool.cal_city_scope_with_half_loop(x, y, len(terrain_map[0]), len(terrain_map))
                for loc in scope:
                    # terrain
                    if (terrain := terrain_map[loc[0]][loc[1]]) not in statis_terrain:
                        statis_terrain[terrain] = 0
                    statis_terrain[terrain] += 1
                    
                    # extra
                    for eid, data in extra_map.items():
                        if (extra := data[loc[0]][loc[1]]) not in statis_extra:
                            statis_extra[extra] = 0
                        statis_extra[extra] += 1

        return statis_terrain, statis_extra

    @staticmethod
    def calulate_cri(location_list:list, 
                    weight:dict=None, 
                    terrain_map:list=None,
                    extra_map:dict=None,
                    terrain_conf:dict=None, 
                    extra_conf:dict=None,
                    topk:int=6):
        """
        Calulating properties.
        :parameter location_list: the list of locations (y,x) of terrain.
        """
        terrain_fpt_list = []
        extra_fpt_list = []
        fpt_list = []

        for location in location_list:
            terrain = terrain_map[location[0]][location[1]]
            terrain_fpt = dict_sum(terrain_conf[terrain], weight)
            extra_fpt = []
            for key in extra_map:
                extra = extra_map[key][location[0]][location[1]]
                if extra in extra_conf:
                    extra_fpt.append(dict_sum(extra_conf[extra], weight))
                else:
                    extra_fpt.append(0)
            extra_fpt = sum(extra_fpt)

            terrain_fpt_list.append(terrain_fpt)
            extra_fpt_list.append(extra_fpt)
            fpt_list.append(terrain_fpt+extra_fpt)

        fpt_list = sorted(fpt_list, reverse=True)
        terrain_fpt_list = sorted(terrain_fpt_list, reverse=True)
        extra_fpt_list = sorted(extra_fpt_list, reverse=True)

        return sum(fpt_list[:topk]), sum(terrain_fpt_list[:topk]), sum(extra_fpt_list[:topk])

    def _cal_statis(self, score_seq, suffix:str=""):
        if suffix > "":
            suffix += "_"
        return {
                suffix+"std": round(score_seq.std(), 3), 
                suffix+"avg": round(score_seq.mean(), 3),
                suffix+"max": round(score_seq.max(),  3),
                suffix+"pct95": round(np.percentile(score_seq, 95), 3),
                suffix+"pct90": round(np.percentile(score_seq, 90), 3),
                suffix+"pct80": round(np.percentile(score_seq, 80), 3),
                suffix+"pct70": round(np.percentile(score_seq, 70), 3),
                suffix+"pct60": round(np.percentile(score_seq, 60), 3),
                suffix+"pct50": round(np.percentile(score_seq, 50), 3),
                suffix+"pct40": round(np.percentile(score_seq, 40), 3),
                suffix+"pct30": round(np.percentile(score_seq, 30), 3),
                suffix+"pct20": round(np.percentile(score_seq, 20), 3),
                suffix+"pct10": round(np.percentile(score_seq, 10), 3),
                suffix+"pct05": round(np.percentile(score_seq, 5), 3),
                suffix+"min": round(score_seq.min(), 3),
        }
    
    def statis_map(self, unit_locations, threshold, topk:int=6, weight:dict=None, 
                   max_turns=10, input_map=None, extra_resources=None):
        """ Statistic map by every location. """
        output = {}
        for player in unit_locations:
            output[player] = {}
            for uid in unit_locations[player]:
                output[player][uid] = {}
                x = unit_locations[player][uid]["location"][0]
                y = unit_locations[player][uid]["location"][1]
                max_turns_scope = UnitTool.cal_unit_max_scope(x, y, max_turns)

                topk_score_list = [[0 for _ in range(self.xsize)] for _ in range(self.ysize)]
                score_seq = list()
                unit_score_seq = list()
                for x in range(self.xsize):
                    for y in range(self.ysize):
                        city_scope = CityTool.cal_city_scope(x, y)
                        city_scope = self._check_loop_locations(city_scope)
                        topk_property, _ = self.calulate_map_properties_by_order(city_scope, 
                                                                                topk=topk, 
                                                                                weight=weight,
                                                                                input_map=input_map,
                                                                                extra_resources=extra_resources)
                        topk_score = dict_sum(topk_property, weight)
                        topk_score_list[y][x] = topk_score
                        score_seq.append(topk_score)
                        if [y, x] in max_turns_scope and input_map[y][x] not in FPT_ZERO_SIGNAL_LIST:
                            unit_score_seq.append(topk_score)
                score_seq = np.array(score_seq)
                unit_score_seq = np.array(unit_score_seq)

                output["global"] = {"topk_score": np.array(topk_score_list)}
                output.update(self._cal_statis(score_seq))
                output[player][uid].update(self._cal_statis(unit_score_seq))
                output[player][uid].update({"optimal": self._find_optimal_locations(output["global"]["topk_score"], 
                                                                            output[threshold], max_turns_scope, max_turns)})
        return output

    def _find_optimal_locations(self, statis_map, threshold, scope=None, max_turns=10):
        """ Find optimal locations. """
        optimal_locations = list()
        for x in range(statis_map.shape[1]):
            for y in range(statis_map.shape[0]):
                if scope is not None and [y, x] not in scope:
                    continue
                if statis_map[y][x] > threshold:
                    optimal_locations.append([y, x])
        return optimal_locations

    def cal_connectivity_layer(self, grid=None):
        """Label the connectivity of map with different layers. For example, the connectivity layer of map would be like
            1 1 1 1 0 2 2 2
            1 1 1 0 0 0 2 0
            1 1 1 1 0 0 0 0
            1 1 1 0 0 3 0 0
           Here, 0 means ocean tiles, and non-0 means different connected lands.
        """
        if grid is None:
            grid = self._global_map
        row = self.ysize
        col = self.xsize
        visited = set()
        count = 0
        directions=[(-1,0), (0,1), (1,0), (0,-1)]
        island_label = dict()
        island_visited = set()
        best_island = -1
        best_count = -1
        def findIsland(x, y):
            for dx, dy in directions:
                nx, ny = x+dx, y+dy
                if 0<=nx<row and 0<=ny<col and grid[nx][ny] not in LOCATION_NEGSIGNAL_LIST and (nx,ny) not in visited:
                    visited.add((nx, ny))
                    island_visited.add((nx, ny))
                    findIsland(nx, ny)

        for x in range(row):
            for y in range(col):
                if grid[x][y] not in LOCATION_NEGSIGNAL_LIST and (x,y) not in visited:
                    island_visited.clear()
                    count +=1
                    # visited
                    visited.add((x,y))
                    island_visited.add((x,y))
                    # find island
                    findIsland(x,y)
                    # label island
                    island_label[count] = copy.deepcopy(island_visited)
                    if len(island_visited) > best_count:
                        best_count = len(island_visited)
                        best_island = count
                    for _x, _y in island_visited:
                        self._layers["connectivity"][_x][_y] = count

        # metrics initialize
        metrics = {"count": count, "best_island": best_island, "best_tiles_count": best_count, "best_locations": island_label[best_island]}
        return metrics

    @staticmethod
    def map_parser(map_data):
        """ 
        Parse map string from sav file to 2-d array. 
        :parameter map_data: 2-d map string, like
            t0000="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            t0001="                   a   a   aaa    a  a     a  a    aa       a    a    a      a"
            t0002="      g                                                                       "
            t0003="     gg                    gp          :::::            ::               ::   "
            t0004="::    gp  p p             p gg      ::::::::::::::     ::::          pg   ::::"
            t0005=":    pffp g p             ppgppp   :::::::::::::::     :::       pp  gp    :::"
            t0006="    pppgp fgff        pgfgghhfhfp  :::::::::::::::  g         ggggpgppgg    ::"
            t0007="    ghfhffmfhhgp        gpffppgp    ::::::::::::::  p      g gpfpfgppgpg  g   "
            t0008=" gppghfmhfddhhgp      gggfffpgpg p      :::::::::  pgp     ppggggfffppgf  gg  "
            t0009=" ggppshsfmmdhfgg      g++gfffppgggp      :::::::    pgggg  ggfpppfsfhfpfg ggg "
            t0010=" pppfggfmdddfpp       pggpfffppppgppgpg   :::::  pgggpfghp ggfghffssmsghgfppp "
            t0011="    hsss    p p       fhgpffffppppgphff   :::::  pfhfghhgpfhfhhfgmffmmpgppp+g "
            t0012="     pfgpg        :   fpfppfffppsgpphppf  ::::   gpfphhfffhmfgfhghdgpphmpfhfpg"
            t0013="p    pp      ::  ::  ggggpgfffpppppdddhpf :::    gp+ffghdphhfpfpdfpffhpmshhhg "
            t0014="p    gp   :::::::::       gfffpsfgdpfdgf   ::  ggpggpgphdsmmmhhpffmhhshfmggggg"
            t0015="p        :::::::::      sfffffgfsdspfdppp      pggfpphpmdhhmmfpphpphmffffhfpfp"
            t0016="gg      :::::           sffffffghddfmmgpg       pggppppmmspppddhfhhdddgsdphgfp"
            t0017="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        """
        return [[element for element in line.split('=')[1] if element != '"'] 
                for line in map_data.split('\n') if line > '']
    
    @staticmethod
    def check_player_map_align_to_total(player_map, total_map):
        unalign_dict = []
        for x in range(len(player_map)):
            for y in range(len(player_map[x])):
                player_val = player_map[x][y]
                total_val = total_map[x][y]
                if  player_val != total_val and player_val != UNSEEN_SIGNAL:
                    print(f'location ({x}, {y}), player is "{player_val}", total is "{total_val}"')
                    unalign_dict.append({'x': x, 'y': y, 'player_val': player_val, 'total_val': total_val})
        return unalign_dict

    @staticmethod
    def align_to_extra(eid, extra_map, resource_map):
        for x in range(len(extra_map)):
            for y in range(len(extra_map[x])):
                if resource_map[x][y] is None:
                    extra_map[x][y] = "0"
                elif eid in resource_map[x][y]:
                    extras = resource_map[x][y].split(",")
                    for extra in extras:
                        if extra.startswith(eid):
                            extra_map[x][y] = extra.split("_")[1]
                else:
                    extra_map[x][y] = "0"                    
        return extra_map

    @staticmethod
    def align_to_map(player_map, total_map):
        """ 
        Align to the goal map. 
        :parameter player_map: 2-d map string, the map of player
        :parameter total_map: 2-d map string, the map of global, like
            t0000="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            t0001="                   a   a   aaa    a  a     a  a    aa       a    a    a      a"
            t0002="      g                                                                       "
            t0003="     gg                    gp          :::::            ::               ::   "
            t0004="::    gp  p p             p gg      ::::::::::::::     ::::          pg   ::::"
            t0005=":    pffp g p             ppgppp   :::::::::::::::     :::       pp  gp    :::"
            t0006="    pppgp fgff        pgfgghhfhfp  :::::::::::::::  g         ggggpgppgg    ::"
            t0007="    ghfhffmfhhgp        gpffppgp    ::::::::::::::  p      g gpfpfgppgpg  g   "
            t0008=" gppghfmhfddhhgp      gggfffpgpg p      :::::::::  pgp     ppggggfffppgf  gg  "
            t0009=" ggppshsfmmdhfgg      g++gfffppgggp      :::::::    pgggg  ggfpppfsfhfpfg ggg "
            t0010=" pppfggfmdddfpp       pggpfffppppgppgpg   :::::  pgggpfghp ggfghffssmsghgfppp "
            t0011="    hsss    p p       fhgpffffppppgphff   :::::  pfhfghhgpfhfhhfgmffmmpgppp+g "
            t0012="     pfgpg        :   fpfppfffppsgpphppf  ::::   gpfphhfffhmfgfhghdgpphmpfhfpg"
            t0013="p    pp      ::  ::  ggggpgfffpppppdddhpf :::    gp+ffghdphhfpfpdfpffhpmshhhg "
            t0014="p    gp   :::::::::       gfffpsfgdpfdgf   ::  ggpggpgphdsmmmhhpffmhhshfmggggg"
            t0015="p        :::::::::      sfffffgfsdspfdppp      pggfpphpmdhhmmfpphpphmffffhfpfp"
            t0016="gg      :::::           sffffffghddfmmgpg       pggppppmmspppddhfhhdddgsdphgfp"
            t0017="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        """
        for x in range(len(player_map)):
            for y in range(len(player_map[x])):
                if  player_map[x][y] != total_map[x][y] and player_map[x][y] not in (UNSEEN_SIGNAL, "0"):
                    player_map[x][y] = total_map[x][y]
        return player_map

    @staticmethod
    def align_to_resource(player_map, total_map):
        for x in range(len(player_map)):
            for y in range(len(player_map[x])):
                if  player_map[x][y] != total_map[x][y].split("_")[-1] and player_map[x][y] not in (UNSEEN_SIGNAL, "0"):
                    player_map[x][y] = total_map[x][y].split("_")[-1]
        return player_map

    @staticmethod
    def gen_map(map_data, suffix):
        output = '\n'.join([suffix+MapTool.cal_map_row(i)+'="'+''.join(row)+'"' for i, row in enumerate(map_data)])
        return output

    @staticmethod
    def cal_map_row(i, capacity=4):
        str_i = str(i)
        return '0'*(capacity-len(str_i))+str_i

if __name__ == "__main__":
    from freeciv_sav.parser.sav import SavParser
    from freeciv_sav.parser.ruleset import RulesetParser
    from freeciv_sav.utils.io import IOManager
    from freeciv_sav.components.terrain import TerrainTool
    from freeciv_sav.components.resource import ResourceTool

    sav_parser = SavParser("tests/testminitask_T1_test.sav")
    rule_parser = RulesetParser("src/freeciv_sav/config/classic/")

    # id data
    tid_conf = TerrainTool.get_tid()
    rid_conf = ResourceTool.get_rid()

    # fpt & rel data
    terrain_fpt_conf = exchange_key(
        rule_parser.get_properties("terrain", "terrain", ["food", "shield", "trade"]),
        tid_conf
    )
    resource_fpt_conf = exchange_key(
        rule_parser.get_resource_conf(),
        rid_conf
    )
    terrain_resource_conf = exchange_key_value(
        rule_parser.get_terrain_resource(),
        dict(tid_conf, **rid_conf)
    )

    # sav data
    extra_resources = ResourceTool.exchagne_rawdata(sav_parser.get_extra_resources())
    global_map = sav_parser.get_global_map()
    player_map = sav_parser.get_players_map()
    seen_map = sav_parser.get_seen_map()
    player_resource = sav_parser.get_players_resource()

    # map tool method
    map_tool = MapTool(raw_data=global_map,
                       player_map_data=player_map,
                       player_resource_data=player_resource,
                       seen_map=seen_map,
                       terrain_fpt_conf=terrain_fpt_conf,
                       resource_fpt_conf=resource_fpt_conf,
                       terrain_resource_conf=terrain_resource_conf,
                       extra_resources=extra_resources)
    metrics = map_tool.cal_connectivity_layer()
    print(map_tool._layers)
    print(metrics)

    # print(map_tool.calulate_map_properties_by_total([[i, j] for i in range(5, 15) for j in range(5, 16)]))
    # assert map_tool.cal_size() == (16, 16)
    # statis_topk = map_tool.statis_city_scope(method="topk", max_steps=1000000, topk=6, weight={"food": 0.4, "shield": 0.4, "trade": 0.2})
    # statis_all = map_tool.statis_city_scope(method="all", max_steps=1000000, weight={"food": 0.4, "shield": 0.4, "trade": 0.2})
    # IOManager.save_csv_from_dict(statis_all, filename="tests/statis/map/env_total.csv")
    # IOManager.save_csv_from_dict(statis_topk, filename="tests/statis/map/env_top6.csv")
    # terrain_output, resource_output = map_tool.gen_random_map(format_type="line")
    # output = map_tool.gen_random_walk_map(format_type="line", score_bound=[0, 10], 
    #                              max_steps=1, max_walks=1000, topk=6, weight={"food": 0.4, "shield": 0.4, "trade": 0.2})
    # print(output)
    # scope = UnitTool.cal_unit_max_scope(13, 11, 10)
    # statis_map = map_tool.statis_map(uid=101, threshold="unit_pct80", topk=6, 
    #                                  weight={"food": 0.4, "shield": 0.4, "trade": 0.2}, scope=scope)
    # print(statis_map)
    # IOManager.save_json(statis_map, filename="tests/minitasks/base/myagent_T1_task_build_city.json")
    
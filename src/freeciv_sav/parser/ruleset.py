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

import re
import glob
from freeciv_sav.utils.dic_tools import recursive_dict, search_dict 
from freeciv_sav.utils.type import TypeEnum, reg_type

IGNORE_SUFFIX = ";"
TAG_PATTERN = r"^\[([a-zA-Z0-9_]+)\]$"
KV_PATTERN = r"(.*)\=[^>](.*)"
HASH_PATTERN = r"#\ ([a-zA-Z,\ ]+).*$"
QUO_STR_PATTERN = r"^\"([a-zA-Z0-9_\ ]+)\"$"
NAME_PATTERN = r"_\(\"([a-zA-Z0-9_\.\ \']+)\"\)"
NAME2_PATTERN = r"_\(\"\?.*\:([a-zA-Z0-9_\.\ ]+)\"\)"

EXTRA_MAP = {
    "mining_shield_incr": "mine",
    "irrigation_food_incr": "irrigation",
    "road_food_incr_pct": "road",
    "road_shield_incr_pct": "road",
    "road_trade_incr_pct": "road",
}

def reg_quo_str(line:str):
    tag = re.match(QUO_STR_PATTERN, line)
    if tag:
        return tag[1]
    return

def reg_tag(line:str):
    tag = re.match(TAG_PATTERN, line)
    if tag: 
        return tag[1]
    return

def reg_name(line:str):
    if tag := re.match(NAME_PATTERN, line): 
        return tag[1]
    if tag := re.match(NAME2_PATTERN, line): 
        return tag[1]
    return reg_quo_str(line)

def reg_kv_pair(line:str):
    tag = re.match(KV_PATTERN, line)
    if tag: 
        return tag[1].strip(), tag[2].strip()
    return

def reg_hash_line(line:str):
    tag = re.match(HASH_PATTERN, line)
    if tag:
        return "#", [i.strip() for i in tag[1].split(',')], TypeEnum.HashtagProperty
    return 

def glob_dir(dir:str):
    if dir is None:
        raise ValueError("Please input the right directory of ruleset!")
    if dir.endswith("/"):
        return glob.glob(dir+"*.ruleset")
    return glob.glob(dir+"/*.ruleset")

    

class TreeNode(object):
    tech: str

    # Incoming edges
    nrequire: int
    require: list[super]

    # Outgoing edges
    nprovide: int
    provide: list[super]

class RulesetParser(object):
    """
    Ruleset file parser.
    :parameter dir: str, the path of ruleset files.
    :attribute data: dict<str, dict<str, any>>, the data after parse ruleset files.
    """

    hashkey = "#"
    hashconf = {"resource_": "terrain"}

    def __init__(self, dir:str):
        rulesets = glob_dir(dir)

        self._raw_data = dict()
        self.data = dict()

        for ruleset in rulesets:
            with open(ruleset, "r", encoding="utf-8") as filep:
                name = ruleset.split(".")[0].split("/")[-1]
                self._raw_data[name] = list()
                for line in filep:
                    self._raw_data[name] += ([] if (tmp := line.strip()) == "" else [tmp])
            self.data[name] = dict()
            self._parse(name)

    def _parse(self, name):
        """Parse ruleset into dict structure."""
        last_tag = None
        for _, raw_line in enumerate(self._raw_data[name]):
            # ignore special lines
            if raw_line.startswith(IGNORE_SUFFIX): 
                continue
            # mark the tag
            tag = reg_tag(raw_line)
            if tag:
                self.data[name][tag] = dict()
                last_tag = tag
            # get data belong to the tag
            kv_pair = reg_kv_pair(raw_line)
            reg_hash = reg_hash_line(raw_line)
            if last_tag:
                if kv_pair:
                    value = reg_type(kv_pair[1])[0]
                    stype = reg_type(kv_pair[1])[1]
                    self.data[name][last_tag][kv_pair[0]] = {"__value__": value, "__type__": stype}
                elif reg_hash:
                    if_flag = None
                    for key, mapping_value in self.hashconf.items():
                        if last_tag.startswith(key):
                            if_flag = mapping_value
                            break
                    if if_flag is not None:
                        self.data[name][last_tag][if_flag] = {"__value__": reg_hash[1], "__type__":reg_hash[2]}
                    else:
                        self.data[name][last_tag][reg_hash[0]] = {"__value__": reg_hash[1], "__type__":reg_hash[2]}
        return

    def get_value(self, keys:list, fetch_key:str=None):
        """Get data from keys."""
        return recursive_dict(keys, self.data, fetch_key)

    def search(self, key, fetch_key:str=None):
        """Search ambiguous key."""
        return search_dict(key, self.data, fetch_key)

    def get_property(self, module:str, tag:str, property:str, attribute:str="__value__"):
        if attribute == "__value__":
            return self.data[module][tag][property]["__value__"]
        return self.data[module][tag][property]

    def get_properties(self, firstkey, keyword, properties:list, name:str="name", value_type=None, lower=False, default_value=0):
        output = dict()
        for key in self.data[firstkey]:
            _keyword = keyword+"_"
            if key.startswith(_keyword):
                _key = reg_name(self.data[firstkey][key][name]["__value__"]).lower()
                output[_key] = dict()
                for property in properties:
                    if property in self.data[firstkey][key]:
                        if value_type is None:
                            output[_key][property] = self.data[firstkey][key][property]["__value__"]
                        else:
                            output[_key][property] = reg_quo_str(self.data[firstkey][key][property]["__value__"])
                        if lower and isinstance(output[_key][property], str):
                            output[_key][property] = output[_key][property].lower()
                    else:
                        output[_key][property] = default_value
        return output

    def get_terrain_resource(self):
        output = dict()
        resource_conf = self.get_properties("terrain", "resource", ["food", "shield", "trade", "terrain"], name="extra")
        for resource, fpdt in resource_conf.items():
            for terrain in fpdt["terrain"]:
                if terrain not in output:
                    output[terrain] = list()
                output[terrain].append(resource)
        return output

    def get_terrain_extra(self):
        output = dict()
        extra_conf = self.get_properties("terrain", "terrain", ["mining_shield_incr", "irrigation_food_incr", 
                                                                "road_food_incr_pct", "road_shield_incr_pct",
                                                                "road_trade_incr_pct"])
        for terrain, extra_dict in extra_conf.items():
            output[terrain] = {}
            for extra, value in extra_dict.items():
                if value > 0:
                    if EXTRA_MAP[extra] not in output[terrain]:
                        output[terrain][EXTRA_MAP[extra]] = {}
                    if "food" in extra:
                        output[terrain][EXTRA_MAP[extra]]["food"] = value
                    elif "shield" in extra:
                        output[terrain][EXTRA_MAP[extra]]["shield"] = value
                    elif "trade" in extra:
                        output[terrain][EXTRA_MAP[extra]]["trade"] = value if value < 100 else value/100

        return output

    def get_extra_conflicts(self):
        conflicts_conf = self.get_properties("terrain", "extra", ["conflicts"], default_value="")
        output = {}
        for key, conflicts in conflicts_conf.items():
            if conflicts["conflicts"] > "":
                conflicts_list = conflicts["conflicts"].split(",")
                conflicts_list = [reg_quo_str(confl.strip()).lower() for confl in conflicts_list]
                output[key] = conflicts_list
        return output

    def get_terrain_optimal_extra(self):
        terrain_extra_conf = self.get_terrain_extra()
        conflicts_conf = self.get_extra_conflicts()
        output = dict()
        print("ori: ", terrain_extra_conf)
        for terrain, extra_dict in terrain_extra_conf.items():
            output[terrain] = list()
            extra_conf = terrain_extra_conf[terrain]
            keys = list(extra_conf.keys())
            for extra in keys:
                if extra not in extra_conf:
                    continue
                fpd = extra_conf[extra]
                if extra in conflicts_conf:
                    conflicts_extra = conflicts_conf[extra]
                    for conflict in conflicts_extra:
                        if conflict in extra_conf:
                            if list(extra_conf[conflict].values())[0] <= list(fpd.values())[0]:
                                del extra_conf[conflict]
        return terrain_extra_conf

    def get_resource_conf(self):
        return self.get_properties("terrain", "resource", ["food", "shield", "trade"], name="extra")
    
    def get_wonder_conf(self):
        conf = self.get_properties("buildings", "building", ["genus"])
        print(conf)
        wonder_list = list()
        for key, genus in conf.items():
            if genus["genus"] == '"GreatWonder"':
                wonder_list.append(key)
        return wonder_list

    def get_vision_radius_sq(self):
        output = self.get_properties("units", "unit", ["vision_radius_sq"])
        for key, value in output.items():
            output[key] = value["vision_radius_sq"]
        return output
    
    def get_tech_tree(self):
        output = self.get_properties("techs", "advance", ["req1", "req2"], value_type="quo", lower=True)
        req = dict()
        pro = dict()
        for key, reqs in output.items():
            tmp = list()
            for _, _tech in reqs.items():
                if _tech is not None and _tech != "None" and _tech != "none":
                    tmp.append(_tech)
            if len(tmp) == 0:
                tmp.append("a_none")
            req[key] = tmp
            for _tmp in tmp:
                if _tmp not in pro:
                    pro[_tmp] = list()
                pro[_tmp].append(key)
        return {"req": req, "pro": pro}

    def get_unit_obsolete(self):
        output = self.get_properties("units", "unit", ["obsolete_by"], value_type="quo", lower=True)
        req = dict()
        pro = dict()
        for key, reqs in output.items():
            tmp = list()
            for _, _tech in reqs.items():
                if _tech is not None and _tech != "None" and _tech != "none":
                    tmp.append(_tech)
            if len(tmp) == 0:
                tmp.append("none")
            req[key] = tmp
            for _tmp in tmp:
                if _tmp != "none":
                    if _tmp not in pro:
                        pro[_tmp] = list()
                    pro[_tmp].append(key)
        return {"pro": req, "req": pro}

if __name__ == "__main__":
    rule_parser = RulesetParser(dir="src/freeciv_sav/config/classic/")
    assert list(rule_parser.data.keys()) == ["buildings", "effects", "styles", "nations", "units", 
                                             "cities", "actions", "techs", "game", "terrain", "governments"], "Ruleset not completed!"
    assert len(rule_parser.data["terrain"]["terrain_ocean"].keys()) == 40, "Check data structure!"
    assert rule_parser.get_value(["terrain", "terrain_ocean", "shield"])["__value__"] == 0, "Check get_value method!"
    assert rule_parser.get_property("terrain", "terrain_ocean", "shield") == 0, "Check get_property method!"
    # print(rule_parser.search("forest", fetch_key="__value__"))
    # print(rule_parser.get_value(["terrain", "resource_gold"]))
    # print(rule_parser.get_properties("terrain", "resource", ["food", "shield", "trade", "terrain"], name="extra"))
    # print(rule_parser.get_resource_conf())
    # print(rule_parser.get_vision_radius_sq())
    # print(rule_parser.get_unit_obsolete()['pro'])
    print(rule_parser.get_terrain_optimal_extra())

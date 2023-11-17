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

# count = 20
RESOURCE_CLASS = ["gold", "iron", "game", "furs", "coal", "fish", "fruit", "gems", "buffalo", "wheat",
        "oasis", "peat", "pheasant", "bonus", "ivory", "silk", "spice", "whales", "wine",
        "oil"]

EXTRA_CLASS = ["irrigation", "mine", "oil well", "pullution", "hut", "fallout", "farmland", "fortress",
        "airbase", "airbase", "buoy", "ruins", "road", "railroad", "river"]

# sav -e conf
RESOURCE_CONF = {
    "irrigation": {"row": "e00", "value": "1"}, # 0
    "mine": {"row": "e00", "value": "2"}, # 1
    "oil well": {"row": "e00", "value": "4"}, # 2
    "pollution": {"row": "e00", "value": "8"}, # 3

    "hut": {"row": "e01", "value": "1"}, # 4
    "fallout": {"row": "e01", "value": "2"}, # 5
    "farmland": {"row": "e01", "value": "4"}, # 6
    "fortress": {"row": "e01", "value": "8"},  # 7

    "airbase": {"row": "e02", "value": "1"}, 
    "buoy": {"row": "e02", "value": "2"}, 
    "ruins": {"row": "e02", "value": "4"}, 
    "road": {"row": "e02", "value": "8"}, 

    "railroad": {"row": "e03", "value": "1"}, 
    "river": {"row": "e03", "value": "2"}, 
    "gold": {"row": "e03", "value": "4"}, 
    "iron": {"row": "e03", "value": "8"}, 

    "game": {"row": "e04", "value": "1"}, 
    "furs": {"row": "e04", "value": "2"}, 
    "coal": {"row": "e04", "value": "4"}, 
    "fish": {"row": "e04", "value": "8"}, 

    "fruit": {"row": "e05", "value": "1"}, 
    "gems": {"row": "e05", "value": "2"}, 
    "buffalo": {"row": "e05", "value": "4"}, 
    "wheat": {"row": "e05", "value": "8"}, 

    "oasis": {"row": "e06", "value": "1"}, 
    "peat": {"row": "e06", "value": "2"}, 
    "pheasant": {"row": "e06", "value": "4"}, 
    "resources": {"row": "e06", "value": "8"}, 

    "ivory": {"row": "e07", "value": "1"}, 
    "silk": {"row": "e07", "value": "2"}, 
    "spice": {"row": "e07", "value": "4"}, 
    "whales": {"row": "e07", "value": "8"}, 

    "wine": {"row": "e08", "value": "1"}, 
    "oil": {"row": "e08", "value": "2"}, 
}

OPTIMAL_EXTRA_CONF = {
    "inaccessible":{

    },
    "lake":{

    },
    "ocean":{

    },
    "deep ocean":{

    },
    "glacier":{
        "mine":{
            "shield":1
        }
    },
    "desert":{
        "mine":{
            "shield":1
        },
        "road":{
            "trade":1
        }
    },
    "forest":{

    },
    "grassland":{
        "irrigation":{
            "food":1
        },
        "road":{
            "trade":1
        }
    },
    "hills":{
        "mine":{
            "shield":3
        }
    },
    "jungle":{

    },
    "mountains":{
        "mine":{
            "shield":1
        }
    },
    "plains":{
        "irrigation":{
            "food":1
        },
        "road":{
            "trade":1
        }
    },
    "swamp":{

    },
    "tundra":{
        "irrigation":{
            "food":1
        }
    }
}

class ResourceTool(object):

    """
    The tool for modified resource.
    """

    def __init__(self):
        self.rid_data = ResourceTool.get_extra_dict()
    
    @staticmethod
    def get_resource_conf():
        return RESOURCE_CONF

    @staticmethod
    def get_extra_dict():
        output = dict()
        for resource, property in RESOURCE_CONF.items():
            output[property["row"]+"_"+property["value"]] = resource
        return output
    
    def get_rid(self, rid:str):
        return self.rid_data[rid]

    @staticmethod
    def get_rid():
        output = dict()
        for resource, property in RESOURCE_CONF.items():
            if resource in RESOURCE_CLASS:
                output[resource] = property["row"]+"_"+property["value"]
        return output
    
    @staticmethod
    def exchagne_rawdata(raw_data):
        for e_table, e_value in raw_data.items():
            for row_key, row_list in e_value.items():
                for index, resource in enumerate(row_list):
                    row_list[index] = e_table+"_"+resource
        return raw_data
    
if __name__ == "__main__":
    obj = ResourceTool()
    print(ResourceTool.get_rid())

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

class PropertyBean(object):

    """
    Define data structure: [score, {property, terrain, resource, location, terrain_property, resource_property}]
    -- Score is used to sort array.
    """
    
    @staticmethod
    def set_prop(property, key, value):
        if key == "score":
            property[0] = value
        elif key == "terrain_score":
            property[1] = value
        elif key == "resource_score":
            property[2] = value
        elif key == "property":
            property[-1]["property"] = value
        elif key == "terrain":
            property[-1]["terrain"] = value
        elif key == "terrain_property":
            property[-1]["terrain_property"] = value
        elif key == "resource_property":
            property[-1]["resource_property"] = value
        elif key == "resource":
            property[-1]["resource"] = value
        elif key == "location":
            property[-1]["location"] = value
        return 
    
    @staticmethod
    def get_prop(property, key):
        """
        property structure: [score, {property, terrain, resource, location, terrain_property, resource_property}]
        """
        if key == "score":
            return property[0]
        elif key == "terrain_score":
            return property[1]
        elif key == "resource_score":
            return property[2]
        elif key == "property":
            return property[-1]["property"]
        elif key == "terrain":
            return property[-1]["terrain"]
        elif key == "terrain_property":
            return property[-1]["terrain_property"]
        elif key == "resource_property":
            return property[-1]["resource_property"]
        elif key == "resource":
            return property[-1]["resource"]
        elif key == "location":
            return property[-1]["location"]
        return 


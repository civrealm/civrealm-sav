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

TERRIDENT_CONF = {
    "inaccessible": "i",
    "lake": "+",
    "ocean": " ",
    "deep ocean": ":",
    "glacier": "a",
    "desert": "d",
    "forest": "f",
    "grassland": "g",
    "hills": "h",
    "jungle": "j",
    "mountains": "m",
    "plains": "p",
    "swamp": "s",
    "tundra": "t"
}

LOW_LAND_TERRIDENT_CONF = ["d", "h", "j", "m", "s", "t", "f", "g", "p"]

class TerrainTool(object):

    @staticmethod
    def get_tid():
        return TERRIDENT_CONF
    
    @staticmethod
    def get_land():
        return LOW_LAND_TERRIDENT_CONF

if __name__ == "__main__":
    obj = TerrainTool()

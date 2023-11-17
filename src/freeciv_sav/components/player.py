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
from freeciv_sav.bean.parse_type import ParseTypeBean

PLAYER_PREFIX = "player"
AI_SKILL_LEVEL = {"easy": "Easy", "hard": "Hard", "normal": "Normal"}

class PlayerTool(object):
    """The modified tool for player information."""
    def __init__(self, raw_data:dict):
        self.data = copy.deepcopy(raw_data)
        self._data = raw_data

    def _get_player_uid(self, player_id):
        return PLAYER_PREFIX+str(player_id)

    def set_name(self, player_id:int, name:str):
        player_uid = self._get_player_uid(player_id)
        ParseTypeBean.set_value(self.data[player_uid], "name", name.capitalize())
        ParseTypeBean.set_value(self.data[player_uid], "username", name)
        return

    def get_old_name(self, player_id:int):
        return ParseTypeBean.get_realvalue(self._data[self._get_player_uid(player_id)]["name"])

    def get_new_name(self, player_id:int):
        return ParseTypeBean.get_realvalue(self.data[self._get_player_uid(player_id)]["name"])

    def get_conf(self):
        return self.data
    
    def set_nunits(self, conf):
        for player_uid in self.data:
            ParseTypeBean.set_value(self.data[player_uid], "nunits", str(conf[player_uid]))
        return
        
    def set_difficulty(self, player_id:int, difficulty:str):
        player_uid = self._get_player_uid(player_id)
        ParseTypeBean.set_value(self.data[player_uid], "ai.level", AI_SKILL_LEVEL[difficulty])
        return

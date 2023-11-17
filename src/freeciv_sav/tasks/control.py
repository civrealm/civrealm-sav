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

from freeciv_sav.config.lua_script_minitask import *

CODE_SUFFIX = "code"
VAR_SUFFIX = "var"

class Control(object):

    @staticmethod
    def change_type(arr):
        return '{'+','.join(['{'+','.join([str(_) for _ in list(x)])+'}' for x in arr])+'}'
    
    @staticmethod
    def ctrl_build_city(max_turns, score_goal, score_conf, difficulty):
        return BUILD_CITY_START_SCRIPT+BUILD_CITY_INPUT_CONF.format(Control.change_type(score_conf), 
                                 max_turns, 
                                 score_goal,
                                 difficulty)+BUILD_CITY_END_SCRIPT
    
    @staticmethod
    def ctrl_battle(max_turns):
        return BATTLE_START_SCRIPT+BATTLE_INPUT_CONF.format(max_turns)+BATTLE_END_SCRIPT
    
    @staticmethod
    def ctrl_attackcity(max_turns):
        return ATTACK_CITY_START_SCRIPT+ATTACK_CITY_INPUT_CONF.format(max_turns)+ATTACK_CITY_END_SCRIPT
    
    @staticmethod
    def ctrl_defendcity(max_turns):
        return DEFEND_CITY_START_SCRIPT+DEFEND_CITY_INPUT_CONF.format(max_turns)+DEFEND_CITY_END_SCRIPT
    
    @staticmethod
    def ctrl_tradetech(max_turns):
        return TRADE_TECH_START_SCRIPT+TRADE_TECH_INPUT_CONF.format(max_turns)+TRADE_TECH_END_SCRIPT

    @staticmethod
    def ctrl_naval(max_turns):
        return NAVAL_START_SCRIPT+NAVAL_INPUT_CONF.format(max_turns)+NAVAL_END_SCRIPT

    @staticmethod
    def ctrl_citytile_wonder(max_turns):
        return CITY_TILE_WONDER_START_SCRIPT+CITY_TILE_WONDER_INPUT_CONF.format(max_turns)+CITY_TILE_WONDER_END_SCRIPT

    @staticmethod
    def ctrl_build_infra(max_turns, goal):
        return BUILD_INFRA_START_SCRIPT+BUILD_INFRA_INPUT_CONF.format(max_turns, goal)+BUILD_INFRA_END_SCRIPT

    @staticmethod
    def ctrl_transport(goal):
        return TRANSPORT_START_SCRIPT+TRANSPORT_INPUT_CONF.format(goal)+TRANSPORT_END_SCRIPT

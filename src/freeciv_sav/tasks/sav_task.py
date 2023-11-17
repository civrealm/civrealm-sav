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
import random
import numpy as np
from freeciv_sav.parser.sav import SavParser
from freeciv_sav.parser.ruleset import RulesetParser
from freeciv_sav.components.map import MapTool
from freeciv_sav.utils.dic_tools import exchange_key, exchange_key_value
from freeciv_sav.utils.io import IOManager
from freeciv_sav.components.terrain import TerrainTool
from freeciv_sav.components.resource import ResourceTool
from freeciv_sav.components.player import PlayerTool
from freeciv_sav.components.city import CityTool
from freeciv_sav.bean.format_type import FormatTypeBean
from freeciv_sav.components.unit import UnitTool
from freeciv_sav.components.game import GameTool
from freeciv_sav.components.event import EventTool
from freeciv_sav.components.treaty import TreatyTool
from freeciv_sav.components.research import ResearchTool
from freeciv_sav.tasks.control import Control
from civrealm.freeciv.build_server import run_bash_command
from sys import argv

TAG_PATTERN = r"^\[([a-zA-Z0-9_]+)\]$"

class SavTaskGenerator(object):
    """
    Task Generator for sav files.

    :param user_name: string, user name
    :param task_type: string, type of mini task

    """
    def __init__(self, user_name:str, task_type:str, task_subtype:str,
                 max_turns:int, goal:float, pct_require:str, input_file:str, ruleset_dir:str, docker_path:str, shared_mas_path:str=None):
        self.user_name = user_name
        self.task_type = task_type
        self.task_subtype = task_subtype
        self.max_turns = max_turns
        self.goal = goal
        self.pct_require = pct_require
        self.docker_path = docker_path
        self.shared_mas_path = shared_mas_path
        self.sav_parser = SavParser(input_file)
        self.rule_parser = RulesetParser(ruleset_dir)
        self._init()

    def _init(self):
        self.map_op = self._register_map_op()
        self.player_op = self._register_player_op()
        self.unit_op = self._register_unit_op()
        self.game_op = self._register_game_op()
        self.city_op = self._register_city_op()
        self.event_op = self._register_event_op()
        self.research_op = self._register_research_op()
        self.treaty_op = self._register_treaty_op()
        return

    def _register_event_op(self):
        print(" =======> BEGIN BUILD EVENT OPERATOR <==========")
        return EventTool(self.sav_parser.get_events())

    def _register_treaty_op(self):
        print(" =======> BEGIN BUILD TREATY OPERATOR <==========")
        return TreatyTool(self.sav_parser.get_treaty())

    def _register_research_op(self):
        print(" =======> BEGIN BUILD RESEARCH OPERATOR <==========")
        return ResearchTool(self.sav_parser.get_global_techs_info(),
                            self.rule_parser.get_tech_tree())

    def _register_player_op(self):
        print(" =======> BEGIN BUILD PLAYER OPERATOR <==========")
        return PlayerTool(self.sav_parser.get_players_info())

    def _register_city_op(self):
        print(" =======> BEGIN BUILD CITY OPERATOR <==========")
        return CityTool(self.sav_parser.get_city_info(),
                             global_owner_data=self.sav_parser.get_tiles_own_info(),
                             global_eowner_data=self.sav_parser.get_tiles_eown_info(),
                             global_source_data=self.sav_parser.get_tiles_source_info(),
                             global_worked_data=self.sav_parser.get_tiles_worked_info())

    def _register_game_op(self):
        print(" =======> BEGIN BUILD GAME OPERATOR <==========")
        return GameTool(self.sav_parser.get_game_info())

    def _register_unit_op(self):
        print(" =======> BEGIN BUILD UNIT OPERATOR <==========")
        return UnitTool(self.sav_parser.get_player_unit_info(), unit_obsolete_conf=self.rule_parser.get_unit_obsolete())

    def _register_map_op(self):
        print(" =======> BEGIN BUILD MAP OPERATOR <==========")
        tid_conf = TerrainTool.get_tid()
        rid_conf = ResourceTool.get_rid()

        # fpt & rel data
        terrain_fpt_conf = exchange_key(
            self.rule_parser.get_properties("terrain", "terrain", ["food", "shield", "trade"]),
            tid_conf
        )
        resource_fpt_conf = exchange_key(
            self.rule_parser.get_resource_conf(),
            rid_conf
        )
        terrain_resource_conf = exchange_key_value(
            self.rule_parser.get_terrain_resource(),
            dict(tid_conf, **rid_conf)
        )

        print("terrain_fpt_conf: ", terrain_fpt_conf)
        print("\nresource_fpt_conf: ", resource_fpt_conf)
        print("\nterrain_resource_conf: ", terrain_resource_conf)

        # sav data
        extra_resources = ResourceTool.exchagne_rawdata(self.sav_parser.get_extra_resources())
        global_map = self.sav_parser.get_global_map()
        player_map = self.sav_parser.get_players_map()
        seen_map = self.sav_parser.get_seen_map()
        players_resource = self.sav_parser.get_players_resource()

        return MapTool(raw_data=global_map,
                       player_map_data=player_map,
                       player_resource_data=players_resource,
                       seen_map=seen_map,
                       terrain_fpt_conf=terrain_fpt_conf,
                       resource_fpt_conf=resource_fpt_conf,
                       terrain_resource_conf=terrain_resource_conf,
                       extra_resources=extra_resources)

    @staticmethod
    def push_to_docker(filename:str, docker_path:str):
        run_bash_command(f'docker exec -it {docker_path.split(":")[0]} mkdir {docker_path.split(":")[1]}')
        run_bash_command(f'docker cp {filename} {docker_path}')
        return

    def _gen_line(self, gen_terrain_conf, 
                  gen_resource_conf, 
                  gen_player_conf,
                  gen_unit_conf,
                  gen_city_conf,
                  gen_city_map_conf,
                  gen_game_conf,
                  lua_conf,
                  event_conf,
                  treaty_conf,
                  research_conf,
                  player_key, 
                  row_key,
                  if_flag):
        line = None
        if player_key is None and if_flag == 1:
            if gen_terrain_conf is not None and row_key in gen_terrain_conf.get("global", {}):
                # terrain global map
                line = gen_terrain_conf["global"][row_key]
            elif gen_terrain_conf is not None and row_key in gen_terrain_conf.get("seen", {}):
                # terrain seen map
                line = gen_terrain_conf["seen"][row_key]
            elif gen_resource_conf is not None and row_key in gen_resource_conf:
                # resource global map
                line = gen_resource_conf[row_key]
            elif gen_game_conf is not None and row_key in gen_game_conf:
                # resource global map
                line = gen_game_conf[row_key]
            elif gen_city_map_conf is not None and row_key in gen_city_map_conf:
                line = gen_city_map_conf[row_key]
            elif row_key in ["var", "vars", "code"]:
                line = lua_conf
        elif player_key is not None:
            # Modified all the player maps of file handler
            if gen_terrain_conf is not None and row_key in gen_terrain_conf.get(player_key, {}):
                line = gen_terrain_conf[player_key][row_key]
            elif gen_player_conf is not None and row_key in gen_player_conf.get(player_key, {}):
                line = gen_player_conf[player_key][row_key]
            elif gen_resource_conf is not None and row_key in gen_resource_conf.get(player_key, {}):
                # resource global map
                line = gen_resource_conf[player_key][row_key]
            elif gen_unit_conf is not None and row_key in gen_unit_conf.get(player_key, {}):
                if if_flag == 1:
                    line = FormatTypeBean.line_from_dataframe(gen_unit_conf[player_key][row_key], "u=")
                else:
                    line = ""
            elif gen_city_conf is not None and row_key in gen_city_conf.get(player_key, {}):
                if if_flag == 1:
                    line = FormatTypeBean.line_from_dataframe(gen_city_conf[player_key][row_key], "c=")
                else:
                    line = ""
            elif event_conf is not None and row_key in event_conf:
                line = event_conf[row_key] if if_flag == 1 else ""
            elif treaty_conf is not None and row_key in treaty_conf:
                line = treaty_conf[row_key]
            elif research_conf is not None and row_key in research_conf:
                line = research_conf[row_key] if if_flag == 1 else ""

        if line is not None:
            return line
        return

    def _gen_sav(self, filename:str, 
                gen_terrain_conf:dict=None,
                gen_resource_conf:dict=None,
                gen_player_conf:dict=None,
                gen_game_conf:dict=None,
                lua_conf:str=None,
                unit_conf:dict=None,
                city_conf:dict=None,
                city_map_conf:dict=None,
                event_conf:dict=None,
                treaty_conf:dict=None,
                research_conf:dict=None):
        """Generate a new sav file.
        :parameter gen_map: list<list<str>>
        todo: inverse parse step
        """
        filep = IOManager.get_handler(filename)
        player_key = None
        row_key = ""
        if_flag = 0
        for line in self.sav_parser.lines:
            if len(line.split("=")) > 1 and "," not in line.split("=")[0]:
                row_key = line.split("=")[0]
                if_flag = 1

            if _player_key := re.match(r"\[(player\d+)\]", line):
                player_key = _player_key[1]

            if re.match(TAG_PATTERN, line) is None:
                _line = self._gen_line(gen_terrain_conf, gen_resource_conf, 
                                   gen_player_conf, unit_conf, city_conf,
                                   city_map_conf, gen_game_conf, lua_conf, 
                                   event_conf, treaty_conf, research_conf,
                                   player_key, row_key, if_flag)
                if _line is not None:
                    line = _line

            if len(line) > 0:
                if isinstance(line, str):
                    filep.write(line+"\n")
                elif isinstance(line, list):
                    for l in line:
                        filep.write(l+"\n")

            # mark where first get the key
            if_flag = 0

        # close file handler
        filep.close()

        return

    def gen_sav(self, terrain_conf=None, 
                resource_conf=None, 
                unit_conf=None, 
                city_conf=None, 
                city_map_conf=None, 
                game_conf=None, 
                event_conf=None, 
                lua_conf=None, 
                treaty_conf=None,
                research_conf=None,
                output_file=None, 
                player_conf:dict=dict()):
        print(" =======> GENERATEING SAV FILE <==========")
        self._gen_sav(output_file, 
                    gen_terrain_conf=terrain_conf,
                    gen_resource_conf=resource_conf,
                    gen_player_conf=player_conf,
                    gen_game_conf=game_conf,
                    lua_conf=lua_conf,
                    unit_conf=unit_conf,
                    city_conf=city_conf,
                    city_map_conf=city_map_conf,
                    event_conf=event_conf,
                    treaty_conf=treaty_conf,
                    research_conf=research_conf
                    )

        # submit to the mnt path: ~/mas
        run_bash_command(f'docker cp {output_file} {self.docker_path}')

        # push to docker
        if self.docker_path is not None:
            SavTaskGenerator.push_to_docker(output_file, self.docker_path)

        return

    def gen_random_task(self, format_type:str, 
                             output_file:str,
                             map_cnt:int=1):
        for i in range(map_cnt):
            terrain_conf, resource_conf = self.map_op.gen_random_map(format_type=format_type)
            self.gen_sav(terrain_conf, resource_conf, output_file.format(i))
        return

    def _get_name(self):
        return self.user_name
    
    def _format_output_file(self, output_file, difficulty, map_id):
        return output_file.format(self.user_name, self.task_type+'_'+self.task_subtype, self.user_name, difficulty, map_id)+".sav"
    
    def gen_build_city(self, format_type:str, 
                             score_bound:float,
                             max_steps:int,
                             max_walks:int,
                             topk:int, 
                             weight:dict,
                             difficulty:str,
                             output_file:str,
                             keep_ocean:bool=True,
                             map_id:int=1):
        # global map & resource update
        terrain_conf, resource_conf, report = self.map_op.gen_random_walk_map(format_type=format_type, 
                                                score_bound=score_bound, 
                                                max_steps=max_steps, 
                                                max_walks=max_walks,
                                                topk=topk, 
                                                weight=weight,
                                                keep_ocean=keep_ocean)

        # unit update
        unit_conf = self.unit_op.set_location_random(self.map_op.get_unit_accessible_locations(terrain_conf["__raw__"], connectivity=True))
        unit_locations = self.unit_op.get_location()

        # player update
        self.player_op.set_name(0, self._get_name())
        player_conf = FormatTypeBean.line_from_kv_parse_type(self.player_op.get_conf())

        # game update
        self.game_op.set_init_status()
        game_conf = FormatTypeBean.line_from_kv_parse_type_first_level(self.game_op.get_conf())

        # other map update
        terrain_conf, resource_conf = self.map_op.gen_other_map(terrain_conf, resource_conf, unit_locations, format_type=format_type)

        # control game
        statis_map = self.map_op.statis_map(unit_locations, threshold=self.pct_require, topk=6, 
                                        weight={"food": 0.4, "shield": 0.4, "trade": 0.2},
                                        input_map=terrain_conf["__raw__"],
                                        extra_resources=resource_conf["__raw__"],
                                        )
        lua_conf = Control.ctrl_build_city(self.max_turns, statis_map[self.pct_require], 
                                            statis_map["global"]["topk_score"], difficulty)
        
        # gen sav
        conv = int(np.mean(report["covergence"][-int(0.1*len(report["covergence"])):])/np.max(report["covergence"])*100)
        self.gen_sav(terrain_conf, resource_conf, 
                        player_conf=player_conf, 
                        unit_conf=unit_conf, 
                        game_conf=game_conf, 
                        lua_conf=lua_conf,
                        output_file=self._format_output_file(output_file, difficulty, map_id))

        return

    def gen_naval(self, format_type:str, 
                             score_bound:float,
                             max_steps:int,
                             max_walks:int,
                             topk:int, 
                             rate:list, 
                             weight:dict,
                             difficulty:str,
                             output_file:str,
                             keep_ocean:bool=True,
                             map_id:int=1):
        while True:
            # global map & resource update
            terrain_conf, resource_conf, _ = self.map_op.gen_random_walk_map(format_type=format_type, 
                                                    score_bound=score_bound, 
                                                    max_steps=max_steps, 
                                                    max_walks=max_walks,
                                                    topk=topk, 
                                                    weight=weight,
                                                    keep_ocean=keep_ocean)
            ocean_location = self.map_op.get_unit_accessible_locations(terrain_conf["__raw__"], is_ocean=True)
            if len(ocean_location) == 0: continue

            # unit update
            set_cluster = self.unit_op.set_location_with_cluster(self.map_op.get_unit_clusters, land_locations=[], ocean_locations=ocean_location)
            if not set_cluster:
                self.unit_op.reset()
                continue
            self.unit_op.set_unit_number(rate=rate)
            unit_conf = self.unit_op.get_conf()
            unit_locations = self.unit_op.get_location()

            # player update
            self.player_op.set_name(0, self._get_name())
            self.player_op.set_difficulty(1, "normal")
            self.player_op.set_nunits(self.unit_op.get_unit_number())
            player_conf = FormatTypeBean.line_from_kv_parse_type(self.player_op.get_conf())

            # game update
            self.game_op.set_init_status()
            game_conf = FormatTypeBean.line_from_kv_parse_type_first_level(self.game_op.get_conf())

            # other map update with multi-player
            terrain_conf, resource_conf = self.map_op.gen_other_map(terrain_conf, resource_conf, unit_locations, format_type=format_type)

            # control game
            lua_conf = Control.ctrl_naval(self.max_turns)

            # gen sav
            self.gen_sav(terrain_conf, resource_conf, 
                         player_conf=player_conf, 
                         unit_conf=unit_conf, 
                         game_conf=game_conf, 
                         lua_conf=lua_conf,
                         output_file=self._format_output_file(output_file, difficulty, map_id))
            break

        return

    def gen_battle(self, format_type:str, 
                             score_bound:float,
                             max_steps:int,
                             max_walks:int,
                             topk:int, 
                             weight:dict,
                             rate:list, 
                             difficulty:str,
                             output_file:str,
                             keep_ocean:bool=True,
                             map_id:int=1):
        while True:
            # global map & resource update
            terrain_conf, resource_conf, _ = self.map_op.gen_random_walk_map(format_type=format_type, 
                                                    score_bound=score_bound, 
                                                    max_steps=max_steps, 
                                                    max_walks=max_walks,
                                                    topk=topk, 
                                                    weight=weight,
                                                    keep_ocean=keep_ocean)

            # unit update
            set_cluster = self.unit_op.set_location_with_cluster(self.map_op.get_unit_clusters, 
                                                   self.map_op.get_unit_accessible_locations(terrain_conf["__raw__"], connectivity=True))
            if not set_cluster:
                self.unit_op.reset()
                continue
            self.unit_op.set_unit_number(rate=rate)
            self.unit_op.set_unit_type()

            unit_conf = self.unit_op.get_conf()
            unit_locations = self.unit_op.get_location()

            # player update
            self.player_op.set_name(0, self._get_name())
            self.player_op.set_difficulty(1, "normal")
            self.player_op.set_nunits(self.unit_op.get_unit_number())
            player_conf = FormatTypeBean.line_from_kv_parse_type(self.player_op.get_conf())

            # game update
            self.game_op.set_init_status()
            game_conf = FormatTypeBean.line_from_kv_parse_type_first_level(self.game_op.get_conf())

            # other map update with multi-player
            terrain_conf, resource_conf = self.map_op.gen_other_map(terrain_conf, resource_conf, unit_locations, format_type=format_type)

            # control game
            lua_conf = Control.ctrl_battle(self.max_turns)

            # gen sav
            self.gen_sav(terrain_conf, resource_conf, 
                         player_conf=player_conf, 
                         unit_conf=unit_conf, 
                         game_conf=game_conf, 
                         lua_conf=lua_conf,
                         output_file=self._format_output_file(output_file, difficulty, map_id))
            break

        return

    def gen_attack_defend_city(self, format_type:str, 
                             score_bound:float,
                             max_steps:int,
                             max_walks:int,
                             topk:int, 
                             rate:list, 
                             weight:dict,
                             difficulty:str,
                             output_file:str,
                             keep_ocean:bool=True,
                             map_id:int=1):
        while True:
            # global map & resource update
            terrain_conf, resource_conf, _ = self.map_op.gen_random_walk_map(format_type=format_type, 
                                                    score_bound=score_bound, 
                                                    max_steps=max_steps, 
                                                    max_walks=max_walks,
                                                    topk=topk, 
                                                    weight=weight,
                                                    keep_ocean=keep_ocean)

            # unit update
            clusters = self.unit_op.set_location_with_cluster(self.map_op.get_unit_clusters, 
                                                   self.map_op.get_unit_accessible_locations(terrain_conf["__raw__"], connectivity=True),
                                                   # special for city
                                                   extra=1)
            if len(clusters) == 0:
                self.unit_op.reset()
                continue

            self.unit_op.set_unit_number(rate=rate)
            self.unit_op.set_unit_type()
            unit_conf = self.unit_op.get_conf()
            unit_locations = self.unit_op.get_location()

            # city update
            self.city_op.set_location_with_cluster(clusters, unit_locations)
            city_conf = self.city_op.get_player_city_data()
            city_location = self.city_op.get_location()
            city_map_conf = FormatTypeBean.line_from_dict(self.city_op.get_city_map_data(), sep=",")

            # player update
            self.player_op.set_name(0, self._get_name())     
            self.player_op.set_difficulty(1, "normal")
            self.player_op.set_nunits(self.unit_op.get_unit_number())
            player_conf = FormatTypeBean.line_from_kv_parse_type(self.player_op.get_conf())

            # game update
            self.game_op.set_init_status()
            game_conf = FormatTypeBean.line_from_kv_parse_type_first_level(self.game_op.get_conf())

            # other map update with multi-player
            terrain_conf, resource_conf = self.map_op.gen_other_map(terrain_conf, resource_conf, 
                                                                    unit_locations, 
                                                                    city_location,
                                                                    format_type)

            # control game
            if self.task_subtype == "attack_city":
                lua_conf = Control.ctrl_attackcity(self.max_turns)
            elif self.task_subtype == "defend_city":
                lua_conf = Control.ctrl_defendcity(self.max_turns)

            # gen sav
            self.gen_sav(terrain_conf, resource_conf, 
                         player_conf=player_conf, 
                         unit_conf=unit_conf, 
                         city_conf=city_conf,
                         city_map_conf=city_map_conf,
                         game_conf=game_conf, 
                         lua_conf=lua_conf,
                         output_file=self._format_output_file(output_file, difficulty, map_id))
            break

        return

    def gen_tradetech(self, format_type:str, 
                             difficulty:str,
                             output_file:str,
                             map_id:int=1):
        while True:

            # player update
            self.player_op.set_name(0, self._get_name())    
            self.player_op.set_difficulty(1, difficulty)
            self.player_op.set_difficulty(2, difficulty)
            player_conf = FormatTypeBean.line_from_kv_parse_type(self.player_op.get_conf())

            # game update
            self.game_op.set_init_status()
            game_conf = FormatTypeBean.line_from_kv_parse_type_first_level(self.game_op.get_conf())

            # event update
            self.event_op.set_name(old_name=self.player_op.get_old_name(0), new_name=self.player_op.get_new_name(0))
            event_conf = self.event_op.get_format(format="line")

            # treaty update
            self.treaty_op.set_name(old_name=self.player_op.get_old_name(0), new_name=self.player_op.get_new_name(0))
            treaty_conf = self.treaty_op.get_format(format="line")

            # research update
            if not self.research_op.random_walk(pos_depth=3, neg_depth=3, max_walks=5):
                self.research_op.reset()
                continue
            research_conf = self.research_op.get_format(format="line")

            # control game
            lua_conf = Control.ctrl_tradetech(self.max_turns)

            # gen sav
            self.gen_sav(event_conf=event_conf,
                         player_conf=player_conf,
                         treaty_conf=treaty_conf,
                         game_conf=game_conf, 
                         lua_conf=lua_conf,
                         research_conf=research_conf,
                         output_file=self._format_output_file(output_file, difficulty, map_id))
            break

        return

    def gen_citytile_wonder(self, format_type:str, 
                             score_bound:float,
                             max_steps:int,
                             max_walks:int,
                             topk:int, 
                             weight:dict,
                             difficulty:str,
                             output_file:str,
                             keep_ocean:bool=True,
                             map_id:int=1):
        while True:
            # global map & resource update
            terrain_conf, resource_conf, _ = self.map_op.gen_random_walk_map(format_type=format_type, 
                                                    score_bound=score_bound, 
                                                    max_steps=max_steps, 
                                                    max_walks=max_walks,
                                                    topk=topk, 
                                                    weight=weight,
                                                    keep_ocean=keep_ocean)

            # unit update
            clusters = self.unit_op.set_location_with_cluster(self.map_op.get_unit_clusters, 
                                                   self.map_op.get_unit_accessible_locations(terrain_conf["__raw__"]),
                                                   # special for city
                                                   ocean_locations=self.map_op.get_unit_accessible_locations(terrain_conf["__raw__"], is_ocean=True),
                                                   extra=1)
            if len(clusters) == 0:
                self.unit_op.reset()
                continue
            unit_conf = self.unit_op.get_conf()
            unit_locations = self.unit_op.get_location()

            # city update
            self.city_op.set_location_with_cluster(clusters, unit_locations)
            city_conf = self.city_op.get_player_city_data()
            city_location = self.city_op.get_location()
            city_map_conf = FormatTypeBean.line_from_dict(self.city_op.get_city_map_data(), sep=",")

            # player update
            self.player_op.set_name(0, self._get_name())     
            player_conf = FormatTypeBean.line_from_kv_parse_type(self.player_op.get_conf())

            # game update
            self.game_op.set_init_status()
            game_conf = FormatTypeBean.line_from_kv_parse_type_first_level(self.game_op.get_conf())

            # other map update with multi-player
            terrain_conf, resource_conf = self.map_op.gen_other_map(terrain_conf, resource_conf, 
                                                                    unit_locations, 
                                                                    city_location,
                                                                    format_type)

            # control game
            lua_conf = Control.ctrl_citytile_wonder(self.max_turns)

            # gen sav
            self.gen_sav(terrain_conf, resource_conf, 
                         player_conf=player_conf, 
                         unit_conf=unit_conf, 
                         city_conf=city_conf,
                         city_map_conf=city_map_conf,
                         game_conf=game_conf, 
                         lua_conf=lua_conf,
                         output_file=self._format_output_file(output_file, difficulty, map_id))
            break

        return

    def gen_transport(self, format_type:str, 
                             difficulty:str,
                             output_file:str,
                             goal:int,
                             map_id:int=1):
        while True:
            # init parameters
            rotation = random.choice([0, np.pi, np.pi*1.5])

            # global map & resource update
            terrain_conf, resource_conf, _ = self.map_op.gen_rotation_shift_map(format_type=format_type, rotation=rotation)

            # unit update
            self.unit_op.rotation_location(rotation, xsize=self.map_op.xsize, ysize=self.map_op.ysize)
            self.unit_op.set_unit_number()
            unit_locations = self.unit_op.get_location()
            unit_conf = self.unit_op.get_conf()

            # city update
            self.city_op.rotation_location(rotation)
            city_location = self.city_op.get_location()
            city_conf = self.city_op.get_player_city_data()
            print(self.city_op.get_city_map_data())
            city_map_conf = FormatTypeBean.line_from_dict(self.city_op.get_city_map_data(), sep=",")

            # other map update with multi-player
            terrain_conf, resource_conf = self.map_op.gen_other_map(terrain_conf, resource_conf, 
                                                                    unit_locations, 
                                                                    city_location,
                                                                    format_type)
            # player update
            self.player_op.set_name(0, self._get_name())     
            self.player_op.set_nunits(self.unit_op.get_unit_number())
            player_conf = FormatTypeBean.line_from_kv_parse_type(self.player_op.get_conf())

            # game update
            self.game_op.set_init_status()
            game_conf = FormatTypeBean.line_from_kv_parse_type_first_level(self.game_op.get_conf())

            # control game
            lua_conf = Control.ctrl_transport(goal)

            self.gen_sav(terrain_conf, resource_conf, 
                         player_conf=player_conf, 
                         unit_conf=unit_conf, 
                         city_conf=city_conf,
                         city_map_conf=city_map_conf,
                         game_conf=game_conf, 
                         lua_conf=lua_conf,
                         output_file=self._format_output_file(output_file, difficulty, map_id))
            break

        return

    def gen_build_infra(self, format_type:str, 
                             score_bound:float,
                             max_steps:int,
                             max_walks:int,
                             topk:int, 
                             weight:dict,
                             difficulty:str,
                             output_file:str,
                             keep_ocean:bool=True,
                             map_id:int=1):
        while True:
            # global map & resource update
            terrain_conf, resource_conf, _ = self.map_op.gen_random_walk_map(format_type=format_type, 
                                                    score_bound=score_bound, 
                                                    max_steps=max_steps, 
                                                    max_walks=max_walks,
                                                    topk=topk, 
                                                    weight=weight,
                                                    keep_ocean=keep_ocean)

            # unit update
            clusters = self.unit_op.set_location_with_cluster(self.map_op.get_unit_clusters, 
                                                   self.map_op.get_unit_accessible_locations(terrain_conf["__raw__"], connectivity=True),
                                                   # special for city
                                                   extra=1)
            if len(clusters) == 0:
                self.unit_op.reset()
                continue
            self.unit_op.set_unit_number()
            unit_conf = self.unit_op.get_conf()
            unit_locations = self.unit_op.get_location()

            # city update
            self.city_op.set_location_with_cluster(clusters, unit_locations)
            city_conf = self.city_op.get_player_city_data()
            city_location = self.city_op.get_location()
            city_map_conf = FormatTypeBean.line_from_dict(self.city_op.get_city_map_data(), sep=",")

            # player update
            self.player_op.set_name(0, self._get_name())     
            self.player_op.set_nunits(self.unit_op.get_unit_number())
            player_conf = FormatTypeBean.line_from_kv_parse_type(self.player_op.get_conf())

            # game update
            self.game_op.set_init_status()
            game_conf = FormatTypeBean.line_from_kv_parse_type_first_level(self.game_op.get_conf())

            # other map update with multi-player
            terrain_conf, resource_conf = self.map_op.gen_other_map(terrain_conf, resource_conf, 
                                                                    unit_locations, 
                                                                    city_location,
                                                                    format_type)

            statis_map = self.map_op.statis_map(unit_locations, threshold=self.pct_require, topk=21, 
                                            weight={"food": 0.4, "shield": 0.4, "trade": 0.2},
                                            input_map=terrain_conf["__raw__"],
                                            extra_resources=resource_conf["__raw__"],
                                            )

            # control game
            lua_conf = Control.ctrl_build_infra(self.max_turns, statis_map[self.pct_require])

            # gen sav
            self.gen_sav(terrain_conf, resource_conf, 
                         player_conf=player_conf, 
                         unit_conf=unit_conf, 
                         city_conf=city_conf,
                         city_map_conf=city_map_conf,
                         game_conf=game_conf, 
                         lua_conf=lua_conf,
                         output_file=self._format_output_file(output_file, difficulty, map_id))
            break

        return

if __name__ == "__main__":
    print("Sav Manager!")
    """
    """
    from freeciv_sav.config.minitask_config import TASK_CONFIG
    import multiprocessing

    user_name = argv[1]
    map_cnt = int(argv[2])
    docker_image = argv[3]
    control_list = argv[4].split(",")

    shared_mas_path = None
    docker_path = "{}:/var/lib/tomcat10/webapps/data/savegames/{}/".format(docker_image, user_name)
    ruleset_dir = "src/freeciv_sav/config/classic/"
    pct_require = "pct80"
    format_type = "line"
    weight = {"food": 0.4, "shield": 0.4, "trade": 0.2}
    max_steps = 100
    max_walks = 200
    topk = 6

    def func(params):
        user_name, task, difficulty, map_id = params["user_name"], params["task"], params["difficulty"], params["map_id"]
        sav_manager = SavTaskGenerator(
            user_name=user_name,
            task_type=task["type"],
            task_subtype=task["subtype"],
            max_turns=task["max_turns"],
            goal=task.get("goal"),
            pct_require=pct_require,
            input_file=task["input_file"],
            ruleset_dir=ruleset_dir, 
            docker_path=docker_path,
            shared_mas_path=shared_mas_path)

        if task["subtype"] == "build_city":
            sav_manager.gen_build_city(format_type=format_type, 
                                score_bound=difficulty["score_bound"],
                                max_steps=max_steps, 
                                max_walks=max_walks,
                                topk=topk, 
                                weight=weight,
                                difficulty=difficulty["level"],
                                output_file=task["output_file"],
                                keep_ocean=True,
                                map_id=map_id,
                                )
        elif task["subtype"] in ("ancient_era", "modern_era", "industry_era", "info_era", "medieval"):
            sav_manager.gen_battle(format_type=format_type, 
                                    score_bound=[-1, 100], 
                                    max_steps=max_steps, 
                                    max_walks=max_walks,
                                    topk=topk, 
                                    weight=weight,
                                    difficulty=difficulty["level"],
                                    rate=difficulty["rate"],
                                    output_file=task["output_file"],
                                    keep_ocean=True,
                                    map_id=map_id,
                                    )
        elif task["subtype"] in ("naval", "naval_modern"):
            sav_manager.gen_naval(format_type=format_type, 
                                    score_bound=[-1, 100], 
                                    max_steps=max_steps, 
                                    max_walks=max_walks,
                                    topk=topk, 
                                    weight=weight,
                                    rate=difficulty["rate"],
                                    difficulty=difficulty["level"],
                                    output_file=task["output_file"],
                                    keep_ocean=True,
                                    map_id=map_id,
                                    )
        elif task["subtype"] == "trade_tech":
            sav_manager.gen_tradetech(format_type=format_type, 
                                    difficulty=difficulty["level"],
                                    output_file=task["output_file"],
                                    map_id=map_id,
                                    )
        elif task["subtype"] in ("attack_city", "defend_city"):
            sav_manager.gen_attack_defend_city(format_type=format_type, 
                                    score_bound=[-1, 100], 
                                    max_steps=max_steps, 
                                    max_walks=max_walks,
                                    topk=topk, 
                                    rate=difficulty["rate"],
                                    weight=weight,
                                    difficulty=difficulty["level"],
                                    output_file=task["output_file"],
                                    keep_ocean=True,
                                    map_id=map_id,
                                    )
        elif task["subtype"] in ("citytile_wonder", ):
            sav_manager.gen_citytile_wonder(format_type=format_type, 
                                    score_bound=[-1, 100], 
                                    max_steps=max_steps, 
                                    max_walks=max_walks,
                                    topk=topk, 
                                    weight=weight,
                                    difficulty=difficulty["level"],
                                    output_file=task["output_file"],
                                    keep_ocean=True,
                                    map_id=map_id,
                                    )
        elif task["subtype"] in ("build_infra", ):
            sav_manager.gen_build_infra(format_type=format_type, 
                                    score_bound=[-1, 100], 
                                    max_steps=max_steps, 
                                    max_walks=max_walks,
                                    topk=topk, 
                                    weight=weight,
                                    difficulty=difficulty["level"],
                                    output_file=task["output_file"],
                                    keep_ocean=True,
                                    map_id=map_id,
                                    )
        elif task["subtype"] in ("transport", ):
            sav_manager.gen_transport(format_type=format_type, 
                                    difficulty=difficulty["level"],
                                    output_file=task["output_file"],
                                    goal=difficulty["goal"],
                                    map_id=map_id,
                                    )
        return

    from freeciv_sav.tasks.checker import Checker
    params_list = list()

    for task in TASK_CONFIG:
        if task.get("status") in control_list:
            checker = Checker("/tmp/", f"/tmp/{user_name}/")
            checker.init_task(name=user_name, mas_path="/tmp/mas/minitasks/", minitask=task["type"]+"_"+task["subtype"])
            for difficulty in task["difficulty"]:
                for map_id in range(map_cnt):
                    if task.get("status") == "supple":
                        if not checker.check_task(user_name, task["type"]+"_"+task["subtype"], difficulty['level'], map_id):
                            params_list.append({"task": task, "difficulty": difficulty, "map_id": map_id, "user_name": user_name})
                    else:
                        params_list.append({"task": task, "difficulty": difficulty, "map_id": map_id, "user_name": user_name})
    if "online" in control_list:
        pool = multiprocessing.Pool(50)
        res = pool.map(func, params_list)
        pool.close()
        pool.join()
    else:
        for param in params_list:
            func(param)
        print(f"FINISHED {len(params_list)} TASKS!")

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
from io import StringIO
import pandas as pd
from freeciv_sav.bean.parse_type import ParseTypeBean
from freeciv_sav.bean.format_type import FormatTypeBean

# terrain map
PLAYER_TERRAIN_SIGNAL = "map_t"
# extra resource map
PLAYER_EXTRA_SIGNAL = "map_e"
# unseen map
PLAYER_UNSEEN_SIGNAL = "map_u"
# the tiles owned by player id
GLOBAL_OWN_SIGNAL = "owner"
# the city center
GLOBAL_EOWN_SIGNAL = "eowner"
# unknown id
GLOBAL_SOURCE_SIGNAL = "source"
# the tiles worked by citizens, satisfied: city_size = worked_count - free_worked_tiles + specialists
GLOBAL_WORKED_SIGNAL = "worked"

# player string pattern
PATTERN_PLAYER_KEY = r"player\d+"
# raw representation
RAW_REPRE = "__raw__"
GLOBAL_TERRAIN_SIGNAL = "t"
SEEN_TERRAIN_SIGNAL = "k00"
EXTRA_RESOURCE_SIGNAL = "e0"
EXTRA_RESOURCE_PATTERN = r"(e0\d)"
PLAYER_RESOURCE_PATTERN = r"map_(e0\d)"
UNIT_SIGNAL = "u"
CITY_SIGNAL = "c"
TECH_SIGNAL = "t"
# placing
# owner
# eowner
# dc

class SavParser:
    """Sav file parser."""

    def __init__(self, filename: str = None):
        """
        Parameters
        ----------
        filename: name of sav file. Must be a unzipped file ending with `.sav`
        """
        self.filename = filename
        self.lines = []
        self.tags = {}
        self.players = list()
        if self.filename is not None:
            self._parse()

    def reset(self, filename: str):
        self.filename = filename
        self.lines.clear()
        self.tags.clear()
        self.players.clear()
        self._parse()
        return

    def _parse(self):
        with open(self.filename, "r", encoding="utf-8") as filep:
            for line in filep:
                self.lines += ([] if (tmp := line.strip()) == "" else [tmp])

        # Probably we can change the model to "read a line and parse"
        # instead of this "read all and parse parts" strategy?
        self.parse(self.tag_cond, self.tags)
        for key in self.tags:
            self.parse_tag(key)
            # record player keys
            if re.match(PATTERN_PLAYER_KEY, key):
                self.players.append(key)
        return

    def _parse_map(self):
        """
        Convert raw_data to 2-d array.
        todo: only finished global map parser.
        """
        return

    @staticmethod
    def tag_cond(line: str):
        """
        Condition for tags.

        Return
        ------
        condition, name, rest
        """
        return line[0] == "[" and line[-1] == "]", line[1:-1], -1

    @staticmethod
    def def_cond(line: str):
        """
        Condition for an item in a tag.

        Return
        ------
        (is_a_tag: bool, name_of_tag: str, end_position: int)
        """
        return ((x, line[:x.end() - 1], x.end()) if
                (x := re.match(R"^[\.a-zA-Z0-9_-]+=", line)) else
                (False, "", 0))

    def parse(self, cond: callable, coll: dict):
        """Parse the stored lines."""
        last = 0
        last_tag = "__head__"
        for index, line in enumerate(self.lines):
            result, name, rest = cond(line)
            if result:
                if last_tag != "":
                    coll[last_tag] = {
                        RAW_REPRE: (  # [ self.lines[last][rest:]] +
                            self.lines[last + 1:index])
                    }

                last = index
                last_tag = name

        coll[last_tag] = {
            RAW_REPRE: (  # [self.lines[last][rest:]] +
                self.lines[last + 1:])
        }

    def parse_code(self, lines: list, cur_index: int, prefix: int):
        """
        Parse code-style item.

        cur_index: int. Is set to be a "previous line number"
        """

        text = ""
        while (lines[cur_index][prefix:] == ""
               or lines[cur_index][prefix:][-1] != "$"):
            text += lines[cur_index][prefix:] + "\n"
            prefix = 0
            cur_index += 1

        return text, cur_index + 1

    def parse_table(self, lines: list, cur_index: int, prefix: int):
        """
        Parse table-style item.

        Parameters
        ----------
        cur_index: int. Is set to be a "previous line number"
        """

        text = ""
        while (lines[cur_index][prefix:][-1] != "}"):
            text += lines[cur_index][prefix:] + "\n"
            prefix = 0
            cur_index += 1
        try:
            table = pd.read_csv(StringIO(text))
        except pd.errors.ParserError:
            table = text.split("\n")
        return table, cur_index+1

    def parse_basic(self, lines: list, cur_index: int, prefix: int):
        """
        Parse simple items.
        (one-liner of csv format, no tables, no codes)

        Convert
            "Workers",12,FALSE,"Great Library"
        into
            [('"', 'Workers'), ('', '12'), ('', 'FALSE'), ('"', 'Great Library')]
        """
        line = lines[cur_index][prefix:]
        return re.findall(
            R"""(?:^|,)(?=[^"]|(")?)"?((?(1)[^"]*|[^,"]*))"?(?=,|$)""",
            line), cur_index + 1

    def parse_line(self, lines: list, cur_index: int, prefix: int):
        """

        """
        # print("PARSE_LINE", lines)
        if lines[cur_index][prefix] == "$":
            return self.parse_code(lines, cur_index, prefix + 1)
        if lines[cur_index][prefix] == "{":
            return self.parse_table(lines, cur_index, prefix + 1)

        return self.parse_basic(lines, cur_index, prefix)

    def parse_tag(self, key: str):
        """
        """
        lines = self.tags[key][RAW_REPRE]
        cur_index = 0
        while cur_index < len(lines):
            if len(lines[cur_index].strip()) == 0:
                cur_index += 1
                continue
            result, name, prefix = self.def_cond(lines[cur_index])

            if result:
                # print(name)
                data, cur_index = self.parse_line(lines, cur_index, prefix)
                self.tags[key][name] = data
            else:
                cur_index += 1

    def get(self, key):
        """Get data by key."""
        return self.tags[key]
    
    def get_game_map(self, tag_name: str = "", prefix: str = None):
        """
        Get a specific map from sav.

        If prefix is None, then get available map names from tag_name.
        Otherwise, get the map itself.
        """
        if prefix is None:
            search_base = ({tag_name: self.tags[tag_name]}
                           if tag_name in self.tags else self.tags)
            prefix_available = {}
            for name, tag in search_base.items():
                if len(prefix_list := [item[:-4] for item in tag.keys() if item[-4:] == "0000"]) > 0:
                    prefix_available[name] = prefix_list
            return prefix_available

        assert tag_name in self.tags

        tag = self.tags[tag_name]
        assert prefix+"0000" in tag

        line_names = sorted([name for name in tag.keys() if prefix==name[:-4]])
        if "," in tag[line_names[0]][0][1]:
            method = lambda x: x.split(",")
        else:
            method = lambda x: [y for y in x]
        data = [method(tag[x][0][1]) for x in line_names]
        return data

    def get_map_abbr_dict(self):
        terrident = self.tags["savefile"]["terrident"].copy()
        terrident["name"] = terrident["name"].str.lower()
        return {
            "full": terrident.set_index("name").to_dict()["identifier"],
            "abbr": terrident.set_index("identifier").to_dict()["name"]
        }

    def _get_map(self, key, feature, sep=""):
        map_data = self.get(key)
        data = dict()
        for key, row in map_data.items():
            if key.startswith(feature):
                if sep == "":
                    data[key] = list(ParseTypeBean.adapt_to_parser(row))
                else:
                    data[key] = ParseTypeBean.adapt_to_parser(row).split(sep)
        return data

    def _get_player_inf(self, cond_func, value_func=None):
        players_info = dict()
        for player in self.players:
            player_data = self.get(player)
            players_info[player] = dict()
            for key, row in player_data.items():
                if cond_func(key, row):
                    players_info[player][key] = row if value_func is None else value_func(row)
        return players_info

    def get_global_map(self):
        return self._get_map("map", GLOBAL_TERRAIN_SIGNAL)

    def get_seen_map(self):
        return self._get_map("map", SEEN_TERRAIN_SIGNAL)

    def get_extra_resources(self):
        map_data = self.get("map")
        extra_resources = dict()
        for key, row in map_data.items():
            if key.startswith(EXTRA_RESOURCE_SIGNAL):
                extra_key = re.match(EXTRA_RESOURCE_PATTERN, key)[0]
                if extra_key not in extra_resources:
                    extra_resources[extra_key] = dict()
                extra_resources[extra_key][key] = list(ParseTypeBean.adapt_to_parser(row))
        return extra_resources
    
    def get_players_map(self):
        return self._get_player_inf(lambda key, row: key.startswith(PLAYER_TERRAIN_SIGNAL), 
                                    lambda row: list(ParseTypeBean.adapt_to_parser(row)))
    
    def get_players_resource(self):
        players_info = dict()
        for player in self.players:
            player_data = self.get(player)
            players_info[player] = dict()
            for key, row in player_data.items():
                if key.startswith(PLAYER_EXTRA_SIGNAL):
                    extra_key = re.match(PLAYER_RESOURCE_PATTERN, key)[1]
                    if extra_key not in players_info[player]:
                        players_info[player][extra_key] = dict()
                    players_info[player][extra_key][key] = list(ParseTypeBean.adapt_to_parser(row))
        return players_info

    def get_players_info(self):
        def _player_info(key, row):
            return not key.startswith(PLAYER_TERRAIN_SIGNAL) and \
                    not key.startswith(PLAYER_EXTRA_SIGNAL) and \
                     not key.startswith(PLAYER_UNSEEN_SIGNAL) and \
                      key != RAW_REPRE and isinstance(row, list)
        return self._get_player_inf(_player_info)

    def get_player_unit_info(self):
        return self._get_player_inf(lambda key, row: key == UNIT_SIGNAL)

    def get_game_info(self):
        dic = dict()
        for key, value in self.tags["game"].items():
            if key != "__raw__":
                dic[key] = value
        return dic
    
    def get_city_info(self):
        return self._get_player_inf(lambda key, row: key == CITY_SIGNAL)
    
    def get_tiles_own_info(self):
        return self._get_map("map", GLOBAL_OWN_SIGNAL, sep=",")
    
    def get_tiles_eown_info(self):
        return self._get_map("map", GLOBAL_EOWN_SIGNAL, sep=",")

    def get_tiles_source_info(self):
        return self._get_map("map", GLOBAL_SOURCE_SIGNAL, sep=",")
    
    def get_tiles_worked_info(self):
        return self._get_map("map", GLOBAL_WORKED_SIGNAL, sep=",")
    
    def get_global_techs_info(self):
        return self.tags["research"]["r"]
    
    def get_events(self):
        return self.tags["event_cache"]["events"]

    def get_treaty(self):
        output = dict()
        if "treaty0" in self.tags:
            for key, value in self.tags["treaty0"].items():
                if key != "__raw__":
                    output[key] = value
        return output

if __name__ == "__main__":
    sav_parser = SavParser("tests/minitasks/base/myagent_T1_task_tradetech.sav")
    print(sav_parser.get_players_info())

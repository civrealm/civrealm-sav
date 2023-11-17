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
from freeciv_sav.bean.parse_type import ParseTypeBean

class GameTool(object):
    """The modified tool for game information."""
    def __init__(self, raw_data:dict):
        self.data = raw_data

    def set_init_status(self):
        ParseTypeBean.set_value(self.data, "turn", 1)
        ParseTypeBean.set_value(self.data, "phase", 0)
        return

    def get_conf(self):
        return self.data

    def get_turn(self):
        return ParseTypeBean.get_value(self.data["turn"], "int")

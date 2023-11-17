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

from freeciv_sav.bean.format_type import FormatTypeBean
from freeciv_sav.bean.parse_type import ParseTypeBean

class TreatyTool(object):
    def __init__(self, treaty_data):
        self._treaty_data = treaty_data

    def set_name(self, old_name, new_name):
        for key, row in self._treaty_data.items():
            ParseTypeBean.set_value(self._treaty_data, key, ParseTypeBean.get_realvalue(row).replace(old_name, new_name))
        return

    def get_conf(self):
        return self._treaty_data

    def get_format(self, format="line"):
        return FormatTypeBean.line_from_kv_parse_type_first_level(self._treaty_data)

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

class EventTool(object):
    def __init__(self, event_data):
        self._event_data = event_data
    
    def set_name(self, old_name, new_name):
        for index, row in enumerate(self._event_data):
            self._event_data[index] = row.replace(old_name, new_name)
        return

    def get_conf(self):
        return self._event_data

    def get_format(self, format="line"):
        return {"events": "events="+FormatTypeBean.line_from_list(self._event_data)}

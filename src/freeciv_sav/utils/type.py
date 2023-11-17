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
from enum import Enum, unique

INTEGER_PATTERN = r"^(\-?[1-9][0-9]*|0)$"
INTEGER_COMMENT_PATTERN = r"^(\-?[1-9][0-9]*|0)\ *;.*$"
INTEGERSTR_PATTERN = r"^0[0-9]+$"
QUOTATION_STR_PATTERN = r"^\"[a-zA-Z0-9_\-\ ]+\"$"
STR_PATTERN = r"^[a-zA-Z0-9_\-\ ]+$"

@unique
class TypeEnum(Enum):
    Unknown = 0
    Integer = 1
    IntegerStr = 2
    Str = 3
    QuotationStr = 4
    IntegerCommentAfter = 5
    HashtagProperty = 6

def reg_type(value:str):
    if re.match(INTEGER_PATTERN, value):
        return int(value), TypeEnum.Integer
    elif re.match(INTEGERSTR_PATTERN, value):
        return value, TypeEnum.IntegerStr
    elif new_v := re.match(INTEGER_COMMENT_PATTERN, value):
        return new_v[1], TypeEnum.IntegerCommentAfter
    elif re.match(QUOTATION_STR_PATTERN, value):
        return value, TypeEnum.QuotationStr
    elif re.match(STR_PATTERN, value):
        return value, TypeEnum.Str
    return value, TypeEnum.Unknown

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
import random
from freeciv_sav.utils.dic_tools import recursive_dict_out
from freeciv_sav.bean.format_type import FormatTypeBean

TECH_VECTOR = ["A_NONE","Advanced Flight","Alphabet","Amphibious Warfare",
                   "Astronomy","Atomic Theory","Automobile","Banking","Bridge Building",
                   "Bronze Working","Ceremonial Burial","Chemistry","Chivalry","Code of Laws",
                   "Combined Arms","Combustion","Communism","Computers","Conscription",
                   "Construction","Currency","Democracy","Economics","Electricity",
                   "Electronics","Engineering","Environmentalism","Espionage","Explosives",
                   "Feudalism","Flight","Fusion Power","Genetic Engineering","Guerilla Warfare",
                   "Gunpowder","Horseback Riding","Industrialization","Invention","Iron Working",
                   "Labor Union","Laser","Leadership","Literacy","Machine Tools","Magnetism",
                   "Map Making","Masonry","Mass Production","Mathematics","Medicine","Metallurgy",
                   "Miniaturization","Mobile Warfare","Monarchy","Monotheism","Mysticism",
                   "Navigation","Nuclear Fission","Nuclear Power","Philosophy","Physics",
                   "Plastics","Polytheism","Pottery","Radio","Railroad","Recycling",
                   "Refining","Refrigeration","Robotics","Rocketry","Sanitation","Seafaring",
                   "Space Flight","Stealth","Steam Engine","Steel","Superconductors","Tactics",
                   "The Corporation","The Republic","The Wheel","Theology","Theory of Gravity",
                   "Trade","University","Warrior Code","Writing"]

class ResearchTool(object):

    tech_vector = [tech.lower() for tech in TECH_VECTOR]
    tech_mapping = {tech.lower(): tech for tech in TECH_VECTOR}
    
    def __init__(self, techs_data, techs_conf):
        """
        techs_data: like
            [research]
            r={"number","goal_name","techs","futuretech","bulbs_before","saved_name","bulbs","now_name","got_tech","got_tech_multi","done"
            0,"A_UNSET",1,0,0,"A_UNSET",0,"Horseback Riding",FALSE,FALSE,"1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
            1,"A_UNSET",1,0,0,"A_UNSET",0,"Warrior Code",FALSE,FALSE,"1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
            }
        """
        self._techs_data = techs_data
        self.__techs_data = copy.deepcopy(techs_data)
        self._techs_conf = techs_conf

    def reset(self):
        self._techs_data = self.__techs_data
        return

    def _get_techs_done(self, done):
        output = list()
        for i, d in enumerate(list(done)):
            if d == "1":
                output.append(self.tech_vector[i].lower())
        return output
    
    def get_techs_done(self, count=False):
        techs = dict()
        for _, row in self._techs_data.iterrows():
            techs_done = self._get_techs_done(row["done"])
            techs[FormatTypeBean.player_id_format(row["number"])] = len(techs_done) if count else techs_done
        return techs
    
    def set_techs_done(self, done, known_techs):
        output = ""
        known_ids = [self.tech_vector.index(tech) for tech in known_techs]
        for i, d in enumerate(list(done)):
            if i > 0:
                if i in known_ids:
                    output += "1"
                else:
                    output += "0"
            else:
                output += d
        return output
    
    def count_techs(self, done):
        cnt = 0
        for i in list(done):
            if i == "1":
                cnt += 1
        return cnt
    
    def set_techs(self, players_info):
        for _, row in self._techs_data.iterrows():
            player_id = FormatTypeBean.player_id_format(row["number"])
            self._techs_data.loc[row["number"], "done"] = self.set_techs_done(row["done"], players_info[player_id]["done"])
            self._techs_data.loc[row["number"], "now_name"] = self.tech_mapping[players_info[player_id]["now_name"]]
            self._techs_data.loc[row["number"], "techs"] = self.count_techs(self._techs_data.loc[row["number"], "done"])
            self._techs_data.loc[row["number"], "goal_name"] = "A_UNSET"
        return 

    def set_now_name(self, name):
        return

    def set_goal_name(self, name="A_UNSET"):
        return

    def set_saved_name(self, name):
        return

    def set_future_tech(self, name):
        return

    def get_format(self, format="line"):
        return {"r": FormatTypeBean.line_from_dataframe(self._techs_data, "r=")}

    def get_full_techs_by_edge(self, edge_techs):
        output = list()
        for tech in edge_techs:
            tmp = list()
            recursive_dict_out(key=tech, dic=self._techs_conf["req"], output=tmp)
            output.extend([ele for group in tmp for ele in group])
        output = list(set(output))
        return output

    def get_techs_edge(self, techs):
        output = list()
        for tech in techs:
            flag = 0
            if tech in self._techs_conf["pro"]:
                future_techs = self._techs_conf["pro"][tech]
                for _fut in future_techs:
                    if _fut in techs:
                        flag = 1
                        break
            if flag == 0:
                output.append(tech)
        return output
    
    def call_diff(self, last_techs, current_techs):
        if len(last_techs) == 0:
            return False
        _a = set(last_techs)
        _b = set(current_techs)
        _c = _a.intersection(_b)
        if len(_c) < len(_a) and len(_c) < len(_b):
            return False
        return True

    def random_walk(self, neg_depth=3, pos_depth=3, max_walks=10):
        players_known_techs = self.get_techs_done()
        players_info = dict()
        last_known_techs = []
        for playerid, known_techs in players_known_techs.items():
            print(f"___________________________ {playerid} ___________________________________")
            players_info[playerid] = dict()
            techs_edge = self.get_techs_edge(known_techs)
            walk = 0

            while walk < max_walks:
                print("known_techs: ", known_techs)
                print("techs_edge: ", techs_edge)

                rand = random.random()
                choice_tech = "a_none"

                if rand < 0.7:
                    # pos
                    print("========= pos ========")
                    choice_tech = random.choice(techs_edge)
                    depth = random.randint(1, pos_depth)
                    _depth = 0
                    print("pos ---------> ", choice_tech)
                    while _depth < depth:
                        if choice_tech not in self._techs_conf["pro"]:
                            break
                        choice_tech = random.choice(self._techs_conf["pro"][choice_tech])
                        print("add -------> ", choice_tech)
                        _depth += 1
                elif rand > 0.7 and rand < 0.9:
                    # neg
                    print("========= neg ========")
                    random.shuffle(techs_edge)
                    choice_tech = techs_edge.pop()
                    depth = random.randint(1, neg_depth)
                    _depth = 0
                    print("neg ---------> ", choice_tech)
                    while _depth < depth:
                        if choice_tech not in self._techs_conf["req"]:
                            break
                        choice_tech = random.choice(self._techs_conf["req"][choice_tech])
                        print("pop -------> ", choice_tech)
                        _depth += 1
                # update known_techs
                print("choice_tech: ", choice_tech)
                if choice_tech not in techs_edge:
                    techs_edge.append(choice_tech)
                print(techs_edge)
                known_techs = self.get_full_techs_by_edge(techs_edge)
                techs_edge = self.get_techs_edge(known_techs)
                walk += 1
            
            if self.call_diff(last_known_techs, known_techs):
                return False
            print("final known_techs: ", known_techs)
            print("final techs_edge: ", techs_edge)
            players_info[playerid]["done"] = known_techs
            players_info[playerid]["edge"] = techs_edge
            players_info[playerid]["now_name"] = self.find_now_tech(known_techs, techs_edge)
            last_known_techs = list(set(known_techs + last_known_techs))

        self.set_techs(players_info)
        return True

    def find_now_tech(self, known_techs, techs_edge):
        for tech in techs_edge:
            pro_techs = self._techs_conf["pro"][tech]
            for _future_tech in pro_techs:
                req_techs = self._techs_conf["req"][_future_tech]
                flag = 1
                for _req_tech in req_techs:
                    if _req_tech not in known_techs:
                        flag = 0
                if flag:
                    return _future_tech
        return ""

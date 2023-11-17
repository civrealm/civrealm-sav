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

import glob
from civrealm.envs.freeciv_minitask_env import MAX_ID, MinitaskDifficulty, MinitaskType
from civrealm.freeciv.build_server import run_bash_command

class Checker(object):
    def __init__(self, tmp_path, tmp_mas_path):
        self.tmp_path = tmp_path
        self.tmp_mas_path = tmp_mas_path
        self.mkdir(tmp_path, tmp_mas_path)
        self.lack_list = list()

    def mkdir(self, tmp_path, tmp_mas_path):
        run_bash_command(f"mkdir {tmp_path}")
        run_bash_command(f"rm -rf {tmp_mas_path}")
        run_bash_command(f"mkdir {tmp_mas_path}")
        return
    
    def check_mas(self, name, mas_path, max_id=MAX_ID):
        print(mas_path+f"{name}/*")
        zip_set = glob.glob(mas_path+f"{name}/*")
        print(f"ZIP SET: {zip_set}")
        for zip in zip_set:
            run_bash_command(f"unzip -o {zip} -d {self.tmp_mas_path}")
        check_list = glob.glob(self.tmp_mas_path+"*.sav")

        for minitask in MinitaskType.list():
            print(f"----------- checking {minitask}--------------")
            if_flag = 0
            cnt = 0
            for level in MinitaskDifficulty.list():
                for id in range(max_id):
                    sav_name = self.tmp_mas_path+'{}_T1_task_{}_level_{}_id_{}.sav'.format(name, minitask, level, id)
                    if sav_name not in check_list:
                        cnt += 1
                print(f"{minitask} LACK: {cnt}")
        return
    
    def init_task(self, name, mas_path, minitask=None, max_id=MAX_ID):
        zip_set = mas_path+f"{name}/{minitask}.zip"
        run_bash_command(f"unzip -o {zip_set} -d {self.tmp_mas_path}")
        check_list = glob.glob(self.tmp_mas_path+"*.sav")
        for level in MinitaskDifficulty.list():
            for id in range(max_id):
                sav_name = self.tmp_mas_path+'{}_T1_task_{}_level_{}_id_{}.sav'.format(name, minitask, level, id)
                if sav_name not in check_list:
                    print(f"sav {sav_name} not in {minitask} zip!")
                    self.lack_list.append(sav_name)
        return 

    def check_task(self, name, minitask, level, id):
        sav_name = self.tmp_mas_path+'{}_T1_task_{}_level_{}_id_{}.sav'.format(name, minitask, level, id)
        if sav_name in self.lack_list:
            return False
        return True

if __name__ == "__main__":
    from sys import argv
    user_name = argv[1]
    max_id = int(argv[2])
    checker = Checker("~/tmp/", "~/tmp/mas/")
    checker.check_mas(user_name, mas_path="~/mas/minitasks/", max_id=max_id)

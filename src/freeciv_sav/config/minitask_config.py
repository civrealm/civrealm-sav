TASK_CONFIG = [
        {
                "type": "development",
                "subtype": "build_city",
                "status": "online",
                "max_turns": 30,
                "input_file": "tests/minitasks/base/myagent_T1_task_development_build_city.sav",
                "output_file": "tests/minitasks/{}/{}/{}_T1_task_development_build_city_level_{}_id_{}",
                "difficulty": [
                    {"level": "hard", "score_bound": [0, 2.5]},
                    {"level": "normal", "score_bound": [2.5, 7]},
                    {"level": "easy", "score_bound": [7, 10]},
                    ]
         },
        {
                "type": "battle",
                "subtype": "ancient_era",
                "status": "online",
                "max_turns": 50,
                "input_file": "tests/minitasks/base/myagent_T1_task_battle_ancient_era.sav",
                "output_file": "tests/minitasks/{}/{}/{}_T1_task_battle_ancient_era_level_{}_id_{}",
                "difficulty":[{"level": "normal", "rate": [0.9, 1.1]}, {"level": "hard", "rate": [1.1, 2]}, {"level": "easy", "rate": [0.5, 0.9]}]
         },
        {
                "type": "battle",
                "subtype": "industry_era",
                "status": "online",
                "max_turns": 50,
                "input_file": "tests/minitasks/base/myagent_T1_task_battle_industry_era.sav",
                "output_file": "tests/minitasks/{}/{}/{}_T1_task_battle_industry_era_level_{}_id_{}",
                "difficulty":[{"level": "normal", "rate": [0.9, 1.1]}, {"level": "hard", "rate": [1.1, 2]}, {"level": "easy", "rate": [0.5, 0.9]}]
         },
        {
                "type": "battle",
                "subtype": "info_era",
                "status": "online",
                "max_turns": 50,
                "input_file": "tests/minitasks/base/myagent_T1_task_battle_info_era.sav",
                "output_file": "tests/minitasks/{}/{}/{}_T1_task_battle_info_era_level_{}_id_{}",
                "difficulty":[{"level": "normal", "rate": [0.9, 1.1]}, {"level": "hard", "rate": [1.1, 2]}, {"level": "easy", "rate": [0.5, 0.9]}]
         },
        {
                "type": "battle",
                "subtype": "medieval",
                "status": "online",
                "max_turns": 50,
                "input_file": "tests/minitasks/base/myagent_T1_task_battle_medieval.sav",
                "output_file": "tests/minitasks/{}/{}/{}_T1_task_battle_medieval_level_{}_id_{}",
                "difficulty":[{"level": "normal", "rate": [0.9, 1.1]}, {"level": "hard", "rate": [1.1, 2]}, {"level": "easy", "rate": [0.5, 0.9]}]
         },
        {
                "type": "battle",
                "subtype": "modern_era",
                "status": "online",
                "max_turns": 50,
                "input_file": "tests/minitasks/base/myagent_T1_task_battle_modern_era.sav",
                "output_file": "tests/minitasks/{}/{}/{}_T1_task_battle_modern_era_level_{}_id_{}",
                "difficulty":[{"level": "normal", "rate": [0.9, 1.1]}, {"level": "hard", "rate": [1.1, 2]}, {"level": "easy", "rate": [0.5, 0.9]}]
         },
        {
                "type": "battle",
                "subtype": "defend_city",
                "status": "online",
                "max_turns": 50,
                "input_file": "tests/minitasks/base/myagent_T1_task_battle_defend_city.sav",
                "output_file": "tests/minitasks/{}/{}/{}_T1_task_battle_defend_city_level_{}_id_{}",
                "difficulty":[{"level": "normal", "rate": [0.9, 1.1]}, {"level": "hard", "rate": [1.1, 2]}, {"level": "easy", "rate": [0.5, 0.9]}]
         },
        {
                "type": "battle",
                "subtype": "attack_city",
                "status": "online",
                "max_turns": 50,
                "input_file": "tests/minitasks/base/myagent_T1_task_battle_attack_city.sav",
                "output_file": "tests/minitasks/{}/{}/{}_T1_task_battle_attack_city_level_{}_id_{}",
                "difficulty":[{"level": "normal", "rate": [0.9, 1.1]}, {"level": "hard", "rate": [1.1, 2]}, {"level": "easy", "rate": [0.5, 0.9]}]
         },
        {
                "type": "battle",
                "subtype": "naval",
                "status": "online",
                "max_turns": 50,
                "input_file": "tests/minitasks/base/myagent_T1_task_battle_naval.sav",
                "output_file": "tests/minitasks/{}/{}/{}_T1_task_battle_naval_level_{}_id_{}",
                "difficulty":[{"level": "normal", "rate": [0.9, 1.1]}, {"level": "hard", "rate": [1.1, 2]}, {"level": "easy", "rate": [0.5, 0.9]}]
         },
        {
                "type": "battle",
                "subtype": "naval_modern",
                "status": "online",
                "max_turns": 50,
                "input_file": "tests/minitasks/base/myagent_T1_task_battle_naval_modern.sav",
                "output_file": "tests/minitasks/{}/{}/{}_T1_task_battle_naval_modern_level_{}_id_{}",
                "difficulty":[{"level": "normal", "rate": [0.9, 1.1]}, {"level": "hard", "rate": [1.1, 2]}, {"level": "easy", "rate": [0.5, 0.9]}]
         },
        {
                "type": "development",
                "subtype": "citytile_wonder",
                "status": "online",
                "max_turns": 30,
                "input_file": "tests/minitasks/base/myagent_T1_task_development_citytile_wonder.sav",
                "output_file": "tests/minitasks/{}/{}/{}_T1_task_development_citytile_wonder_level_{}_id_{}",
                "difficulty":
                [
                    {"level": "hard", "score_bound": [0, 2.5]},
                    {"level": "normal", "score_bound": [2.5, 7]},
                    {"level": "easy", "score_bound": [7, 10]},
                ]
         },
        {
                "type": "development",
                "subtype": "build_infra",
                "status": "online",
                "max_turns": 30,
                "input_file": "tests/minitasks/base/myagent_T1_task_development_build_infra.sav",
                "output_file": "tests/minitasks/{}/{}/{}_T1_task_development_build_infra_level_{}_id_{}",
                "difficulty":
                [
                    {"level": "hard", "score_bound": [0, 2.5]},
                    {"level": "normal", "score_bound": [2.5, 7]},
                    {"level": "easy", "score_bound": [7, 10]},
                ]
         },
        {
                "type": "development",
                "subtype": "transport",
                "status": "online",
                "max_turns": 30,
                "input_file": "tests/minitasks/base/myagent_T1_task_development_transport.sav",
                "output_file": "tests/minitasks/{}/{}/{}_T1_task_development_transport_level_{}_id_{}",
                "difficulty":
                [
                    {"level": "easy", "goal": 15},
                    {"level": "hard", "goal": 5},
                    {"level": "normal", "goal": 10},
                ]
         },
         # not sensible for ai.skill level
        {
                "type": "diplomacy",
                "subtype": "trade_tech",
                "status": "online",
                "max_turns": 3,
                "input_file": "tests/minitasks/base/myagent_T1_task_diplomacy_trade_tech.sav",
                "output_file": "tests/minitasks/{}/{}/{}_T1_task_diplomacy_trade_tech_level_{}_id_{}",
                "difficulty": [{"level": "normal"}, {"level": "easy"}, {"level": "hard"}]
         },
]


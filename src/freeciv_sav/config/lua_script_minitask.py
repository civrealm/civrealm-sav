####################
# BUILD CITY SCRIPT
####################
BUILD_CITY_START_SCRIPT = """
code=$

function concat(met, key, value, sep)
  if sep then
    return met .. '"' .. key .. '"' .. ':' .. value .. ','
  end
  return met .. '"' .. key .. '"' .. ':' .. value
end

function get_build_city_msg(turn)
    -- get metrics
    player = find.player(0)
    metrics = '[{'
    for city in player:cities_iterate() do
        tile = city.tile
        score = map_conf[math.floor(tile.y+1)][math.floor(tile.x+1)]
        city_id = math.floor(city.id)
        is_mini_success = 0
        if score >= score_goal - 0.0001 then
            is_mini_success = 1
        end
        metrics = concat(metrics, 'city_id', city_id, true)
        metrics = concat(metrics, 'x', math.floor(tile.x), true)
        metrics = concat(metrics, 'y', math.floor(tile.y), true)
        metrics = concat(metrics, 'mini_score', score, true)
        metrics = concat(metrics, 'mini_goal', score_goal, true)
        metrics = concat(metrics, 'max_turn', max_turn, true)
        metrics = concat(metrics, 'is_mini_success', is_mini_success, false)
    end
    -- no city built
    if is_mini_success == -1 then
        metrics = concat(metrics, 'city_id', -1, true)
        metrics = concat(metrics, 'mini_score', 0, true)
        metrics = concat(metrics, 'mini_goal', score_goal, true)
        metrics = concat(metrics, 'max_turn', max_turn, true)
        metrics = concat(metrics, 'is_mini_success', 0, false)
    end
    metrics = metrics .. '}]'
    return metrics
end

function get_unit_reward(turn)
    -- get metrics
    player = find.player(0)
    metrics = '[{'
    for unit in player:units_iterate() do
        tile = unit.tile
        turn_score = map_conf[math.floor(tile.y+1)][math.floor(tile.x+1)]
        metrics = concat(metrics, 'x', math.floor(tile.x), true)
        metrics = concat(metrics, 'y', math.floor(tile.y), true)
        metrics = concat(metrics, 'mini_score', turn_score, true)
        metrics = concat(metrics, 'mini_goal', score_goal, true)
        metrics = concat(metrics, 'is_mini_success', is_mini_success, true)
        metrics = concat(metrics, 'max_turn', max_turn, false)
    end
    metrics = metrics .. '}]'
    return metrics
end

function msg_success_or_failed()
  if is_mini_success == 1 then
    msg = 'You scored ' .. score .. '>=' .. score_goal .. ', congratulations on the successful completion of this mission!'
  else
    msg = 'You scored ' .. score .. '<' .. score_goal .. ', unfortunately this mission failed!'
  end
  return msg
end

function minitask_msg_handle(turn)
  metrics = get_build_city_msg(turn)
  msg = '{"task": "minitask", "name": "build_city", "status": 1,' .. '"turn":' .. math.floor(turn) .. ', "metrics":' ..  metrics .. '}'
  return msg
end

function unit_moved_callback(unit, src_tile, dst_tile)
  metrics = get_unit_reward(game.current_turn())
  msg = '{"task": "minitask", "name": "build_city", "status": 0,' .. '"turn":' .. math.floor(game.current_turn()) .. ', "metrics":' ..  metrics .. '}'
  notify.event(nil, nil, E.SCRIPT, _(msg))
end

function turn_terminate_callback(turn, year)
  if turn == max_turn then
    json_msg = minitask_msg_handle(turn)
    doc_msg = msg_success_or_failed()
    notify.event(nil, nil, E.SCRIPT, _(json_msg))
    notify.event(nil, nil, E.SCRIPT, _(doc_msg))
  end
end

function city_built_callback(city)
  if city.owner:is_human() then
    json_msg = minitask_msg_handle(game.current_turn())
    doc_msg = msg_success_or_failed()
    notify.event(nil, nil, E.SCRIPT, _(json_msg))
    notify.event(nil, nil, E.SCRIPT, _(doc_msg))
  end
end

function pulse_start_msg()
    unit_moved_callback(nil, nil, nil)
    notify.event(nil, nil, E.SCRIPT, _(start_msg))
    signal.remove('pulse', 'pulse_start_msg')
end

function game_started_udf_callback(player)
    unit_moved_callback(nil, nil, nil)
    notify.event(nil, nil, E.SCRIPT, _(start_msg))
end

function game_ended_udf_callback(player)
  if is_mini_success > -1 then
    return
  end
  is_mini_success = 0
  json_msg = minitask_msg_handle(game.current_turn())
  doc_msg = msg_success_or_failed()
  notify.event(nil, nil, E.SCRIPT, _(json_msg))
  notify.event(nil, nil, E.SCRIPT, _(doc_msg))
end

"""

BUILD_CITY_INPUT_CONF = """
map_conf = {}
max_turn = {}
score_goal = {}
difficulty = '{}'
"""

BUILD_CITY_END_SCRIPT = """
score = 0
turn_score = 0
is_mini_success = -1

start_msg = 'Welcome to the challenge of mini-task named "Build City", the difficulty is ' .. difficulty .. ' level, and the target value is ' .. score_goal .. '. The specific task is to use settler to find the suitable location to build the city, so that the resources near it are as abundant as possible and above the target value.'
signal.connect('game_started', 'game_started_udf_callback')
signal.connect('city_built', 'city_built_callback')
signal.connect('turn_begin', 'turn_terminate_callback')
signal.connect('unit_moved', 'unit_moved_callback')
signal.connect('game_ended', 'game_ended_udf_callback')
$
"""

####################
# BATTLE SCRIPT
####################
BATTLE_START_SCRIPT = """
code=$

function has_unit_type_name(unit, utype_name) 
  return (unit.utype.id == find.unit_type(utype_name).id)
end

function concat(met, key, value, sep)
  if sep then
    return met .. '"' .. key .. '"' .. ':' .. value .. ','
  end
  return met .. '"' .. key .. '"' .. ':' .. value
end

function msg_success_or_failed()
  if is_mini_success == 1 then
    msg = 'You scored ' .. mini_score .. ', congratulations on the successful completion of this mission!'
  else
    msg = 'You scored ' .. mini_score .. ', unfortunately this mission failed!'
  end
  return msg
end

function start_msg()
  msg = 'Welcome to the challenge of mini-task named "Battle", the target value is ' .. human_cnt .. '. The specific task is to use the existing unit to protect the leader and destroy the enemy leader.'
  notify.event(nil, nil, E.SCRIPT, _(msg))
end

function end_msg()
    doc_msg = msg_success_or_failed()
    notify.event(nil, nil, E.SCRIPT, _(doc_msg))
end

function msg_handle()
    mini_score = human_cnt - ai_cnt
    mini_goal = human_cnt
    metrics = '[{'
    metrics = concat(metrics, 'human_cnt', human_cnt, true)
    metrics = concat(metrics, 'ai_cnt', ai_cnt, true)
    metrics = concat(metrics, 'mini_score', mini_score, true)
    metrics = concat(metrics, 'mini_goal', mini_goal, true)
    metrics = concat(metrics, 'max_turn', max_turn, true)
    metrics = concat(metrics, 'human_leader_alive', human_leader_alive, true)
    metrics = concat(metrics, 'ai_leader_alive', ai_leader_alive, true)
    metrics = concat(metrics, 'is_mini_success', is_mini_success, false)
    metrics = metrics .. '}]'
    return metrics
end

function minitask_msg_handle(turn)
  metrics = msg_handle()
  if is_mini_success > -1 then
    status = 1
  else
    status = 0
  end
  msg = '{"task": "minitask", "name": "battle", "status": ' .. status .. ', "turn":' .. math.floor(turn) .. ', "metrics":' ..  metrics .. '}'
  return msg
end

function metrics_msg()
  json_msg = minitask_msg_handle(game.current_turn())
  notify.event(nil, nil, E.SCRIPT, _(json_msg))
end

function cnt_units(human_loss, ai_loss)
    human = find.player(0)
    ai = find.player(1)
    human_cnt = human:num_units() - human_loss
    ai_cnt = ai:num_units() - ai_loss
end

function turn_terminate_callback(turn, year)
  cnt_units(0, 0)
  if turn == max_turn then
    is_mini_success = 0
    metrics_msg()
    end_msg()
  end
end

function unit_lost_udf_callback(unit, loser, reason)
    if has_unit_type_name(unit, 'Leader') then
      -- end-game
      if loser:is_human() then
        human_leader_alive = 0
        is_mini_success = 0
      else 
        is_mini_success = 1
        ai_leader_alive = 0
      end
      cnt_units(1, 0)
      metrics_msg()
      end_msg()
    else
      -- in-game
      if loser:is_human() then
        cnt_units(1, 0)
      else 
        cnt_units(0, 1)
      end
      mini_score = human_cnt - ai_cnt
      metrics_msg()
    end
end

function game_started_udf_callback(player)
    cnt_units(0, 0)
    metrics_msg()
    start_msg()
end

"""

BATTLE_INPUT_CONF = """
is_mini_success = -1
mini_score = 0
mini_goal = 0
human_cnt = 0
ai_cnt = 0
human_leader_alive = 1
ai_leader_alive = 1
max_turn = {}
"""

BATTLE_END_SCRIPT = """
signal.connect('game_started', 'game_started_udf_callback')
signal.connect('turn_begin', 'turn_terminate_callback')
signal.connect('unit_lost', 'unit_lost_udf_callback')
$
"""

####################
# ATTACK CITY SCRIPT
####################
ATTACK_CITY_START_SCRIPT = """
code=$
function has_unit_type_name(unit, utype_name) 
  return (unit.utype.id == find.unit_type(utype_name).id)
end

function concat(met, key, value, sep)
  if sep then
    return met .. '"' .. key .. '"' .. ':' .. value .. ','
  end
  return met .. '"' .. key .. '"' .. ':' .. value
end

function msg_success_or_failed()
  if is_mini_success == 1 then
    mini_goal = mini_score
    msg = 'You scored ' .. mini_score .. '>=' .. mini_goal .. ', congratulations on the successful completion of this mission!'
  else
    msg = 'You scored ' .. mini_score .. '<' .. mini_goal .. ', unfortunately this mission failed!'
  end
  return msg
end

function start_msg()
  msg = 'Welcome to the challenge of mini-task named "Attack City", the target value is ' .. human_cnt .. '. The specific task is to use the existing unit to conquer the city of enemy.'
  notify.event(nil, nil, E.SCRIPT, _(msg))
end

function end_msg()
    doc_msg = msg_success_or_failed()
    notify.event(nil, nil, E.SCRIPT, _(doc_msg))
end

function metrics_handle()
    mini_score = human_cnt - ai_unit_cnt - ai_city_cnt
    mini_goal = human_cnt
    metrics = '[{'
    metrics = concat(metrics, 'human_cnt', human_cnt, true)
    metrics = concat(metrics, 'ai_unit_cnt', ai_unit_cnt, true)
    metrics = concat(metrics, 'ai_city_cnt', ai_city_cnt, true)
    metrics = concat(metrics, 'mini_score', mini_score, true)
    metrics = concat(metrics, 'mini_goal', mini_goal, true)
    metrics = concat(metrics, 'max_turn', max_turn, true)
    metrics = concat(metrics, 'is_mini_success', is_mini_success, false)
    metrics = metrics .. '}]'
    return metrics
end

function minitask_msg_handle(turn)
  metrics = metrics_handle()
  if is_mini_success > -1 then
    status = 1
  else
    status = 0
  end
  msg = '{"task": "minitask", "name": "attackcity", "status": ' .. status .. ', "turn":' .. math.floor(turn) .. ', "metrics":' ..  metrics .. '}'
  return msg
end

function metrics_msg()
  json_msg = minitask_msg_handle(game.current_turn())
  notify.event(nil, nil, E.SCRIPT, _(json_msg))
end

function cnt_units(human_loss, ai_loss)
    human = find.player(0)
    ai = find.player(1)
    human_cnt = human:num_units() - human_loss
    ai_unit_cnt = ai:num_units() - ai_loss
end

function cnt_city(ai_loss)
    ai = find.player(1)
    ai_city_cnt = ai:num_cities()-ai_loss
end

function turn_terminate_callback(turn, year)
  cnt_city(0)
  cnt_units(0, 0)
  if turn == max_turn then
    is_mini_success = 0
    metrics_msg()
    end_msg()
  end
end

function unit_lost_callback(unit, loser, reason)
    if reason == "city_lost" then
      return
    end

    if loser:is_human() then
      cnt_units(1, 0)
    else
      cnt_units(0, 1)
    end
    cnt_city(0)
    mini_score = human_cnt - ai_unit_cnt - ai_city_cnt
    if human_cnt == 0 then
      -- end-game
      is_mini_success = 0
      metrics_msg()
      end_msg()
    elseif ai_unit_cnt == 0 and ai_city_cnt == 0 then
      is_mini_success = 1
      metrics_msg()
      end_msg()
    else
      -- in-game
      metrics_msg()
    end
end

function city_destroyed_udf_callback(city, loser, destroyer)
    -- end-game
    cnt_units(0, 0)
    cnt_city(1)
    mini_score = human_cnt - ai_unit_cnt - ai_city_cnt
    is_mini_success = 1
    metrics_msg()
    end_msg()
end

function city_transferred_callback(city, loser, winner, reason)
    -- end-game
    cnt_units(0, 0)
    cnt_city(1)
    mini_score = human_cnt - ai_unit_cnt - ai_city_cnt
    is_mini_success = 1
    metrics_msg()
    end_msg()
end

function game_started_udf_callback(player)
    cnt_city(0)
    cnt_units(0, 0)
    metrics_msg()
    start_msg()
end

function game_ended_udf_callback(player)
  if is_mini_success > -1 then
    return
  end
  cnt_city(0)
  cnt_units(0, 0)
  if ai_city_cnt == 0 then
    is_mini_success = 1
  else
    is_mini_success = 0
  end
  metrics_msg()
  end_msg()
end
"""

ATTACK_CITY_INPUT_CONF = """
is_mini_success = -1
mini_score = 0
mini_goal = 0
human_cnt = 0
ai_unit_cnt = 0
ai_city_cnt = 0
max_turn = {}
"""

ATTACK_CITY_END_SCRIPT = """
signal.connect('game_started', 'game_started_udf_callback')
signal.connect('turn_begin', 'turn_terminate_callback')
signal.connect('unit_lost', 'unit_lost_callback')
signal.connect('city_destroyed', 'city_destroyed_udf_callback')
signal.connect('city_transferred', 'city_transferred_callback')
signal.connect('game_ended', 'game_ended_udf_callback')
$
"""

####################
# DEFEND CITY SCRIPT
####################
DEFEND_CITY_START_SCRIPT = """
code=$

function has_unit_type_name(unit, utype_name) 
  return (unit.utype.id == find.unit_type(utype_name).id)
end

function concat(met, key, value, sep)
  if sep then
    return met .. '"' .. key .. '"' .. ':' .. value .. ','
  end
  return met .. '"' .. key .. '"' .. ':' .. value
end

function msg_success_or_failed()
  if is_mini_success == 1 then
    mini_goal = mini_score
    msg = 'You scored ' .. mini_score .. '>=' .. mini_goal .. ', congratulations on the successful completion of this mission!'
  else
    msg = 'You scored ' .. mini_score .. '<' .. mini_goal .. ', unfortunately this mission failed!'
  end
  return msg
end

function start_msg()
  msg = 'Welcome to the challenge of mini-task named "Defend City", the target value is ' .. human_cnt .. '. The specific task is to use the existing unit to defend city.'
  notify.event(nil, nil, E.SCRIPT, _(msg))
end

function end_msg()
    doc_msg = msg_success_or_failed()
    notify.event(nil, nil, E.SCRIPT, _(doc_msg))
end

function metrics_handle()
    mini_score = human_cnt + human_city_cnt - ai_unit_cnt
    mini_goal = human_cnt + human_city_cnt
    metrics = '[{'
    metrics = concat(metrics, 'human_unit_cnt', human_cnt, true)
    metrics = concat(metrics, 'ai_unit_cnt', ai_unit_cnt, true)
    metrics = concat(metrics, 'human_city_cnt', human_city_cnt, true)
    metrics = concat(metrics, 'mini_score', mini_score, true)
    metrics = concat(metrics, 'mini_goal', mini_goal, true)
    metrics = concat(metrics, 'max_turn', max_turn, true)
    metrics = concat(metrics, 'is_mini_success', is_mini_success, false)
    metrics = metrics .. '}]'
    return metrics
end

function minitask_msg_handle(turn)
  metrics = metrics_handle()
  if is_mini_success > -1 then
    status = 1
  else
    status = 0
  end
  msg = '{"task": "minitask", "name": "defendcity", "status": ' .. status .. ', "turn":' .. math.floor(turn) .. ', "metrics":' ..  metrics .. '}'
  return msg
end

function metrics_msg()
  json_msg = minitask_msg_handle(game.current_turn())
  notify.event(nil, nil, E.SCRIPT, _(json_msg))
end

function cnt_units(human_loss, ai_loss)
    human = find.player(0)
    ai = find.player(1)
    human_cnt = human:num_units() - human_loss
    ai_unit_cnt = ai:num_units() - ai_loss
end

function cnt_city(human_loss)
    human = find.player(0)
    human_city_cnt = human:num_cities()-human_loss
end

function turn_terminate_callback(turn, year)
  if turn == max_turn then
    is_mini_success = 1
    metrics_msg()
    end_msg()
  end
end

function unit_lost_callback(unit, loser, reason)
    if reason == "city_lost" then
      return
    end
    if loser:is_human() then
      cnt_units(1, 0)
    else
      cnt_units(0, 1)
    end
    cnt_city(0)
    mini_score = human_cnt + human_city_cnt - ai_unit_cnt
    if ai_unit_cnt == 0 then
      -- end-game
      is_mini_success = 1
      metrics_msg()
      end_msg()
    elseif human_city_cnt == 0 then
      -- end-game
      is_mini_success = 0
      metrics_msg()
      end_msg()
    else
      -- in-game
      metrics_msg()
    end
end

function city_destroyed_udf_callback(city, loser, destroyer)
    -- end-game
    cnt_units(0, 0)
    cnt_city(1)
    mini_score = human_cnt + human_city_cnt - ai_unit_cnt
    is_mini_success = 0
    metrics_msg()
    end_msg()
end

function city_transferred_callback(city, loser, winner, reason)
    -- end-game
    cnt_units(0, 0)
    cnt_city(1)
    mini_score = human_cnt + human_city_cnt - ai_unit_cnt
    is_mini_success = 0
    metrics_msg()
    end_msg()
end

function game_started_udf_callback(player)
    cnt_city(0)
    cnt_units(0, 0)
    metrics_msg()
    start_msg()
end

function game_ended_udf_callback(player)
  if is_mini_success > -1 then
    return
  end
  cnt_city(0)
  cnt_units(0, 0)

  if human_city_cnt == 1 then
    is_mini_success = 1
  else
    is_mini_success = 0
  end
  metrics_msg()
  end_msg()

end


"""

DEFEND_CITY_INPUT_CONF = """
is_mini_success = -1
mini_score = 0
mini_goal = 0
human_cnt = 0
human_city_cnt = 0
ai_unit_cnt = 0
max_turn = {}
"""

DEFEND_CITY_END_SCRIPT = """
signal.connect('game_started', 'game_started_udf_callback')
signal.connect('unit_lost', 'unit_lost_callback')
signal.connect('turn_begin', 'turn_terminate_callback')
signal.connect('city_destroyed', 'city_destroyed_udf_callback')
signal.connect('city_transferred', 'city_transferred_callback')
signal.connect('game_ended', 'game_ended_udf_callback')
$
"""

####################
# TRADE TECH SCRIPT
####################
TRADE_TECH_START_SCRIPT = """
code=$
function concat(met, key, value, sep)
  if sep then
    return met .. '"' .. key .. '"' .. ':' .. value .. ','
  end
  return met .. '"' .. key .. '"' .. ':' .. value
end

function msg_success_or_failed()
  if is_mini_success == 1 then
    mini_goal = mini_score
    msg = 'You scored ' .. mini_score .. '>=' .. mini_goal .. ', congratulations on the successful completion of this mission!'
  else
    msg = 'You scored ' .. mini_score .. '<' .. mini_goal .. ', unfortunately this mission failed!'
  end
  return msg
end

function start_msg()
  msg = 'Welcome to the challenge of mini-task named "Trade Technology", the target value is ' .. 1 .. '. The specific task is to use existing technology to exchange new technology from other civilizations.'
  notify.event(nil, nil, E.SCRIPT, _(msg))
end

function end_msg()
    doc_msg = msg_success_or_failed()
    notify.event(nil, nil, E.SCRIPT, _(doc_msg))
end

function metrics_handle()
    metrics = '[{'
    metrics = concat(metrics, 'mini_score', mini_score, true)
    metrics = concat(metrics, 'mini_goal', mini_goal, true)
    metrics = concat(metrics, 'max_turn', max_turn, true)
    metrics = concat(metrics, 'is_mini_success', is_mini_success, false)
    metrics = metrics .. '}]'
    return metrics
end

function minitask_msg_handle(turn)
  metrics = metrics_handle()
  if is_mini_success > -1 then
    status = 1
  else
    status = 0
  end
  msg = '{"task": "minitask", "name": "tradetech", "status": ' .. status .. ', "turn":' .. math.floor(turn) .. ', "metrics":' ..  metrics .. '}'
  return msg
end

function metrics_msg()
  json_msg = minitask_msg_handle(game.current_turn())
  notify.event(nil, nil, E.SCRIPT, _(json_msg))
end

function turn_terminate_callback(turn, year)
  if turn == max_turn then
    is_mini_success = 0
    metrics_msg()
    end_msg()
  end
end

function tech_researched_callback(type, player, source)
  if player:is_human() and source == "traded" then
    is_mini_success = 1
    mini_score = 1
    metrics_msg()
    end_msg()
  end
end

function game_started_udf_callback()
    metrics_msg()
    start_msg()
end

function game_ended_udf_callback(player)
  if is_mini_success > -1 then
    return
  end
  is_mini_success = 0
  metrics_msg()
  end_msg()
end
"""
TRADE_TECH_INPUT_CONF = """
is_mini_success = -1
mini_score = 0
mini_goal = 1
max_turn = {}
"""
TRADE_TECH_END_SCRIPT = """
signal.connect('game_started', 'game_started_udf_callback')
signal.connect('turn_begin', 'turn_terminate_callback')
signal.connect('tech_researched', 'tech_researched_callback')
signal.connect('game_ended', 'game_ended_udf_callback')$
"""

####################
# BATTLE NAVAL SCRIPT
####################
NAVAL_START_SCRIPT = """
code=$

function has_unit_type_name(unit, utype_name) 
  return (unit.utype.id == find.unit_type(utype_name).id)
end

function concat(met, key, value, sep)
  if sep then
    return met .. '"' .. key .. '"' .. ':' .. value .. ','
  end
  return met .. '"' .. key .. '"' .. ':' .. value
end

function msg_success_or_failed()
  if is_mini_success == 1 then
    mini_goal = mini_score
    msg = 'You scored ' .. mini_score .. '>=' .. mini_goal .. ', congratulations on the successful completion of this mission!'
  else
    msg = 'You scored ' .. mini_score .. '<' .. mini_goal .. ', unfortunately this mission failed!'
  end
  return msg
end

function start_msg()
  msg = 'Welcome to the challenge of mini-task named "Naval Battle", the target value is ' .. human_unit_cnt .. '. The specific task is to use the existing naval units to destroy all naval units of enemy.'
  notify.event(nil, nil, E.SCRIPT, _(msg))
end

function end_msg()
    doc_msg = msg_success_or_failed()
    notify.event(nil, nil, E.SCRIPT, _(doc_msg))
end

function metrics_handle()
    mini_score = human_unit_cnt - ai_unit_cnt
    mini_goal = human_unit_cnt
    metrics = '[{'
    metrics = concat(metrics, 'human_unit_cnt', human_unit_cnt, true)
    metrics = concat(metrics, 'ai_unit_cnt', ai_unit_cnt, true)
    metrics = concat(metrics, 'mini_score', mini_score, true)
    metrics = concat(metrics, 'mini_goal', mini_goal, true)
    metrics = concat(metrics, 'max_turn', max_turn, true)
    metrics = concat(metrics, 'is_mini_success', is_mini_success, false)
    metrics = metrics .. '}]'
    return metrics
end

function minitask_msg_handle(turn)
  metrics = metrics_handle()
  if is_mini_success > -1 then
    status = 1
  else
    status = 0
  end
  msg = '{"task": "minitask", "name": "battle_naval", "status": ' .. status .. ', "turn":' .. math.floor(turn) .. ', "metrics":' ..  metrics .. '}'
  return msg
end

function metrics_msg()
  json_msg = minitask_msg_handle(game.current_turn())
  notify.event(nil, nil, E.SCRIPT, _(json_msg))
end

function cnt_units(human_loss, ai_loss)
    human = find.player(0)
    ai = find.player(1)
    human_unit_cnt = human:num_units() - human_loss
    ai_unit_cnt = ai:num_units() - ai_loss
end

function turn_terminate_callback(turn, year)
  cnt_units(0, 0)
  if turn == max_turn then
    is_mini_success = 0
    metrics_msg()
    end_msg()
  end
end

function unit_lost_callback(unit, loser, reason)
    if loser:is_human() then
      cnt_units(1, 0)
    else
      cnt_units(0, 1)
    end
    mini_score = human_unit_cnt - ai_unit_cnt
    if ai_unit_cnt == 0 then
      -- end-game
      is_mini_success = 1
      metrics_msg()
      end_msg()
    elseif human_unit_cnt == 0 then
      -- end-game
      is_mini_success = 0
      metrics_msg()
      end_msg()
    else
      -- in-game
      metrics_msg()
    end
end

function game_started_udf_callback()
    cnt_units(0, 0)
    metrics_msg()
    start_msg()
end

function game_ended_udf_callback(player)
  if is_mini_success > -1 then
    return
  end
  cnt_units(0, 0)
  if ai_unit_cnt == 0 then
    is_mini_success = 1
  else
    is_mini_success = 0
  end
  metrics_msg()
  end_msg()
end
"""

NAVAL_INPUT_CONF = """
is_mini_success = -1
mini_score = 0
mini_goal = 0
human_unit_cnt = 0
ai_unit_cnt = 0
max_turn = {}
"""

NAVAL_END_SCRIPT = """
signal.connect('game_started', 'game_started_udf_callback')
signal.connect('turn_begin', 'turn_terminate_callback')
signal.connect('unit_lost', 'unit_lost_callback')
signal.connect('game_ended', 'game_ended_udf_callback')
$
"""

####################
# CITY TILE WONDER SCRIPT
####################
CITY_TILE_WONDER_START_SCRIPT = """
code=$

function has_unit_type_name(unit, utype_name) 
  return (unit.utype.id == find.unit_type(utype_name).id)
end

function concat(met, key, value, sep)
  if sep then
    return met .. '"' .. key .. '"' .. ':' .. value .. ','
  end
  return met .. '"' .. key .. '"' .. ':' .. value
end

function msg_success_or_failed()
  if is_mini_success == 1 then
    msg = 'You scored ' .. mini_score .. '>=' .. mini_goal .. ', congratulations on the successful completion of this mission!'
  else
    msg = 'You scored ' .. mini_score .. '<' .. mini_goal .. ', unfortunately this mission failed!'
  end
  return msg
end

function start_msg()
  msg = 'Welcome to the challenge of mini-task named "Build Wonder", the target value is ' .. 1 .. '. The specific task is to build a wonder using least turns.'
  notify.event(nil, nil, E.SCRIPT, _(msg))
end

function end_msg()
    doc_msg = msg_success_or_failed()
    notify.event(nil, nil, E.SCRIPT, _(doc_msg))
end

function metrics_handle()
    metrics = '[{'
    metrics = concat(metrics, 'mini_score', mini_score, true)
    metrics = concat(metrics, 'mini_goal', mini_goal, true)
    metrics = concat(metrics, 'max_turn', max_turn, true)
    metrics = concat(metrics, 'is_mini_success', is_mini_success, false)
    metrics = metrics .. '}]'
    return metrics
end

function minitask_msg_handle(turn)
  metrics = metrics_handle()
  if is_mini_success > -1 then
    status = 1
  else
    status = 0
  end
  msg = '{"task": "minitask", "name": "Build Wonder", "status": ' .. status .. ', "turn":' .. math.floor(turn) .. ', "metrics":' ..  metrics .. '}'
  return msg
end

function metrics_msg()
  json_msg = minitask_msg_handle(game.current_turn())
  notify.event(nil, nil, E.SCRIPT, _(json_msg))
end

function turn_terminate_callback(turn, year)
  if turn == max_turn then
    if is_mini_success == -1 then
      is_mini_success = 0
    end
    metrics_msg()
    end_msg()
  end
end

function building_built_callback(type, city)
  if city.owner:is_human() and type:is_great_wonder() then
    is_mini_success = 1
    mini_score = 1
    metrics_msg()
    end_msg()
  end
end

function game_started_udf_callback()
    metrics_msg()
    start_msg()
end

function game_ended_udf_callback(player)
  if is_mini_success > -1 then
    return
  end
  is_mini_success = 0
  metrics_msg()
  end_msg()
end

"""

CITY_TILE_WONDER_INPUT_CONF = """
is_mini_success = -1
mini_score = 0
mini_goal = 1
max_turn = {}
"""

CITY_TILE_WONDER_END_SCRIPT = """
signal.connect('game_started', 'game_started_udf_callback')
signal.connect('turn_begin', 'turn_terminate_callback')
signal.connect('building_built', 'building_built_callback')
signal.connect('game_ended', 'game_ended_udf_callback')
$
"""

##############################
# build infra
##############################
BUILD_INFRA_START_SCRIPT = """
code=$
function concat(met, key, value, sep)
  if sep then
    return met .. '"' .. key .. '"' .. ':' .. value .. ','
  end
  return met .. '"' .. key .. '"' .. ':' .. value
end

function metrics_handle()
    metrics = '[{'
    metrics = concat(metrics, 'mini_score', mini_score, true)
    metrics = concat(metrics, 'mini_goal', mini_goal, true)
    metrics = concat(metrics, 'max_turn', max_turn, true)
    metrics = concat(metrics, 'unit_cnt', unit_cnt, true)
    metrics = concat(metrics, 'city_cnt', city_cnt, true)
    metrics = concat(metrics, 'is_mini_success', is_mini_success, false)
    metrics = metrics .. '}]'
    return metrics
end

function minitask_msg_handle(turn)
  metrics = metrics_handle()
  if is_mini_success > -1 then
    status = 1
  else
    status = 0
  end
  msg = '{"task": "minitask", "name": "Build Infrastructure", "status": ' .. status .. ', "turn":' .. math.floor(turn) .. ', "metrics":' ..  metrics .. '}'
  return msg
end

function msg_success_or_failed()
  if is_mini_success == 1 then
    msg = 'You scored ' .. mini_score .. '>=' .. mini_goal .. ', congratulations on the successful completion of this mission!'
  else
    msg = 'You scored ' .. mini_score .. '<' .. mini_goal .. ', unfortunately this mission failed!'
  end
  return msg
end

function start_msg()
  msg = 'Welcome to the challenge of mini-task named "Build infrastructure", the target value is ' .. mini_goal .. '. The specific task is to use workers to find the suitable location to build the infrastructures, so that the productions near it are as abundant as possible and above the target value.'
  notify.event(nil, nil, E.SCRIPT, _(msg))
end

function metrics_msg()
  json_msg = minitask_msg_handle(game.current_turn())
  notify.event(nil, nil, E.SCRIPT, _(json_msg))
end

function end_msg()
  doc_msg = msg_success_or_failed()
  notify.event(nil, nil, E.SCRIPT, _(doc_msg))
end

function cnt()
  human = find.player(0)
  city_cnt = human:num_cities()
  unit_cnt = human:num_units()
end

function get_success()
  if mini_score >= mini_goal then
    is_mini_success = 1
    return true
  end
  return false
end

function turn_terminate_callback(turn, year)
  cnt()
  if turn == max_turn then
    is_mini_success = 0
  end

  if mini_score >= mini_goal then
    is_mini_success = 1
  end

  if is_mini_success >  -1 then
    metrics_msg()
    end_msg()
  end
end

function action_finished_worker_build_udf_callback(city)
  cnt()
  if city.id == 107 then
    mini_score = city.tri
    metrics_msg()
    if get_success() then
      end_msg()
    end
  end
end

function game_started_udf_callback(player)
  cnt()
  if player:is_human() then
    for city in player:cities_iterate() do
      if city.id == 107 then
        mini_score = city.tri
      end
    end
    metrics_msg()
    start_msg()
  end
end

function game_ended_udf_callback(player)
  if is_mini_success > -1 then
    return
  end
  cnt()
  if player:is_human() then
    for city in player:cities_iterate() do
      if city.id == 107 then
        mini_score = city.tri
      end
    end
    is_mini_success = 0
    get_success()
    metrics_msg()
    end_msg()
  end
end

function city_destroyed_udf_callback(city, loser, destroyer)
  if loser:is_human() then
    city_cnt = 0
    unit_cnt = 0
    is_mini_success = 0
    mini_score = 0
    metrics_msg()
    end_msg()
  end
end
"""

BUILD_INFRA_INPUT_CONF = """
max_turn = {}
mini_goal = {}
"""

BUILD_INFRA_END_SCRIPT = """
city_cnt = 0
unit_cnt = 0
mini_score = 0
is_mini_success = -1

signal.connect('turn_begin', 'turn_terminate_callback')
signal.connect('action_finished_worker_build', 'action_finished_worker_build_udf_callback')
signal.connect('game_started', 'game_started_udf_callback')
signal.connect('city_destroyed', 'city_destroyed_udf_callback')
signal.connect('game_ended', 'game_ended_udf_callback')

$
"""


##############################
# transport
##############################
TRANSPORT_START_SCRIPT = """
code=$
function concat(met, key, value, sep)
  if sep then
    return met .. '"' .. key .. '"' .. ':' .. value .. ','
  end
  return met .. '"' .. key .. '"' .. ':' .. value
end

function metrics_handle()
    metrics = '[{'
    metrics = concat(metrics, 'mini_score', mini_score, true)
    metrics = concat(metrics, 'mini_goal', mini_goal, true)
    metrics = concat(metrics, 'max_turn', max_turn, true)
    metrics = concat(metrics, 'used_turn', used_turn, true)
    metrics = concat(metrics, 'is_mini_success', is_mini_success, false)
    metrics = metrics .. '}]'
    return metrics
end

function minitask_msg_handle(turn)
  metrics = metrics_handle()
  if is_mini_success > -1 then
    status = 1
  else
    status = 0
  end
  msg = '{"task": "minitask", "name": "Transport", "status": ' .. status .. ', "turn":' .. math.floor(turn) .. ', "metrics":' ..  metrics .. '}'
  return msg
end

function msg_success_or_failed()
  if is_mini_success == 1 then
    msg = 'You scored ' .. mini_score .. '>=' .. mini_goal .. ', congratulations on the successful completion of this mission!'
  else
    msg = 'You scored ' .. mini_score .. '<' .. mini_goal .. ', unfortunately this mission failed!'
  end
  return msg
end

function start_msg()
  msg = 'Welcome to the challenge of mini-task named "Transport". The specific task is to use settlers and galleons to build city in the new land before ' .. max_turn .. ' turn.'
  notify.event(nil, nil, E.SCRIPT, _(msg))
end

function metrics_msg()
  json_msg = minitask_msg_handle(game.current_turn())
  notify.event(nil, nil, E.SCRIPT, _(json_msg))
end

function end_msg()
  doc_msg = msg_success_or_failed()
  notify.event(nil, nil, E.SCRIPT, _(doc_msg))
end

function turn_terminate_callback(turn, year)
  used_turn = turn
  if turn == max_turn then
    is_mini_success = 0
  end

  if mini_score >= mini_goal then
    is_mini_success = 1
  end

  if is_mini_success >  -1 then
    metrics_msg()
    end_msg()
  end
end

function game_started_udf_callback(player)
  used_turn = game.current_turn()
  if player:is_human() then
    metrics_msg()
    start_msg()
  end
end

function city_built_udf_callback(city)
  if city.owner:is_human() then
    used_turn = game.current_turn()
    is_mini_success = 1
    metrics_msg()
    end_msg()
  end
end

function game_ended_udf_callback(player)
  if is_mini_success > -1 then
    return
  end
  is_mini_success = 0
  metrics_msg()
  end_msg()
end

"""

TRANSPORT_INPUT_CONF = """
max_turn = {}
"""

TRANSPORT_END_SCRIPT = """
mini_score = 0
used_turn = 0
is_mini_success = -1
mini_goal = 1

signal.connect('game_started', 'game_started_udf_callback')
signal.connect('turn_begin', 'turn_terminate_callback')
signal.connect('city_built', 'city_built_udf_callback')
signal.connect('game_ended', 'game_ended_udf_callback')
$
"""

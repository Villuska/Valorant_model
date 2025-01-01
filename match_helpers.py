import math

def calculate(team1_str, team2_str):
    team_strength_diff = abs(team1_str-team2_str)
    if team1_str > team2_str:
        win_c = 1 / (1 + math.exp(-0.09 * team_strength_diff))
        return win_c 
    else:
        win_c = 1 / (1 + math.exp(-0.09 * team_strength_diff))
        return 1-win_c
    
def scale_min_odds_by_wr_ml(wr, bo_format):
    breakeven_odds = 1/wr
    if bo_format == 1:
        min_margin = 1.06
    elif bo_format == 2:
        min_margin = 1.065
    elif bo_format == 3:
        min_margin = 1.07
    elif bo_format == 4:
        min_margin = 1.0725
    else:
        min_margin = 1.08
    additional_margin = (breakeven_odds-2)* 0.035
    if breakeven_odds < 2:
        additional_margin = 0
    margin = min_margin + additional_margin
    margin = min(margin, 1.15)
    return round(breakeven_odds * margin,2), round(margin*100,1)

def calculate_win_probability_t1_bo5(p_map1, p_map2, p_map3, p_map4, p_map5):
    p_3_0 = p_map1 * p_map2 * p_map3
    p_3_1 = (p_map1 * p_map2 * (1 - p_map3) * p_map4 +
             p_map1 * (1 - p_map2) * p_map3 * p_map4 +
             (1 - p_map1) * p_map2 * p_map3 * p_map4)
    p_3_2 = (p_map1 * p_map2 * (1 - p_map3) * (1 - p_map4) * p_map5 +
             p_map1 * (1 - p_map2) * p_map3 * (1 - p_map4) * p_map5 +
             p_map1 * (1 - p_map2) * (1 - p_map3) * p_map4 * p_map5 +
             (1 - p_map1) * p_map2 * p_map3 * (1 - p_map4) * p_map5 +
             (1 - p_map1) * p_map2 * (1 - p_map3) * p_map4 * p_map5 +
             (1 - p_map1) * (1 - p_map2) * p_map3 * p_map4 * p_map5)
    p_team1_win = p_3_0 + p_3_1 + p_3_2
    return p_team1_win, p_3_1 + p_3_0, p_3_0


def winrate_func_bo5(team1, team2, team1_str, team2_str):
    team1_str_own_pick1 = team1_str * 1.04
    team2_str_own_pick1 = team2_str * 1.04
    team1_str_own_pick2 = team1_str * 1.03
    team2_str_own_pick2 = team2_str * 1.03
    t1_m1_wr = calculate(team1_str_own_pick1, team2_str)
    t1_m2_wr = calculate(team1_str, team2_str_own_pick1)
    t1_m3_wr = calculate(team1_str_own_pick2, team2_str)
    t1_m4_wr = calculate(team1_str, team2_str_own_pick2)
    t1_m5_wr = calculate(team1_str, team2_str)
    t1_wr, t1_hcp_15, t1_hcp_25= calculate_win_probability_t1_bo5(t1_m1_wr, t1_m2_wr, t1_m3_wr, t1_m4_wr, t1_m5_wr)


    t2_wr = 1-t1_wr
    t1_hcp_15_p = round(t1_hcp_15, 2)
    t2_hcp_15_p = round(1-t1_hcp_15_p, 2)
    t1_hcp_25_p = round(t1_hcp_25, 2)
    t2_hcp_25_p = round(1-t1_hcp_25_p, 2)
    print(t1_wr, t2_wr)
    print(t1_hcp_15_p, t2_hcp_15_p)
    print(t1_hcp_25_p, t2_hcp_25_p)
    t1_min_o, t1_margin = scale_min_odds_by_wr_ml(t1_wr, 3)
    t2_min_o, t2_margin = scale_min_odds_by_wr_ml(t2_wr, 3)
    t1_hcp_15_min_o, t1_hcp_15_margin = scale_min_odds_by_wr_ml(t1_hcp_15_p, 2)
    t2_hcp_15_min_o, t2_hcp_15_margin = scale_min_odds_by_wr_ml(t2_hcp_15_p, 2)
    t1_hcp_25_min_o, t1_hcp_25_margin = scale_min_odds_by_wr_ml(t1_hcp_25_p, 2)
    t2_hcp_25_min_o, t2_hcp_25_margin = scale_min_odds_by_wr_ml(t2_hcp_25_p, 2)

    print("")
    print(team1.capitalize() + " vs " + team2.capitalize() + ":")
    print("")
    print(team1.capitalize() + " win rate and min odds: " + str(round(t1_wr*100,2)) +"% " + str(t1_min_o) + "("+ str(t1_margin) + "%)"   + " -1.5: " + str(round(t1_hcp_15_p*100,2)) + "%" + " " + str(t1_hcp_15_min_o) + "(" + str(t1_hcp_15_margin)+ "%)"
          + " -2.5: " + str(round(t1_hcp_25_p*100,2)) + "%" + " " + str(t1_hcp_25_min_o) + "(" + str(t1_hcp_25_margin)+ "%)")
    print(team2.capitalize() + " win rate and min odds: " + str(round(t2_wr*100,2)) +"% " + str(t2_min_o) + "("+ str(t2_margin) + "%)"   + " +1.5: " + str(round(t2_hcp_15_p*100,2)) + "%" + " " + str(t2_hcp_15_min_o) + "(" + str(t2_hcp_15_margin)+ "%)"
          + " +2.5: " + str(round(t2_hcp_25_p*100,2)) + "%" + " " + str(t2_hcp_25_min_o) + "(" + str(t2_hcp_25_margin)+ "%)")
    print("")

def calculate_win_probability_t1_bo3(team1_str, team2_str):
    team1_str_own_pick = team1_str*1.05
    team2_str_own_pick = team2_str*1.05
    t1_m1_wr = calculate(team1_str_own_pick, team2_str)
    t1_m2_wr = calculate(team1_str, team2_str_own_pick)
    t1_m3_wr = calculate(team1_str, team2_str)

    scenario_1 = t1_m1_wr *  t1_m2_wr
    scenario_2 = t1_m1_wr * (1 -  t1_m2_wr) * t1_m3_wr
    scenario_3 = (1 - t1_m1_wr) * t1_m2_wr * t1_m3_wr

    # Calculate the overall win percentage
    win_c = scenario_1 + scenario_2 + scenario_3

    t1_handi = scenario_1

    return win_c, t1_handi

def winrate_func_bo3(team1, team2, team1_str, team2_str):
    print(team1, team2, team1_str, team2_str)
    team1_wr, t1_hcp = calculate_win_probability_t1_bo3(team1_str, team2_str)         
    t1_wr = round(float(team1_wr*100), 2)
    t2_wr = round(float((1-team1_wr)*100), 2)
    t1_o = round(float(1 / (team1_wr)), 2)
    t2_o = round(float(1 / (1 - team1_wr)), 2)
    
    t1_hcp_r = round(float(t1_hcp*100), 2)
    t2_hcp_r = round(float((1-t1_hcp)*100), 2)
    t1_hcp_o = round(float(1 / t1_hcp,), 2)
    t2_hcp_o = round(float(1 / (1-t1_hcp)), 2)
    t1_min_o, t1_margin = scale_min_odds_by_wr_ml(team1_wr, 3)
    t2_min_o, t2_margin = scale_min_odds_by_wr_ml(t2_wr/100, 3)

    t1_hcp_min_o, t1_hcp_margin = scale_min_odds_by_wr_ml(t1_hcp, 2)
    t2_hcp_min_o, t2_hcp_margin = scale_min_odds_by_wr_ml(1-t1_hcp, 2)
    
    print("")
    print(team1.capitalize() + " vs " + team2.capitalize() + ":")
    print()
    print(team1.capitalize() + " win rate and min odds: " + str(round(team1_wr*100,2)) +"% " + str(t1_min_o) + "("+ str(t1_margin) + "%)"   + " -1.5: " + str(round(t1_hcp_r,2)) + "%" + " " + str(t1_hcp_min_o) + "(" + str(t1_hcp_margin)+ "%)")
    print(team2.capitalize() + " win rate and min odds: " + str(round(t2_wr,2)) +"% " + str(t2_min_o) + "("+ str(t2_margin) + "%)"   + " +1.5: " + str(round(t2_hcp_r,2)) + "%" + " " + str(t2_hcp_min_o) + "(" + str(t2_hcp_margin)+ "%)")
    print()

def winrate_func_bo1(team1, team2, team1_str, team2_str):
    team1_wr = calculate(team1_str, team2_str)
    team2_wr = 1 - team1_wr
    t1_wr = round(float(team1_wr*100), 2)
    t2_wr = round(float((1-team1_wr)*100), 2)
    t1_o = round(float(1 / (team1_wr)), 2)
    t2_o = round(float(1 / (1 - team1_wr)), 2)
    
    t1_min_o, t1_margin = scale_min_odds_by_wr_ml(team1_wr, 1)
    t2_min_o, t2_margin = scale_min_odds_by_wr_ml(team2_wr, 1)

    print(team1.capitalize() + " vs " + team2.capitalize() + ":")
    print()
    print(team1.capitalize() + " win rate and min odds: " + str(t1_wr) +"% " + str(round(t1_min_o,2)) + " ("+ str(t1_margin) + ")")
    print(team2.capitalize() + " win rate and min odds: " + str(t2_wr) +"% " + str(round(t2_min_o,2)) + " ("+ str(t2_margin) + ")")
    print()


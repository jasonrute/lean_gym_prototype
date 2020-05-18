def parse_goal_info(goal_info):
    state_ix = int(goal_info.split("Current state index:\n")[1].split("\n")[0])

    if "no goals" in goal_info:
        solved = True
    else:
        solved = False

    if not solved:
        local_vars = []
        for l in goal_info.split("Local names:\n")[1].split("\n"):
            if l:
                local_vars.append(l)
    else:
        local_vars = None

    return {'state_ix': state_ix, 'locals': local_vars, 'solved': solved}
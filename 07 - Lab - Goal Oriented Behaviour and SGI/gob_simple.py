'''Goal Oriented Behaviour - Step 2: Demonstrating SGI Limitations

Created for COS30002 AI for Games, Lab,
by Clinton Woodward <cwoodward@swin.edu.au>

For class use only. Do not publicly share or post this code without permission.

This version modifies the original code to showcase a scenario where SGI can lead to suboptimal behavior.
'''

VERBOSE = True

# Global goals with initial values
goals = {
    'Eat': 4,
    'Sleep': 3,
    'Health': 5
}

# Global (read-only) actions and effects
actions = {
    'get raw food': {'Eat': -3, 'Sleep': 1},
    'get snack': {'Eat': -2, 'Sleep': 1},
    'sleep in bed': {'Sleep': -4, 'Eat': 2},
    'sleep on sofa': {'Sleep': -2, 'Eat': 1},
    'exercise': {'Health': -1, 'Eat': 2, 'Sleep': 1}
}

def apply_action(action):
    '''Change all goal values using this action. An action can change multiple
    goals (positive and negative side effects).
    Negative changes are limited to a minimum goal value of 0.
    '''
    for goal, change in actions[action].items():
        goals[goal] = max(goals[goal] + change, 0)

def action_utility(action, goal):
    '''Return the 'value' of using "action" to achieve "goal".'''
    if goal in actions[action]:
        return -actions[action][goal]
    else:
        return 0

def choose_action():
    '''Return the best action to respond to the current most insistent goal.'''
    assert len(goals) > 0, 'Need at least one goal'
    assert len(actions) > 0, 'Need at least one action'

    # Find the most insistent goal
    best_goal, best_goal_value = max(goals.items(), key=lambda item: item[1])

    if VERBOSE: print('BEST_GOAL:', best_goal, goals[best_goal])

    # Find the best (highest utility) action to take.
    best_action = None
    best_utility = None
    for key, value in actions.items():
        if best_goal in value:
            if best_action is None:
                best_action = key
                best_utility = action_utility(key, best_goal)
            else:
                utility = action_utility(key, best_goal)
                if utility > best_utility:
                    best_action = key
                    best_utility = utility

    return best_action

#==============================================================================

def print_actions():
    print('ACTIONS:')
    for name, effects in actions.items():
        print(" * [%s]: %s" % (name, str(effects)))

def run_until_all_goals_zero():
    HR = '-'*40
    print_actions()
    print('>> Start <<')
    print(HR)
    running = True
    while running:
        print('GOALS:', goals)
        action = choose_action()
        print('BEST ACTION:', action)
        apply_action(action)
        print('NEW GOALS:', goals)
        if all(value == 0 for goal, value in goals.items()):
            running = False
        print(HR)
    print('>> Done! <<')

if __name__ == '__main__':
    run_until_all_goals_zero()
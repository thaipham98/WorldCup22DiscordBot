from match_table import MatchTable
from user_table import UserTable
from database import get_user_table, get_match_table


def get_user_match_result_list(user_id):
    user = get_user_table().view_user(str(user_id))
    if user is None:
        return []
    user_record = user.get_all_record()

    return user_record.history


def calculate_streak(matches, match_start_index=None):
    # loss is L or HL or DHL
    # win is W or HW or DHW
    # draw is D
    # win streak is a positive number of consecutive wins
    # loss streak is a negative number of consecutive losses
    # draw is 0
    # max win streak is 3
    # max loss streak is 4
    # calculate the streak of consecutive wins, losses, and draws, until the streak is broken
    # return a list of streaks
    streaks = []
    streak_counter = None
    first_effective_match_index = 0 if match_start_index is None else match_start_index

    effective_matches = matches[first_effective_match_index:]

    for match in effective_matches:
        if match == 'WIN' or match == 'HALF_WIN' or match == 'DOUBLE_WIN' or match == "DOUBLE_HALF_WIN":
            if streak_counter is None:
                streak_counter = 1
            elif streak_counter <= 0:
                streaks.append(streak_counter)
                streak_counter = 1
            elif streak_counter == 3:
                streaks.append(streak_counter)
                streak_counter = 1
            else:
                streak_counter += 1
        elif match == 'LOSS' or match == 'HALF_LOSS' or match == 'DOUBLE_LOSS' or match == 'DOUBLE_HALF_LOSS':
            if streak_counter is None:
                streak_counter = -1
            elif streak_counter >= 0:
                streaks.append(streak_counter)
                streak_counter = -1
            elif streak_counter == -4:
                streaks.append(streak_counter)
                streak_counter = -1
            else:
                streak_counter -= 1
        else:
            if streak_counter is None:
                streak_counter = 0
            else:
                streaks.append(streak_counter)
                streak_counter = 0
    streaks.append(streak_counter)
    return streaks


def get_total_reward_hopestar_based_on_streak(streaks):
    # streak of 3 wins is a hopestar
    # streak of 4 losses is a hopestar
    # streak of 0 does not get a hopestar
    hopestar = 0
    for streak in streaks:
        if streak == 3:
            hopestar += 1
        elif streak == -4:
            hopestar += 1
    return hopestar


def get_total_reward_hopestar_based_on_match_list(matches,
                                                  match_start_index=None):
    streaks = calculate_streak(matches, match_start_index)
    hopestar = get_total_reward_hopestar_based_on_streak(streaks)
    return hopestar


def get_user_total_reward_hopestar(user_id):
    user = get_user_table().view_user(str(user_id))
    if user is None:
        return 0
    user_record = user.to_record()
    user_start_match_index = user_record.start_match_index

    user_match_result_list = get_user_match_result_list(user_id)

    total_reward_hopestar = get_total_reward_hopestar_based_on_match_list(
        user_match_result_list, user_start_match_index)
    return total_reward_hopestar

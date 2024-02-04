from enum import Enum

import yaml
import copy
import sys

priority_field = 'Priority'
mark_field = 'Mark'
weight_field = 'Weight'


class WeightType(Enum):
    PRIORITY = 1
    MARK = 2


def load_goals() -> dict:
    with open('goals.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def are_child_goals_have_priorities(child_goals: dict) -> bool:
    if type(child_goals) is not dict:
        return False
    assert priority_field not in child_goals or mark_field not in child_goals, \
        'Both priority and mark fields simultaneously are prohibited'
    return priority_field in child_goals


def are_child_goals_have_marks(child_goals: dict) -> bool:
    if type(child_goals) is not dict:
        return False
    assert priority_field not in child_goals or mark_field not in child_goals, \
        'Both priority and mark fields simultaneously are prohibited'
    return mark_field in child_goals


def get_priorities_or_marks_with_goals(goals: dict, weightType: WeightType) -> dict[int: any]:
    priorities_with_goals = {}
    weight_type_field = priority_field if weightType == WeightType.PRIORITY else mark_field
    for name, goal in goals.items():
        if name not in [priority_field, mark_field]:
            if weight_type_field == priority_field and goal[priority_field] == 0:
                return {1: [name]}
            if goal[weight_type_field] not in priorities_with_goals:
                priorities_with_goals[goal[weight_type_field]] = []
            if len(goal) == 1 and weight_type_field in goal:
                priorities_with_goals[goal[weight_type_field]].append(name)
            else:
                priorities_with_goals[goal[weight_type_field]] = [{name + ' — ' + weighted_goal: weight} for
                                                                  weighted_goal, weight in goal.items() if
                                                                  weighted_goal != weight_type_field]
    return priorities_with_goals


def count_goals_with_the_same_priority(goals: list) -> int:
    goal_dict_count = sum(map(lambda goal: type(goal) is dict, goals))
    return len(goals) - (goal_dict_count - 1) if goal_dict_count > 0 else 1


def get_key_from_dict(dictionary: dict, index=0) -> any:
    return list(dictionary.keys())[index]


def get_value_from_dict(dictionary: dict, index=0) -> any:
    return list(dictionary.values())[index]


def put_weighted_goals(weighted_goals: dict, goals: list, weight: float) -> None:
    for goal in goals:
        if type(goal) is dict:
            goal_name = get_key_from_dict(goal)
            goal_weight = weight * get_value_from_dict(get_value_from_dict(goal))
            weighted_goals[goal_name] = {weight_field: goal_weight}
        else:
            weighted_goals[goal] = {weight_field: weight}


def check_sum_of_goal_weights(weighted_goals: dict[str: dict[str: float]]) -> None:
    sum_of_goal_weights = sum(map(lambda weight_dict: weight_dict[weight_field], weighted_goals.values()))
    assert abs(1 - sum_of_goal_weights) < sys.float_info.epsilon, \
        f"Wrong sum of goal weights: {sum_of_goal_weights}"


def get_weighted_goals_by_marks(goals: dict) -> dict[str: dict[str: float]]:
    weighted_goals = {}
    marks_with_goals = get_priorities_or_marks_with_goals(goals, WeightType.MARK)
    sum_priority_marks = sum(map(lambda mark_goal: 11 - mark_goal, marks_with_goals))
    for mark, goal_list in marks_with_goals.items():
        weight = (11 - mark) / sum_priority_marks
        put_weighted_goals(weighted_goals, goal_list, weight)
    check_sum_of_goal_weights(weighted_goals)
    return weighted_goals


def get_weighted_goals_by_priorities(goals: dict) -> dict[str: dict[str: float]]:
    weighted_goals = {}
    priorities_with_goals = get_priorities_or_marks_with_goals(goals, WeightType.PRIORITY)
    min_priority = max(priorities_with_goals)
    for priority, goal_list in priorities_with_goals.items():
        the_same_priority_goal_count = count_goals_with_the_same_priority(goal_list)
        weight = (float(2 ** (min_priority - priority)) / the_same_priority_goal_count) / (2 ** min_priority - 1)
        put_weighted_goals(weighted_goals, goal_list, weight)
    check_sum_of_goal_weights(weighted_goals)
    return weighted_goals


def get_weighted_goals(goals: dict) -> dict[str: dict[str, float]]:
    if any(are_child_goals_have_priorities(child_goals) for child_goals in goals.values()):
        return get_weighted_goals_by_priorities(goals)
    elif any(are_child_goals_have_marks(child_goals) for child_goals in goals.values()):
        return get_weighted_goals_by_marks(goals)
    else:
        raise ValueError("Wrong goals file structure")


def is_it_root_node(node: dict) -> bool:
    return 'Development' in node and 'Routine' in node


def create_processed_goal_node(goals: dict, processed_goals: dict) -> dict[str: any]:
    if is_it_root_node(goals):
        return processed_goals
    in_between_goals = copy.copy(processed_goals)
    for name, value in goals.items():
        if type(value) is int:
            in_between_goals[name] = value
            return in_between_goals
    raise ValueError("Wrong sum of goal weights")


def process_goals(goals: dict) -> dict:
    weights_were_calculated = False
    for name, child_goals in goals.items():
        if type(child_goals) is dict and len(child_goals) > 1:
            processed_goals = process_goals(child_goals)
            weights_were_calculated = True
            goals[name] = create_processed_goal_node(child_goals, processed_goals)

    if weights_were_calculated:
        return create_processed_goal_node(goals, get_weighted_goals(goals))

    return get_weighted_goals(goals)


def select_random_goal() -> None:
    goals = load_goals()
    goals_dict = process_goals(goals)
    print(goals_dict)


if __name__ == '__main__':
    select_random_goal()

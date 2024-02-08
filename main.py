from enum import Enum

import yaml
import sys
import random

priority_field = 'Priority'
mark_field = 'Mark'
weight_field = 'Weight'
start_time_field = 'Start time'
deadline_field = 'Deadline'
last_execution_field = 'Last execution'
start_duration_field = 'Start duration'
escalation_duration_field = 'Escalation duration'
special_fields = [priority_field, last_execution_field, mark_field, weight_field, start_time_field,
                  deadline_field, start_duration_field, escalation_duration_field]


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


def are_fields_special(child_goals: dict) -> bool:
    return all(field in special_fields for field in child_goals)


def get_priorities_or_marks_with_goals(goals: dict, weightType: WeightType) -> dict[int: any]:
    priorities_with_goals = {}
    weight_type_field = priority_field if weightType == WeightType.PRIORITY else mark_field
    for name, goal in goals.items():
        if name not in special_fields:
            if weight_type_field == priority_field and goal[priority_field] == 0:
                return {1: [name]}
            if goal[weight_type_field] not in priorities_with_goals:
                priorities_with_goals[goal[weight_type_field]] = []
            if are_fields_special(goal):
                if len(goal) == 1:
                    priorities_with_goals[goal[weight_type_field]].append(name)
                else:
                    priorities_with_goals[goal[weight_type_field]].append({name: {special_field: special_value for
                                                                                  special_field, special_value in
                                                                                  goal.items() if
                                                                                  special_field != weight_type_field}})
            else:
                for weighted_goal, weight in goal.items():
                    if weighted_goal != weight_type_field:
                        priorities_with_goals[goal[weight_type_field]].append({name + ' — ' + weighted_goal: weight})
    return priorities_with_goals


def get_key_from_dict(dictionary: dict, index=0) -> any:
    return list(dictionary.keys())[index]


def get_value_from_dict(dictionary: dict, index=0) -> any:
    return list(dictionary.values())[index]


def normalize(goals: list[dict[str: dict[str: float]]], priority_weight: float) -> None:
    total_weight = sum(get_value_from_dict(goal)[weight_field] for goal in goals)
    factor = total_weight / priority_weight
    for goal in goals:
        get_value_from_dict(goal)[weight_field] /= factor
    pass


def put_special_fields_into_goal_list(priorities_with_goals: list, priority_weight: float) \
        -> list[dict[str: dict[str: float]]]:
    weighted_goal_list = list()
    for goal in priorities_with_goals:
        goal_fields = get_value_from_dict(goal) if type(goal) is dict else None
        if goal_fields is None:
            weighted_goal_list.append({goal: {weight_field: 1.0}})
        else:
            goal_name = get_key_from_dict(goal)
            if weight_field not in goal_fields:
                goal_fields[weight_field] = 1.0
            weighted_goal_list.append({goal_name: goal_fields})
    normalize(weighted_goal_list, priority_weight)
    return weighted_goal_list


def put_goal_list_into_dict(goals_dict: dict[str: dict[str: float]], goals_list: list[dict[str: dict[str: float]]]):
    for goal in goals_list:
        goals_dict[get_key_from_dict(goal)] = get_value_from_dict(goal)


def check_sum_of_goal_weights(weighted_goals: dict[str: dict[str: float]]) -> None:
    sum_of_goal_weights = sum(map(lambda weight_dict: weight_dict[weight_field], weighted_goals.values()))
    assert abs(1 - sum_of_goal_weights) < sys.float_info.epsilon, f"Wrong sum of goal weights: {sum_of_goal_weights}"


def get_weighted_goals_by_marks(goals: dict) -> dict[str: dict[str: float]]:
    weighted_goals = {}
    marks_with_goals = get_priorities_or_marks_with_goals(goals, WeightType.MARK)
    sum_priority_marks = sum(map(lambda mark_goal: 11 - mark_goal, marks_with_goals))
    for mark, goal_list in marks_with_goals.items():
        priority_weight = (11 - mark) / sum_priority_marks
        put_goal_list_into_dict(weighted_goals, put_special_fields_into_goal_list(goal_list, priority_weight))
    check_sum_of_goal_weights(weighted_goals)
    return weighted_goals


def get_weighted_goals_by_priorities(goals: dict) -> dict[str: dict[str: float]]:
    weighted_goals = {}
    priorities_with_goals = get_priorities_or_marks_with_goals(goals, WeightType.PRIORITY)
    min_priority = max(priorities_with_goals)
    for priority, goal_list in priorities_with_goals.items():
        priority_weight = float(2 ** (min_priority - priority)) / (2 ** min_priority - 1)
        put_goal_list_into_dict(weighted_goals, put_special_fields_into_goal_list(goal_list, priority_weight))
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
    for name, value in goals.items():
        if type(value) is int:
            processed_goals[name] = value
            return processed_goals
    raise ValueError("Wrong sum of goal weights")


def process_goals(goals: dict) -> dict:
    weights_were_calculated = False
    for name, child_goals in goals.items():
        if type(child_goals) is dict and not are_fields_special(child_goals):
            goals[name] = create_processed_goal_node(child_goals, process_goals(child_goals))
            weights_were_calculated = True

    if weights_were_calculated:
        return create_processed_goal_node(goals, get_weighted_goals(goals))

    return get_weighted_goals(goals)


def get_lower_goal(goals: dict[str: dict[str: float]], random_point: float) -> str:
    integral_probability = float()
    for name, weight_dict in goals.items():
        integral_probability += weight_dict[weight_field]
        if integral_probability > random_point:
            return name
    raise ValueError("Wrong sum of goal weights or wrong random point (must be <=1)")


def select_random_goal() -> str:
    goals = load_goals()
    goals_dict = process_goals(goals)
    random_point = random.random()
    return get_lower_goal(goals_dict, random_point)


if __name__ == '__main__':
    print(select_random_goal())

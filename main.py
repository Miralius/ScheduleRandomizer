from enum import Enum

import yaml
import sys
import random
import datetime

priority_field = 'Priority'
mark_field = 'Mark'
weight_field = 'Weight'
start_time_field = 'Start time'
deadline_field = 'Deadline'
last_execution_field = 'Last execution'
start_duration_field = 'Start duration'
escalation_duration_field = 'Escalation duration'
color_field = 'Color'
yellow_field = 'Yellow time'
red_field = 'Red time'
special_fields = [priority_field, last_execution_field, mark_field, weight_field, start_time_field,
                  deadline_field, start_duration_field, escalation_duration_field, color_field]


class WeightType(Enum):
    PRIORITY = 1
    MARK = 2


class Color(Enum):
    NOT_STARTED = 0
    WHITE = 1
    YELLOW = 2
    RED = 3
    BLACK = 4


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
    sum_of_goal_weights = sum(map(lambda weight_dict: weight_dict[weight_field] if type(weight_dict) is dict else 0,
                                  weighted_goals.values()))
    assert abs(1 - sum_of_goal_weights) < sys.float_info.epsilon, f"Wrong sum of goal weights: {sum_of_goal_weights}"


def get_weighted_goals_by_marks(goals: dict) -> dict[str: dict[str: float]]:
    weighted_goals = {}
    marks_with_goals = get_priorities_or_marks_with_goals(goals, WeightType.MARK)
    sum_priority_marks = sum(map(lambda mark_goal: 11 - mark_goal, marks_with_goals))
    for mark, goal_list in marks_with_goals.items():
        assert 0 <= mark <= 10, f"Mark {mark} is out of range [0, 10]"
        priority_weight = (11 - mark) / sum_priority_marks
        put_goal_list_into_dict(weighted_goals, put_special_fields_into_goal_list(goal_list, priority_weight))
    check_sum_of_goal_weights(weighted_goals)
    return weighted_goals


def get_weighted_goals_by_priorities(goals: dict) -> dict[str: dict[str: float]]:
    weighted_goals = {}
    priorities_with_goals = get_priorities_or_marks_with_goals(goals, WeightType.PRIORITY)
    min_priority = max(priorities_with_goals)
    for priority, goal_list in priorities_with_goals.items():
        assert priority >= 0, f"Priority {priority} is negative"
        priority_weight = float(2 ** (min_priority - priority)) / (2 ** min_priority - 1)
        put_goal_list_into_dict(weighted_goals, put_special_fields_into_goal_list(goal_list, priority_weight))
    check_sum_of_goal_weights(weighted_goals)
    return weighted_goals


def calculate_goal_times_with_color(node: dict[str: dict[str: any]], previous_color: Color, current_color: Color):
    previous_color_numerator = 2 ** (-(current_color.value - previous_color.value + 1))
    previous_color_factor = previous_color_numerator / sum(goal_fields[weight_field] for goal_fields in node.values()
                                                           if type(goal_fields) is dict
                                                           and goal_fields[color_field].value <= previous_color.value)
    current_color_factor = (1 - previous_color_numerator) / sum(
        goal_fields[weight_field] for goal_fields in node.values() if type(goal_fields) is dict and
        goal_fields[color_field] == current_color)
    for goal_name, goal_field in node.items():
        if type(goal_field) is not dict:
            continue
        if goal_field[color_field].value <= previous_color.value:
            node[goal_name][weight_field] *= previous_color_factor
        elif goal_field[color_field] == current_color:
            node[goal_name][weight_field] *= current_color_factor


def calculate_goal_times(node: dict[str: dict[str: any]], colors: list[Color]) -> None:
    assert len(colors), "Empty color list"
    assert Color.NOT_STARTED not in colors, "Node shouldn't include not started goals."
    previous_color = None
    for current_color in [Color.WHITE, Color.YELLOW, Color.RED, Color.BLACK]:
        if current_color in colors:
            if not previous_color:
                previous_color = current_color
                continue
            calculate_goal_times_with_color(node, previous_color, current_color)
            previous_color = current_color
    check_sum_of_goal_weights(node)


def get_color_by_time(begin_time: datetime, yellow_time: datetime, red_time: datetime, end_time: datetime) -> Color:
    assert begin_time < yellow_time < red_time < end_time, "Wrong begin/yellow/red/end times"
    if end_time <= datetime.datetime.now():
        return Color.BLACK
    elif red_time <= datetime.datetime.now() < end_time:
        return Color.RED
    elif yellow_time <= datetime.datetime.now() < red_time:
        return Color.YELLOW
    elif begin_time <= datetime.datetime.now() < yellow_time:
        return Color.WHITE
    else:
        return Color.NOT_STARTED


def calculate_repeated_goals(special_goal_fields: dict[str: any]) -> Color:
    assert start_duration_field in special_goal_fields or escalation_duration_field in special_goal_fields, \
        "Goal must have start and/or escalation duration fields"
    start_duration = datetime.timedelta(
        days=special_goal_fields[start_duration_field] if start_duration_field in special_goal_fields else
        special_goal_fields[escalation_duration_field])
    begin_time = (special_goal_fields[last_execution_field] + start_duration)
    next_color_duration = datetime.timedelta(
        days=special_goal_fields[escalation_duration_field] if escalation_duration_field in special_goal_fields else
        special_goal_fields[start_duration_field])
    end_time = begin_time + 3 * next_color_duration
    red_time = begin_time + 2 * next_color_duration
    yellow_time = begin_time + next_color_duration
    return get_color_by_time(begin_time, yellow_time, red_time, end_time)


def calculate_deadlined_goals(special_goal_fields: dict[str: any]) -> Color:
    assert start_time_field in special_goal_fields, "No start time for deadlined goal"
    begin_time = special_goal_fields[start_time_field]
    end_time = special_goal_fields[deadline_field]
    yellow_time = special_goal_fields[yellow_field] if yellow_field in special_goal_fields \
        else begin_time + (end_time - begin_time) / 2
    red_time = special_goal_fields[red_field] if red_field in special_goal_fields \
        else begin_time + (end_time - begin_time) * 3 / 4
    return get_color_by_time(begin_time, yellow_time, red_time, end_time)


def set_and_get_goal_colors(node: dict[str: dict[str: any]]) -> list[Color]:
    colors = []
    for goal_name, special_goal_fields in node.items():
        if type(special_goal_fields) is not dict:
            continue
        color = Color.WHITE
        if deadline_field in special_goal_fields:
            color = calculate_deadlined_goals(special_goal_fields)
        elif last_execution_field in special_goal_fields:
            color = calculate_repeated_goals(special_goal_fields)
        if color != Color.NOT_STARTED:
            node[goal_name] = {weight_field: special_goal_fields[weight_field], color_field: color}
        else:
            del node[goal_name]
        colors.append(color)
    return colors


def calculate_weighted_goals_by_times(goals: dict[str: dict[str: dict[str: any]]]) -> None:
    for node in goals.values():
        calculate_goal_times(node, set_and_get_goal_colors(node))


def get_weighted_goals(goals: dict) -> dict[str: dict[str, any]]:
    if is_it_root_node(goals):
        calculate_weighted_goals_by_times(goals)
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

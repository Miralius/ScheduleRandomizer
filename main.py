import yaml


def load_goals():
    with open('goals.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def select_random_goal():
    goals = load_goals()
    print(goals)


if __name__ == '__main__':
    select_random_goal()

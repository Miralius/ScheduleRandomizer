A small script to convert goal tree to goal dictionary with probabilities according to priorities, marks and deadlines.  
See example [goals.yaml](goals.yaml)  

## Priorities
Priorities are calculated exponentially, for example:  
- Weight of priority 1 = 2 ** (1 - 1) / (2 ** 3 - 1) = 1/7
- Weight of priority 2 = 2 ** (2 - 1) / (2 ** 3 - 1) = 2/7
- Weight of priority 3 = 2 ** (3 - 1) / (2 ** 3 - 1) = 4/7
- ...  

If priority == 0, then script takes only this goal and drops other goals.  
[goals.yaml](goals.yaml) file may have only one zero-priority goal.  
## Marks  
Marks are calculated as a part of calculated their sum, for example:  
- Mark 0 = 11 - 0 = 11
- Mark 5 = 11 - 5 = 6
- Mark 10 = 11 - 10 = 1
- Sum = 11 + 6 + 1 = 17  
Thus,
  - Weight of mark 0 = 11/17
  - Weight of mark 5 = 6/17
  - Weight of mark 10 = 1/17  

> :warning: The sum of weight is always equal to 1!!!  

> :warning: Both priority and mark fields simultaneously in one node are prohibited

## Timed goals
You can use deadline for one-time goals or durations for repeated goals.
### Colors
Times are also calculated exponentially. Each goal has a color:
- :white_small_square: Color.NOT_STARTED - not-started goal (will be dropped)
- :white_circle: Color.WHITE - goal with normal priority
- :yellow_circle: Color.YELLOW - goal with medium priority
- :red_circle: Color.RED - goal with high priority
- :black_circle: Color.BLACK - goal with the highest priority  

#### Examples
1. Let goal tree has all (except NOT_STARTED) colors, then:
  - :white_circle: weight = 1.5625%
  - :yellow_circle: weight = 4.6875%
  - :red_circle: weight = 18.75%
  - :black_circle: weight = 75%
2. Let goal tree has white and black colors, then:
  - :white_circle: weight = 6.25%
  - :black_circle: weight = 93.75%
3. Let goal tree has white and yellow colors, then:
  - :white_circle: weight = 25%
  - :yellow_circle: weight = 75%

### Deadlined goals

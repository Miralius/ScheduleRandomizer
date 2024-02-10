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
If goal has `Deadline` field for the goal will be calculated deadline and according color.
The goal also must have `Start time`. `Yellow time` and `Red time` are optional. How does program calculate colors?  
Let `Goal duration` = `End time` - `Start time`, then:
- :white_small_square: Color.NOT_STARTED - `datetime.datetime.now()` < `Start time`
- :white_circle: Color.WHITE - `Start time` <= `datetime.datetime.now()` < 
`Yellow time` or `Start time` + 50%`Goal duration`
- :yellow_circle: Color.YELLOW - `Yellow time` or `Start time` + 50%`Goal duration` <=
`datetime.datetime.now()` < `Red time` or `Start time` + 75%`Goal duration`
- :red_circle: Color.RED - `Red time` or `Start time` + 75%`Goal duration` <=
`datetime.datetime.now()` < `End time`
- :black_circle: Color.BLACK - `End time` <= `datetime.datetime.now()`
> :warning: `Start time` < `Yellow time` < `Red time` < `End time`
### Repeated goals
If goal has `Last execution` field for the goal will be calculated durations and according color.
The goal also must have `Start duration` and/or `Escalation duration`. How does program calculate colors?  
Let `Start time` = `Last execution` + `Start duration` (or `Escalation duration` if there isn't `Start duration`),
and `Next color duration` = `Escalation duration` if there's `Escalation duration` else `Start duration`. Then:
- :white_small_square: Color.NOT_STARTED - `datetime.datetime.now()` < `Start time`
- :white_circle: Color.WHITE - `Start time` <= `datetime.datetime.now()` < `Start time` + `Next color duration`
- :yellow_circle: Color.YELLOW - `Start time` + `Next color duration` <= `datetime.datetime.now()` < 
`Start time` + 2 × `Next color duration`
- :red_circle: Color.RED - `Start time` + 2 × `Next color duration` <= `datetime.datetime.now()` < 
`Start time` + 3 × `Next color duration`
- :black_circle: Color.BLACK - `Start time` + 3 × `Next color duration` <= `datetime.datetime.now()`  

## Format
- `Priority`: non-negative int
- `Mark`: int &#8712; [0, 10]
- `Start time`: ISO datetime
- `Deadline time`: ISO datetime
- `Last execution`: ISO datetime
- `Start duration`: non-negative int
- `Escalation duration`: positive int
- `Yellow time`: ISO datetime
- `Red time`: ISO datetime
- Other fields are `str`
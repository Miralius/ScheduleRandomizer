A small script to convert goal tree to goal dictionary with probabilities according to priorities, marks and deadlines.  
See example [goals.yaml](goals.yaml)  

## Priorities
Priorities are calculated exponentially, for example:  
- Weight of priority 1 = $2^{1 - 1}/{(2^3 - 1)}$ = $1/7$
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
> :warning: Only goals without sub goals (that is, the 'childest' goals) may have timed fields
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

# How it works (example)
Let [goals.yaml](goals.yaml) has such structure:
```
---
Development:
  Priority: 1
  First sphere:
    Mark: 3
    First goal:
      Priority: 2
      First sub-goal:
        Priority: 3
      Second sub-goal:
        Priority: 2
      Third sub-goal:
        Priority: 1
      Fourth sub-goal:
        Priority: 1
        High important sub-sub-goal:
          Priority: 0
        The second sub-sub-goal:
          Priority: 1
      Fifth sub-goal:
        Priority: 4
    Second goal:
      Priority: 1
      First highly important goal:
        Priority: 0
      Second goal:
        Priority: 1
        First sub-goal:
          Priority: 1
        Second sub-goal:
          Priority: 2
        Third sub-goal:
          Priority: 3
          First sub-sub-goal:
            Priority: 1
          Second sub-sub-goal:
            Priority: 2
          Third sub-sub-goal:
            Priority: 3
          Fourth sub-sub-goal:
            Priority: 4
      Third goal:
        Priority: 2
        First sub-goal:
          Priority: 1
        Second sub-goal:
          Priority: 2
        Third sub-goal:
          Priority: 3
          First sub-sub-goal:
            Priority: 1
          Second sub-sub-goal:
            Priority: 2
          Third sub-sub-goal:
            Priority: 3
          Fourth sub-sub-goal:
            Priority: 4
  Second sphere:
    Mark: 0
    First goal:
      Priority: 1
      First sub-goal:
        Priority: 1
        First sub-sub-goal:
          Priority: 1
          First sub-sub-sub-goal:
            Priority: 1
            Start time: 2023-11-08T13:00:00
            Yellow time: 2023-11-30T00:00:00
            Red time: 2023-12-01T23:59:59
            Deadline: 2023-12-08T23:59:59
Routine:
  Priority: 1
  First sphere:
    Mark: 0
    First goal:
      Priority: 1
      First sub-goal:
        Priority: 1
        Last execution: 2023-11-08T13:00:00
        Start duration: 30
        Escalation duration: 1
```
Then it turns into such dictionary:
```python
{
  'Development — First sphere — First goal — First sub-goal': {'Color': Color.WHITE, 'Weight': 0.00138889},
  'Development — First sphere — First goal — Second sub-goal': {'Color': Color.WHITE, 'Weight': 0.00277778},
  'Development — First sphere — First goal — Third sub-goal': {'Color': Color.WHITE, 'Weight': 0.00277778},
  'Development — First sphere — First goal — Fourth sub-goal — High important sub-sub-goal': {'Color': Color.WHITE, 'Weight': 0.00277778},
  'Development — First sphere — First goal — Fifth sub-goal': {'Color': Color.WHITE, 'Weight': 0.000694444},
  'Development — First sphere — Second goal — First highly important goal': {'Color': Color.WHITE, 'Weight': 0.0208333},
  'Development — Second sphere — First goal — Fifth sub-goal — First sub-sub goal — First sub-sub-sub-goal': {'Color': Color.BLACK, 'Weight': 0.46875},
  'Routine — First sphere — First goal — Fifth sub-goal': {'Color': Color.BLACK, 'Weight': 0.5}
}
```
And program generates random number &#8712; [0, 1), for example, `random_point` = 0.617469.
Then the program finds the first goal which has an accumulated weight not less than `random_point`.
In this case it will be `'Routine — First sphere — First goal — Fifth sub-goal'`
because its accumulated weight = 1.0 &#8814; `random_point = 0.617469`.
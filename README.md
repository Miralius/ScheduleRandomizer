A small script to convert goal tree to goal dictionary with probabilities according to priorities, marks and deadlines.  
See example [goals.yaml](goals.yaml)  

### Priorities
Priorities are calculated exponentially, for example:  
- Weight of priority 1 = 2 ** (1 - 1) / (2 ** 3 - 1) = 1/7
- Weight of priority 2 = 2 ** (2 - 1) / (2 ** 3 - 1) = 2/7
- Weight of priority 3 = 2 ** (3 - 1) / (2 ** 3 - 1) = 4/7
- ...  

If priority == 0, then script takes only this goal and drops other goals.  
goal.yaml file may have only one zero-priority goal.  
### Marks  
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
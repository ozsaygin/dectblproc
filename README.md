# dectblproc

dectblproc is a command-line tool designed to process boolean decision
tables and creates a test suite for each satisfiable rule in the decision table.


## Installation 
```
$ cd dectblproc
$ ./setup.py install
```

## Uninstallation
```
$ pip uninstall dectblproc 
```

## Usage
```
$ dectblproc dt

# You may also run it by typing (if you don't want to install it):
# python dectblproc.py dt
```

## Sample Input File
```
c1: (o3 & o4)| (o2 & o5) 
c2: o4 | o5
c3: -o1
##
c1 TTTTFFFF
c2 TTFFTT-F
c3 TFTFTFT-
a1 XX..X...
a2 X....X..
a3 .X......
a4 ..XXX.XX
``` 

## Sample Output

```
$ python dectblproc.py dt0
Processing file: dt0 
Is table complete?  100% complete
Is table redundant? No
Is table inconsistent? No
Testsuite
=========
╒═════════╤══════╤══════╤══════╤══════╤══════╕
│ rules   │ o1   │ o2   │ o3   │ o4   │ o5   │
╞═════════╪══════╪══════╪══════╪══════╪══════╡
│ r1      │ F    │ F    │ T    │ T    │ T    │
├─────────┼──────┼──────┼──────┼──────┼──────┤
│ r2      │ T    │ F    │ T    │ T    │ T    │
├─────────┼──────┼──────┼──────┼──────┼──────┤
│ r5      │ F    │ F    │ F    │ T    │ F    │
├─────────┼──────┼──────┼──────┼──────┼──────┤
│ r6      │ T    │ F    │ F    │ T    │ F    │
├─────────┼──────┼──────┼──────┼──────┼──────┤
│ r7      │ F    │ F    │ F    │ F    │ F    │
├─────────┼──────┼──────┼──────┼──────┼──────┤
│ r8      │ T    │ F    │ F    │ F    │ F    │
╘═════════╧══════╧══════╧══════╧══════╧══════╛


```
# dectblproc

dectblproc is a command-line tool designed to process boolean decision tables and 


## Installation 

`pip install dectblproc`

## Development

## Usage

**The Quick Way**
System Python (2.7.x or 3.x)

sudo pip install dectblproc

**The Recommended Way**

[virtualenv](https://docs.python-guide.org/dev/virtualenvs/)

```
virtualenv venv
# Python 3 users : use -p to specify your Python 3 location:
# virtualenv -p /usr/bin/python3 venv
source venv/bin/activate
pip install dectblproc
# Python 3 users: sudo pip3 install dectblproc
`dectblproc <inputfilename>`
```

conda env

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
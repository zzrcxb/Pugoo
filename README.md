# Pugoo(Beta)
This is a universal program for Go game.
## Dependencies

You need following python3 libraries to run Pugoo, and you can download Python3 from [here](https://www.python.org/downloads/)<br>
Tkinter, numpy, sqlalchemy, pymysql
### How to install dependencies
#### For Windows users
Make sure your computer has Python 3.x and pip installed.<br>
Open command prompt as administrator, and type<br>
<code>pip install tkinter numpy sqlalchemy pymysql</code><br>
Press enter, then wait...<br>
#### For Linux users
Open terminal, and type<br>
<code>sudo apt-get update</code><br>
<code>sudo apt-get install python3-pip python3-numpy</code><br>
<code>pip3 install tkinter sqlalchemy pymysql</code><br>

## How to run
1. Create a python file at root directory, such as run.py
2. Rename config.py.example to config.py and fill the blanks.
3. You can import things need to run go game from GoGame package.
4. Samples are available at samples directory

# Screenshots
## Final game
<img src="https://github.com/zzrcxb/sd_pics/blob/master/pugoo/blank.png" width="450" height="450"></br>

## Mark groups
<img src="https://github.com/zzrcxb/sd_pics/blob/master/pugoo/groups.png" width="450" height="450"></br>
The number on the piece represents group ID.

## Circle analysis
<img src="https://github.com/zzrcxb/sd_pics/blob/master/pugoo/circle_analysis.png" width="450" height="450"></br>
Green half-crosses represent points enclosed by white, and red half-crosses represent points enclosed by black.

## Remove dead
<img src="https://github.com/zzrcxb/sd_pics/blob/master/pugoo/remove_dead.png" width="900" height="450"></br>
Before removing (left), and after removing (right).

## Scoring
<img src="https://github.com/zzrcxb/sd_pics/blob/master/pugoo/score.png" width="450" height="450"></br>

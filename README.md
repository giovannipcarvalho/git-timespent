# git-timespent
Estimate worked hours per author in a git repo. Python 3, no dependencies.

## Installation

```bash
pip install git-timespent
```

## Usage

```bash
# defaults to current directory
$ python -m timespent
#  1. Giovanni Paolo                35m51s (   7 commits)

# or specify a path and number of authors
$ python -m timespent /tmp/numpy -k 5
#  1. Charles Harris                  5w3d (7030 commits)
#  2. Travis Oliphant                2w22h (2047 commits)
#  3. Eric Wieser                    1w12h (1288 commits)
#  4. Pearu Peterson                  1w3h (1126 commits)
#  5. Mark Wiebe                     5d15h ( 798 commits)
```

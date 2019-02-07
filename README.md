# powershell-extract
Small script to pull out script execution blocks from a PowerShell Operational log.

The script will write every scriptblock to a text file based on the time of execution and the UUID with a directory of the date it was executed.

Example: 

\path\powershell_extract\2019_01_31\03_57_49.88c227db-be89-4f34-82ad-e63181053376.txt

The above example was logged at 03:57:49 on 2019-01-31 and the UUID is 88c227db-be89-4f34-82ad-e63181053376.

For large blocks of code, the winevt will seperate them over multiple log lines. This script just pieces them back together into one output file for easier analysis.

Requires python-evtx - https://github.com/williballenthin/python-evtx

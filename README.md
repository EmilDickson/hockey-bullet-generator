# hockey-bullet-generator
A script that takes hockey statistics for two teams and generate xml files for them

# Who is this for?
This will basically only make sense for graphics operators at Statnet, working with the SHL.

# Do I have to install anything?
It uses the following libraries, so if you don't have them, you'll need to install them in order for the script to run (however, most are included in Python already):
- lxml
- requests
- time
- os
- csv
- datetime
- xml.etree.ElementTree
- operator

# What do I do with it?
Run the script (i.e. navigate to the folder and):
```
python3 bullet-s.py
```
Then choose between two options:
1. Automatically generate bullets for a given game (follow the instructions)
2. Generate bullets from a carefully formatted .csv file:
   - Fields need to be: Team logo, Name/team name/headline, Text field 1, Text field 2

Always check that the information is correct before using these.

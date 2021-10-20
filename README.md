# Count-and-list-TM1-users
This custom Python script uses tm1py (https://github.com/cubewise-code/tm1py) to count and list TM1 users on several TM1 instances on an admin host.
The counts are divided following the user rights (admin/read-write/read-only/disabled/...)
The output is customizable, for example, you can use an alias on the }Clients dimension instead of principal names. This makes more sense than looking at CAM client strings.

Versions used during setup:
- TM1py 1.8.0
- TM1 Server Version: 11.8
- Python version 3.8.6

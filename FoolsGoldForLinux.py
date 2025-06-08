"""
______          _     _____       _     _ ___  
|  ___|        | |   |  __ \     | |   | |__ \ 
| |_ ___   ___ | |___| |  \/ ___ | | __| |  ) |
|  _/ _ \ / _ \| / __| | __ / _ \| |/ _` | / / 
| || (_) | (_) | \__ \ |_\ \ (_) | | (_| ||_|  
\_| \___/ \___/|_|___/\____/\___/|_|\__,_|(_)  
                                               
Module to run dpkg commands on a file string given as input from main.py,
Only run if on a unix-like system for efficiency.
Return whether the file was made by the dpkg package manager 
(has an entry in /var/lib/dpkg/info/ for any .list file)
or was made by the user (no *.list entry).
System files created on installation of the OS should have an entry in /var/lib/dpkg/info/.

See docstring in main.py for the author and copyright information.
"""

import subprocess #for running dpkg commands

def is_dpkg_file(file_path):
    """
    Check if the file string exists in any installed dpkg .list file.
    Return True if it an entry exists, return False if not.
    """
    try:
        result = subprocess.run(
            ['dpkg', '-S', file_path],
            capture_output=True,
            text=True
        )
        return result.returncode == 0 and "no path found" not in result.stderr.lower()
    
    except FileNotFoundError:
        print("dpkg package manager not found on this system")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False



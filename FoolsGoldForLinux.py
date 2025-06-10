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
from datetime import datetime #for comparing file creation dates
import logging #for logging errors and warnings only once (this module is looped through by main.py)
from os import stat # Pull statistics for creation date of a file

# Global variable to track if a ValueError has been logged
logger = logging.getLogger(__name__)
value_error_logged = False

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

        # "dpkg -S" returns 0 if the file is found in a package, non-zero if not.
        # Only accept as True if the output also does not mention "no path found". Prevents false positives.
        return result.returncode == 0 and "no path found" not in result.stderr.lower()
    
    except FileNotFoundError:
        print("dpkg package manager not found on this system, perhaps using a different package manager?")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def after_os_installation(file_path):
    """
    Check if the file was created after the OS installation date.
    This is done by comparing the file's creation date with the OS installation date.
    Returns True if the file was created after the OS installation date, False otherwise.
    If None is returned, it indicates an error in parsing the OS installation date. main.py should skip using this function.
    """

    # Open and read from a file (syslog) and close after grapping creation date using (with) to prevent leaving open.
    try:
        # Get the OS installation date from /var/log/installer/syslog
        with open('/var/log/installer/syslog', 'r') as syslog_file:
            lines = syslog_file.readlines()
            # Get the last line which should contain the installation date (total lines including new line minus 1)
            last_line = lines[-1]

            try:
                # Rip out the date on the last line which should be "Birth: YYYY-MM-DD"
                os_install_date_str = last_line.split()[0]
                os_install_date = datetime.strptime(os_install_date_str, '%Y-%m-%d')
            except ValueError:
                # Since multiple files are looped through this function, let's only display the error once.
                if value_error_logged is False:
                    logger.warning("There was a fault in parsing the OS installation date from syslog. ", 
                                   "There will be a lot of fools gold (false positives) in the results.")
                    value_error_logged = True
                return None
            except Exception as e:
                print(f"An error occurred while reading syslog: {e}")
                return None

        # Get the passed in file's creation date
        file_creation_time = datetime.fromtimestamp(stat(file_path).st_ctime)

        return file_creation_time > os_install_date

    except Exception as e:
        print(f"An error occurred while checking file creation date: {e}")
        return False

def main():
    """
    Test Case Data using hard coded values,
    change test_data to test areas of functionality.
    """

    """
    DPKG def is_dpkg_file(file_path) testing
    """
    test_data_dpkg = [
        "/usr/bin/nmap",  # True
        "/usr/share/wordlists/rockyou.txt.gz",  # True
        "/usr/share/metasploit-framework/msfconsole",  # True
        "/home/user/somefile.txt",  # False
        "/var/lib/dpkg/info/nonexistent.list",  # False
        "/usr/share/wordlists/rockyou.txt",  # False
        "/etc/ssh/sshd_config"  # False
    ]
    # Run tests and print results
    test_results_dpkg = []
    for path_dpkg in test_data_dpkg:
        # Run function
        result_dpkg = is_dpkg_file(path_dpkg)
        # Create tuple to contain results within list
        test_results_dpkg.append((path_dpkg, result_dpkg))
    # Show results
    print("Test Results for DPKG:")
    for file_path, result in test_results_dpkg:
        print(f"File: {file_path}, Has DPKG Entry?: {result}")

    """
    OS install vs file date comparision testing
    def after_os_installation(file_path):
    """
    test_data_os = [
        "/bin/sudo", # during OS system install
        "/bin/ls", # during OS system install
        "/bin/python3", # after OS system install
        "/home/somefile" #A file that does not exist
    ]
    
    # Run tests and print results
    test_results_os = []
    for path_os in test_data_os:
        # run function
        result_os = after_os_installation(path_os)
        # Create tuple to contain data
        test_results_os.append((path_os, result_os))
    # Show results
    print("Test Results for OS:")
    for file_path, result in test_results_os:
        print(f"File: {file_path}, Created during os install?: {result}")

if __name__ == "__main__":
    main()

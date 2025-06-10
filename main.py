"""
 _____                                ______ _           _           
|_   _|                               |  ___(_)         | |          
  | |_ __ ___  __ _ ___ _   _ _ __ ___| |_   _ _ __   __| | ___ _ __ 
  | | '__/ _ \/ _` / __| | | | '__/ _ \  _| | | '_ \ / _` |/ _ \ '__|
  | | | |  __/ (_| \__ \ |_| | | |  __/ |   | | | | | (_| |  __/ |   
  \_/_|  \___|\__,_|___/\__,_|_|  \___\_|   |_|_| |_|\__,_|\___|_|   

  A security tool for digging up hidden files on most operating systems.
  CTF - Red Team - Forensics - Incident Response

  Created by: Connor Gallagher (TheMythicalGryphon)
  Version: 1.0.0
  License: MIT
  https://mit-license.org/ 
"""

##########TODO###########
# Linux(Y)Win(N) 1. using os module have a program that can simply crawl through a file system with try/except for permission errors
# 2. using the ctypes module simply print to stdout a list of hidden windows files
# 3. find a way to remove system files (maybe by keeping a list of names to iterate through) from the printed output
# (Y) 4. find all linux files that start with a dot(.) at the start that represents a hidden file and print to output as it's own section
# 5. user input for if they want to search all or just under a specific user, change code to accomidate this change.
# 6. do some fun stuff with pretty tables to display files, display file extension through os module
# 7. check to see if dump folder exists within project and if not create it
# 8. copy paste found files into folder (sectioned by user it was found under?)
##########################

import os # For crawling through directories
import pwd # For hidden file metadata on Unix-like systems
import ctypes # For hidden file metadata on Windows

"""
import for custom modules (OOP)
"""
import FoolsGoldForLinux # For running dpkg and stat commands on files

os_name = os.name # 'posix' for Unix-like OS, 'nt' for Windows

def collect_system_data(os_name):
    if os_name == 'posix':
        # Unix-like OS
        print("Digging through data for Unix-like OS...")

        # Set up some counters to track metrics
        hidden_files_count = 0
        not_found_count = 0
        permission_denied_count = 0
        unexpected_error_count = 0
        
        # Start digging through the filesystem
        for root, directoryname, filenames in os.walk('/', topdown=True):
            for file in filenames:
                #We only want to check hidden files (those starting with a dot)
                if file.startswith('.'): 
                    try:
                        stat_info = os.stat(os.path.join(root, file))
                        #Need to know if the file is owned by root (uid = 0) or not (uid > 0)
                        uid = stat_info.st_uid
                    except PermissionError:
                        # Inform the user and press onward.
                        permission_denied_count += 1
                        continue
                    except FileNotFoundError:
                        # Highly unlikely, indicates a fault with the program/filesystem
                        not_found_count += 1
                        continue
                    except Exception as e:
                        unexpected_error_count += 1
                        continue
                    if uid != 0:
                        # If the file is hidden and not owned by root
                        print("Here be treasure!", root, file, uid)
                        hidden_files_count += 1
                    if uid == 0:
                        # Owned by root, we need to handle this differently.
                        # Some files under root may be system files and not user made files under root.
                        # First let's compare the creation date and see if it was after the OS was installed.
                        # Using the final line of stat /var/log/installer/syslog we can get the "birth date" of the filesystem.
                        file_path = os.path.join(root, file)

                        if not FoolsGoldForLinux.after_os_installation(file_path):
                            

                        # If it was created later, let's make sure not to include installed program files via dpkg.
                        # Run dpkg -S on the file to if it is known to the package manager, if not it's more likely a user made file.
                        if not FoolsGoldForLinux.is_dpkg_file(file_path):
                            # If the file is not known to the package manager, it's likely a user made file.
                            print("Here be treasure!", root, file, uid)
                            hidden_files_count += 1
                        
        # Print out the metrics
        print(f"Digging complete, {hidden_files_count} hidden treasures (files) found.")
        if not_found_count != 0:
            print(f"{not_found_count} were expected to be found, but were not.")
            print("Low number may indicate corrupted files", 
                "high number may indicate a corruption with this program or target filesystem.")
        if permission_denied_count != 0:
            print(f"{permission_denied_count} could not be accessed due to protections.")
        if unexpected_error_count != 0:
            print(f"{unexpected_error_count} unexpected errors encountered.")

    elif os_name == 'nt':
        # Windows OS
        print("Digging through data for Windows OS...")
    else:
        raise ValueError("Huh oh, tool doesn't support digging through: {}".format(os_name) + ", sorry about that.")
        input("Press any key to exit...")
        exit(1)

collect_system_data(os_name)

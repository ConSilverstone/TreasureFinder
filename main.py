import os # For crawling through directories
import pwd # For hidden file metadata on Unix-like systems
import ctypes # For hidden file metadata on Windows

osName = os.name # 'posix' for Unix-like OS, 'nt' for Windows

def collect_system_data(osName):
    if osName == 'posix':
        # Unix-like OS
        print("Digging through data for Unix-like OS...")
        
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
                        print(f"Permission denied for {file}")
                        continue
                    except FileNotFoundError:
                        # Highly unlikely, indicates a fault with the program/filesystem
                        print(f"Possible filesystem/program corruption")
                        continue
                    except Exception as e:
                        print(f"An error occurred with {file}: {e}")
                        continue
                    if uid != 0:
                        # If the file is hidden and not owned by root
                        print("Here be treasure!", root, file, uid)

    elif osName == 'nt':
        # Windows OS
        print("Digging through data for Windows OS...")
    else:
        raise ValueError("Huh oh, shovel doesn't support digging through: {}".format(osName) + ", sorry about that.")
        input("Press any key to exit...")
        exit(1)

collect_system_data(osName)
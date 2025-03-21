import ftplib
import tempfile
import logging
import sys
import time
from colorama import Fore, Style, init
from typing import Optional
import os

init(autoreset=True)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def grab_banner(target: str) -> None:
    """Grab the FTP server banner."""
    try:
        with ftplib.FTP(target) as ftp:
            banner = ftp.getwelcome()
            logging.info(f"FTP Banner: {banner}")
    except Exception as e:
        logging.error(f"Failed to grab banner: {e}")
def check_anonymous_login(target: str) -> bool:
    """Check if anonymous login is allowed."""
    try:
        with ftplib.FTP(target) as ftp:
            ftp.login()
            logging.info(f"Anonymous login allowed on {target}")
            return True
    except ftplib.error_perm:
        logging.warning(f"Anonymous login not allowed on {target}")
        return False
    except Exception as e:
        logging.error(f"Error checking anonymous login: {e}")
        return False
def list_ftp_directories(target: str, username: str, password: str) -> None:
    """List all files and directories on the FTP server, including hidden ones."""
    try:
        with ftplib.FTP(target) as ftp:
            ftp.login(user=username, passwd=password)
            logging.info(f"Logged in to {target} as {username}")

            logging.info("Attempting 'LIST -al' to show all files:")
            ftp.retrlines('LIST -al')

    except Exception as e:
        logging.error(f"Failed to list directories: {e}")

def list_ftp_directories_recursive(ftp, path="/", depth=0, visited=None):
    """Recursively list all directories and files on the FTP server, excluding `.` and `..`, and avoiding loops."""
    if visited is None:
        visited = set()  # To track already visited directories to avoid infinite loops

    try:
        # Avoid visiting the same directory twice (prevent infinite loops)
        if path in visited:
            return
        visited.add(path)
        
        # Attempt to change to the target directory
        response = ftp.cwd(path)
        
        # Check if we were able to successfully change into the directory
        if "250" not in response:
            logging.error(f"⚠️ Could not access directory {path}")
            return
        
        # List the contents of the directory using 'ls -al' to include hidden files
        files = []
        ftp.retrlines('LIST -al', files.append)  # Retrieving the file list

        for file in files:
            parts = file.split()
            if len(parts) < 9:
                continue  # Skip malformed entries
            
            file_type = parts[0][0]  # File type: 'd' for directory, '-' for file, 'l' for symlink
            name = parts[-1]  # Extract the file/directory name
            
            indent = "  " * depth  # Indentation for clarity
            if name == "." or name == "..":
                continue  # Skip current and parent directory references
            
            if file_type == 'd':  # Directory
                logging.info(f"{indent}[DIR] {name}")
                new_path = f"{path.rstrip('/')}/{name}"
                
                # Recursively list the contents of this directory
                list_ftp_directories_recursive(ftp, new_path, depth + 1, visited)
            elif file_type == '-':  # Regular file
                logging.info(f"{indent}[FILE] {name}")
            elif file_type == 'l':  # Symbolic link
                logging.info(f"{indent}[LINK] {name} -> {parts[-3]}")  # Display symlink target

        # Navigate back to the parent directory
        ftp.cwd("..")

    except Exception as e:
        logging.error(f"⚠️ Error accessing {path}: {e}")

def check_write_permission(target: str, username: str, password: str) -> None:
    """Check if the FTP server allows file uploads (write permissions)."""
    try:
        with ftplib.FTP(target) as ftp:
            ftp.login(user=username, passwd=password)
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(b"This is a test file for write permissions.")
                temp_file_name = temp_file.name
            with open(temp_file_name, "rb") as f:
                ftp.storbinary(f"STOR {temp_file_name}", f)
            logging.info("Write permissions are allowed!")
            ftp.delete(temp_file_name)
    except Exception as e:
        logging.error(f"No write permissions or failed to test: {e}")
def test_anonymous_upload(target: str) -> None:
    """Test if anonymous users can upload a file specified by the user."""
    try:
        # Ask the user for the file to upload
        file_to_upload = input("Please enter the full path of the file to upload: ").strip()

        # Check if the file exists locally
        if not os.path.exists(file_to_upload):
            logging.error(f"File does not exist: {file_to_upload}")
            return
        
        with ftplib.FTP(target) as ftp:
            ftp.login()  # Login anonymously
            
            # Open the file and upload it
            with open(file_to_upload, "rb") as f:
                # Use the basename to upload the file, so it doesn't include the full path
                ftp.storbinary(f"STOR {os.path.basename(file_to_upload)}", f)
            
            logging.info(f"Successfully uploaded {file_to_upload} as an anonymous user.")
        
    except Exception as e:
        logging.error(f"Anonymous upload failed: {e}")
def download_file(target: str, username: str, password: str, remote_file: str, local_file: str) -> None:
    """Download a specific file from the FTP server."""
    try:
        with ftplib.FTP(target) as ftp:
            ftp.login(user=username, passwd=password)
            with open(local_file, "wb") as f:
                ftp.retrbinary(f"RETR {remote_file}", f.write)
            logging.info(f"Successfully downloaded {remote_file} to {local_file}")
    except Exception as e:
        logging.error(f"Failed to download file {remote_file}: {e}")

def simulate_brute_force(target: str, delay: str, username: str, password_file: str) -> Optional[str]:
    """Attempts to brute force FTP login using a list of passwords from a file."""

    logging.warning(Fore.GREEN + Style.BRIGHT + "Warning: Use this feature only for authorized penetration testing on systems you have permission to test.")
    try:
        # Set a default delay if the input is empty
        delay = int(delay) if delay else 1  # Default delay is 1 second
        with open(password_file, 'r') as file:
            passwords = [line.strip() for line in file]  # Strip whitespace and newlines

        no_of_passwords = len(passwords)
        logging.info(Fore.BLUE + f"Starting brute force attack with {no_of_passwords} passwords.")

        start_time = time.time()
        for attempt, password in enumerate(passwords, start=1):
            password = password.strip()
            logging.debug(f"Trying password: {password}")  # Debug log
            try:
                with ftplib.FTP(target) as ftp:
                    ftp.login(user=username, passwd=password)
                    sys.stdout.write("\n")
                    logging.info(Fore.RED + f"Successful login with password: {Style.BRIGHT}{Fore.RED}{password}{Style.RESET_ALL} | {Fore.BLUE} Total attempts: {attempt} | Elapsed time: {time.time() - start_time:.1f} seconds")
                    return password
            except ftplib.error_perm as e:
                logging.debug(f"Failed login with password: {password} | Error: {e}")  # Debug log
                sys.stdout.write(Fore.BLUE + f"\rCurrent Login attempts: {attempt}..")
                sys.stdout.flush()
            except ftplib.error_temp as e:
                logging.warning(Fore.GREEN + f"Temporary error on attempt: {attempt} | {e}")
            except ftplib.all_errors as e:
                logging.error(Fore.GREEN + f"FTP error on attempt: {attempt} | {e}")

            """ to avoid getting blocked by the server i added a delay between attempts | ratelimiting the attack """
            time.sleep(delay)
    except FileNotFoundError:
        logging.error(Fore.BLUE + f"Password file {password_file} was not found.")
    except Exception as e:
        logging.error(Fore.GREEN + f"Error during brute force attempt: {e}")
    sys.stdout.write("\n")
    logging.error(Fore.GREEN +"Brute force attack failed. No valid password found in the list.")
    return None

if __name__ == "__main__":
    target_ip = input("Enter the FTP server IP: ")

    while True:
        print("\nChoose an option:")
        print("1. Grab FTP Banner")
        print("2. Check Anonymous Login")
        print("3. Test Write Permissions")
        print("4. Test Anonymous File Upload")
        print("5. Download a File")
        print("6. Simulate Brute Force Attack")
        print("7. Recursively List Directories & Files")  # NEW OPTION
        print("\nq. Exit")

        choice = input("Enter your choice (1-7 or q to quit): ").strip().lower()

        if choice == "1":
            grab_banner(target_ip)
        elif choice == "2":
            if check_anonymous_login(target_ip):
                list_ftp_directories(target_ip, "anonymous", "")
        elif choice == "3":
            username = input("Enter username: ")
            password = input("Enter password: ")
            check_write_permission(target_ip, username, password)
        elif choice == "4":
            test_anonymous_upload(target_ip)
        elif choice == "5":
            username = input("Enter username: ")
            password = input("Enter password: ")
            remote_file = input("Enter the path of the remote file (e.g., /config/backup.txt): ")
            local_file = input("Enter the path to save the file locally (e.g., backup.txt): ")
            download_file(target_ip, username, password, remote_file, local_file)
        elif choice == "6":
            username = input("Enter username: ")
            delay = input("Enter the delay between attempts (in seconds): ")
            password_file = input("Enter the path to the password file (e.g., passwords.txt): ")
            simulate_brute_force(target_ip, delay, username, password_file)
        elif choice == "7":  # NEW RECURSIVE DIRECTORY LISTING
            username = input("Enter username: ")
            password = input("Enter password: ")
            try:
                with ftplib.FTP(target_ip) as ftp:
                    ftp.login(user=username, passwd=password)
                    logging.info(f"Logged in to {target_ip} as {username}")
                    list_ftp_directories_recursive(ftp, "/")  # Start from root directory
            except Exception as e:
                logging.error(f"Failed to recursively list directories: {e}")
        elif choice == "q":
            print("Exiting FTP Hunter... Goodbye! 👋")
            break
        else:
            logging.error("Invalid choice. Please enter a valid option.")


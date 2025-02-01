import ftplib
import tempfile
import logging
import sys
import time
import keyboard
import os
from colorama import Fore, Style, init
from typing import Optional

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
    """List directories and files on the FTP server."""
    try:
        with ftplib.FTP(target) as ftp:
            ftp.login(user=username, passwd=password)
            logging.info(f"Logged in to {target} as {username}")
            logging.info("Directory Listing:")
            ftp.retrlines('LIST')
    except Exception as e:
        logging.error(f"Failed to list directories: {e}")
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
    """Test if anonymous users can upload files."""
    try:
        with ftplib.FTP(target) as ftp:
            ftp.login()
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(b"This is a test file uploaded anonymously.")
                temp_file_name = temp_file.name
            with open(temp_file_name, "rb") as f:
                ftp.storbinary(f"STOR {temp_file_name}", f)
            logging.info(f"Successfully uploaded {temp_file_name} as an anonymous user.")
            ftp.delete(temp_file_name)
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

# Helper Function to validate user input for integer values.
def get_valid_integer(prompt, default=None):
            while True:
                try:
                    user_input = input(prompt)
                    if user_input == "" and default is not None:
                        return default
                    return int(user_input)
                except ValueError:
                    print(Fore.BLUE + "Invalid input. Please enter an single digit integer.(e.g., 1, 2..)")

# Helper Function to validate user input for file paths.
def get_valid_file_path(prompt):
    while True:
        file_path = input(prompt)
        if os.path.isfile(file_path):
            return file_path
        else:
            print("Invalid file path. Please enter a valid file path.")

def simulate_brute_force(target: str, delay: str, timeout: str, max_retries: int, username: str, password_file: str) -> Optional[str]:
    """Attempts to brute force FTP login using a list of passwords from a file."""

    logging.warning(Fore.GREEN + Style.BRIGHT + "Warning: Use this feature only for authorized penetration testing on systems you have permission to test.")
    
    paused = False
    total_paused_time = 0
    pause_start_time = 0
    consecutive_errors = 0  
    
# Function to toggle pause/resume the attack.
    def toggle_pause():
        nonlocal paused, pause_start_time, total_paused_time
        paused = not paused
        if paused:
            pause_start_time = time.time()
        else:
            total_paused_time += time.time() - pause_start_time
        sys.stdout.write(Fore.YELLOW + Style.BRIGHT + f"\rBrute Force attack {'PAUSED' if paused else 'RESUMED'}")
        sys.stdout.flush()

    keyboard.add_hotkey('p', toggle_pause)
    try:
        with open(password_file, 'r') as file:
            passwords = [line.strip() for line in file]  # Strip whitespace and newlines

        no_of_passwords = len(passwords)
        logging.info(Fore.BLUE + f"Starting Brute Force attack with {no_of_passwords} passwords. Press 'p' to pause/resume the attack.")

        start_time = time.time()
        for attempt, password in enumerate(passwords, start=1):
            while paused:
                sys.stdout.write(Fore.YELLOW + Style.BRIGHT + f"\rBrute force attack PAUSED")
                sys.stdout.flush()
                time.sleep(0.1)
            password = password.strip()
            try:
               with ftplib.FTP(target, timeout=timeout) as ftp:
                    ftp.login(user=username, passwd=password)
                    sys.stdout.write("\n")
                    elapsed_time = time.time() - start_time - total_paused_time
                    logging.critical(Fore.RED + f"SUCCESSFUL LOGIN with password: {Fore.RED}{Style.BRIGHT}{password}{Style.RESET_ALL} | {Fore.BLUE} Total attempts: {attempt} | Elapsed time: {elapsed_time:.1f} seconds")
                    logging.critical(Fore.RED + Style.BRIGHT + "The Server is VULNERABLE to Brute Force Attack!")
                    return password
            except ftplib.error_perm:
                sys.stdout.write(Fore.BLUE + f"\rFailed Login attempts : {attempt}..") # Trying every password in the list.
                sys.stdout.flush()
            except ftplib.error_temp as e:
                logging.warning(Fore.GREEN + f"Temporary ERROR on attempt: {attempt} | {e}")
                consecutive_errors += 1
            except ftplib.all_errors as e:
                logging.error(Fore.GREEN + f"FTP ERROR on attempt: {attempt} | {e}")
                consecutive_errors += 1
            if consecutive_errors >= max_retries:
                break
            """ to avoid getting blocked by the server i added a delay between attempts | ratelimiting the attack """
            delay_interval = 0.1
            for _ in range(int(delay/delay_interval)):
                if paused:
                    break
                time.sleep(delay_interval)
    except FileNotFoundError:
        logging.error(Fore.BLUE + f"Password file {password_file} was NOT FOUND.")
    except Exception as e:
        logging.error(Fore.GREEN + f"Unexpected ERROR during brute force attempt: {e}")
        sys.stdout.write("\n")
    finally:
        keyboard.unhook_all()
    logging.error(Fore.GREEN + f"Brute force attack FAILED {'Due to Consecutive Errors.' if consecutive_errors>=max_retries  else 'No valid password found in the list.'}") # Final Statement.
    return None

if __name__ == "__main__":
    target_ip = input("Enter the FTP server IP: ")
    print("\nChoose an option:")
    print("1. Grab FTP Banner")
    print("2. Check Anonymous Login")
    print("3. Test Write Permissions")
    print("4. Test Anonymous File Upload")
    print("5. Download a File")
    print("6. Simulate Brute Force Attack")
    print("\nq. Exit")
    choice = input("\nEnter your choice (1-6): ")

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
        password_file = get_valid_file_path("Enter the path to the password file (e.g., passwords.txt): ")
        
        print(Fore.BLUE+ "\nEnter the following values to Begin or Hit ENTER to use the default values.")
        # Default values ...
        default_delay = 1
        default_timeout = 10
        default_max_retries = 10
        delay = get_valid_integer("Enter the delay between attempts (in seconds) : ", default_delay)
        timeout = get_valid_integer("Enter the timeout for the FTP connection (in seconds): ", default_timeout)
        max_retries = get_valid_integer("Enter the maximum number of consecutive errors before exiting: ", default_max_retries)
        simulate_brute_force(target_ip, delay, timeout, max_retries, username, password_file)
    elif choice == "q":
        sys.exit()
    else:
        logging.error("Invalid choice. Exiting.")
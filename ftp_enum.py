import ftplib
import tempfile
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

if __name__ == "__main__":
    target_ip = input("Enter the FTP server IP: ")
    print("\nChoose an option:")
    print("1. Grab FTP Banner")
    print("2. Check Anonymous Login")
    print("4. Test Write Permissions")
    print("5. Test Anonymous File Upload")
    print("6. Download a File")
    choice = input("Enter your choice (1-6): ")

    if choice == "1":
        grab_banner(target_ip)
    elif choice == "2":
        if check_anonymous_login(target_ip):
            list_ftp_directories(target_ip, "anonymous", "")
    elif choice == "4":
        username = input("Enter username: ")
        password = input("Enter password: ")
        check_write_permission(target_ip, username, password)
    elif choice == "5":
        test_anonymous_upload(target_ip)
    elif choice == "6":
        username = input("Enter username: ")
        password = input("Enter password: ")
        remote_file = input("Enter the path of the remote file (e.g., /config/backup.txt): ")
        local_file = input("Enter the path to save the file locally (e.g., backup.txt): ")
        download_file(target_ip, username, password, remote_file, local_file)
    else:
        logging.error("Invalid choice. Exiting.")
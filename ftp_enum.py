import ftplib

def grab_banner(target):
    """Grab the FTP server banner."""
    try:
        ftp = ftplib.FTP(target)
        banner = ftp.getwelcome()  # Fetch the banner message
        print(f"[+] FTP Banner: {banner}")
        ftp.quit()
    except Exception as e:
        print(f"[-] Failed to grab banner: {e}")

def check_anonymous_login(target):
    """Check if anonymous login is allowed."""
    try:
        ftp = ftplib.FTP(target)
        ftp.login()  # Attempt to log in with anonymous credentials
        print(f"[+] Anonymous login allowed on {target}")
        ftp.quit()
        return True
    except ftplib.error_perm:
        print(f"[-] Anonymous login not allowed on {target}")
        return False

def list_ftp_directories(target, username, password):
    """List directories and files on the FTP server."""
    try:
        ftp = ftplib.FTP(target)
        ftp.login(user=username, passwd=password)
        print(f"[+] Logged in to {target} as {username}")
        print("[+] Directory Listing:")
        ftp.retrlines('LIST')  # List directories and files
        ftp.quit()
    except Exception as e:
        print(f"[-] Failed to list directories: {e}")

def check_write_permission(target, username, password):
    """Check if the FTP server allows file uploads (write permissions)."""
    try:
        ftp = ftplib.FTP(target)
        ftp.login(user=username, passwd=password)
        test_file = "test_write.txt"
        with open(test_file, "w") as f:
            f.write("This is a test file for write permissions.")
        with open(test_file, "rb") as f:
            ftp.storbinary(f"STOR {test_file}", f)
        print("[+] Write permissions are allowed!")
        ftp.delete(test_file)  # Clean up
        ftp.quit()
    except Exception as e:
        print(f"[-] No write permissions or failed to test: {e}")

def test_anonymous_upload(target):
    """Test if anonymous users can upload files."""
    try:
        ftp = ftplib.FTP(target)
        ftp.login()
        test_file = "anonymous_test.txt"
        with open(test_file, "w") as f:
            f.write("This is a test file uploaded anonymously.")
        with open(test_file, "rb") as f:
            ftp.storbinary(f"STOR {test_file}", f)
        print(f"[+] Successfully uploaded {test_file} as an anonymous user.")
        ftp.delete(test_file)  # Clean up
        ftp.quit()
    except Exception as e:
        print(f"[-] Anonymous upload failed: {e}")

def download_file(target, username, password, remote_file, local_file):
    """Download a specific file from the FTP server."""
    try:
        ftp = ftplib.FTP(target)
        ftp.login(user=username, passwd=password)
        with open(local_file, "wb") as f:
            ftp.retrbinary(f"RETR {remote_file}", f.write)
        print(f"[+] Successfully downloaded {remote_file} to {local_file}")
        ftp.quit()
    except Exception as e:
        print(f"[-] Failed to download file {remote_file}: {e}")

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
        print("[-] Invalid choice. Exiting.")

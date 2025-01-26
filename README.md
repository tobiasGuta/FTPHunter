# FTPHunter
FTPHunter is a powerful and efficient tool designed for FTP server enumeration and vulnerability assessment. It allows security professionals and penetration testers to quickly discover key information about FTP servers, such as anonymous login capabilities, file access permissions, server banners, and more.

## Installation

``` bash
git clone https://github.com/tobiasGuta/FTPHunter.git
```

```bash
cd FTPHunter
```

```bash
python3 ftp_enum.py
```

## Output

```bash
$ python3 ftp_enum.py
Enter the FTP server IP: <IP-ADDRESS>

Choose an option:
1. Grab FTP Banner
2. Check Anonymous Login
3. Test Write Permissions
4. Test Anonymous File Upload
5. Download a File
Enter your choice (1-6):
```

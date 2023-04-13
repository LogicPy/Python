import requests

# List of common Admin Login directories
Admin_Login_directories = [
    "/admin/",
    "/cgi-bin/",
    "/config/",
    "/database/",
    "/db/",
    "/includes/",
    "/phpMyAdmin/",
    "/webadmin/",
    "/wp-admin/",
    "/user/login",
    "/admin/index.php",
    "/admincp/",
    "/administrator/",
    "/wiki/Special:UserLogin",
    "/admin123/",
    "/typo3/",
    "/admin.php",
    "/system/index.php",
    "/manage",
    "/login/index.php",
    "/index.php/login",
    "/web/guest/home",
    "/Security/login",
]

# Replace this with the target website URL
target_url = input("Enter your host address (http://example.com): " ) 

# Check if the vulnerable directories exist
def check_vulnerable_directories(url, directories):
    found_directories = []

    for directory in directories:
        try:
            response = requests.get(url + directory)
            if response.status_code == 200:
                found_directories.append(directory)
        except requests.exceptions.RequestException as e:
            print(f"Error checking {url + directory}: {e}")

    return found_directories

found = check_vulnerable_directories(target_url, Admin_Login_directories)

if found:
    print("Found potentially Admin Login directories:")
    for directory in found:
        print(target_url + directory)
else:
    print("No potentially Admin Login directories found.")

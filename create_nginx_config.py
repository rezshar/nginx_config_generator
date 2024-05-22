#WrittenbyRezshar
import os
import subprocess

# Check if Nginx is installed
try:
    subprocess.run(["nginx", "-v"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except subprocess.CalledProcessError:
    # Nginx is not installed, try to install it
    print("Nginx is not installed. Attempting to install...")
    try:
        subprocess.run(["apt", "install", "nginx", "-y"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Nginx has been installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to install Nginx. Error code: {e.returncode}")
        print("Please ensure you have the necessary permissions and try again.")
        exit(1)

# Check if the 'include /etc/nginx/conf.d/*.conf;' line exists in nginx.conf
nginx_conf_file = "/etc/nginx/nginx.conf"
include_conf_d_line = "include /etc/nginx/conf.d/*.conf;"

with open(nginx_conf_file, "r") as f:
    nginx_conf_content = f.read()

if include_conf_d_line not in nginx_conf_content:
    print("The 'include /etc/nginx/conf.d/*.conf;' line is missing in nginx.conf.")
    print("Adding the line and reloading Nginx configuration...")

    # Add the line to nginx.conf
    with open(nginx_conf_file, "a") as f:
        f.write("\n" + include_conf_d_line)

    # Reload Nginx configuration
    try:
        subprocess.run(["nginx", "-s", "reload"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Nginx configuration reloaded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to reload Nginx configuration. Error code: {e.returncode}")
        exit(1)

# Prompt the user to enter the domain name
domain_name = input("Enter the domain name: ")

# Prompt the user for the website root directory
website_root = input("Enter the website root directory (e.g., /var/www/html): ")

# Prompt the user to add a special header
add_special_header = input("Do you want to add a special header? (y/n) ").lower()

# Prompt the user for redirection
use_redirection = input("Do you want to set up a redirection? (y/n) ").lower()

# Build the Nginx configuration content
config_content = f"""
server {{
    listen 80;
    server_name {domain_name};

    access_log /var/log/nginx/{domain_name}_access.log combined;
    error_log /var/log/nginx/{domain_name}_error.log;

    root {website_root};
    index index.html;
"""

if add_special_header == "y":
    special_header_name = input("Enter the name of the special header: ")
    special_header_value = input("Enter the value of the special header: ")
    config_content += f"    add_header {special_header_name} '{special_header_value}';\n"

config_content += """
    location / {
        try_files $uri $uri/ =404;
    }
"""

if use_redirection == "y":
    redirection_type = input("Enter the redirection type (301 or 302): ")
    redirection_url = input("Enter the redirection URL: ")
    config_content += f"""
    return {redirection_type} {redirection_url};
"""

config_content += """
}
"""

# Create the Nginx configuration file
config_file = f"/etc/nginx/conf.d/{domain_name}.conf"

# Check if the configuration file already exists
if os.path.isfile(config_file):
    print(f"Error: The configuration file for {domain_name} already exists.")
    exit(1)

# Write the Nginx configuration to the file
try:
    with open(config_file, "w") as f:
        f.write(config_content)
    print(f"Nginx configuration file for {domain_name} has been created successfully.")
except IOError:
    print(f"Error: Failed to create the configuration file for {domain_name}.")
    exit(1)

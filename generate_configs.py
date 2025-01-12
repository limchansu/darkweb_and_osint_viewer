import os

def create_alarm_config():
    print('Setting up notification features')
    discord_token = input('Discord token: ')
    darkweb_channel_id = int(input('Channel ID for dark web: '))
    osint_channel_id = int(input('Channel ID for OSINT: '))
    print()
    print('Gmail accounts only')
    email_sender = input('Email: ')
    email_password = input('APP Password: ')
    print('\n')

    return f"""DISCORDTOKEN = '{discord_token}' # Discord token
DARKWEB_CHANNEL_ID = {darkweb_channel_id}  # Dark web channel ID
OSINT_CHANNEL_ID = {osint_channel_id} # OSINT channel ID

# Gmail accounts only
EMAIL_SENDER = '{email_sender}' # Gmail email address
EMAIL_PASSWORD = '{email_password}' # Gmail password
"""

def create_dw_crawler_config():
    print('Setting up dark web crawler')
    print('\n')
    return """# TOR_PROXY = "socks5://tor:9050" # For Docker
TOR_PROXYh = "socks5h://tor:9050" # For Docker
# TOR_PROXY = "socks5://127.0.0.1:9050" # For local setup
# TOR_PROXYh = "socks5h://127.0.0.1:9050" # For local setup
"""

def create_osint_crawler_config():
    print('Setting up OSINT crawler')
    github_token = input('GitHub token: ')
    print('\n')
    return f"""TOR_PROXY = "socks5://tor:9050" # For Docker
TOR_PROXYh = "socks5h://tor:9050" # For Docker
# TOR_PROXY = "socks5://127.0.0.1:9050" # For local setup
# TOR_PROXYh = "socks5h://127.0.0.1:9050" # For local setup

GITHUB_TOKEN = '{github_token}' # GitHub token
"""

def create_crawler_config():
    print('Specify the daily execution time')
    schedule_time = input('Time (e.g., 13:00): ')
    print('\n')
    return f"""SCHEDULE_TIME = '{schedule_time}'"""

def create_config_file(directory, content_function):
    config_path = os.path.join(directory, "config.py")

    if os.path.exists(config_path):
        os.remove(config_path)

    with open(config_path, "w") as config_file:
        config_file.write(content_function())

def main():
    project_root = os.path.dirname(os.path.abspath(__file__))

    directories = {
        "alarm": create_alarm_config,
        # "dw_crawler": create_dw_crawler_config,
        "osint_crawler": create_osint_crawler_config,
        "": create_crawler_config,
    }

    for directory, content_function in directories.items():
        full_path = os.path.join(project_root, 'crawling/app', directory)
        if os.path.exists(full_path):
            create_config_file(full_path, content_function)
        else:
            print(f"[WARNING] Directory not found: {full_path}")

if __name__ == "__main__":
    main()

import os



def create_alarm_config():
    print('알림 기능 설정')
    discord_token = input('디스코드 토큰: ')
    darkweb_channel_id = int(input('다크웹으로 사용할 채널ID: '))
    osint_channel_id = int(input('OSINT으로 사용할 채널ID: '))
    print()
    print('지메일만 계정만 가능')
    email_sender = input('이메일: ')
    email_password = input('비밀번호: ')
    print('\n')

    return f"""DISCORDTOKEN = '{discord_token}' # 디스코드 토큰
DARKWEB_CHANNEL_ID = {darkweb_channel_id}  # 다크웹 채널 아이디
OSINT_CHANNEL_ID = {osint_channel_id} # 오신트 채널 아이디

# 지메일만 가능
EMAIL_SENDER = '{email_sender}' # 자매일 이메일
EMAIL_PASSWORD = '{email_password}' # 지메일 패스워드
"""


def create_dw_crawler_config():
    print('다크웹 크롤러 설정')
    print('\n')
    return """# TOR_PROXY = "socks5://tor:9050" # 도커 사용시
TOR_PROXYh = "socks5h://tor:9050" # 도커 사용시
# TOR_PROXY = "socks5://127.0.0.1:9050" # 로컬
# TOR_PROXYh = "socks5h://127.0.0.1:9050" # 로컬
"""


def create_osint_crawler_config():
    print('OSINT 크롤러 설정')
    github_token = input('깃허브 토큰: ')
    print('\n')
    return f"""TOR_PROXY = "socks5://tor:9050" # 도커 사용시
TOR_PROXYh = "socks5h://tor:9050" # 도커 사용시
# TOR_PROXY = "socks5://127.0.0.1:9050" # 로컬
# TOR_PROXYh = "socks5h://127.0.0.1:9050" # 로컬

GITHUB_TOKEN = '{github_token}' # 깃허브 토큰
"""

def create_crawler_config():
    print('매일 실행할 시간 지정')
    schedule_time = input('시간 (예시 13:00):')
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

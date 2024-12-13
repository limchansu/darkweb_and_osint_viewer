from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time




# Chrome 옵션 설정
options = Options()
options.add_argument("--headless")  # 브라우저 창 표시 없이 실행
options.add_argument("--disable-blink-features=AutomationControlled")  # Selenium 탐지 방지
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--proxy-server=socks5://127.0.0.1:9050")  # Tor 프록시 설정

# "headless"에서 자동화된 속성 비활성화
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

# WebDriver 실행

driver = webdriver.Chrome(options=options)

# Selenium 자동화 탐지 방지 스크립트 실행
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
    """
})

# URL 요청
url = "http://breached26tezcofqla4adzyn22notfqwcac7gpbrleg4usehljwkgqd.onion/"
driver.get(url)

time.sleep(10)

# 페이지 HTML 가져오기
html_content = driver.page_source
print(html_content)

# WebDriver 종료
driver.quit()

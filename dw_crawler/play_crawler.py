import asyncio
import aiohttp
from aiohttp import ClientTimeout
from aiohttp_socks import ProxyConnector
from bs4 import BeautifulSoup
from datetime import datetime


async def fetch_page(session, url):
    try:
        async with session.get(url, timeout=ClientTimeout(total=60)) as response:
            return await response.text()
    except Exception as e:
        print(f"[ERROR] 페이지 요청 실패 ({url}): {e}")
        return None


async def play(db):
    collection = db["play"]
    url = "http://k7kg3jqxang3wh7hnmaiokchk7qoebupfgoik6rha6mjpzwupwtj25yd.onion/"

    proxy = "socks5://127.0.0.1:9050"  # Tor SOCKS5 프록시 설정
    connector = ProxyConnector.from_url(proxy)

    async with aiohttp.ClientSession(connector=connector) as session:
        try:
            print(f"[INFO] 페이지 접근: {url}")
            html = await fetch_page(session, url)
            if not html:
                print("[ERROR] 첫 페이지 접근 실패.")
                return

            soup = BeautifulSoup(html, "html.parser")
            pages = soup.find_all("span", class_="Page")
            total_pages = int(pages[-1].text) if pages else 1
            print(f"[INFO] 총 페이지 수: {total_pages}")

            for page_num in range(1, total_pages + 1):
                page_url = f"{url}index.php?page={page_num}"
                print(f"[INFO] 페이지 요청: {page_url}")

                page_html = await fetch_page(session, page_url)
                if not page_html:
                    continue

                soup = BeautifulSoup(page_html, "html.parser")
                items = soup.find_all("th", class_="News")

                for item in items:
                    try:
                        onclick_content = item["onclick"]
                        post_id = onclick_content.split("'")[1]
                        post_url = f"{url}topic.php?id={post_id}"

                        post_html = await fetch_page(session, post_url)
                        if not post_html:
                            continue

                        result = {
                            "title": "",
                            "update_date": "",
                            "content": "",
                            "links": [],
                            "rar_password": "",
                            "crawled_time": str(datetime.now())
                        }

                        soup = BeautifulSoup(post_html, "html.parser")
                        info = soup.find("th")

                        temp = info.find("div").text.split("\xa0")
                        result["title"] = temp[0]

                        info_text = info.find("div").text
                        start = info_text.find("added: ")
                        end = info_text.find("publication date: ")
                        result["update_date"] = info_text[start + len("added: "): end].strip() if start != -1 and end != -1 else ""

                        start = info_text.find("information: ")
                        end = info_text.find("DOWNLOAD LINKS: ")
                        result["content"] = info_text[start + len("information: "): end].strip() if start != -1 and end != -1 else ""

                        start = info_text.find("DOWNLOAD LINKS: ") + len("DOWNLOAD LINKS: ")
                        password_index = info_text.find("Rar password: ")
                        end = password_index if password_index != -1 else len(info_text)
                        if start != -1 and end != -1:
                            links = info_text[start:end].split("http")
                            for link in links:
                                if len(link.strip()) > 0:
                                    result["links"].append(f"http{link.strip()}")

                        result["rar_password"] = info_text[password_index + len("Rar password: "):].strip() if password_index != -1 else ""

                        if not await collection.find_one({"title": result["title"]}):
                            await collection.insert_one(result)
                            print(f"Saved: {result['title']}")
                        else:
                            print(f"Skipped (duplicate): {result['title']}")

                    except Exception as e:
                        print(f"[ERROR] 데이터 처리 중 오류 발생: {e}")

        except Exception as e:
            print(f"[ERROR] 크롤링 중 오류 발생: {e}")




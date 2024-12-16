import os
from pymongo import MongoClient
from dw_crawler.htdark_crawler import scrape_htdark_posts
from dw_crawler.darknetARMY_crawler import scrape_darknetarmy_posts
from dw_crawler.ctifeeds_crawler import run as run_ctifeeds
from email_alarm import watch_collection

# MongoDB 연결 설정
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "darkweb"

# 크롤러 실행 및 데이터 적재 함수
def setup_and_run_crawlers():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    # htdark 크롤러 실행
    print("[INFO] htdark 크롤러 실행 시작")
    scrape_htdark_posts(db, pages=10)
    print("[INFO] htdark 크롤러 실행 완료")

    # darknetARMY 크롤러 실행
    print("[INFO] darknetARMY 크롤러 실행 시작")
    scrape_darknetarmy_posts(db, pages=3)
    print("[INFO] darknetARMY 크롤러 실행 완료")

    # ctifeeds 크롤러 실행
    print("[INFO] ctifeeds 크롤러 실행 시작")
    run_ctifeeds(db)
    print("[INFO] ctifeeds 크롤러 실행 완료")

# main 함수
if __name__ == "__main__":
    # 크롤러 실행 및 데이터 업데이트
    setup_and_run_crawlers()

    # MongoDB 컬렉션 변경 사항 감지 및 이메일 알림
    watch_collection(MONGO_URI, DB_NAME, "htdark")        # htdark 컬렉션 모니터링
    watch_collection(MONGO_URI, DB_NAME, "darknetARMY")   # darknetARMY 컬렉션 모니터링
    watch_collection(MONGO_URI, DB_NAME, "ctifeeds")      # ctifeeds 컬렉션 모니터링

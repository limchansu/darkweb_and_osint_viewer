from pymongo import MongoClient
from datetime import datetime
from dw_crawler.htdark_crawler import scrape_htdark_posts
from dw_crawler.darknetARMY_crawler import scrape_darknetarmy_posts
from dw_crawler.ctifeeds_crawler import run as run_ctifeeds
from dw_crawler.blacksuit_crawler import run as run_blacksuit
from dw_crawler.blackbasta_crawler import run as run_blackbasta
from dw_crawler.daixin_crawler import run as run_daixin
from dw_crawler.darkleak_crawler import run as run_darkleak
from dw_crawler.everest_crawler import run as run_everest
from dw_crawler.island_crawler import run as run_island
from dw_crawler.abyss_crawler import run as run_abyss



def setup_database():
    """
    MongoDB 데이터베이스 및 컬렉션 생성
    """
    print("[INFO] MongoDB 설정 시작")
    client = MongoClient("mongodb://localhost:27017/")  # MongoDB 연결
    db = client["darkweb"]  # 데이터베이스 이름

    # 컬렉션 목록
    collections = ["abyss", "blackbasta", "blacksuit", "breachdetector", "ctifeeds",
                   "daixin", "darkleak", "darknetARMY", "everest", "island",
                   "leakbase", "lockbit", "play", "rhysida", "htdark"]

    # 컬렉션 생성
    for collection in collections:
        if collection not in db.list_collection_names():
            db.create_collection(collection)
            print(f"[INFO] {collection} 컬렉션 생성 완료!")

    print("[INFO] MongoDB 설정 완료")
    return db

if __name__ == "__main__":
    # 데이터베이스 및 컬렉션 초기화
    db = setup_database()


    scrape_htdark_posts(db, pages=10)
    scrape_darknetarmy_posts(db, pages=3)
    run_blacksuit(db)
    run_blackbasta(db)    
    run_ctifeeds(db)
    run_daixin(db)
    run_darkleak(db)
    run_everest(db)
    run_island(db)
    run_abyss(db)


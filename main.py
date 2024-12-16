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

def setup_database(db_name, collection_names):
    """
    MongoDB 데이터베이스 및 컬렉션 생성
    """
    print(f"[INFO] MongoDB 설정 시작: {db_name}")
    client = MongoClient("mongodb://localhost:27017/")  # MongoDB 연결
    db = client[db_name]  # 데이터베이스 이름

    # 컬렉션 생성
    for collection in collection_names:
        if collection not in db.list_collection_names():
            db.create_collection(collection)
            print(f"[INFO] {collection} 컬렉션 생성 완료! ({db_name})")

    print(f"[INFO] MongoDB 설정 완료: {db_name}")
    return db

if __name__ == "__main__":
    db1_collections = ["abyss", "blackbasta", "blacksuit", "breachdetector", "ctifeeds",
                       "daixin", "darkleak", "darknetARMY", "everest", "island",
                       "leakbase", "lockbit", "play", "rhysida", "htdark"]
    db1 = setup_database("darkweb", db1_collections)

    # 첫 번째 DB에서 크롤러 실행
    scrape_htdark_posts(db1, pages=10)
    scrape_darknetarmy_posts(db1, pages=3)
    run_blacksuit(db1)
    run_blackbasta(db1)
    run_ctifeeds(db1)
    run_daixin(db1)
    run_darkleak(db1)
    run_everest(db1)
    run_island(db1)
    run_abyss(db1)


    db2_collections = ["github", "tuts4you", "0x00org"]
    db2 = setup_database("osint", db2_collections)


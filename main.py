from pymongo import MongoClient
from datetime import datetime
from dw_crawler.darknetARMY_crawler import scrape_darknetarmy_posts
from dw_crawler.ctifeeds_crawler import run as run_ctifeeds
from dw_crawler.blacksuit_crawler import run as run_blacksuit
from dw_crawler.blackbasta_crawler import run as run_blackbasta
from dw_crawler.daixin_crawler import run as run_daixin
from dw_crawler.darkleak_crawler import run as run_darkleak
from dw_crawler.abyss_crawler import run as run_abyss
from osint_crawler.tuts4you_crawler import run as run_tuts4you
# from osint_crawler.github_crawler import run as run_github
from osint_crawler.x00org_crawler import run as run_0x00org


def setup_database(db_name, collection_names):
    """
    MongoDB 데이터베이스 및 컬렉션 생성
    """
    print(f"[INFO] MongoDB 설정 시작: {db_name}")
    client = MongoClient("mongodb://mongo1:30001,mongo2:30002,mongo:30003/?replicaSet=my-rs")  # MongoDB 연결
    db = client[db_name]  # 데이터베이스 이름

    # 컬렉션 생성
    for collection in collection_names:
        if collection not in db.list_collection_names():
            db.create_collection(collection)
            print(f"[INFO] {collection} 컬렉션 생성 완료! ({db_name})")

    print(f"[INFO] MongoDB 설정 완료: {db_name}")
    return db

def run_crawling():
    db1_collections = ["abyss", "blackbasta", "blacksuit", "breachdetector", "ctifeeds",
                       "daixin", "darkleak", "darknetARMY", "everest", "island",
                       "leakbase", "lockbit", "play", "rhysida", "htdark"]
    db1 = setup_database("darkweb", db1_collections)
    db2_collections = ["github", "tuts4you", "0x00org"]
    db2 = setup_database("osint", db2_collections)

    # 첫 번째 DB에서 크롤러 실행
    # scrape_htdark_posts(db1, pages=10)
    scrape_darknetarmy_posts(db1, pages=3)
    run_blacksuit(db1)
    run_blackbasta(db1)
    run_ctifeeds(db1)
    run_daixin(db1)
    run_darkleak(db1)
    run_abyss(db1)

    
    run_tuts4you(db2)
    # run_github(db2)
    run_0x00org(db2)



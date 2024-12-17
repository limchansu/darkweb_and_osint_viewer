from pymongo import MongoClient
from datetime import datetime
# from dw_crawler.darknetARMY_crawler import scrape_darknetarmy_posts
# from dw_crawler.ctifeeds_crawler import run as run_ctifeeds
# from dw_crawler.blacksuit_crawler import run as run_blacksuit
# from dw_crawler.blackbasta_crawler import run as run_blackbasta
# from dw_crawler.daixin_crawler import run as run_daixin
# from dw_crawler.darkleak_crawler import run as run_darkleak
# from dw_crawler.everest_crawler import run as run_everest
# from dw_crawler.island_crawler import run as run_island
# from dw_crawler.abyss_crawler import run as run_abyss
# from dw_crawler.lockbit_crawler import run as run_lockbit
# from dw_crawler.rhysida_crawler import run as run_rhysida
# from dw_crawler.play_crawler import run as run_play
# from dw_crawler.leakbase_crawler import run as run_leakbase

from osint_crawler.tuts4you_crawling import run as run_tuts4you
from osint_crawler.github_crawling import run as run_github

import asyncio


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


def run_crawling():
    dw_collections = ["abyss", "blackbasta", "blacksuit", "breachdetector", "ctifeeds",
                        "daixin", "darkleak", "darknetARMY", "everest", "island",
                        "leakbase", "lockbit", "play", "rhysida", "htdark"]
    dw_db = setup_database("darkweb", dw_collections)

    osint_collections = ["github", "tuts4you", "0x00org"]
    osint_db = setup_database("osint", osint_collections)

    # # 첫 번째 DB에서 크롤러 실행
    # scrape_darknetarmy_posts(db1, pages=3)
    # run_blacksuit(db1)
    # run_blackbasta(db1)
    # run_ctifeeds(db1)
    # run_daixin(db1)
    # run_darkleak(db1)
    # run_everest(db1)
    # run_island(db1)
    # run_abyss(db1)
    # run_rhysida(db1)
    # run_play(db1)
    # run_lockbit(db1)
    # run_leakbase(db1)

    asyncio.run(run_tuts4you(osint_db))
    asyncio.run(run_github(osint_db))



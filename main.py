import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dw_crawler.abyss_crawler import abyss
from dw_crawler.blackbasta_crawler import blackbasta
from dw_crawler.blacksuit_crawler import blacksuit
from dw_crawler.ctifeeds_crawler import ctifeeds
from dw_crawler.daixin_crawler import daixin
from dw_crawler.darkleak_crawler import darkleak
from dw_crawler.darknetARMY_crawler import darknetARMY
from dw_crawler.htdark_crawler import htdark
from dw_crawler.island_crawler import island
from dw_crawler.leakbase_crawler import leakbase
from dw_crawler.lockbit_crawler import lockbit
from dw_crawler.play_crawler import play
from dw_crawler.rhysida_crawler import rhysida
from osint_crawler.github_crawler import github
from osint_crawler.tuts4you_crawler import tuts4you
from osint_crawler.x00org_crawler import x00org


async def setup_database(db_name, collection_names):

    client = AsyncIOMotorClient("mongodb://mongo1:30001,mongo2:30002,mongo:30003/?replicaSet=my-rs")
    db = client[db_name]

    existing_collections = await db.list_collection_names()
    for collection in collection_names:
        if collection not in existing_collections:
            await db.create_collection(collection)

    return db

async def exec_crawler():
    darkweb_collection_name = ['abyss','blackbasta','ctifeeds','daixin','darknetARMY', 'htdark', 'island', 'leakbase', 'lockbit', 'play', 'rhysida']
    darkweb_db = await setup_database('darkweb', darkweb_collection_name)
    osint_collection_name = ['github', 'tuts4you', 'x00org']
    osint_db = await setup_database('osint', osint_collection_name)

    await asyncio.gather(
        # abyss(darkweb_db, True),
        # blackbasta(darkweb_db, True),
        # blacksuit(darkweb_db, True),
        # ctifeeds(darkweb_db, True),
        # daixin(darkweb_db, True),
        # darkleak(darkweb_db, True),
        # darknetARMY(darkweb_db, True),
        htdark(darkweb_db, True),
        # island(darkweb_db, True),
        # leakbase(darkweb_db, True),
        lockbit(darkweb_db, True),
        # play(darkweb_db, True),
        # rhysida(darkweb_db, True),
        # github(osint_db, True),
        # tuts4you(osint_db, True),
        # x00org(osint_db, True)
    )

asyncio.run(exec_crawler())
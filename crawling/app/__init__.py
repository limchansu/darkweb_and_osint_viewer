import time
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import asyncio
import multiprocessing
import os
import time
import sys

# Flask 앱 초기화
app = Flask(__name__)
CORS(app)

from crawler import setup_database, exec_crawler, run_crawler_periodically

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
async def search():
    # 데이터베이스 생성 및 연결
    dw_collections = ["abyss", "blackbasta", "blacksuit", "breachdetector", "ctifeeds",
                      "daixin", "darkleak", "darknetARMY", "everest", "island",
                      "leakbase", "lockbit", "play", "rhysida", "htdark"]
    osint_collections = ["github", "tuts4you", "x00org"]

    dw_db, osint_db = await asyncio.gather(
        setup_database("darkweb", dw_collections),
        setup_database("osint", osint_collections)
    )

    # 요청 파라미터
    data = request.get_json()
    keywords = data.get('keywords', '').strip()
    category = data.get('category', '')
    option = data.get('option', '')

    # 초기화
    results = []

    if category == "all" and option == "all":
        # 두 카테고리의 모든 컬렉션을 순회
        for collection_name in dw_collections + osint_collections:
            db_collection = dw_db[collection_name] if collection_name in dw_collections else osint_db[collection_name]

            # 필터 조건 설정
            filter_query = {}
            if keywords:
                filter_query = {"title": {"$regex": keywords, "$options": "i"}}

            # MongoDB 쿼리 실행
            cursor = db_collection.find(filter_query).sort("_id", -1)  # _id 기준으로 내림차순 정렬 (최신순)

            # 비동기로 결과 순회
            async for doc in cursor:
                result = {key: (str(value) if key == "_id" else value) for key, value in doc.items()}
                results.append(result)


    else:
        # 카테고리 및 옵션에 따라 컬렉션 선택
        if category == "osint":
            if option not in osint_collections:
                return jsonify({"error": f"Invalid collection '{option}' in osint"}), 400
            db_collection = osint_db[option]
        elif category == "darkweb":
            if option not in dw_collections:
                return jsonify({"error": f"Invalid collection '{option}' in darkweb"}), 400
            db_collection = dw_db[option]
        else:
            return jsonify({"error": "Invalid category or option"}), 400

        # 검색 필터
        if keywords:
            search_filter = {"title": {"$regex": keywords, "$options": "i"}}
            cursor = db_collection.find(search_filter).sort("_id", -1)
        else:
            cursor = db_collection.find().sort("_id", -1)

        async for doc in cursor:
            result = {key: (str(value) if key == "_id" else value) for key, value in doc.items()}
            results.append(result)

    return jsonify({"results": results})


def run_flask():
    """
    Flask 서버를 실행
    """
    print("[START] Flask 웹 서버를 실행합니다...")
    app.run(debug=True, use_reloader=False, threaded=True, host="0.0.0.0")


def run_crawler():
    """
    크롤러 작업을 실행
    """
    print("[INFO] 크롤러 작업을 실행합니다...")
    asyncio.run(run_crawler_periodically())


def run_email_alarm():
    """
    email_alarm.py를 실행하는 함수
    """
    print("[INFO] email_alarm.py를 실행합니다...")
    # os.system("python app/alarm/email_alarm.py") # 로컬
    os.system("python /app/crawling/app/alarm/email_alarm.py") # 도커


def run_discord_alarm():
    """
    discord_alarm.py를 실행하는 함수
    """
    print("[INFO] discord_alarm.py를 실행합니다...")
    # os.system("python app/alarm/discord_alarm.py") # 로컬
    os.system("python /app/crawling/app/alarm/discord_alarm.py") # 도커


if __name__ == "__main__":
    time.sleep(25)
    try:
        # discord_alarm.py 작업을 별도의 프로세스로 실행
        discord_alarm_process = multiprocessing.Process(target=run_discord_alarm, daemon=True)
        discord_alarm_process.start()
        time.sleep(5)

        # email_alarm.py 작업을 별도의 프로세스로 실행
        email_alarm_process = multiprocessing.Process(target=run_email_alarm, daemon=True)
        email_alarm_process.start()


        # 크롤러 작업을 별도의 프로세스로 실행
        crawler_process = multiprocessing.Process(target=run_crawler, daemon=True)
        crawler_process.start()

        # 메인 프로세스에서 Flask 서버 실행
        run_flask()

        # 모든 프로세스 종료 관리
        crawler_process.join()
        email_alarm_process.join()
        discord_alarm_process.join()
    except KeyboardInterrupt:
        print("\n[EXIT] 프로그램을 종료합니다.")
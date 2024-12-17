from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import asyncio
import threading
import sys, os

# Flask 앱 초기화
app = Flask(__name__)
CORS(app)

# 경로 설정
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from main import setup_database, exec_crawler

# 라우팅
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    # 요청 파라미터
    data = request.get_json()
    keywords = data.get('keywords', '').strip()
    category = data.get('category', '')
    option = data.get('option', '')

    # 데이터베이스 생성 및 연결
    dw_collections = ["abyss", "blackbasta", "blacksuit", "breachdetector", "ctifeeds",
                      "daixin", "darkleak", "darknetARMY", "everest", "island",
                      "leakbase", "lockbit", "play", "rhysida", "htdark"]
    osint_collections = ["github", "tuts4you", "0x00org"]

    dw_db = asyncio.run(setup_database("darkweb", dw_collections))
    osint_db = asyncio.run(setup_database("osint", osint_collections))

    # 초기화
    db_collection = None
    results = []

    # 컬렉션 선택
    if category == "osint":
        db_collection = osint_db.get(option)
    elif category == "darkweb":
        db_collection = dw_db.get(option)
    else:
        return jsonify({"error": "Invalid collection"}), 400

    # 검색어가 있을 경우 제목에서 검색
    if keywords:
        search_filter = {"title": {"$regex": keywords, "$options": "i"}}
        cursor = db_collection.find(search_filter)
    else:
        cursor = db_collection.find()

    # DB 탐색 결과 가공
    for doc in cursor:
        result = {
            "_id": str(doc.get("_id")),
            "title": doc.get("title"),
            "url": doc.get("url"),
            "keyword": doc.get("keyword", "")
        }
        results.append(result)

    return jsonify({"results": results})


def run_flask():
    """
    Flask 서버를 별도의 쓰레드에서 실행
    """
    print("[START] Flask 웹 서버를 실행합니다...")
    app.run(debug=True, use_reloader=False, threaded=True)


async def main():
    """
    Flask 서버 및 크롤링 작업 실행
    """
    # Flask 서버를 쓰레드에서 실행
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # 크롤러 실행
    print("[INFO] 크롤러 작업을 실행합니다...")
    await exec_crawler()


if __name__ == "__main__":
    asyncio.run(main())

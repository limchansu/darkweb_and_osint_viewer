from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # 추가된 부분
import sys, os

# 실행 시 경로 포함
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from connect_db import connect_databases

app = Flask(__name__)
CORS(app)  # 모든 도메인에 대해 CORS를 허용

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    # 요청 파라미터
    data = request.get_json()  # JSON 데이터 파싱

    keywords = data.get('keywords', '').strip()  # 검색어
    category = data.get('category', '')
    option = data.get('option', '')

    # 데이터베이스 연결
    dw_db, osint_db = connect_databases()

    # 초기화
    db_collection = None
    results = []

    # 컬렉션 선택
    if category == "osint":
        db_collection = osint_db[option]
    elif category == "darkweb":
        db_collection = dw_db[option]
    else:
        return jsonify({"error": "Invalid collection"}), 400

    # 검색어가 있을 경우 제목에서 검색
    if keywords:
        search_filter = {"title": {"$regex": keywords, "$options": "i"}}  # 대소문자 구분 없는 검색
        cursor = db_collection.find(search_filter)
    else:
        cursor = db_collection.find()

    # DB 탐색 결과 가공
    for doc in cursor:
        result = {
            "_id": str(doc.get("_id")),  # ObjectId를 문자열로 변환
            "title": doc.get("title"),
            "url": doc.get("url"),
            "keyword": doc.get("keyword", "")  # 필요한 다른 필드도 추가 가능
        }
        results.append(result)

    return jsonify({
        "results": results
    })

if __name__ == '__main__':
    app.run(debug=True)
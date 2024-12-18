# Flask 빌드 환경
FROM python:3.11

# Tor 설치를 위한 패키지 업데이트 및 설치
RUN apt-get update && apt-get install -y \
    tor \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 복사
COPY . .

# Flask 실행 포트
EXPOSE 5000

# Tor SOCKS 포트 노출
EXPOSE 9050

# Flask 앱과 Tor 동시 실행 (Tor 실행 후 10초 대기)
CMD tor --defaults-torrc crawling/torrc && sleep 10 && python crawling/app/__init__.py

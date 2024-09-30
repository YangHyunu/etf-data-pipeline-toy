# Python 베이스 이미지 사용
FROM python:3.11.6

# 작업 디렉토리 설정
WORKDIR /app

# 의존 라이브러리 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# local 에 있는 소스파일들 복사해서 작업 디렉토리인 app 에 저장함 
# gitignore에 있는 venv는 복사 안됌
COPY . .

# FastAPI 애플리케이션 실행
CMD ["uvicorn", "app.main:app","--host", "0.0.0.0", "--port", "8000"]
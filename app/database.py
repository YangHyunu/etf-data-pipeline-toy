from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
# 데이터베이스 URL 환경 변수 (MySQL 사용)
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy 데이터베이스 엔진 생성 (MySQL 연결)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# 세션 생성 (ORM과 데이터베이스 간의 세션을 관리)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy 모델의 베이스 클래스
Base = declarative_base()

# 세션을 제공하는 함수 (FastAPI 종속성 주입에 사용됨)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

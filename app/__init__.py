'''from fastapi import FastAPI
from .database import engine, Base

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

# 데이터베이스 테이블 생성 (모델 기반으로 MySQL에 테이블 생성)
Base.metadata.create_all(bind=engine)
'''
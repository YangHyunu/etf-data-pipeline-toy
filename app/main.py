from fastapi import FastAPI, Depends, Form,Request
from sqlalchemy.orm import Session
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from .database import engine, Base, get_db, SessionLocal
from .client import ETFClient
from .predictions import apply_model_to_etf
import io
from base64 import b64encode

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()
scheduler = BackgroundScheduler(timezone='Asia/Seoul')
templates = Jinja2Templates(directory="templates")

etf_list = {
    '시장지수': ['SPY', 'QQQ', 'TQQQ', 'DIA'],
    '금': ['GLD', 'IAU'],
    '채권': ['TLT', 'AGG', 'BND'],
    '반도체': ['SMH', 'SOXX', 'SOXL'],
    '원자재': ['DBC', 'USO', 'PDBC']
}

# FastAPI 애플리케이션 시작 시 데이터베이스 테이블 생성 및 초기 데이터 저장
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine) # 데이터베이스에 테이블을 최초로 생성
    with SessionLocal() as db:
        client = ETFClient(db)
        client.store_initial_data(etf_list)  # 만약 기존 데이터가 없다면 최초 데이터 저장
    scheduler.start()
    scheduler.add_job(schedule_daily_update, 'cron',hour=12,minute=00)
# 매일 아침 데이터와 모델을 업데이트하는 작업 스케줄링
def schedule_daily_update():
    with SessionLocal() as db:
        client = ETFClient(db)
        client.update_daily_data(etf_list)
        client.update_model(etf_list)
    print(f"스케줄러가 실행되었습니다: {datetime.now()}")
    
# GET 요청: ETF 심볼 입력 폼을 제공
@app.get("/predict-etf", response_class=HTMLResponse)
def get_etf_form(request: Request):
    return templates.TemplateResponse("predict_etf_form.html", {
        "request": request,
        "etf_list": etf_list  # etf_list 전달 추가
    })

@app.post("/predict-etf", response_class=HTMLResponse)
def predict_etf(request: Request, etf_symbol: str = Form(...), db: Session = Depends(get_db)):

    # 머신러닝 모델로 예측 수행
    predictions = apply_model_to_etf(etf_symbol)
    
    if not predictions:
        return {"error": "Model not found for this symbol."}

    # 시각화된 그래프 생성
    image_base64 = b64encode(predictions['buffer'].getvalue()).decode('utf-8')
    print(f"Buffer size: {len(predictions['buffer'].getvalue())}")
       # 예측 결과와 그래프를 템플릿에 전달하여 웹 페이지에 표시
    return templates.TemplateResponse("predict_etf.html", {
        "request": request,
        "symbol": etf_symbol,
        "prediction": predictions["prediction"],
        "image": image_base64
    }) 

import datetime
import pathlib
import joblib
from sqlalchemy.orm import Session
import matplotlib.pyplot as plt
import pandas as pd
from .models import ETFData  # ETFData는 SQLAlchemy 모델
import numpy as np
from io import BytesIO
np.float_ = np.float64
from prophet import Prophet

BASE_DIR = pathlib.Path(__file__).resolve(strict=True).parent
TRAINED_DIR = pathlib.Path(BASE_DIR) / "trained"
PLOTS_DIR = pathlib.Path(BASE_DIR) / "plots"
TODAY = datetime.date.today()

# 디렉터리가 없으면 생성
TRAINED_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

# MySQL에서 ETF 데이터를 가져와 pandas DataFrame으로 변환하는 함수
def get_etf_data_from_db(etf_symbol: str, db: Session):
    model_file = TRAINED_DIR / f"{etf_symbol}.joblib"
    # 만약 이미 모델이 존재한다면 데이터 LOAD $ 모델 학습 X 
    if model_file.exists():
        return False
    else:
        # 해당 ETF 심볼에 맞는 데이터를 쿼리하는 쿼리 객체를 생성
        query = db.query(ETFData).filter(ETFData.etf_symbol == etf_symbol)
        
        # 쿼리 결과를 리스트로 받아 pandas DataFrame으로 변환
        df_for_prophet= pd.DataFrame([(row.date, row.adj_close) for row in query.all()],
                                columns=['ds', 'y'])
        model = Prophet()
        model.fit(df_for_prophet)

        joblib.dump(model, TRAINED_DIR / f"{etf_symbol}.joblib")
        return df_for_prophet

# ETF 데이터를 머신러닝 모델에 적용하는 함수
def apply_model_to_etf(etf_symbol:str,period=30):
    model_file = TRAINED_DIR / f"{etf_symbol}.joblib"
    if not model_file.exists():
        return False
    
    model = joblib.load(model_file)
    # 30일 동안의 미래 예측 데이터 생성
    future = model.make_future_dataframe(period)
    forecast = model.predict(future)
    fig = model.plot(forecast)
    
    # 예측 그래프를 버퍼에 저장
    buffer = BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    output ={}
    for data in forecast.tail(period).to_dict("records"):
        date = data["ds"].strftime("%Y/%m/%d")
        output[date] = data["trend"]
    return {"symbol":etf_symbol,"prediction":output,"buffer":buffer}


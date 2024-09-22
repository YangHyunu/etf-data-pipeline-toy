import yfinance as yf
from sqlalchemy.orm import Session
from .models import ETFData
from datetime import timedelta
# ETF 데이터를 관리하는 클래스
class ETFClient:
    def __init__(self, db: Session):
        self.db = db
    
    # yfinance에서 데이터를 가져오는 메서드
    def fetch_data(self, symbol: str,period:str ='5y'):
        return yf.download(symbol, period=period)  # 과거 5년치 데이터
    
    # 데이터를 데이터베이스에 저장하는 메서드
    def save_to_db(self, symbol: str, data,category:str):
        for date, row in data.iterrows():
            etf_data = ETFData(
                etf_symbol=symbol,
                date=date,
                open_price=row['Open'],
                close_price=row['Close'],
                adj_close=row['Adj Close'],
                high_price=row['High'],
                low_price=row['Low'],
                volume=row['Volume'],
                category =category
            )
            self.db.add(etf_data)
        self.db.commit()

        # 초기 데이터를 저장하는 메서드
    def store_initial_data(self, etf_list: dict):
        # 이미 저장된 데이터가 있는지 확인
        existing_data = self.db.query(ETFData).first()

        if existing_data:
            # 데이터가 이미 있으면 저장 작업을 생략
            print("Initial data already exists.")
            return

        for category, etfs in etf_list.items():
            for etf in etfs:
                data = self.fetch_data(etf)  # 5년치 데이터 수집
                self.save_to_db(etf, data, category)  # 데이터 저장

    # 매일 데이터를 업데이트하는 메서드
    def update_daily_data(self, etf_list: dict):
        for category, etfs in etf_list.items():
            for etf in etfs:
                # 데이터베이스에서 가장 최신 날짜를 가져옴
                last_entry = self.db.query(ETFData).filter(ETFData.etf_symbol == etf).order_by(ETFData.date.desc()).first()
                last_date = last_entry.date if last_entry else None

                # yfinance에서 마지막 업데이트 이후의 데이터를 가져옴
                if last_date:
                    start_date = last_date + timedelta(days=1)
                    data = self.fetch_data(etf, period='1d', start=start_date.strftime('%Y-%m-%d'))
                    if not data.empty:
                        self.save_to_db(etf, data, category)
    
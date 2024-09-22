from sqlalchemy import Column, Integer, String, DECIMAL, Date, TIMESTAMP
from .database import Base

# ETF 데이터를 저장하는 테이블 모델
class ETFData(Base):
    __tablename__ = "etf_data"
    
    id = Column(Integer, primary_key=True, index=True)
    etf_symbol = Column(String(10), index=True)  # ETF의 심볼 (예: 'XLK')
    date = Column(Date, index=True)  # 데이터 수집 날짜
    open_price = Column(DECIMAL(10, 4))  # 시가
    close_price = Column(DECIMAL(10, 4))  # 종가
    adj_close= Column(DECIMAL(10, 4))
    high_price = Column(DECIMAL(10, 4))  # 고가
    low_price = Column(DECIMAL(10, 4))  # 저가
    volume = Column(Integer)  # 거래량
    category = Column(String(50))  # ETF 카테고리 (예: 기술, 금융 등)

    
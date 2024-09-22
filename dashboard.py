import dash
from dash import dcc, html
import requests
import pandas as pd
import plotly.graph_objects as go

app = dash.Dash(__name__)

# FastAPI에서 예측 데이터를 가져오는 함수 (사용자가 ETF 심볼 입력)
def fetch_etf_predictions(etf_symbol):
    response = requests.post(f"http://localhost:8000/predict_etf", data={"etf_symbol": etf_symbol})
    data = response.json()
    return data["predictions"]

# ETF 심볼을 사용자 입력을 통해 동적으로 가져오기
etf_symbol = "XLK"  # 기본값, 나중에 사용자 입력으로 대체 가능
predictions = fetch_etf_predictions(etf_symbol)
df = pd.DataFrame(predictions)

# Plotly 그래프 생성
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['date'], y=df['predicted_return'], mode='lines', name='Predicted Return'))

# Dash 레이아웃 설정
app.layout = html.Div(children=[
    html.H1(children='ETF 수익률 예측 대시보드'),
    dcc.Graph(id='etf-predictions', figure=fig)
])

if __name__ == '__main__':
    app.run_server(debug=True)

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="시청가구수 대시보드", layout="wide")

st.title("홈앤쇼핑 시청가구수 분석 대시보드")

# CSV 파일 읽기
@st.cache_data
def load_data():
    df = pd.read_csv('viewing_data.csv')
    df['시간'] = pd.to_datetime(df['시간'])
    return df

df = load_data()

# 데이터 정보
st.write(f"📊 데이터 범위: {df['시간'].min().strftime('%Y-%m-%d %H:%M:%S')} ~ {df['시간'].max().strftime('%Y-%m-%d %H:%M:%S')}")
st.write(f"총 {len(df)}개의 데이터 포인트 (10초 간격)")

# 그래프 1: 홈앤쇼핑 비교 (오늘, 어제, 지난주)
st.subheader("📈 그래프 1: 홈앤쇼핑 시간대별 비교 (오늘/어제/지난주)")

fig1 = go.Figure()

fig1.add_trace(go.Scatter(
    x=df['시간'],
    y=df['홈앤쇼핑(오늘)'],
    mode='lines',
    name='오늘',
    line=dict(color='#FF6B6B', width=2)
))

fig1.add_trace(go.Scatter(
    x=df['시간'],
    y=df['홈앤쇼핑(어제)'],
    mode='lines',
    name='어제',
    line=dict(color='#4ECDC4', width=2)
))

fig1.add_trace(go.Scatter(
    x=df['시간'],
    y=df['홈앤쇼핑(지난주'],
    mode='lines',
    name='지난주',
    line=dict(color='#95E1D3', width=2)
))

fig1.update_layout(
    title='',
    xaxis_title='시간',
    yaxis_title='시청가구수 (명)',
    hovermode='x unified',
    height=500,
    template='plotly_white'
)

st.plotly_chart(fig1, use_container_width=True)

# 그래프 2: 홈앤쇼핑 vs 경쟁사 비교
st.subheader("⚔️ 그래프 2: 홈앤쇼핑 vs 경쟁사 비교 (오늘)")

fig2 = go.Figure()

fig2.add_trace(go.Scatter(
    x=df['시간'],
    y=df['홈앤쇼핑(오늘)'],
    mode='lines',
    name='홈앤쇼핑',
    line=dict(color='#FF6B6B', width=3)
))

# 경쟁사 데이터 추가 (컬럼명이 있는 경우만)
competitor_columns = [col for col in df.columns if col not in ['시간', '홈앤쇼핑(오늘)', '홈앤쇼핑(어제)', '홈앤쇼핑(지난주']]
colors = ['#4ECDC4', '#95E1D3', '#FFE66D', '#A8E6CF', '#FFD3B6']

for idx, col in enumerate(competitor_columns):
    fig2.add_trace(go.Scatter(
        x=df['시간'],
        y=df[col],
        mode='lines',
        name=col,
        line=dict(color=colors[idx % len(colors)], width=2)
    ))

fig2.update_layout(
    title='',
    xaxis_title='시간',
    yaxis_title='시청가구수 (명)',
    hovermode='x unified',
    height=500,
    template='plotly_white'
)

st.plotly_chart(fig2, use_container_width=True)

# 통계 정보
st.subheader("📊 통계 정보")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("홈앤쇼핑(오늘) 평균", f"{df['홈앤쇼핑(오늘)'].mean():.0f}",
              delta=f"{df['홈앤쇼핑(오늘)'].iloc[-1] - df['홈앤쇼핑(오늘)'].iloc[0]:.0f}")

with col2:
    st.metric("홈앤쇼핑(어제) 평균", f"{df['홈앤쇼핑(어제)'].mean():.0f}")

with col3:
    st.metric("홈앤쇼핑(지난주) 평균", f"{df['홈앤쇼핑(지난주'].mean():.0f}")

# 세부 데이터 테이블
st.subheader("📋 세부 데이터")
st.dataframe(df, use_container_width=True)

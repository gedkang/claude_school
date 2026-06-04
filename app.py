import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="시청가구수 대시보드", layout="wide")
st.title("홈앤쇼핑 시청가구수 대시보드")

try:
    # CSV 파일 읽기
    csv_path = r'c:\biyam_work\viewing_data.csv'
    df = pd.read_csv(csv_path)

    # 컬럼 이름 설정
    df.columns = ['시간', '오늘', '어제', '지난주', 'NS홈쇼핑', 'CJ_ONSTYLE', '기타']

    # 시간 컬럼을 datetime으로 변환
    df['시간'] = pd.to_datetime(df['시간'])

    st.success(f"✓ 데이터 로드 완료: {len(df)}개 행")

    # 그래프 1: 홈앤쇼핑 (오늘, 어제, 지난주)
    st.subheader("📊 홈앤쇼핑 시청가구수 비교 (오늘/어제/지난주)")

    # 데이터를 긴 형식으로 변환
    df_melted = df.melt(
        id_vars=['시간'],
        value_vars=['오늘', '어제', '지난주'],
        var_name='구분',
        value_name='시청가구수'
    )

    fig1 = px.line(
        df_melted,
        x='시간',
        y='시청가구수',
        color='구분',
        labels={'시청가구수': '시청가구수 (명)', '시간': '시간'}
    )
    fig1.update_layout(height=500, hovermode='x unified')
    st.plotly_chart(fig1, use_container_width=True, key='chart1')

    # 그래프 2: 홈앤쇼핑 vs 경쟁사
    st.subheader("⚔️ 경쟁사 비교 (오늘)")

    df_melted2 = df.melt(
        id_vars=['시간'],
        value_vars=['오늘', 'NS홈쇼핑', 'CJ_ONSTYLE'],
        var_name='채널',
        value_name='시청가구수'
    )

    # 채널명 수정
    df_melted2['채널'] = df_melted2['채널'].replace({'오늘': '홈앤쇼핑'})

    fig2 = px.line(
        df_melted2,
        x='시간',
        y='시청가구수',
        color='채널',
        labels={'시청가구수': '시청가구수 (명)', '시간': '시간'}
    )
    fig2.update_layout(height=500, hovermode='x unified')
    st.plotly_chart(fig2, use_container_width=True, key='chart2')

except Exception as e:
    st.error(f"에러 발생: {str(e)}")
    import traceback
    st.write(traceback.format_exc())

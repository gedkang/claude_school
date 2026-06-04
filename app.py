import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client, Client

st.set_page_config(page_title="시청가구수 대시보드", layout="wide")
st.title("홈앤쇼핑 시청가구수 대시보드")

try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Supabase에서 데이터 가져오기
    response = supabase.table("viewing_data").select("*").execute()
    raw_data = response.data

    df = pd.DataFrame(raw_data)
    df['시간'] = pd.to_datetime(df['시간'])
    df = df.sort_values('시간')

    st.success(f"✓ Supabase에서 데이터 로드 완료: {len(df)}개 행")

    # 시간별 채널별 최신 값만 유지
    df_pivot = df.pivot_table(index='시간', columns='채널명', values='시청가구수', aggfunc='last').reset_index()

    # 채널 분류
    home_channel = [col for col in df_pivot.columns if '홈앤쇼핑' in col][0] if any('홈앤쇼핑' in col for col in df_pivot.columns) else None
    all_channels = [col for col in df_pivot.columns if col != '시간']

    if home_channel:
        st.subheader("📊 시청가구수 추이")
        df_melted = df_pivot.melt(
            id_vars=['시간'],
            value_vars=all_channels,
            var_name='채널',
            value_name='시청가구수'
        )

        fig1 = px.line(
            df_melted,
            x='시간',
            y='시청가구수',
            color='채널',
            labels={'시청가구수': '시청가구수 (명)', '시간': '시간'}
        )
        fig1.update_layout(height=500, hovermode='x unified')
        st.plotly_chart(fig1, use_container_width=True, key='chart1')

        st.subheader("⚔️ 채널별 최신 시청가구수")
        latest = df_pivot.iloc[-1]
        channels = latest[all_channels].sort_values(ascending=False)

        fig2 = px.bar(
            x=channels.values,
            y=channels.index,
            orientation='h',
            labels={'x': '시청가구수 (명)', 'y': '채널'},
            color=channels.values,
            color_continuous_scale='Blues'
        )
        fig2.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True, key='chart2')

        st.subheader("📋 최근 데이터")
        st.dataframe(df_pivot.tail(10), use_container_width=True)

except Exception as e:
    st.error(f"에러 발생: {str(e)}")
    import traceback
    st.write(traceback.format_exc())

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="시청가구수 대시보드", layout="wide")

st.title("홈앤쇼핑 시청가구수 대시보드")

try:
    csv_path = 'viewing_data_2.csv'
    df = pd.read_csv(csv_path)
    df['시간'] = pd.to_datetime(df['시간'])

    st.success(f"데이터 로드 완료: {len(df)}개 행 | {len(df.columns)}개 컬럼")

    home_cols = ['홈앤쇼핑(오늘)', '홈앤쇼핑(어제)', '홈앤쇼핑(지난주)']
    competitor_cols = [col for col in df.columns if col not in ['시간'] + home_cols]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("현재 시청가구수", f"{df['홈앤쇼핑(오늘)'].iloc[-1]:,.0f}")
    with col2:
        prev = df['홈앤쇼핑(어제)'].iloc[-1]
        curr = df['홈앤쇼핑(오늘)'].iloc[-1]
        diff = curr - prev
        st.metric("어제 대비", f"{diff:+,.0f}")
    with col3:
        avg_today = df['홈앤쇼핑(오늘)'].mean()
        st.metric("평균 시청가구수", f"{avg_today:,.0f}")

    st.subheader("📊 홈앤쇼핑 시청가구수 추이")
    df_melted = df.melt(
        id_vars=['시간'],
        value_vars=home_cols,
        var_name='구분',
        value_name='시청가구수'
    )
    df_melted['구분'] = df_melted['구분'].str.replace('홈앤쇼핑(', '').str.replace(')', '')

    fig1 = px.line(
        df_melted,
        x='시간',
        y='시청가구수',
        color='구분',
        labels={'시청가구수': '시청가구수 (명)', '시간': '시간'},
        hover_data={'시청가구수': ':.0f'}
    )
    fig1.update_layout(height=450, hovermode='x unified')
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("⚔️ 경쟁사 비교 (현재값 기준 상위 10)")
    latest_data = df.iloc[-1]
    competitor_latest = latest_data[competitor_cols].sort_values(ascending=False).head(10)

    fig2 = px.bar(
        x=competitor_latest.values,
        y=competitor_latest.index,
        orientation='h',
        labels={'x': '시청가구수 (명)', 'y': '채널'},
        color=competitor_latest.values,
        color_continuous_scale='Viridis'
    )
    fig2.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 경쟁사 채널 선택")
        selected_competitors = st.multiselect(
            "비교할 경쟁사 선택 (최대 5개)",
            competitor_cols,
            default=competitor_cols[:3]
        )
    with col2:
        st.write("")

    if selected_competitors:
        selected_data = ['홈앤쇼핑(오늘)'] + selected_competitors
        df_melted3 = df.melt(
            id_vars=['시간'],
            value_vars=selected_data,
            var_name='채널',
            value_name='시청가구수'
        )
        df_melted3['채널'] = df_melted3['채널'].str.replace('홈앤쇼핑(오늘)', '홈앤쇼핑')

        fig3 = px.line(
            df_melted3,
            x='시간',
            y='시청가구수',
            color='채널',
            labels={'시청가구수': '시청가구수 (명)', '시간': '시간'}
        )
        fig3.update_layout(height=450, hovermode='x unified')
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("📋 데이터 테이블")
    st.dataframe(df.iloc[-10:].iloc[::-1], use_container_width=True)

except Exception as e:
    st.error(f"에러 발생: {str(e)}")
    import traceback
    st.write(traceback.format_exc())

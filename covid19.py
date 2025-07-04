import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title = '코로나19 한국 대시보드', layout = 'wide')
st.title('코로나19 한국 감염자 대시보드')

# 파일 업로드
uploaded_confirmed  = st.file_uploader('확진자 CSV 파일 업로드', type = ['csv'])
uploaded_deaths = st.file_uploader('사망자 CSV 파일 업로드', type = ['csv'])
uploaded_recovered = st.file_uploader('회복자 CSV 파일 업로드', type = ['csv'])

# 모든 파일이 업로드 되었다면 실행
if uploaded_confirmed and uploaded_deaths and uploaded_recovered :
    df_confirmed = pd.read_csv(uploaded_confirmed)
    df_deaths = pd.read_csv(uploaded_deaths)
    df_recovered = pd.read_csv(uploaded_recovered)

    # 함수 정의 - 대한민국 데이터만 추출, 날짜형식도 대한민국 스타일
    def get_korea_data(df, value_name):
        df_korea = df[df['Country/Region'] == 'Korea, South']
        df_korea = df_korea.drop(columns=['Province/State', 'Country/Region', 'Lat', 'Long'])
        series_korea = df_korea.sum().reset_index()
        series_korea.columns = ['날짜', value_name]
        series_korea['날짜'] = pd.to_datetime(series_korea['날짜'], format='%m/%d/%y')
        return series_korea

    df_confirmed = get_korea_data(df_confirmed, '확진자')
    df_deaths = get_korea_data(df_deaths, '사망자')
    df_recovered = get_korea_data(df_recovered, '회복자')

    # 데이터 병합
    df_merged = df_confirmed.merge(df_deaths, on='날짜').merge(df_recovered, on='날짜')
    # 날짜부분에서 00:00:00 시간 부분 제거
    df_merged['날짜'] = df_merged['날짜'].dt.date

    df_merged['신규 확진자'] = df_merged['확진자'].diff().fillna(0).astype(int)
    df_merged['신규 사망자'] = df_merged['사망자'].diff().fillna(0).astype(int)
    df_merged['신규 회복자'] = df_merged['회복자'].diff().fillna(0).astype(int)

    # 탭 3개 구성 (감염 추이, 통계 요약, 비율 분석)
    tab1, tab2, tab3 = st.tabs(['감염 추이', '통계 요약', '비율 분석'])

    # 첫 번째 탭 : 감염 추이
    with tab1 :
        st.subheader('누적 추이 그래프')
        selected = st.multiselect(
            '표시할 항목을 선택하세요.',
            ['확진자', '사망자', '회복자'],
            default = ['확진자', '회복자']
        )
        if selected :
            fig = px.line(df_merged, x = '날짜', y = selected, markers = True)
            st.plotly_chart(fig, use_container_width = True)

        st.subheader('일일 증가량 그래프')
        selected_new = st.multiselect(
            '표시할 항목(신규)을 선택하세요.',
            ['신규 확진자', '신규 사망자', '신규 회복자'],
            default = ['신규 확진자']
        )
        if selected_new :
            fig_new = px.bar(df_merged, x = '날짜', y = selected_new)
            st.plotly_chart(fig_new, use_container_width = True)

    # 두 번째 탭 : 통계 요약
    with tab2 :
        st.subheader('일자별 통계 테이블')
        st.dataframe(df_merged.tail(10), use_container_width = True)

    # 세 번째 탭 : 비율 분석
    with tab3 :
        st.subheader('최신일 기준 회복률 / 사망률')
        lastest = df_merged.iloc[-1]

        confirmed = lastest['확진자']
        deaths = lastest['사망자']
        recovered = lastest['회복자']

        # 회복률 = (회복자 / 확진자) * 100
        recovered_rate = (recovered / confirmed) * 100 if confirmed else 0
        # 사망률 = (사망자 / 확진자) * 100
        death_rate = (deaths / confirmed) * 100 if confirmed else 0

        col1, col2 = st.columns(2)
        col1.metric('회복률', f'{recovered_rate:.2f}%')
        col2.metric('사망률', f'{death_rate:.2f}%')

        st.subheader('감영자 분포 비율')
        # 원형그래프의 원본이 될 데이터프레임 생성
        df_pie = pd.DataFrame({
            '구분' : ['회복자', '사망자','격리중'],
            '인원수' : [recovered, deaths, confirmed - recovered - deaths]
        })
        fig_pie = px.pie(df_pie, names = '구분', values = '인원수', title = '감염자 분포')
        st.plotly_chart(fig_pie, use_container_width = True)

else :
    st.info('3개의 CSV 파일(확진자, 사망자, 회복자)을 모두 업로드 해주세요.')
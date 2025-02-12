import streamlit as st
import pandas as pd
import io

# 📌 마디 계산기 실행
st.title("📈 해외선물 마디 계산기")
st.write("📌 시가를 입력하면 위로 24마디, 아래로 24마디를 자동 계산합니다.")

# 💰 시가 입력
price = st.number_input("💰 시가 입력", min_value=0.0, format="%.2f")

# 📊 C열(마디 간격) 고정값 (엑셀 데이터 그대로 사용)
c_values = [
    0.6, 0.55, 0.7, 0.65, 0.6, 0.75, 0.5, 0.65, 0.6, 0.55,
    0.7, 0.65, 0.6, 0.75, 0.5, 0.65, 0.6, 0.55, 0.7, 0.65,
    0.6, 0.75, 0.5, 0.65,
    0,  # 시가 (마디 간격 없음)
    0.6, 0.55, 0.7, 0.65, 0.6, 0.75, 0.5, 0.65, 0.6, 0.55,
    0.7, 0.65, 0.6, 0.75, 0.5, 0.65, 0.6, 0.55, 0.7, 0.65,
    0.6, 0.75, 0.5, 0.65
]

if price:
    # 📌 위쪽 24개 값 계산 (시가에서 C열 값을 빼는 방식으로 정렬 맞추기)
    upper_prices = [price]
    for gap in reversed(c_values[:24]):  
        upper_prices.insert(0, round(upper_prices[0] + gap, 2))  # 가장 앞에 추가

    # 📌 아래쪽 24개 값 계산 (시가에서 C열 값을 빼기)
    lower_prices = [price]
    for gap in c_values[25:]:  
        lower_prices.append(round(lower_prices[-1] - gap, 2))

    # 📌 최종 리스트 구성 (위쪽 + 시가 + 아래쪽)
    final_prices = upper_prices[:-1] + [price] + lower_prices[1:]

    # 📌 마디 번호 올바르게 정렬
    madi_numbers = list(range(24, 0, -1)) + ["시가"] + list(range(1, 25))

    # ✅ **길이 확인**
    assert len(final_prices) == 49, f"가격 리스트 길이 오류: {len(final_prices)} (49 필요)"
    assert len(c_values) == 49, f"마디 간격 길이 오류: {len(c_values)} (49 필요)"
    assert len(madi_numbers) == 49, f"마디 번호 길이 오류: {len(madi_numbers)} (49 필요)"

    # 📌 데이터프레임 생성 (엑셀과 100% 동일하게 맞추기)
    df = pd.DataFrame({
        "마디 번호": madi_numbers,  
        "계산된 가격": [f"{p:.2f}" for p in final_prices],  
        "마디 간격": [str(int(gap)) if gap.is_integer() else f"{gap:.2f}" for gap in c_values]  
    })

    # 📌 색 대비 적용 (위쪽 오렌지, 시가 녹색, 아래쪽 파란색)
    def highlight_rows(row):
        idx = df.index.get_loc(row.name)  # 행 인덱스 가져오기
        if row["마디 번호"] == "시가":
            return ["background-color: lightgreen"] * len(row)  # 시가 (녹색)
        elif idx < 24:
            return ["background-color: lightsalmon"] * len(row)  # 위쪽 (오렌지)
        else:
            return ["background-color: lightblue"] * len(row)  # 아래쪽 (파란색)

    styled_df = df.style.apply(highlight_rows, axis=1)

    # 📌 표로 출력 (색 대비 적용 + 불필요한 자동 번호 제거)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    # 📥 **엑셀 파일(.xlsx) 다운로드 기능 추가**
    @st.cache_data
    def convert_df_to_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="마디 계산")
        processed_data = output.getvalue()
        return processed_data

    xlsx_data = convert_df_to_excel(df)

    st.download_button(
        label="📥 엑셀 다운로드",
        data=xlsx_data,
        file_name="마디_계산.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

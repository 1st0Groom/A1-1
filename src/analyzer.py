"""Reusable analysis of the 1Scoop snapshot and transaction data."""
# JSON 파일을 읽는 표준 라이브러리를 불러온다.
import json
# 파일 경로를 다루는 Path를 불러온다.
from pathlib import Path

# NumPy를 np라는 이름으로 불러온다.
import numpy as 넘파이
# Pandas를 pd라는 이름으로 불러온다.
import pandas as 판다스


# 데이터 분석에 필요한 기능을 하나의 클래스로 묶는다.
class DataAnalyzer:
    # 객체를 만들 때 데이터 경로를 전달받는다.
    def __init__(self, data_path):
        # 전달받은 경로를 Path 객체로 저장한다.
        self.data_path = Path(data_path)
        # 아직 데이터를 읽지 않았으므로 표를 비워 둔다.
        self.df = None

    # 파일을 읽어 DataFrame으로 저장하고 반환한다.
    def load_data(self, key="verified_products"):
        # 파일 확장자가 JSON인지 확인한다.
        if self.data_path.suffix.lower() == ".json":
            # JSON 파일을 UTF-8로 열고 사용 후 닫는다.
            with self.data_path.open(encoding="utf-8") as 파일:
                # JSON 내용을 파이썬 데이터로 읽는다.
                데이터 = json.load(파일)
            # 지정한 항목을 DataFrame으로 만든다.
            self.df = 판다스.DataFrame(데이터[key])
        # 엑셀 파일이면 이 분기로 들어간다.
        elif self.data_path.suffix.lower() in (".xlsx", ".xls"):
            # 엑셀 파일을 DataFrame으로 읽는다.
            self.df = 판다스.read_excel(self.data_path)
        # 앞의 조건에 해당하지 않는 경우다.
        else:
            # CSV 파일을 DataFrame으로 읽는다.
            self.df = 판다스.read_csv(self.data_path)
        # 처리한 DataFrame을 반환한다.
        return self.df

    # 그룹의 통계값으로 지정한 열의 결측치를 채운다.
    def handle_missing_values(self, column, group_col, strategy="median", output_col=None):
        # 지원하는 대치 방법인지 확인한다.
        if strategy not in ("mean", "median"):
            # 지원하지 않는 방법이면 오류를 알려준다.
            raise ValueError("strategy must be mean or median")
        # 결과 열 이름이 없으면 원래 이름 뒤에 _filled를 붙인다.
        결과열 = output_col or f"{column}_filled"
        # 각 행에 해당 그룹의 평균 또는 중앙값을 맞춘다.
        그룹통계 = self.df.groupby(group_col)[column].transform(strategy)
        # 빈 값만 그룹 통계로 채워 새 열에 저장한다.
        self.df[결과열] = self.df[column].fillna(그룹통계)
        # 처리한 DataFrame을 반환한다.
        return self.df

    # IQR 경계를 벗어나는 값의 위치를 찾는다.
    def detect_outliers(self, column, threshold=1.5):
        # 사분위수 계산을 위해 결측값을 제외한다.
        값들 = self.df[column].dropna()
        # 유효한 값이 없거나 임계값이 음수인지 확인한다.
        if 값들.empty or threshold < 0:
            # 계산할 수 없는 입력이면 오류를 알려준다.
            raise ValueError("column must contain values and threshold must be nonnegative")
        # 25% 지점과 75% 지점의 값을 구한다.
        q1, q3 = 값들.quantile([0.25, 0.75])
        # 사분위 범위를 구한다.
        iqr = q3 - q1
        # 이상치 탐지에 사용할 아래·위 경계를 계산한다.
        하한, 상한 = q1 - threshold * iqr, q3 + threshold * iqr
        # 결측값은 제외하고 경계 밖인 행을 True로 표시한다.
        이상치여부 = self.df[column].notna() & ~self.df[column].between(하한, 상한)
        # 사분위수, 경계와 이상치 표시를 함께 반환한다.
        return {"q1": q1, "q3": q3, "iqr": iqr, "lower": 하한, "upper": 상한, "mask": 이상치여부}

    # 상품명에서 문자 수를 계산한다.
    def add_text_features(self, column="name"):
        # 각 상품명의 길이를 새 열에 저장한다.
        self.df["name_length"] = self.df[column].str.len()
        # 처리한 DataFrame을 반환한다.
        return self.df

    # 객체의 상태를 쓰지 않는 독립적인 기능임을 표시한다.
    @staticmethod
    # 이미지별 픽셀 평균과 표준편차를 계산한다.
    def image_features(이미지들):
        # 입력 이미지를 NumPy 배열로 변환한다.
        이미지들 = 넘파이.asarray(이미지들)
        # 흑백 또는 컬러 이미지 묶음의 차원 수인지 확인한다.
        if 이미지들.ndim not in (3, 4):
            # 예상과 다른 배열 형태면 오류를 알려준다.
            raise ValueError("expected images shaped (N, H, W) or (N, H, W, C)")
        # 이미지 번호인 0번 축을 빼고 나머지 축을 선택한다.
        계산축 = tuple(range(1, 이미지들.ndim))
        # 이미지마다 모든 픽셀의 평균과 표준편차를 반환한다.
        return 이미지들.mean(axis=계산축), 이미지들.std(axis=계산축)

    # 거래 기록에서 고객별 최근성·주문 빈도·구매금액을 계산한다.
    def calculate_rfm(self, customer_col, date_col, amount_col, order_col, reference_date=None):
        # 필요한 열만 복사해 원본 DataFrame을 보존한다.
        df = self.df[[customer_col, date_col, amount_col, order_col]].copy()
        # 날짜로 변환하고 변환할 수 없는 값은 결측 처리한다.
        df[date_col] = 판다스.to_datetime(df[date_col], errors="coerce")
        # 금액을 숫자로 변환하고 변환할 수 없는 값은 결측 처리한다.
        df[amount_col] = 판다스.to_numeric(df[amount_col], errors="coerce")
        # 필수 값이 비어 있는 거래 행을 제외한다.
        df = df.dropna(subset=[customer_col, date_col, amount_col, order_col])
        # 구매금액이 양수인 거래 행만 남긴다.
        df = df[df[amount_col] > 0]
        # 조건을 만족한 거래가 하나도 없는지 확인한다.
        if df.empty:
            # 계산할 거래가 없으면 오류를 알려준다.
            raise ValueError("no valid positive transactions")
        # 기준일이 주어지지 않으면 마지막 거래일을 사용한다.
        기준일 = 판다스.Timestamp(reference_date) if reference_date is not None else df[date_col].max()
        # 기준일이 마지막 거래보다 이른지 확인한다.
        if 기준일 < df[date_col].max():
            # 기준일이 너무 이르면 오류를 알려준다.
            raise ValueError("reference date precedes the latest transaction")
        # 고객별 마지막 주문일, 고유 주문 수, 금액 합계를 구한다.
        결과 = df.groupby(customer_col).agg(last_order=(date_col, "max"), frequency=(order_col, "nunique"), monetary=(amount_col, "sum"))
        # 기준일과 마지막 주문일의 날짜 차이를 일 단위로 구한다.
        결과["recency"] = (기준일.normalize() - 결과["last_order"].dt.normalize()).dt.days
        # 고객 ID를 일반 열로 바꾼 결과를 반환한다.
        return 결과.reset_index()

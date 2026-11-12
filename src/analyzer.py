"""상품과 거래 데이터 분석에 사용하는 클래스."""
import json                                                                                                                         # JSON 파일을 읽는 표준 라이브러리를 불러온다.
from pathlib import Path                                                                                                            # 파일 경로를 다루는 Path를 불러온다.

import numpy as 넘파이                                                                                                              # NumPy를 넘파이라는 이름으로 불러온다.
import pandas as 판다스                                                                                                             # Pandas를 판다스라는 이름으로 불러온다.


class 데이터분석기:                                                                                                                 # 데이터 분석에 필요한 기능을 하나의 클래스로 묶는다.
    def __init__(self, 데이터경로):                                                                                                 # 객체를 만들 때 데이터 경로를 전달받는다.
        self.데이터경로 = Path(데이터경로)                                                                                          # 전달받은 경로를 Path 객체로 저장한다.
        self.데이터표 = None                                                                                                        # 아직 데이터를 읽지 않았으므로 표를 비워 둔다.

    def 데이터불러오기(self, 항목키="verified_products"):                                                                           # 파일을 읽어 DataFrame으로 저장하고 반환한다.
        if self.데이터경로.suffix.lower() == ".json":                                                                               # 파일 확장자가 JSON인지 확인한다.
            with self.데이터경로.open(encoding="utf-8") as 파일:                                                                    # JSON 파일을 UTF-8로 열고 사용 후 닫는다.
                데이터 = json.load(파일)                                                                                            # JSON 내용을 파이썬 데이터로 읽는다.
            self.데이터표 = 판다스.DataFrame(데이터[항목키])                                                                        # 지정한 항목을 DataFrame으로 만든다.
        elif self.데이터경로.suffix.lower() in (".xlsx", ".xls"):                                                                   # 엑셀 파일이면 이 분기로 들어간다.
            self.데이터표 = 판다스.read_excel(self.데이터경로)                                                                      # 엑셀 파일을 DataFrame으로 읽는다.
        else:                                                                                                                       # 앞의 조건에 해당하지 않는 경우다.
            self.데이터표 = 판다스.read_csv(self.데이터경로)                                                                        # CSV 파일을 DataFrame으로 읽는다.
        return self.데이터표                                                                                                        # 처리한 DataFrame을 반환한다.

    def 결측치처리(self, 열이름, 그룹열, 대치방법="median", 출력열=None):                                                           # 그룹의 통계값으로 지정한 열의 결측치를 채운다.
        if 대치방법 not in ("mean", "median"):                                                                                      # 지원하는 대치 방법인지 확인한다.
            raise ValueError("strategy must be mean or median")                                                                     # 지원하지 않는 방법이면 오류를 알려준다.
        결과열 = 출력열 or f"{열이름}_filled"                                                                                       # 결과 열 이름이 없으면 원래 이름 뒤에 _filled를 붙인다.
        그룹통계 = self.데이터표.groupby(그룹열)[열이름].transform(대치방법)                                                        # 각 행에 해당 그룹의 평균 또는 중앙값을 맞춘다.
        self.데이터표[결과열] = self.데이터표[열이름].fillna(그룹통계)                                                              # 빈 값만 그룹 통계로 채워 새 열에 저장한다.
        return self.데이터표                                                                                                        # 처리한 DataFrame을 반환한다.

    def 이상치탐지(self, 열이름, 임계값=1.5):                                                                                       # IQR 경계를 벗어나는 값의 위치를 찾는다.
        값들 = self.데이터표[열이름].dropna()                                                                                       # 사분위수 계산을 위해 결측값을 제외한다.
        if 값들.empty or 임계값 < 0:                                                                                                # 유효한 값이 없거나 임계값이 음수인지 확인한다.
            raise ValueError("column must contain values and threshold must be nonnegative")                                        # 계산할 수 없는 입력이면 오류를 알려준다.
        제1사분위수, 제3사분위수 = 값들.quantile([0.25, 0.75])                                                                      # 25% 지점과 75% 지점의 값을 구한다.
        사분위범위 = 제3사분위수 - 제1사분위수                                                                                      # 사분위 범위를 구한다.
        하한, 상한 = 제1사분위수 - 임계값 * 사분위범위, 제3사분위수 + 임계값 * 사분위범위                                           # 이상치 탐지에 사용할 아래·위 경계를 계산한다.
        이상치여부 = self.데이터표[열이름].notna() & ~self.데이터표[열이름].between(하한, 상한)                                     # 결측값은 제외하고 경계 밖인 행을 True로 표시한다.
        return {"q1": 제1사분위수, "q3": 제3사분위수, "iqr": 사분위범위, "lower": 하한, "upper": 상한, "mask": 이상치여부}          # 사분위수, 경계와 이상치 표시를 함께 반환한다.

    def 텍스트특성추가(self, 열이름="name"):                                                                                        # 상품명에서 문자 수를 계산한다.
        self.데이터표["name_length"] = self.데이터표[열이름].str.len()                                                              # 각 상품명의 길이를 새 열에 저장한다.
        return self.데이터표                                                                                                        # 처리한 DataFrame을 반환한다.

    @staticmethod                                                                                                                   # 객체의 상태를 쓰지 않는 독립적인 기능임을 표시한다.
    def 이미지특성계산(이미지들):                                                                                                   # 이미지별 픽셀 평균과 표준편차를 계산한다.
        이미지들 = 넘파이.asarray(이미지들)                                                                                         # 입력 이미지를 NumPy 배열로 변환한다.
        if 이미지들.ndim not in (3, 4):                                                                                             # 흑백 또는 컬러 이미지 묶음의 차원 수인지 확인한다.
            raise ValueError("expected images shaped (N, H, W) or (N, H, W, C)")                                                    # 예상과 다른 배열 형태면 오류를 알려준다.
        계산축 = tuple(range(1, 이미지들.ndim))                                                                                     # 이미지 번호인 0번 축을 빼고 나머지 축을 선택한다.
        return 이미지들.mean(axis=계산축), 이미지들.std(axis=계산축)                                                                # 이미지마다 모든 픽셀의 평균과 표준편차를 반환한다.

    def RFM계산(self, 고객열, 날짜열, 금액열, 주문열, 분석기준일=None):                                                             # 거래 기록에서 고객별 최근성·주문 빈도·구매금액을 계산한다.
        데이터표 = self.데이터표[[고객열, 날짜열, 금액열, 주문열]].copy()                                                           # 필요한 열만 복사해 원본 DataFrame을 보존한다.
        데이터표[날짜열] = 판다스.to_datetime(데이터표[날짜열], errors="coerce")                                                    # 날짜로 변환하고 변환할 수 없는 값은 결측 처리한다.
        데이터표[금액열] = 판다스.to_numeric(데이터표[금액열], errors="coerce")                                                     # 금액을 숫자로 변환하고 변환할 수 없는 값은 결측 처리한다.
        데이터표 = 데이터표.dropna(subset=[고객열, 날짜열, 금액열, 주문열])                                                         # 필수 값이 비어 있는 거래 행을 제외한다.
        데이터표 = 데이터표[데이터표[금액열] > 0]                                                                                   # 구매금액이 양수인 거래 행만 남긴다.
        if 데이터표.empty:                                                                                                          # 조건을 만족한 거래가 하나도 없는지 확인한다.
            raise ValueError("no valid positive transactions")                                                                      # 계산할 거래가 없으면 오류를 알려준다.
        기준일 = 판다스.Timestamp(분석기준일) if 분석기준일 is not None else 데이터표[날짜열].max()                                 # 기준일이 주어지지 않으면 마지막 거래일을 사용한다.
        if 기준일 < 데이터표[날짜열].max():                                                                                         # 기준일이 마지막 거래보다 이른지 확인한다.
            raise ValueError("reference date precedes the latest transaction")                                                      # 기준일이 너무 이르면 오류를 알려준다.
        결과 = 데이터표.groupby(고객열).agg(last_order=(날짜열, "max"), frequency=(주문열, "nunique"), monetary=(금액열, "sum"))    # 고객별 마지막 주문일, 고유 주문 수, 금액 합계를 구한다.
        결과["recency"] = (기준일.normalize() - 결과["last_order"].dt.normalize()).dt.days                                          # 기준일과 마지막 주문일의 날짜 차이를 일 단위로 구한다.
        return 결과.reset_index()                                                                                                   # 고객 ID를 일반 열로 바꾼 결과를 반환한다.

    load_data = 데이터불러오기                                                                                                      # 과제에서 요구한 영문 메서드 이름도 동일한 기능에 연결한다.
    handle_missing_values = 결측치처리
    detect_outliers = 이상치탐지
    calculate_rfm = RFM계산
    add_text_features = 텍스트특성추가
    image_features = 이미지특성계산

DataAnalyzer = 데이터분석기                                                                                                         # 과제에서 요구한 클래스 이름을 한국어 클래스에 연결한다.

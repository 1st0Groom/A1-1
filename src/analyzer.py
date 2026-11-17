"""상품과 거래 데이터 분석에 사용하는 클래스."""
import json
from pathlib import Path
import numpy as 넘파이
import pandas as 판다스
import matplotlib.image as 이미지읽기

class 데이터분석기:
    def __init__(self, 데이터경로):
        self.데이터경로 = Path(데이터경로)
        self.데이터표 = None

    def 데이터불러오기(self, JSON항목이름="verified_products"):
        if self.데이터경로.suffix.lower() == ".json":
            with self.데이터경로.open(encoding="utf-8") as 파일:
                데이터 = json.load(파일)
            self.데이터표 = 판다스.DataFrame(데이터[JSON항목이름])
        elif self.데이터경로.suffix.lower() in (".xlsx", ".xls"):
            self.데이터표 = 판다스.read_excel(self.데이터경로)
        else:
            self.데이터표 = 판다스.read_csv(self.데이터경로)
        return self.데이터표

    def 그룹별결측치채우기(self, 열이름, 그룹열, 대치방법="median", 출력열=None):
        if 대치방법 not in ("mean", "median"):
            raise ValueError("strategy must be mean or median")
        대치결과열 = 출력열 or f"{열이름}_filled"
        그룹별대치값 = self.데이터표.groupby(그룹열)[열이름].transform(대치방법)
        self.데이터표[대치결과열] = self.데이터표[열이름].fillna(그룹별대치값)
        return self.데이터표

    def IQR이상치찾기(self, 열이름, 임계값=1.5):
        결측제외값 = self.데이터표[열이름].dropna()
        if 결측제외값.empty or 임계값 < 0:
            raise ValueError("column must contain values and threshold must be nonnegative")
        제1사분위수, 제3사분위수 = 결측제외값.quantile([0.25, 0.75])
        사분위범위 = 제3사분위수 - 제1사분위수
        하한, 상한 = 제1사분위수 - 임계값 * 사분위범위, 제3사분위수 + 임계값 * 사분위범위
        이상치여부표 = self.데이터표[열이름].notna() & ~self.데이터표[열이름].between(하한, 상한)
        return {"q1": 제1사분위수, "q3": 제3사분위수, "iqr": 사분위범위, "lower": 하한, "upper": 상한, "mask": 이상치여부표}

    def 텍스트길이추가(self, 열이름="name"):
        self.데이터표["name_length"] = self.데이터표[열이름].str.len()
        return self.데이터표

    @staticmethod
    def 이미지평균표준편차계산(이미지들):
        이미지들 = 넘파이.asarray(이미지들)
        if 이미지들.ndim not in (3, 4):
            raise ValueError("expected images shaped (N, H, W) or (N, H, W, C)")
        픽셀축 = tuple(range(1, 이미지들.ndim))
        return 이미지들.mean(axis=픽셀축), 이미지들.std(axis=픽셀축)

    def 상품이미지특성추가(self, 이미지폴더):
        이미지경로들 = sorted(Path(이미지폴더).rglob("*.jpg"))
        if not 이미지경로들:
            raise ValueError("이미지 폴더에 JPEG 파일이 없습니다.")
        이미지들 = 넘파이.stack([
            이미지읽기.imread(이미지경로)[::20, ::20, :3][:20, :20, :]
            for 이미지경로 in 이미지경로들
        ])
        평균들, 표준편차들 = self.이미지평균표준편차계산(이미지들)
        이미지표 = 판다스.DataFrame({
            "article_id": [이미지경로.stem for 이미지경로 in 이미지경로들],
            "image_mean": 평균들,
            "image_std": 표준편차들,
        })
        if not 이미지표["article_id"].isin(self.데이터표["article_id"]).all():
            raise ValueError("상품표에 연결되지 않는 이미지 ID가 있습니다.")
        self.데이터표 = self.데이터표.merge(이미지표, on="article_id", how="left", validate="one_to_one")
        return self.데이터표

    def 고객별RFM계산(self, 고객열, 날짜열, 금액열, 구매횟수기준열, 분석기준일=None):
        데이터표 = self.데이터표[[고객열, 날짜열, 금액열, 구매횟수기준열]].copy()
        데이터표[날짜열] = 판다스.to_datetime(데이터표[날짜열], errors="coerce")
        데이터표[금액열] = 판다스.to_numeric(데이터표[금액열], errors="coerce")
        데이터표 = 데이터표.dropna(subset=[고객열, 날짜열, 금액열, 구매횟수기준열])
        데이터표 = 데이터표[데이터표[금액열] > 0]
        if 데이터표.empty:
            raise ValueError("no valid positive transactions")
        기준일 = 판다스.Timestamp(분석기준일) if 분석기준일 is not None else 데이터표[날짜열].max()
        if 기준일 < 데이터표[날짜열].max():
            raise ValueError("reference date precedes the latest transaction")
        결과 = 데이터표.groupby(고객열).agg(last_order=(날짜열, "max"), frequency=(구매횟수기준열, "nunique"), monetary=(금액열, "sum"))
        결과["recency"] = (기준일.normalize() - 결과["last_order"].dt.normalize()).dt.days
        for 열이름 in ["recency", "frequency", "monetary"]:
            백분위순위 = 결과[열이름].rank(method="average", pct=True, ascending=(열이름 != "recency"))
            결과[열이름 + "_score"] = 넘파이.ceil(백분위순위 * 4).clip(1, 4).astype(int)
        결과["segment"] = 넘파이.select(
            [
                (결과.recency_score >= 3) & (결과.frequency_score >= 3) & (결과.monetary_score >= 3),
                (결과.recency_score >= 3) & (결과.frequency == 1),
                결과.recency_score <= 2,
                결과.frequency_score >= 3,
            ],
            ["VIP", "Recent one-day", "Older activity", "Repeat"],
            default="Other",
        )
        return 결과.reset_index()

    load_data = 데이터불러오기
    handle_missing_values = 그룹별결측치채우기
    detect_outliers = IQR이상치찾기
    calculate_rfm = 고객별RFM계산
    add_text_features = 텍스트길이추가
    image_features = 이미지평균표준편차계산

DataAnalyzer = 데이터분석기

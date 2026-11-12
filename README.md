# H&M 상품 데이터 분석과 고객 세분화

H&M 공개 상품·거래 데이터를 이용해 결측치 처리, 이미지 수치화, 탐색적 데이터 분석(EDA), RFM 고객 세분화를 연습하는 프로젝트입니다.

## 현재 진행 상태

이 저장소는 **학습 중인 분석 초안**입니다. 상품 정보 105,542행과 거래 데이터의 첫 200,000행(2018-09-20~24), 상품 이미지 40장을 분석했습니다. 거래 표본은 짧은 연속 기간이므로 장기 단골이나 실제 이탈을 판단하는 근거로 사용할 수 없습니다.

- 상품명 길이와 이미지의 평균·표준편차 추출
- 상품과 거래 데이터를 상품 ID로 연결
- IQR 이상치 탐지 및 차트 6종
- 고객별 구매일 수와 금액을 이용한 RFM 분류
- 남은 작업: 실제 결측값 대치 검증, 의미 있는 변수 쌍의 상관관계 해석, 수치 근거·실행·검증을 포함한 인사이트 3개, 표본 범위 개선, 실제 화면 캡처

## 데이터와 한계

원본은 [H&M Personalized Fashion Recommendations](https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations/data)입니다. 데이터는 비상업·학술 연구용 원본 조건을 따릅니다. 재배포 조건과 크기를 고려해 원본 데이터 및 상품 이미지는 저장소에 포함하지 않습니다.

- 상품: [상품 데이터 배포처](https://huggingface.co/datasets/microsoft/hnm-search-data/tree/main/data/raw), `articles.csv`
- 거래: [거래 데이터 배포처](https://huggingface.co/datasets/dinhlnd1610/HM-Personalized-Fashion-Recommendations/tree/main/transactions), 7개 분할 중 첫 번째 Parquet 파일의 첫 200,000행
- 이미지: [상품 이미지 배포처](https://huggingface.co/datasets/einrafh/hnm-fashion-recommendations-data/tree/main/data/raw/images), 상품 ID별 JPEG 40장
- 거래 데이터에 주문번호가 없어 Frequency는 **고유 구매일 수**를 사용합니다. 원본 `price`의 정확한 변환·통화 단위가 확인되지 않아 원화 또는 실제 금액으로 표시하지 않습니다.

## 실행 방법

Python 3.8 이상에서 NumPy, Pandas, Matplotlib, Seaborn과 Jupyter 환경을 준비합니다. 거래 Parquet을 CSV로 변환할 때는 추가로 Parquet 읽기 엔진이 필요합니다. 과제 분석 자체는 허용된 네 라이브러리를 사용합니다.

```bash
python -m pip install numpy pandas matplotlib seaborn notebook
jupyter notebook notebooks/analysis_report.ipynb
```

노트북 실행 전 아래 경로에 데이터를 직접 준비해야 합니다.

```text
data/raw/hm/
├── articles.csv
├── transactions_sample_200000.csv
└── images/<상품 ID 앞 세 자리>/<상품 ID>.jpg
```

거래 CSV는 첫 번째 Parquet 분할의 첫 200,000행을 변환한 것입니다. 이미지 파일명은 10자리 상품 ID입니다. 데이터 준비 절차는 원본의 이용 조건을 확인하고 진행해 주세요.

## 파일 구성

- `src/pipeline.py`: 초기 데이터 탐색 및 `DataAnalyzer` 진입점
- `src/analyzer.py`: 데이터 로드, 그룹별 대치, IQR, 이미지 피처, RFM 계산
- `notebooks/analysis_report.ipynb`: 실제 실행 결과가 저장된 분석 노트북
- `MISSION.md`: 과제 요구사항과 학습 계획

## 표본에서 확인한 수치

2026-11-12에 실행한 노트북 기준, 거래 표본 200,000행 중 상품 ID 미매칭은 0행이며, IQR 1.5배 기준 가격 이상치 후보는 16,578행입니다. 이는 오류로 확정된 값이 아닙니다. 5일 표본에서 고객 51,527명이 관찰되었으며, 분류 결과는 해당 표본에만 적용됩니다.

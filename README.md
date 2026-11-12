# H&M 상품 분석과 RFM 고객 세분화

H&M 상품·거래·이미지 데이터를 연결해 결측치를 처리하고, NumPy 이미지 특성, IQR, 시각화, 고객 세분화를 구현한 데이터 분석 프로젝트다.

## 분석 데이터

- 상품: 105,542행, 25개 컬럼. 상품명, 카테고리, 설명 등을 포함한다.
- 거래: 원본 첫 번째 분할에서 고객 ID의 SHA-256 해시를 이용해 고객 약 1%를 선택하고, 선택된 고객의 해당 분할 내 거래를 모두 사용했다. 45,374행, 고객 5,932명, 기간 2018-09-20~2019-01-04다.
- 이미지: 상품 ID에 연결된 사진 40장. 사진 전체가 아닌 슬라이싱한 공통 20×20 영역의 픽셀을 분석한다.
- 출처: [H&M Personalized Fashion Recommendations](https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations/data). [상품 메타데이터](https://huggingface.co/datasets/microsoft/hnm-search-data/tree/main/data/raw), [거래 분할](https://huggingface.co/datasets/dinhlnd1610/HM-Personalized-Fashion-Recommendations/tree/main/transactions), [상품 이미지](https://huggingface.co/datasets/einrafh/hnm-fashion-recommendations-data/tree/main/data/raw/images). 원본 조건에 따른 비상업·학술 연구용 자료다.

**해석의 한계:** 구매일 수는 주문 횟수의 대용값이다. 첫 번째 분할과 한정된 관찰기간 밖의 구매는 보이지 않으므로 고객의 실제 신규 가입·이탈·생애가치를 확정할 수 없다. 판매 채널에는 오프라인도 포함된다. `price`는 원본의 정규화 값이며 통화 단위와 실제 금액으로 해석하지 않는다.

## 분석 결과와 비즈니스 제안

1. **최근성과 빈도가 모두 높은 VIP 규칙 대상**
   - 근거: 5,932명 중 1,647명(27.76%)이고 관찰 기간 평균 구매일 수는 4.50일이다.
   - 실행: VIP 대상에게 상품 우선 안내나 멤버십 혜택을 제공해 재방문을 유도한다.
   - 검증: 이후 기간 거래와 혜택 제공 여부를 결합해 무작위 비교군의 재구매율과 비교해야 효과를 판단할 수 있다.
2. **관찰 기간 초반 이후 구매가 드문 Older activity 대상**
   - 근거: 2,963명(49.95%)이고 기준일 이후가 아닌 기준일까지의 평균 마지막 구매 경과일은 67.44일이다.
   - 실행: 이 그룹에 맞춤형 상품 안내를 시범 제공해 다시 방문하도록 유도한다.
   - 검증: 관찰 종료 후의 구매 기록과 메시지 수신 동의가 필요하며, 기간 밖에 구매한 고객이 있다면 실제 이탈로 보기 어렵다.
3. **최근 한 구매일만 관찰된 Recent one-day 대상**
   - 근거: 890명(15.00%)이며 관찰 기간 내 구매일은 고객당 1일이다.
   - 실행: 이 그룹에 구매 상품과 연관된 카테고리 안내를 제공해 다음 구매를 유도한다.
   - 검증: 이전 구매 이력과 캠페인 비교군이 필요하다. 관찰 기간 전 구매가 있었다면 신규 고객이라는 가정은 성립하지 않는다.

위 제안은 표본에 근거한 가설이며 성과를 보장하지 않는다.

## 주요 구현

- 상품 설명 길이 결측 416개를 상품군별 중앙값으로 대치했다.
- 이미지 평균·표준편차를 NumPy 배열 연산으로 계산하고 상품표에 연결했다.
- IQR 1.5배 기준 이상치 후보 2,893행을 탐지하고 전후 박스플롯을 비교했다. 원본 거래를 삭제하지 않았다.
- 히스토그램, 박스플롯, 막대그래프, 히트맵, 산점도, 월별 라인차트를 작성했다.
- Recency, Frequency, Monetary 점수와 4개 이상 그룹을 계산했다.

## 실행 방법

Python 3.8 이상과 NumPy, Pandas, Matplotlib, Seaborn, Jupyter가 필요하다. 최초 데이터 준비를 위해서만 Parquet 읽기 엔진 `pyarrow`가 추가로 필요하다. 분석에는 NumPy, Pandas, Matplotlib, Seaborn을 사용한다.

```bash
python -m pip install numpy pandas matplotlib seaborn notebook pyarrow
```

원본 이용 조건을 확인하고 다음을 `data/raw/hm/`에 준비한다.

1. 상품 배포처에서 `articles.csv`를 다운로드한다.
2. 거래 배포처의 `train-00000-of-00007.parquet`을 `transactions-part-00000.parquet`이라는 이름으로 다운로드한다.
3. 아래 이미지 준비 스크립트로 상품 파일 앞쪽 40개 ID의 이미지를 다운로드한다.
4. 고객 표본을 생성하고 노트북을 실행한다.

```bash
python scripts/prepare_hm_sample.py
python scripts/prepare_hm_images.py
jupyter notebook notebooks/analysis_report.ipynb
```

노트북의 이미지 피처는 준비한 이미지 파일을 읽으므로, 다른 이미지를 선택하면 이미지 관련 수치가 달라진다. 원본 데이터와 이미지는 재배포 조건 및 용량 때문에 이 저장소에 포함하지 않는다.

## 프로젝트 구조

```text
src/pipeline.py                    # 과제용 DataAnalyzer 클래스
src/analyzer.py                    # 분석 메서드 구현
notebooks/analysis_report.ipynb    # 실행 결과와 해석
scripts/prepare_hm_sample.py       # 원본 거래 분할에서 표본 생성
scripts/prepare_hm_images.py       # 상품 이미지 준비
```

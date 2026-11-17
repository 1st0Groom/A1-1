# 분석 데이터 준비

이 프로젝트는 H&M Personalized Fashion Recommendations 데이터를 사용한다.

- 원본: https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations/data
- 이용 규정: https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations/rules

공식 규정 7.B(Data Security)는 규정에 동의하지 않은 비참가자에게 데이터를 공개·재배포하지 않도록 정하고 있다. 따라서 이 공개 저장소에는 원본 CSV·거래 표본·상품 이미지를 재업로드하지 않는다. 비상업적 학습 목적의 사용과 공개 재배포 허용은 별개다.

로컬 분석에 필요한 파일:

| 경로 | 내용 |
|---|---|
| `raw/hm/articles.csv` | 상품 105,542행·25열 |
| `raw/hm/transactions_customer_sample.csv` | 분석 거래 표본 45,374행·5열 |
| `raw/hm/images/` | 상품 ID 기반 JPEG 40장 |

`manifest.json`에는 실제 분석 입력 파일들의 바이트 크기와 SHA-256을 기록했다. 데이터 내용은 포함하지 않는다. 기존 코드의 데이터 출처와 준비 스크립트는 저장소 루트 README에서 확인한다. 다운로드·사용 전 원본 규정을 확인한다.

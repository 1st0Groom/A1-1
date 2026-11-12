"""미션에서 요구하는 데이터 분석 파이프라인 진입점."""
try:
    from .analyzer import 데이터분석기
except ImportError:
    from analyzer import 데이터분석기


class DataAnalyzer(데이터분석기):
    """전처리, 특성 추출 및 RFM을 제공하는 분석 클래스."""

    def 요약통계(self, 열목록):
        """선택한 수치형 열의 평균, 사분위수와 표준편차를 반환한다."""
        return self.데이터표[열목록].describe()

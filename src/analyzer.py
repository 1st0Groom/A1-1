"""기존 학습 코드의 분석기 이름을 유지한다."""
if __package__:
    from .pipeline import DataAnalyzer
else:
    from pipeline import DataAnalyzer

데이터분석기 = DataAnalyzer

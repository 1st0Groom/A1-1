"""과제에서 요구하는 데이터 분석 클래스의 공개 진입점."""

try:
    from .analyzer import DataAnalyzer
except ImportError:
    from analyzer import DataAnalyzer

__all__ = ["DataAnalyzer"]

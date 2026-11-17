import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd

from src.pipeline import DataAnalyzer


class PipelineTests(unittest.TestCase):
    def test_rfm_values_scores_and_ties(self):
        분석기 = DataAnalyzer('unused.csv')
        분석기.데이터표 = pd.DataFrame({
            'customer_id': ['A', 'A', 'A', 'B', 'C'],
            'order_date': ['2020-01-01', '2020-01-03', '2020-01-03', '2020-01-01', '2020-01-01'],
            'amount': [10, 20, 5, 5, 5],
            'purchase_day': ['1', '3', '3', '1', '1'],
        })
        결과 = 분석기.calculate_rfm('customer_id', 'order_date', 'amount', 'purchase_day').set_index('customer_id')
        self.assertEqual(결과.loc['A', 'monetary'], 35)
        self.assertEqual(결과.loc['A', 'frequency'], 2)
        self.assertEqual(결과.loc['A', 'recency'], 0)
        self.assertEqual(결과.loc['B', 'recency'], 2)
        self.assertGreater(결과.loc['A', 'recency_score'], 결과.loc['B', 'recency_score'])
        self.assertEqual(결과.loc['B', 'monetary_score'], 결과.loc['C', 'monetary_score'])
        self.assertIn('segment', 결과.columns)
        with self.assertRaises(ValueError):
            분석기.calculate_rfm('customer_id', 'order_date', 'amount', 'purchase_day', 분석기준일='2019-12-31')

    def test_images_join_by_id_and_use_vector_statistics(self):
        분석기 = DataAnalyzer('unused.csv')
        분석기.데이터표 = pd.DataFrame({'article_id': ['0000000002', '0000000001', '0000000003']})
        with tempfile.TemporaryDirectory() as directory:
            for name in ['0000000001.jpg', '0000000002.jpg']:
                (Path(directory) / name).touch()
            def read(path):
                return np.full((400, 400, 3), int(Path(path).stem))
            with patch('src.analyzer.이미지읽기.imread', side_effect=read):
                결과 = 분석기.상품이미지특성추가(directory)
        self.assertEqual(결과['image_mean'].iloc[:2].tolist(), [2, 1])
        self.assertEqual(결과['image_std'].iloc[:2].tolist(), [0, 0])
        self.assertTrue(pd.isna(결과['image_mean'].iloc[2]))

    def test_real_missing_values_and_iqr(self):
        분석기 = DataAnalyzer('unused.csv')
        분석기.데이터표 = pd.DataFrame({'group': ['a'] * 5, 'value': [1, 2, 3, None, 100]})
        분석기.handle_missing_values('value', 'group')
        self.assertEqual(분석기.데이터표['value_filled'].iloc[3], 2.5)
        self.assertTrue(분석기.detect_outliers('value')['mask'].iloc[4])


if __name__ == '__main__':
    unittest.main()

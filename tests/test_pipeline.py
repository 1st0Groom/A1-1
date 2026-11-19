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
            with patch('src.pipeline.mpimg.imread', side_effect=read):
                결과 = 분석기.상품이미지특성추가(directory)
        self.assertEqual(결과['image_mean'].iloc[:2].tolist(), [2, 1])
        self.assertEqual(결과['image_std'].iloc[:2].tolist(), [0, 0])
        self.assertTrue(pd.isna(결과['image_mean'].iloc[2]))

    def test_complete_pipeline_preserves_inputs_and_can_run_again(self):
        with tempfile.TemporaryDirectory() as directory:
            폴더 = Path(directory)
            상품파일 = 폴더 / 'articles.csv'
            거래파일 = 폴더 / 'transactions.csv'
            이미지폴더 = 폴더 / 'images'
            이미지폴더.mkdir()
            상품원본 = pd.DataFrame({
                'article_id': [1, 2], 'prod_name': ['Shirt', 'Trousers'],
                'product_group_name': ['Clothing', 'Clothing'],
                'detail_desc': ['Soft cotton', None],
            })
            상품원본.to_csv(상품파일, index=False)
            pd.DataFrame({
                'customer_id': ['A', 'A', 'B', 'B', 'A'],
                'article_id': [1, 2, 1, 2, 2],
                't_dat': ['2020-01-01', '2020-01-02', '2020-01-02', '2020-01-03', '2020-01-04'],
                'price': [10, 20, 20, 30, 100],
            }).to_csv(거래파일, index=False)
            for 번호 in [1, 2]:
                (이미지폴더 / f'{번호:010d}.jpg').touch()
            분석기 = DataAnalyzer(상품파일)
            with patch('src.pipeline.mpimg.imread', return_value=np.ones((400, 400, 3))):
                결과 = 분석기.run(거래파일, 이미지폴더, 분석기준일='2020-01-05')
                재실행결과 = 분석기.run(거래파일, 이미지폴더, 분석기준일='2020-01-05')
            pd.testing.assert_frame_equal(결과['상품원본표'], pd.read_csv(상품파일))
            self.assertEqual(결과['대치전결측수'], 1)
            self.assertEqual(결과['대치후결측수'], 0)
            self.assertEqual(결과['결측치현황'].loc['detail_desc', 'missing_ratio'], .5)
            self.assertTrue(결과['상품표']['image_mean'].eq(1).all())
            self.assertEqual(int(결과['이상치결과']['mask'].sum()), 1)
            self.assertIn('description_length_filled', 결과['상관행렬'].columns)
            self.assertTrue(결과['거래표']['amount'].equals(결과['거래표']['price']))
            고객A = 결과['고객지표'].set_index('customer_id').loc['A']
            self.assertEqual(고객A['monetary'], 130)
            self.assertEqual(고객A['frequency'], 3)
            self.assertEqual(고객A['recency'], 1)
            pd.testing.assert_frame_equal(결과['고객지표'], 재실행결과['고객지표'])
            잘못된거래 = pd.read_csv(거래파일)
            잘못된거래.loc[0, 'article_id'] = 999
            잘못된거래.to_csv(거래파일, index=False)
            with patch('src.pipeline.mpimg.imread', return_value=np.ones((400, 400, 3))):
                with self.assertRaisesRegex(ValueError, '연결되지 않는 거래'):
                    분석기.run(거래파일, 이미지폴더)


    def test_real_missing_values_and_iqr(self):
        분석기 = DataAnalyzer('unused.csv')
        분석기.데이터표 = pd.DataFrame({'group': ['a'] * 5, 'value': [1, 2, 3, None, 100]})
        분석기.handle_missing_values('value', 'group')
        self.assertEqual(분석기.데이터표['value_filled'].iloc[3], 2.5)
        self.assertTrue(분석기.detect_outliers('value')['mask'].iloc[4])


if __name__ == '__main__':
    unittest.main()

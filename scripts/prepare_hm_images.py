"""Download the first 40 H&M article images used in the notebook."""
from pathlib import Path
import csv
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1] / 'data/raw/hm'
BASE = 'https://huggingface.co/datasets/einrafh/hnm-fashion-recommendations-data/resolve/main/data/raw/images'
with (ROOT / 'articles.csv').open(encoding='utf-8', newline='') as file:
    ids = [row['article_id'].zfill(10) for _, row in zip(range(40), csv.DictReader(file))]
failed = []
for article_id in ids:
    target = ROOT / 'images' / article_id[:3] / (article_id + '.jpg')
    if target.exists() and target.read_bytes()[:2] == b'\xff\xd8':
        continue
    try:
        with urllib.request.urlopen(f'{BASE}/{article_id[:3]}/{article_id}.jpg', timeout=30) as response:
            image = response.read()
        if image[:2] != b'\xff\xd8':
            raise ValueError('not a JPEG')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(image)
    except (OSError, ValueError) as error:
        failed.append((article_id, str(error)))
if failed:
    raise RuntimeError(f'Failed to download {len(failed)} images: {failed}')
print(f'Confirmed {len(ids)} JPEG images')

"""Prepare a reproducible customer sample from the downloaded H&M parquet part."""
from pathlib import Path
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/raw/hm/transactions-part-00000.parquet'
OUTPUT = ROOT / 'data/raw/hm/transactions_customer_sample.csv'
# Select customers by a stable SHA-256 prefix; retain every transaction of each selected customer.
import hashlib
file = pq.ParquetFile(SOURCE)
selected = []
for batch in file.iter_batches(batch_size=100000):
    data = batch.to_pandas()
    customers = data['customer_id'].dropna().unique()
    eligible = {c for c in customers if int(hashlib.sha256(c.encode()).hexdigest()[:8],16) % 100 == 0}
    selected.append(data[data['customer_id'].isin(eligible)])
result = pd.concat(selected, ignore_index=True)
result.to_csv(OUTPUT,index=False)
print(f'rows={len(result)} customers={result.customer_id.nunique()} dates={result.t_dat.min()}..{result.t_dat.max()}')

import numpy as np
import pandas as pd

n_files = 5
rows_per_file = 10
letters = ["A", "B", "C", "D"]

rng = np.random.default_rng(1488)

for i in range(1, n_files + 1):
    categories = rng.choice(letters, size=rows_per_file)
    values = rng.random(rows_per_file) * 100.0
    df = pd.DataFrame({"category": categories, "value": values})
    df.to_csv(f"data_{i}.csv", index=False, float_format="%.3f")

print("Готово: создано 5 файлов data_1.csv ... data_5.csv в текущей папке.")

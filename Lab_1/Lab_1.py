import numpy
import pandas
from concurrent.futures import ProcessPoolExecutor

LETTERS = ["A", "B", "C", "D"]
N_FILES = 5
ROWS_PER_FILE = 20
SEED = 2025
CSV_DECIMALS = 3
PRINT_DECIMALS = 3

def generate_csv_files():
    rng = numpy.random.default_rng(SEED)
    for i in range(1, N_FILES + 1):
        categories = rng.choice(LETTERS, size=ROWS_PER_FILE)
        values = rng.random(ROWS_PER_FILE) * 100.0
        data = pandas.DataFrame({"category": categories, "value": values})
        data.to_csv(
            f"data_{i}.csv",
            index=False,
            float_format=f"%.{CSV_DECIMALS}f"
        )

def per_file_stats(filename):
    data = pandas.read_csv(filename)
    group = data.groupby("category")["value"]
    median = group.median()
    std = group.std(ddof=1)
    result = pandas.DataFrame({"median": median, "std": std}).reindex(LETTERS)
    return filename, result

def fmt(x):
    return "nan" if pandas.isna(x) else f"{x:.{PRINT_DECIMALS}f}"

def main():
    generate_csv_files()

    files = [f"data_{i}.csv" for i in range(1, N_FILES + 1)]
    with ProcessPoolExecutor() as pool:
        results = list(pool.map(per_file_stats, files))

    print("Пофайловые статистики (буква: median, std):")
    all_medians = {L: [] for L in LETTERS}
    for fname, stats in results:
        stats.to_csv(fname.replace(".csv", "_stats.csv"), float_format=f"%.{CSV_DECIMALS}f")
        print(f"\nФайл: {fname}")
        for L in LETTERS:
            m = stats.loc[L, "median"] if L in stats.index else numpy.nan
            s = stats.loc[L, "std"] if L in stats.index else numpy.nan
            print(f"{L}: median={fmt(m)}, std={fmt(s)}")
            if not pandas.isna(m):
                all_medians[L].append(float(m))

    rows = []
    for L in LETTERS:
        ser = pandas.Series(all_medians[L], dtype="float")
        median_of_medians = ser.median() if not ser.empty else numpy.nan
        std_of_medians = ser.std(ddof=1) if len(ser) >= 2 else numpy.nan
        rows.append((L, median_of_medians, std_of_medians))

    agg_data = pandas.DataFrame(rows, columns=["category", "median_of_medians", "std_of_medians"])
    agg_data.set_index("category", inplace=True)
    agg_data.to_csv("median_of_medians.csv", float_format=f"%.{CSV_DECIMALS}f")

    print("\nИтог: медиана из медиан и стандартное отклонение из медиан (по буквам):")
    for L in LETTERS:
        mom = agg_data.loc[L, "median_of_medians"]
        som = agg_data.loc[L, "std_of_medians"]
        print(f"{L}: median_of_medians={fmt(mom)}, std_of_medians={fmt(som)}")

if __name__ == "__main__":
    main()

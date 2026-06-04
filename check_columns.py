import pandas as pd

df = pd.read_csv('viewing_data.csv')
print("컬럼명:")
for i, col in enumerate(df.columns):
    print(f"{i}: {repr(col)}")

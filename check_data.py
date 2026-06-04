import pandas as pd

df = pd.read_csv(r'c:\biyam_work\viewing_data.csv')
print('데이터프레임 형태:', df.shape)
print('\n컬럼:', df.columns.tolist())
print('\n첫 3행:')
print(df.head(3))
print('\n데이터 통계:')
print(df.describe())

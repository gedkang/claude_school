import os
import csv
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TABLE_NAME = "viewing_data"

# CSV 파일 읽기
csv_file = "viewing_data_long.csv"
data = []

with open(csv_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        data.append({
            "시간": row["시간"],
            "채널명": row["채널명"],
            "시청가구수": int(row["시청가구수"])
        })

# 테이블이 있으면 전체 데이터 삭제 후 새로 삽입
try:
    supabase.table(TABLE_NAME).delete().neq("시간", "").execute()
    print(f"기존 {TABLE_NAME} 테이블 데이터 삭제됨")
except Exception as e:
    print(f"테이블이 없거나 삭제 중 오류: {e}")

# 데이터 삽입 (배치 처리)
batch_size = 1000
for i in range(0, len(data), batch_size):
    batch = data[i:i + batch_size]
    try:
        supabase.table(TABLE_NAME).insert(batch).execute()
        print(f"배치 {i // batch_size + 1} 삽입 완료: {len(batch)}개 행")
    except Exception as e:
        print(f"배치 {i // batch_size + 1} 삽입 오류: {e}")

print(f"\n총 {len(data)}개의 행이 {TABLE_NAME} 테이블에 업로드되었습니다!")

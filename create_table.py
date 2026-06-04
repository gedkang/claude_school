import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# SQL로 테이블 생성
create_table_sql = """
CREATE TABLE IF NOT EXISTS viewing_data (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  "시간" TIMESTAMP NOT NULL,
  "채널명" TEXT NOT NULL,
  "시청가구수" INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_viewing_data_time ON viewing_data("시간");
CREATE INDEX IF NOT EXISTS idx_viewing_data_channel ON viewing_data("채널명");
"""

try:
    result = supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
    print("테이블 생성 시도 (RPC 방식)")
except Exception as e:
    print(f"RPC 방식 실패: {e}")
    print("\n대신 직접 SQL 쿼리 실행 시도...")

    try:
        # 직접 SQL 실행 (Supabase admin API)
        from postgrest import AsyncPostgrestClient
        import httpx

        async def create_table():
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
                    headers={
                        "Authorization": f"Bearer {SUPABASE_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={"sql": create_table_sql}
                )
                print(response.text)

        import asyncio
        asyncio.run(create_table())
    except Exception as e2:
        print(f"직접 SQL 실행도 실패: {e2}")
        print("\nSupabase 대시보드에서 수동으로 다음 SQL을 실행하세요:")
        print(create_table_sql)

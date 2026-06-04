import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 프로젝트 ID 추출
project_id = SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")

# PostgreSQL 연결 정보
# Supabase는 기본값으로 postgres 사용자를 제공합니다
# 비밀번호는 프로젝트 생성 시 설정한 것입니다

# 더 나은 방법: Supabase의 SQL 편집기 API 사용
print("Supabase 테이블 생성 중...")

# SQL 쿼리
sql_query = """
CREATE TABLE IF NOT EXISTS public.viewing_data (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  "시간" TIMESTAMP NOT NULL,
  "채널명" TEXT NOT NULL,
  "시청가구수" INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_viewing_data_time ON public.viewing_data("시간");
CREATE INDEX IF NOT EXISTS idx_viewing_data_channel ON public.viewing_data("채널명");

ALTER TABLE public.viewing_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for all users" ON public.viewing_data
  FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users" ON public.viewing_data
  FOR INSERT WITH CHECK (true);
"""

# Supabase의 관리 API를 사용하려면 service_role 키가 필요합니다
# 대신 REST API를 통해 직접 데이터를 삽입합니다

# 테이블 생성을 위해서는 Supabase 대시보드를 수동으로 사용해야 할 수도 있습니다
print("\n[안내] 다음 단계를 실행하세요:")
print("1. Supabase 대시보드 접속: https://supabase.com/dashboard")
print("2. 프로젝트 선택")
print("3. 좌측 메뉴에서 'SQL Editor' 클릭")
print("4. '+ New Query' 버튼 클릭")
print("5. 아래 SQL을 복사하여 붙여넣기:")
print("\n" + "="*80)
print(sql_query)
print("="*80)
print("\n6. '▶ Run' 버튼 클릭하여 실행")
print("\n또는 아래 명령을 실행하세요 (리눅스/맥에서 psql이 설치된 경우):")
print(f"psql -h db.{project_id}.supabase.co -U postgres -d postgres < create_viewing_data_table.sql")

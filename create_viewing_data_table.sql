-- viewing_data 테이블 생성
CREATE TABLE IF NOT EXISTS public.viewing_data (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  "시간" TIMESTAMP NOT NULL,
  "채널명" TEXT NOT NULL,
  "시청가구수" INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_viewing_data_time ON public.viewing_data("시간");
CREATE INDEX IF NOT EXISTS idx_viewing_data_channel ON public.viewing_data("채널명");

-- RLS 정책 (모든 사용자가 읽을 수 있도록)
ALTER TABLE public.viewing_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for all users" ON public.viewing_data
  FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users" ON public.viewing_data
  FOR INSERT WITH CHECK (true);

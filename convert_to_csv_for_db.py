import json
from datetime import datetime, timedelta
import sys
from datetime import datetime as dt
import oracledb

LOG_FILE = r'c:\biyam_work\convert_log.txt'

# ──────────────────────────────────────────────
# [수정 필요] Oracle DB 접속 정보
# ──────────────────────────────────────────────
DB_USER     = "your_username"
DB_PASSWORD = "your_password"
DB_HOST     = "your_host"
DB_PORT     = 1521
DB_SERVICE  = "your_service_name"   # SID 사용 시: oracledb.makedsn(host, port, sid="SID")

# [수정 필요] 입력 대상 테이블 및 컬럼명
TABLE_NAME   = "TMBSDATA"
COL_TIME     = "GATHER_DATE"            # 시간 컬럼
COL_CHANNEL  = "CHANNEL_NM"  # 채널명 컬럼
COL_VIEWERS  = "WATCH_CNT"  # 시청가구수 컬럼
# ──────────────────────────────────────────────


def log(msg):
    timestamp = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def parse_lasttime(lasttime_str):
    return datetime.strptime(lasttime_str, "%Y%m%d%H%M%S")


def generate_timestamps(base_time, num_data_points):
    timestamps = []
    current_time = base_time
    for i in range(num_data_points):
        timestamps.append(current_time)
        current_time -= timedelta(seconds=10)
    return timestamps[::-1]


def load_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def build_rows(json_file):
    """JSON 파일을 읽어 (시간, 채널명, 시청가구수) 행 목록으로 반환"""
    data = load_json_data(json_file)

    base_time = parse_lasttime(data['lastTime'])

    today_data     = data['cvc']['today']
    yesterday_data = data['cvc']['yesterday']
    lastweek_data  = data['cvc']['lastWeek']
    competitors    = data['shch']

    timestamps_today     = generate_timestamps(base_time, len(today_data))
    timestamps_yesterday = generate_timestamps(base_time, len(yesterday_data))
    timestamps_lastweek  = generate_timestamps(base_time, len(lastweek_data))

    competitor_data  = {}
    competitor_order = []
    for comp in competitors:
        comp_name = comp['name']
        competitor_data[comp_name] = {'data': comp['list'][::-1]}
        competitor_order.append(comp_name)

    today_data_rev     = today_data[::-1]
    yesterday_data_rev = yesterday_data[::-1]
    lastweek_data_rev  = lastweek_data[::-1]

    competitor_data_lengths = [len(competitor_data[n]['data']) for n in competitor_order]
    min_competitor_rows = min(competitor_data_lengths) if competitor_data_lengths else 0
    max_rows = min(len(today_data), len(yesterday_data), len(lastweek_data), min_competitor_rows)

    rows = []

    for i in range(max_rows):
        rows.append((timestamps_today[i],     '홈앤쇼핑(오늘)',   today_data_rev[i]))
    for i in range(max_rows):
        rows.append((timestamps_yesterday[i], '홈앤쇼핑(어제)',   yesterday_data_rev[i]))
    for i in range(max_rows):
        rows.append((timestamps_lastweek[i],  '홈앤쇼핑(지난주)', lastweek_data_rev[i]))
    for comp_name in competitor_order:
        comp_info = competitor_data[comp_name]
        for i in range(max_rows):
            if i < len(comp_info['data']):
                rows.append((timestamps_today[i], comp_name, comp_info['data'][i]))

    return rows


def insert_rows(rows):
    """행 목록을 Oracle DB에 row by row 입력. PK 무결성 오류는 무시하고 계속 진행."""
    dsn = f"{DB_HOST}:{DB_PORT}/{DB_SERVICE}"

    # thin=True 가 기본값이므로 Oracle Instant Client 불필요
    conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=dsn)
    cursor = conn.cursor()

    sql = (
        f"INSERT INTO {TABLE_NAME} ({COL_TIME}, {COL_CHANNEL}, {COL_VIEWERS}, INSERT_ID, INSERT_DATE, MODIFY_ID, MODIFY_DATE) "
        f"VALUES (:1, :2, :3, '161067', SYSDATE, '161067', SYSDATE)"
    )

    inserted = 0
    skipped  = 0

    for row in rows:
        try:
            cursor.execute(sql, row)
            inserted += 1
        except oracledb.IntegrityError:
            # PK 중복 등 무결성 오류 → 무시하고 다음 행 진행
            skipped += 1
        except Exception as e:
            # 예상치 못한 오류는 로그 후 계속
            log(f"  행 입력 오류 (무시): {e} | 데이터: {row}")
            skipped += 1

    conn.commit()
    cursor.close()
    conn.close()

    return inserted, skipped


if __name__ == '__main__':
    json_file = r'c:\biyam_work\latest.json'

    try:
        log("데이터 변환 시작")
        rows = build_rows(json_file)
        log(f"변환 완료: 총 {len(rows)}개 행")

        log("Oracle DB 입력 시작")
        inserted, skipped = insert_rows(rows)
        log(f"DB 입력 완료 — 성공: {inserted}건 / PK 중복 등 무시: {skipped}건")

    except Exception as e:
        import traceback
        log(f"오류 발생: {e}")
        log(traceback.format_exc())
        sys.exit(1)

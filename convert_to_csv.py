import json
from datetime import datetime, timedelta
import csv
import sys
from datetime import datetime as dt

LOG_FILE = r'c:\biyam_work\convert_log.txt'

def log(msg):
    timestamp = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {msg}"
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def parse_lasttime(lasttime_str):
    """Parse lastTime string (YYYYMMDDHHmmss) to datetime"""
    return datetime.strptime(lasttime_str, "%Y%m%d%H%M%S")

def generate_timestamps(base_time, num_data_points):
    """Generate timestamps going backwards in 10-second intervals"""
    timestamps = []
    current_time = base_time
    for i in range(num_data_points):
        timestamps.append(current_time)
        current_time -= timedelta(seconds=10)
    return timestamps[::-1]

def load_json_data(file_path):
    """Load JSON data from file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def convert_to_csv(json_file, csv_file):
    """Convert JSON viewing data to CSV"""
    data = load_json_data(json_file)

    base_time = parse_lasttime(data['lastTime'])

    # Prepare CVC data
    today_data = data['cvc']['today']
    yesterday_data = data['cvc']['yesterday']
    lastweek_data = data['cvc']['lastWeek']
    competitors = data['shch']

    # Generate timestamps for each dataset
    timestamps_today = generate_timestamps(base_time, len(today_data))
    timestamps_yesterday = generate_timestamps(base_time, len(yesterday_data))
    timestamps_lastweek = generate_timestamps(base_time, len(lastweek_data))

    # Process competitor data
    competitor_data = {}
    competitor_order = []
    for comp in competitors:
        comp_name = comp['name']
        comp_list = comp['list']
        comp_id = comp['chSvcId']

        competitor_data[comp_name] = {
            'id': comp_id,
            'rank': comp['rank'],
            'current': comp['current'],
            'data': comp_list[::-1],
        }
        competitor_order.append(comp_name)

    # Reverse data to chronological order
    today_data_rev = today_data[::-1]
    yesterday_data_rev = yesterday_data[::-1]
    lastweek_data_rev = lastweek_data[::-1]

    # Create CSV with proper fieldnames
    with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['시간', '홈앤쇼핑(오늘)', '홈앤쇼핑(어제)', '홈앤쇼핑(지난주)'] + competitor_order
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()

        # Determine max rows (최소 공통 데이터 길이 사용)
        competitor_data_lengths = [len(competitor_data[name]['data']) for name in competitor_order]
        min_competitor_rows = min(competitor_data_lengths) if competitor_data_lengths else 0
        max_rows = min(len(today_data), len(yesterday_data), len(lastweek_data), min_competitor_rows)

        for i in range(max_rows):
            row = {
                '시간': timestamps_today[i].strftime('%Y-%m-%d %H:%M:%S'),
                '홈앤쇼핑(오늘)': today_data_rev[i],
                '홈앤쇼핑(어제)': yesterday_data_rev[i] if i < len(yesterday_data_rev) else '',
                '홈앤쇼핑(지난주)': lastweek_data_rev[i] if i < len(lastweek_data_rev) else ''
            }

            # Add all competitor data in order
            for comp_name in competitor_order:
                comp_info = competitor_data[comp_name]
                row[comp_name] = comp_info['data'][i] if i < len(comp_info['data']) else ''

            writer.writerow(row)

    log(f"CSV 생성 완료: {csv_file}")
    log(f"  - 시간 행: {max_rows}개")
    log(f"  - 경쟁사 채널: {len(competitors)}개")
    log(f"  - 총 컬럼: {len(fieldnames)}개")

if __name__ == '__main__':
    json_file = r'c:\biyam_work\latest.json'
    csv_file = r'c:\biyam_work\viewing_data_3.csv'

    try:
        convert_to_csv(json_file, csv_file)
        log("작업 성공")
    except Exception as e:
        import traceback
        log(f"오류 발생: {e}")
        log(traceback.format_exc())
        sys.exit(1)

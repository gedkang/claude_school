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

def convert_to_csv_long(json_file, csv_file):
    """Convert JSON viewing data to long-format CSV (시간 | 채널명 | 시청가구수)"""
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

        competitor_data[comp_name] = {
            'data': comp_list[::-1],
        }
        competitor_order.append(comp_name)

    # Reverse data to chronological order
    today_data_rev = today_data[::-1]
    yesterday_data_rev = yesterday_data[::-1]
    lastweek_data_rev = lastweek_data[::-1]

    # Determine max rows
    competitor_data_lengths = [len(competitor_data[name]['data']) for name in competitor_order]
    min_competitor_rows = min(competitor_data_lengths) if competitor_data_lengths else 0
    max_rows = min(len(today_data), len(yesterday_data), len(lastweek_data), min_competitor_rows)

    # Create long-format CSV
    with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
        fieldnames = ['시간', '채널명', '시청가구수']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()

        # Write Home & Shopping data for today
        for i in range(max_rows):
            row = {
                '시간': timestamps_today[i].strftime('%Y-%m-%d %H:%M:%S'),
                '채널명': '홈앤쇼핑(오늘)',
                '시청가구수': today_data_rev[i]
            }
            writer.writerow(row)

        # Write Home & Shopping data for yesterday
        for i in range(max_rows):
            row = {
                '시간': timestamps_yesterday[i].strftime('%Y-%m-%d %H:%M:%S'),
                '채널명': '홈앤쇼핑(어제)',
                '시청가구수': yesterday_data_rev[i]
            }
            writer.writerow(row)

        # Write Home & Shopping data for last week
        for i in range(max_rows):
            row = {
                '시간': timestamps_lastweek[i].strftime('%Y-%m-%d %H:%M:%S'),
                '채널명': '홈앤쇼핑(지난주)',
                '시청가구수': lastweek_data_rev[i]
            }
            writer.writerow(row)

        # Write competitor data
        for comp_name in competitor_order:
            comp_info = competitor_data[comp_name]
            for i in range(max_rows):
                if i < len(comp_info['data']):
                    row = {
                        '시간': timestamps_today[i].strftime('%Y-%m-%d %H:%M:%S'),
                        '채널명': comp_name,
                        '시청가구수': comp_info['data'][i]
                    }
                    writer.writerow(row)

    total_rows = max_rows * (3 + len(competitors))
    log(f"Long-format CSV 생성 완료: {csv_file}")
    log(f"  - 총 행: {total_rows}개 (헤더 제외)")
    log(f"  - 시간 포인트: {max_rows}개")
    log(f"  - 채널: {3 + len(competitors)}개 (홈앤쇼핑 3개 + 경쟁사 {len(competitors)}개)")

if __name__ == '__main__':
    json_file = r'c:\biyam_work\latest.json'
    csv_file = r'c:\biyam_work\viewing_data_long.csv'

    try:
        convert_to_csv_long(json_file, csv_file)
        log("작업 성공")
    except Exception as e:
        import traceback
        log(f"오류 발생: {e}")
        log(traceback.format_exc())
        sys.exit(1)

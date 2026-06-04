import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open(r'c:\biyam_work\latest.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("shch 채널 수:", len(data['shch']))
for i, comp in enumerate(data['shch'], 1):
    print(f"  {i}. {comp['name']} (list: {len(comp['list'])})")

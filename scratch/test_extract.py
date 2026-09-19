import json
import re

with open('data/staging/phase1-candidate/parsed.json', 'r', encoding='utf-8') as f:
    parsed = json.load(f)
doc = parsed.get('doc:02/2025/NĐ-CP')
content = ''
for a in doc['articles']:
    if 'Điều 14' in a['content'] and a['structural_path'] == ['body', 'article:1', 'item:1']:
        content = a['content']

match = re.search(r'như sau:\s*[\n]*\s*[“\x22](.*?)[”\x22]?\s*$', content, re.DOTALL | re.IGNORECASE)
if match:
    print('MATCHED!')
    print(repr(match.group(1)[:100]))
else:
    print('NO MATCH')

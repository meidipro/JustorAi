import os
import sys
from supabase import create_client

sys.stdout.reconfigure(encoding='utf-8')

env_path = os.path.join(os.path.dirname(__file__), '.env')
env_vars = {}
with open(env_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            if '=' in line:
                key, val = line.split('=', 1)
                env_vars[key.strip()] = val.strip().strip('"').strip("'")

url = env_vars.get('VITE_SUPABASE_URL')
key = env_vars.get('SUPABASE_SERVICE_ROLE_KEY')

supabase = create_client(url, key)

print("Fetching chunks from Supabase (paginated)...")
all_data = []
limit = 1000
offset = 0

while True:
    res = supabase.table('document_chunks').select('act_name, section_number').range(offset, offset + limit - 1).execute()
    data = res.data
    if not data:
        break
    all_data.extend(data)
    offset += limit
    print(f"Fetched {len(all_data)} rows so far...")

from collections import Counter
counts = Counter([r['act_name'] for r in all_data])

print('\n=== ACTS IN DATABASE (AND CHUNK COUNTS) ===')
for act, count in counts.most_common():
    safe_act = str(act).encode('utf-8', 'ignore').decode('utf-8')
    print(f'{count} chunks | {safe_act}')

print('\n=== CHECKING SPECIFIC MISSING ONES ===')
missing_targets = [
    'Income Tax Act', 
    'Labour Act', 
    'Civil Courts Act', 
    'Hindu Women\'s Rights to Property Act, 1937',
    'Income Tax Ordinance',
    'State Acquisition and Tenancy Act',
    'Limitation Act'
]
for target in missing_targets:
    found = any(target.lower() in str(act).lower() for act in counts.keys() if act)
    print(f'{target}: {"FOUND" if found else "MISSING"}')

# Let's check SATA 1950 Section 96
sata_chunks = [r for r in all_data if r['act_name'] and 'State Acquisition and Tenancy Act' in r['act_name']]
sata_sections = [r['section_number'] for r in sata_chunks if r['section_number']]
print(f"\nSATA 1950 has {len(sata_sections)} sections in DB. Checking for Section 96:")
print(f"Section 96: {'YES' if '96' in sata_sections else 'NO'}")

# Let's check Penal Code Section 500
penal_chunks = [r for r in all_data if r['act_name'] and 'Penal Code' in r['act_name']]
penal_sections = [r['section_number'] for r in penal_chunks if r['section_number']]
print(f"\nPenal Code has {len(penal_sections)} sections in DB. Checking for Section 500:")
print(f"Section 500: {'YES' if '500' in penal_sections else 'NO'}")

# Let's also check if Article 113 or 115 is in Limitation Act
limitation_chunks = [r for r in all_data if r['act_name'] and 'Limitation Act' in r['act_name']]
lim_sections = [r['section_number'] for r in limitation_chunks if r['section_number']]
print(f"\nLimitation Act has {len(lim_sections)} sections in DB. Checking for Articles 113 and 115:")
print(f"Article 113: {'YES' if '113' in lim_sections else 'NO'}")
print(f"Article 115: {'YES' if '115' in lim_sections else 'NO'}")

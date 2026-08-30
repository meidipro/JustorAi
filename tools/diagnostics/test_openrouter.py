import urllib.request, json, os
from dotenv import load_dotenv

load_dotenv('.env')
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')

url = 'https://openrouter.ai/api/v1/embeddings'
headers = {
    'Authorization': f'Bearer {OPENROUTER_API_KEY}',
    'Content-Type': 'application/json'
}
data = {
    'model': 'baai/bge-m3',
    'input': ['Hello world', 'Justor AI test']
}
req = urllib.request.Request(url, headers=headers, data=json.dumps(data).encode('utf-8'))
try:
    with urllib.request.urlopen(req) as res:
        out = json.loads(res.read())
        print(f"Success! Got {len(out['data'])} embeddings.")
        print(f"Dimensions: {len(out['data'][0]['embedding'])}")
except Exception as e:
    print(f'Error: {e}')
    if hasattr(e, 'read'):
        print(e.read().decode())

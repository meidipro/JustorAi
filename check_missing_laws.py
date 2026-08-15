import os, json, glob

folders = ['knowledge', 'knowledge/new json']
for f in folders:
    for path in glob.glob(os.path.join(f, '*.json')):
        try:
            with open(path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                if isinstance(data, list) and len(data) > 0:
                    title = data[0].get('act_name') or data[0].get('title')
                elif isinstance(data, dict):
                    title = data.get('act_name') or data.get('title')
                else:
                    title = 'Unknown'
                print(f"{path}: {title} ({len(data) if isinstance(data, list) else 1} items)")
        except Exception as e:
            pass

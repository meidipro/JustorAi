from backend.backend import supabase

print('=== Civil Courts Act ===')
r = supabase.table('document_chunks').select('id, section_number, section_title, content').ilike('act_name', '%Civil Courts Act%').execute()
for c in sorted(r.data or [], key=lambda x: int(x['section_number']) if x.get('section_number') and str(x['section_number']).isdigit() else 999):
    sec = c.get('section_number')
    title = c.get('section_title')
    cid = c.get('id')
    content = (c.get('content') or '')[:60]
    print(f'  Sec: {sec} | Title: {title} | ID: {cid} | Content: {content}')

print('\n=== Criminal Procedure Sec 4, 7, 9, 4(1) ===')
r2 = supabase.table('document_chunks').select('id, section_number, section_title, content').ilike('act_name', '%Criminal Procedure%').in_('section_number', ['4', '7', '9', '4(1)', '4A', '6']).execute()
for c in sorted(r2.data or [], key=lambda x: str(x.get('section_number', ''))):
    sec = c.get('section_number')
    title = c.get('section_title')
    cid = c.get('id')
    content = (c.get('content') or '')[:60]
    print(f'  Sec: {sec} | Title: {title} | ID: {cid} | Content: {content}')

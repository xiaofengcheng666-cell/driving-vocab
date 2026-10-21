"""Road-test examiner commands as listening cards: hear the command -> know what to do."""
import sys, json, urllib.request
src, audio = sys.argv[1], sys.argv[2]
MODEL, DECK = 'Freya路考指令', '读音-驾校单词'
def ac(a, **p):
    r = json.load(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8765', json.dumps({'action': a, 'version': 6, 'params': p}).encode()), timeout=120))
    if r.get('error'): raise RuntimeError(a + ': ' + r['error'])
    return r['result']
base_css = ac('modelStyling', modelName='Freya单词')['css']
if MODEL not in ac('modelNames'):
    ac('createModel', modelName=MODEL, inOrderFields=['Key', 'English', 'Chinese', 'Action', 'Category', 'Audio'],
       css=base_css + '\n.cmd{font-size:28px;font-weight:600;margin-top:10px}.act{color:#1d6a48;font-size:20px;margin-top:10px}',
       cardTemplates=[{'Name': '听指令',
                       'Front': '<div class="hint">{{Category}} · 听考官指令，想一想该做什么</div><div class="word">{{Audio}}</div>',
                       'Back': '{{FrontSide}}<hr id="answer"><div class="cmd">{{English}}</div><div class="zh">{{Chinese}}</div><div class="act">👉 {{Action}}</div>'}])
rows = json.load(open(src, encoding='utf-8'))
have = {i['fields']['Key']['value'] for i in ac('notesInfo', notes=ac('findNotes', query=f'note:{MODEL}'))} if ac('findNotes', query=f'note:{MODEL}') else set()
notes = []
for n, (cat, en, zh, act) in enumerate(rows, 1):
    key = f'cmd-{n}'
    if key in have: continue
    name = f'freya_cmd_{n}.mp3'
    ac('storeMediaFile', filename=name, path=f'{audio}/cmd/{n}.mp3')
    notes.append({'deckName': DECK, 'modelName': MODEL, 'tags': ['驾照', '路考指令', 'freya单词卡'], 'options': {'allowDuplicate': True},
                  'fields': {'Key': key, 'English': en, 'Chinese': zh, 'Action': act, 'Category': cat, 'Audio': f'[sound:{name}]'}})
res = ac('addNotes', notes=notes) if notes else []
print('added', sum(1 for r in res if r), 'skipped', len(have))
print(DECK, len(ac('findCards', query=f'"deck:{DECK}"')), 'cards')

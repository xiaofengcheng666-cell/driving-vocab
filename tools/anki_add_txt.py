"""Add textbook words that are not yet in Anki (by Key), route cards to 读音-/拼写-教材单词, tag source + unit."""
import sys, json, urllib.request
textbook, audio, unit = sys.argv[1], sys.argv[2], sys.argv[3]
def ac(a, **p):
    r = json.load(urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8765', json.dumps({'action': a, 'version': 6, 'params': p}).encode()), timeout=120))
    if r.get('error'): raise RuntimeError(a + ': ' + r['error'])
    return r['result']
have = {i['fields']['Key']['value'] for i in ac('notesInfo', notes=ac('findNotes', query='note:Freya单词'))}
media = set(ac('getMediaFilesNames', pattern='freya_txt_*'))
def snd(key):
    name = f'freya_txt_{key}.mp3'
    if name not in media:
        ac('storeMediaFile', filename=name, path=f'{audio}/txt/{key}.mp3'); media.add(name)
    return f'[sound:{name}]'
notes = []
for n, r in enumerate(json.load(open(textbook, encoding='utf-8'))['data'], 1):
    key = f'txt-{n}'
    if key in have: continue
    src = '蓝色新词' if len(sys.argv) > 4 and r[0] in sys.argv[4].split(',') else '圈词'
    notes.append({'deckName': '读音-教材单词', 'modelName': 'Freya单词', 'tags': ['教材', src, unit, 'freya单词卡'], 'options': {'allowDuplicate': True},
                  'fields': {'Key': key, 'Word': r[0], 'Chinese': r[1], 'IPA': r[2], 'Phrase': r[3], 'PhraseZh': r[4],
                             'WordAudio': snd(f'w{n}'), 'WordSlow': snd(f'w{n}s'), 'PhraseAudio': snd(f'p{n}'), 'PhraseSlow': snd(f'p{n}s'),
                             'Source': f'教材 Pathways 1 · {unit} · {"蓝色印刷新词" if src == "蓝色新词" else "我圈的生词"} · p{r[5]}'}})
ids = ac('addNotes', notes=notes) if notes else []
ids = [i for i in ids if i]
if ids:
    ac('changeDeck', cards=ac('findCards', query='nid:' + ','.join(map(str, ids)) + ' card:拼写'), deck='拼写-教材单词')
print('added', len(ids), [n['fields']['Word'] for n in notes])

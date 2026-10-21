"""Load Freya's word lists into Anki through AnkiConnect.

Each word is one note (Key = drv-12 / txt-50, stable, so re-running only adds what is missing and never
touches review history). Two cards per note: 认词 (Chinese -> say the English) and 拼写 (hear it -> type it).
"""
import sys, os, json, urllib.request

driving_json, textbook_json, audio_dir = sys.argv[1:4]
MODEL = 'Freya单词'
ROOT = 'Freya单词卡'

def ac(action, **params):
    req = urllib.request.Request('http://127.0.0.1:8765', json.dumps({'action': action, 'version': 6, 'params': params}).encode())
    r = json.load(urllib.request.urlopen(req, timeout=60))
    if r.get('error'):
        raise RuntimeError(f'{action}: {r["error"]}')
    return r['result']

FIELDS = ['Key', 'Word', 'Chinese', 'IPA', 'Phrase', 'PhraseZh', 'WordAudio', 'WordSlow', 'PhraseAudio', 'PhraseSlow', 'Source']
CSS = """.card{font-family:-apple-system,"PingFang SC",sans-serif;font-size:22px;text-align:center;color:#1b2420;background:#f3f5f2;line-height:1.5}
.nightMode .card,.card.nightMode{color:#e6ece8;background:#121815}
.zh{font-size:30px;font-weight:600;margin:12px 0}
.word{font-size:40px;font-weight:700;color:#1d6a48;margin-top:8px}
.nightMode .word{color:#5bb47e}
.ipa{color:#5d6b64;font-size:20px}
.ph{margin-top:18px;font-size:22px}
.phzh{color:#5d6b64;font-size:18px}
.src{color:#97a69e;font-size:13px;margin-top:20px}
.hint{color:#5d6b64;font-size:16px}
input#typeans{font-size:24px}"""
TEMPLATES = [
    {'Name': '认词', 'Front': '<div class="zh">{{Chinese}}</div><div class="hint">先大声说出英文，再翻面</div>',
     'Back': '{{FrontSide}}<hr id="answer"><div class="word">{{Word}}</div><div class="ipa">{{IPA}}</div>{{WordAudio}}'
             '<div class="ph">{{Phrase}}</div><div class="phzh">{{PhraseZh}}</div>{{PhraseAudio}}'
             '<div class="hint">慢速：单词 {{WordSlow}} · 短语 {{PhraseSlow}}</div><div class="src">{{Source}}</div>'},
    {'Name': '拼写', 'Front': '<div class="hint">听读音，拼出英文</div>{{WordAudio}}<div class="zh">{{Chinese}}</div>'
             '<div class="hint">慢速 {{WordSlow}}</div>{{type:Word}}',
     'Back': '<div class="zh">{{Chinese}}</div>{{type:Word}}<div class="word">{{Word}}</div><div class="ipa">{{IPA}}</div>{{WordAudio}}'
             '<div class="ph">{{Phrase}}</div><div class="phzh">{{PhraseZh}}</div><div class="src">{{Source}}</div>'},
]

if MODEL not in ac('modelNames'):
    ac('createModel', modelName=MODEL, inOrderFields=FIELDS, css=CSS, cardTemplates=TEMPLATES)
    print('model created')

decks = []
drv = json.load(open(driving_json, encoding='utf-8'))
for n, r in enumerate(drv, 1):
    decks.append(('drv', n, r[:5], f'{ROOT}::1 驾校词汇', '加州驾照', ['驾照']))
txt = json.load(open(textbook_json, encoding='utf-8'))['data']
for n, r in enumerate(txt, 1):
    if n <= 49:
        decks.append(('txt', n, r[:5], f'{ROOT}::2 教材生词', f'教材 Animal Behavior · 我圈的生词 · p{r[5]}', ['教材', '圈词']))
    else:
        decks.append(('txt', n, r[:5], f'{ROOT}::2 教材生词', f'教材 Animal Behavior · 蓝色印刷新词 · p{r[5]}', ['教材', '蓝色新词']))

for d in sorted({x[3] for x in decks}):
    ac('createDeck', deck=d)

existing = set()
ids = ac('findNotes', query=f'note:{MODEL}')
if ids:
    for info in ac('notesInfo', notes=ids):
        existing.add(info['fields']['Key']['value'])

media_done = set(ac('getMediaFilesNames', pattern='freya_*'))
def media(deck, key):
    name = f'freya_{deck}_{key}.mp3'
    if name not in media_done:
        ac('storeMediaFile', filename=name, path=os.path.join(audio_dir, deck, key + '.mp3'))
        media_done.add(name)
    return f'[sound:{name}]'

notes = []
for deck, n, (w, zh, ipa, ph, phzh), deck_name, src, tags in decks:
    key = f'{deck}-{n}'
    if key in existing:
        continue
    notes.append({'deckName': deck_name, 'modelName': MODEL, 'tags': tags + ['freya单词卡'],
                  'options': {'allowDuplicate': True},
                  'fields': {'Key': key, 'Word': w, 'Chinese': zh, 'IPA': ipa, 'Phrase': ph, 'PhraseZh': phzh,
                             'WordAudio': media(deck, f'w{n}'), 'WordSlow': media(deck, f'w{n}s'),
                             'PhraseAudio': media(deck, f'p{n}'), 'PhraseSlow': media(deck, f'p{n}s'), 'Source': src}})

added = ac('addNotes', notes=notes) if notes else []
print('already there', len(existing), 'added', sum(1 for a in added if a), 'failed', sum(1 for a in added if not a))
for d in sorted({x[3] for x in decks}):
    print(d, ac('findCards', query=f'"deck:{d}"').__len__(), 'cards')

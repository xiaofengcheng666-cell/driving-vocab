"""Add a 'Senses' field (part of speech, Chinese meaning, English definition, example + translation for each
main sense) to every Freya单词 note, and show it on the back of both cards."""
import sys, json, html, urllib.request

MODEL = 'Freya单词'

def ac(action, **params):
    req = urllib.request.Request('http://127.0.0.1:8765', json.dumps({'action': action, 'version': 6, 'params': params}).encode())
    r = json.load(urllib.request.urlopen(req, timeout=120))
    if r.get('error'):
        raise RuntimeError(f'{action}: {r["error"]}')
    return r['result']

AUDIO = sys.argv[1]
senses = {}
for f in sys.argv[2:]:
    senses.update(json.load(open(f, encoding='utf-8')))

# Example audio is played by a small script button, not a [sound:] tag, so it never autoplays with the word.
# Leading "_" keeps Anki's Check Media from treating these files as unused.
stored = set(ac('getMediaFilesNames', pattern='_freya_ex_*'))
def ex_sound(key, i):
    deck, n = key.split('-')
    name = f'_freya_ex_{deck}_{n}_{i}.mp3'
    if name not in stored:
        ac('storeMediaFile', filename=name, path=f'{AUDIO}/ex/{deck}_{n}_{i}.mp3'); stored.add(name)
    return name

PLAY_ICON = '<svg viewBox="0 0 64 64"><circle cx="32" cy="32" r="29"/><path d="M26 20l18 12-18 12z"/></svg>'

def example(key, i, ex, exzh):
    """The whole example block (sentence + translation) is one tap target, like Momo.
    Example 1 keeps a [sound:] tag so it autoplays after the word; tapping its own button is left to Anki."""
    name = ex_sound(key, i)
    play = ("if(event.target.closest('.replay-button'))return;"
            f"if(window._fx)window._fx.pause();window._fx=new Audio('{name}');window._fx.play();")
    btn = f'[sound:{name}]' if i == 1 else f'<span class="explay">{PLAY_ICON}</span>'
    return (f'<div class="exrow" onclick="{play}"><div class="ex"><span class="extext">{html.escape(ex)}</span>{btn}</div>'
            f'<div class="exzh">{html.escape(exzh)}</div></div>')

def render(key, items):
    out = []
    for i, (pos, zh, en, ex, exzh, mark) in enumerate(items, 1):
        tag = {'本课': '<span class="tag here">本课</span>', '常用': '<span class="tag common">常用</span>'}.get(mark, '')
        out.append(f'<div class="sense"><div class="head"><span class="pos">{html.escape(pos)}</span> '
                   f'<span class="szh">{html.escape(zh)}</span>{tag}</div>'
                   f'<div class="def">{html.escape(en)}</div>'
                   + example(key, i, ex, exzh) + '</div>')
    return ''.join(out)

if 'Senses' not in ac('modelFieldNames', modelName=MODEL):
    ac('modelFieldAdd', modelName=MODEL, fieldName='Senses', index=10)

SENSES_BLOCK = '<div class="senses">{{Senses}}</div>'
ac('updateModelTemplates', model={'name': MODEL, 'templates': {
    '读音': {'Front': '<div class="zh">{{Chinese}}</div><div class="hint">先大声说出英文，再翻面</div>',
             'Back': '{{FrontSide}}<hr id="answer"><div class="word">{{Word}} {{WordAudio}}</div><div class="ipa">{{IPA}}</div>'
                     + SENSES_BLOCK + '<div class="src">{{Source}}</div>'},
    '拼写': {'Front': '<div class="hint">听读音，拼出英文</div>{{WordAudio}}<div class="zh">{{Chinese}}</div>{{type:Word}}',
             'Back': '<div class="zh">{{Chinese}}</div>{{type:Word}}<div class="word">{{Word}} {{WordAudio}}</div><div class="ipa">{{IPA}}</div>'
                     + SENSES_BLOCK + '<div class="src">{{Source}}</div>'}}})

css = ac('modelStyling', modelName=MODEL)['css']
if '.senses' not in css:
    css += """
.senses{text-align:left;max-width:640px;margin:22px auto 0;border-top:1px solid #d9e0db;padding-top:10px}
.sense{padding:10px 0;border-bottom:1px dashed #d9e0db}
.head{font-size:19px}
.pos{display:inline-block;min-width:2.6em;font-style:italic;color:#1d6a48;font-weight:600}
.szh{font-weight:600}
.tag{font-size:12px;border-radius:999px;padding:1px 8px;margin-left:8px;vertical-align:2px;border:1px solid currentColor}
.tag.here{color:#1d6a48}.tag.common{color:#b07a12}
.def{font-size:17px;color:#3b4a43;margin-top:3px}
.ex{font-size:17px;margin-top:4px}
.exzh{font-size:15px;color:#5d6b64}
.nightMode .def{color:#c9d3ce}.nightMode .pos,.nightMode .tag.here{color:#5bb47e}.nightMode .senses,.nightMode .sense{border-color:#2c3732}"""
    ac('updateModelStyling', model={'name': MODEL, 'css': css})

css2 = ac('modelStyling', modelName=MODEL)['css']
if '.explay' not in css2:
    ac('updateModelStyling', model={'name': MODEL, 'css': css2 + '''
/* example play buttons (script, not autoplay) */
.explay{display:inline-block;vertical-align:-8px;margin-left:3em;text-decoration:none}
.explay svg{width:32px;height:32px}
.explay circle{fill:#1d6a48}.explay path{fill:#fff}
.nightMode .explay circle{fill:#5bb47e}'''})

ids = ac('findNotes', query=f'note:{MODEL}')
infos = ac('notesInfo', notes=ids)
actions, missing = [], []
for info in infos:
    key = info['fields']['Key']['value']
    if key not in senses:
        missing.append(key); continue
    actions.append({'action': 'updateNoteFields', 'params': {'note': {'id': info['noteId'], 'fields': {'Senses': render(key, senses[key])}}}})
res = ac('multi', actions=actions)
errors = [r for r in res if isinstance(r, dict) and r.get('error')]
print('notes', len(infos), 'updated', len(actions), 'errors', len(errors), 'missing', missing)

import sys, os, re, json, asyncio
import edge_tts

driving, textbook, out = sys.argv[1], sys.argv[2], sys.argv[3]
VOICE = 'en-US-AvaNeural'

def speakable(t):
    t = t.replace('’', "'").replace(' / ', ', ').replace('—', ', ')
    # all-caps sign text reads better in normal case; keep short acronyms like HOV
    return re.sub(r"\b[A-Z][A-Z']{3,}\b", lambda m: m.group(0).lower(), t)

jobs = []
for d, rows in (('drv', json.load(open(driving, encoding='utf-8'))),
                ('txt', json.load(open(textbook, encoding='utf-8'))['data'])):
    os.makedirs(os.path.join(out, d), exist_ok=True)
    for n, r in enumerate(rows, 1):
        w, ph = speakable(r[0]), speakable(r[3])
        jobs += [(d, f'w{n}', w, '+0%'), (d, f'w{n}s', w, '-40%'),
                 (d, f'p{n}', ph, '+0%'), (d, f'p{n}s', ph, '-30%')]

async def one(sem, d, key, text, rate):
    path = os.path.join(out, d, key + '.mp3')
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return
    async with sem:
        for attempt in range(6):
            try:
                await edge_tts.Communicate(text, VOICE, rate=rate).save(path)
                if os.path.getsize(path) > 0:
                    return
            except Exception as e:
                err = e
            await asyncio.sleep(1.5 * (attempt + 1))
        print('FAILED', d, key, text, err)

async def main():
    sem = asyncio.Semaphore(4)
    await asyncio.gather(*(one(sem, *j) for j in jobs))

asyncio.run(main())
missing = [j[:2] for j in jobs if not os.path.exists(os.path.join(out, j[0], j[1] + '.mp3')) or os.path.getsize(os.path.join(out, j[0], j[1] + '.mp3')) == 0]
print(len(jobs), 'jobs,', len(missing), 'missing', missing[:10])

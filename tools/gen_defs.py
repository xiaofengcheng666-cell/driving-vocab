"""Ava (en-US-AvaNeural) audio for every English definition in the senses files.
Output: <out>/def/<drv|txt>_<n>_<i>.mp3 where <i> is the sense number (1-based)."""
import sys, os, json, asyncio
import edge_tts

out, files = sys.argv[1], sys.argv[2:]
os.makedirs(os.path.join(out, 'def'), exist_ok=True)
jobs = []
for f in files:
    for key, senses in json.load(open(f, encoding='utf-8')).items():
        deck, n = key.split('-')
        for i, s in enumerate(senses, 1):
            jobs.append((os.path.join(out, 'def', f'{deck}_{n}_{i}.mp3'), s[2].replace('’', "'")))

async def one(sem, path, text):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return
    async with sem:
        for attempt in range(6):
            try:
                await edge_tts.Communicate(text, 'en-US-AvaNeural').save(path)
                if os.path.getsize(path) > 0:
                    return
            except Exception as e:
                err = e
            await asyncio.sleep(1.5 * (attempt + 1))
        print('FAILED', path, text, err)

async def main():
    sem = asyncio.Semaphore(4)
    await asyncio.gather(*(one(sem, p, t) for p, t in jobs))

asyncio.run(main())
missing = [p for p, _ in jobs if not os.path.exists(p) or os.path.getsize(p) == 0]
print(len(jobs), 'definitions,', len(missing), 'missing')

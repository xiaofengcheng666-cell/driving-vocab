import sys, os, json, asyncio
import edge_tts
src, out = sys.argv[1], sys.argv[2]
os.makedirs(os.path.join(out, 'cmd'), exist_ok=True)
rows = json.load(open(src, encoding='utf-8'))
async def one(sem, n, text):
    p = os.path.join(out, 'cmd', f'{n}.mp3')
    if os.path.exists(p) and os.path.getsize(p) > 0: return
    async with sem:
        for a in range(6):
            try:
                await edge_tts.Communicate(text, 'en-US-AvaNeural').save(p)
                if os.path.getsize(p) > 0: return
            except Exception as e: err = e
            await asyncio.sleep(1.5 * (a + 1))
        print('FAILED', n, text)
async def main():
    sem = asyncio.Semaphore(4)
    await asyncio.gather(*(one(sem, n, r[1].replace('’', "'")) for n, r in enumerate(rows, 1)))
asyncio.run(main())
print(len(rows), 'commands')

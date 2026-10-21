"""Make every clip louder: +GAIN dB with a look-ahead peak limiter (ceiling -1 dBFS), re-encoded as
24 kHz mono 48 kbps MP3. Reads from src_dir, writes the same tree into dst_dir."""
import sys, os, subprocess, wave, array, tempfile
from concurrent.futures import ProcessPoolExecutor

GAIN_DB = 11.0
CEIL = 10 ** (-1.0 / 20) * 32767
LOOK = 120      # samples of look-ahead (5 ms at 24 kHz)
RELEASE = 0.9995

def boost(paths):
    src, dst = paths
    with tempfile.TemporaryDirectory() as td:
        wav, out = os.path.join(td, 'a.wav'), os.path.join(td, 'b.wav')
        subprocess.run(['lame', '--quiet', '--decode', src, wav], check=True)
        w = wave.open(wav); rate = w.getframerate(); a = array.array('h', w.readframes(w.getnframes())); w.close()
        g = 10 ** (GAIN_DB / 20)
        x = [s * g for s in a]
        n = len(x)
        # required gain per sample so that |x| never exceeds the ceiling, spread over the look-ahead window
        need = [1.0] * n
        for i, v in enumerate(x):
            av = abs(v)
            if av > CEIL:
                r = CEIL / av
                for j in range(max(0, i - LOOK), i + 1):
                    if need[j] > r: need[j] = r
        y = array.array('h', [0] * n)
        env = 1.0
        for i in range(n):
            t = need[i]
            env = t if t < env else min(1.0, 1 - (1 - env) * RELEASE)
            if env > t: env = t
            v = x[i] * env
            y[i] = int(max(-32767, min(32767, v)))
        o = wave.open(out, 'w'); o.setnchannels(1); o.setsampwidth(2); o.setframerate(rate); o.writeframes(y.tobytes()); o.close()
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        subprocess.run(['lame', '--quiet', '-m', 'm', '-b', '48', '--resample', '24', out, dst], check=True)
    return dst

if __name__ == '__main__':
    src_dir, dst_dir = sys.argv[1], sys.argv[2]
    jobs = []
    for root, _, files in os.walk(src_dir):
        for f in files:
            if f.endswith('.mp3'):
                s = os.path.join(root, f)
                jobs.append((s, os.path.join(dst_dir, os.path.relpath(s, src_dir))))
    with ProcessPoolExecutor() as ex:
        done = list(ex.map(boost, jobs, chunksize=4))
    print(len(done), 'clips boosted')

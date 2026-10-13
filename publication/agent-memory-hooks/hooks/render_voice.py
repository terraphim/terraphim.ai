#!/usr/bin/env python3
"""Use the existing local Emma voice at its natural rate, then verify timings."""
from pathlib import Path
import hashlib
import json
import wave
import numpy as np
from kokoro_onnx import Kokoro

ROOT = Path(__file__).resolve().parent
plan = json.loads((ROOT / "storyboard.json").read_text())
voice_dir = ROOT / "voice"
voice_dir.mkdir(exist_ok=True)
engine = Kokoro('/private/tmp/terraphim-kokoro-v1.0.onnx', '/private/tmp/terraphim-kokoro-voices-v1.0.bin')
engine.sess.disable_telemetry_events() if hasattr(engine.sess, 'disable_telemetry_events') else None
audio = np.zeros(plan['durationSeconds'] * 24000, dtype=np.float64)
for i, beat in enumerate(plan['beats']):
    path = voice_dir / (hashlib.sha256(beat['text'].encode()).hexdigest()[:16] + '.wav')
    if not path.exists():
        samples, rate = engine.create(beat['text'], voice='bf_emma', speed=1.0, lang='en-gb')
        with wave.open(str(path), 'wb') as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(rate)
            f.writeframes(np.round(np.clip(samples, -1, 1) * 32767).astype('<i2').tobytes())
    with wave.open(str(path)) as f:
        assert f.getframerate() == 24000 and f.getnchannels() == 1
        duration = f.getnframes() / f.getframerate()
        samples = np.frombuffer(f.readframes(f.getnframes()), dtype='<i2').astype(float) / 32768
    assert duration <= beat['end'] - beat['start'] - .25, (i, duration, beat)
    offset = round((beat['start'] + .2) * 24000)
    audio[offset:offset + len(samples)] += samples
    beat.update(audio=str(path.relative_to(ROOT)), audioDuration=duration,
                audioSha256=hashlib.sha256(path.read_bytes()).hexdigest())
    print(i, round(duration, 2), beat['title'], flush=True)
peak = float(np.max(np.abs(audio)))
assert peak > .01
audio *= 10**(-2/20) / peak
with wave.open(str(ROOT / 'narration.wav'), 'wb') as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(24000)
    f.writeframes(np.round(audio * 32767).astype('<i2').tobytes())
plan['voice']['processing'] = 'Fixed gain and scheduled silence; no time stretching or pitch change'
(ROOT / 'storyboard.json').write_text(json.dumps(plan, indent=2) + '\n')

def stamp(seconds):
    ms = round(seconds * 1000)
    return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d}.{ms%1000:03d}'

vtt = ['WEBVTT', '']
for beat in plan['beats']:
    words = beat['text'].split()
    count = (len(words) + 13) // 14
    for cue in range(count):
        start = cue * len(words) // count
        end = (cue + 1) * len(words) // count
        t0 = beat['start'] + .2 + beat['audioDuration'] * start / len(words)
        t1 = beat['start'] + .2 + beat['audioDuration'] * end / len(words)
        vtt += [f'{stamp(t0)} --> {stamp(t1)}', ' '.join(words[start:end]), '']
(ROOT / 'captions.vtt').write_text('\n'.join(vtt))
(ROOT / 'transcript.txt').write_text(plan['title'] + '\nSynthetic British female voice: Emma (Kokoro).\n\n' + '\n\n'.join(f"{b['start']}–{b['end']}s | {b['title']}\n{b['text']}" for b in plan['beats']) + '\n')

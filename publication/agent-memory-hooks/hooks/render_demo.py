#!/usr/bin/env python3
"""Render readable excerpts from the verified released hook and host receipts."""
import html
import json
from pathlib import Path
import subprocess
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / 'evidence/fresh-run'
OUT = ROOT / 'rendered'
OUT.mkdir(exist_ok=True)
(OUT / 'screenshots').mkdir(exist_ok=True)
read = lambda name: json.loads((EVIDENCE / name).read_text())
verification = read('verification.json')
assert verification['pass'] and verification['baseline_exit'] == 2 and verification['corrected_exit'] == 0
events = [json.loads(line) for line in (EVIDENCE / 'host-events.jsonl').read_text().splitlines()]
after = [event['data'] for event in events if event['type'] == 'native-after']
assert len(after) == 2
baseline, corrected = after
assert corrected['input']['command'] == verification['host_executed']
assert corrected['result']['metadata']['exit'] == 0
saved = read('validation.json')
assert json.loads(corrected['result']['output']['output']) == saved
plan = json.loads((ROOT / 'storyboard.json').read_text())
identity = read('identities.json')
esc = html.escape

def box(label, value, kind=''):
    return f'<section class="box {kind}"><h2>{esc(label)}</h2><pre>{esc(value)}</pre></section>'

disabled = json.loads(read('rewrite-disabled.json')['stdout'])
enabled = json.loads(read('rewrite-enabled.json')['stdout'])
learning = (EVIDENCE / 'learning-before-correction.md').read_text()
learning_excerpt = '\n'.join(line for line in learning.splitlines() if line.startswith(('id:', 'command:', 'exit_code:', 'captured_at:')))
items = [
    box('Actual host command', baseline['input']['command'], 'command') + box('Actual tool output · exit 2', baseline['result']['output']['output'], 'result') + '<p class="hero">A mistake worth<br><em>remembering.</em></p>',
    box('Saved learning · Markdown excerpt', learning_excerpt) + box('Error retained in the learning', baseline['result']['output']['output']) + '<p class="note">Actual after-tool event → project adapter → released learning hook</p>',
    box('Explicit reviewed mapping', 'python3 validate-brief.py --chek\n→ python3 validate-brief.py --check') + box('Actual compilation output', read('compile-corrections.json')['stdout'], 'result') + '<p class="note">Manual promotion to a tool preference · selected role loads compiled JSON</p>',
    box('Rewrite disabled · returned command', disabled['tool_input']['command'], 'command') + box('Rewrite enabled · actual returned JSON', json.dumps(enabled, indent=2), 'result') + '<p class="note">Standalone hook result. No validator has executed in this comparison.</p>',
    box('New host process · original attempt', verification['host_attempted'], 'command') + box('Actual after-tool event · excerpt', json.dumps({'command': corrected['input']['command'], 'exit': corrected['result']['metadata']['exit']}, indent=2), 'result') + '<p class="note">Included OpenCode V2 adapter applies the command through event.input.</p>',
    box('validation.json · actual saved file', json.dumps(saved, indent=2), 'result') + '<p class="note">Unrelated command: unchanged<br>Unrelated role: unchanged<br>Baseline: exit 2 → corrected execution: exit 0</p>',
    '<p class="hero">A reviewed correction.<br><em>A result you can check.</em></p><div class="download">Public brief + local adapter + saved traces<br>Release download + reproduction script</div><p class="url">terraphim.ai/how-tos/command-rewriting-howto/</p>'
]
css = '*{box-sizing:border-box}body{margin:0;background:#0c1422;color:#f5f7fa;font-family:Arial,sans-serif}.frame{width:1440px;height:960px;padding:38px 64px;display:flex;flex-direction:column}.top{font-size:19px;letter-spacing:.06em;color:#a2b8ce;display:flex;justify-content:space-between}.title{font-size:42px;margin:30px 0 24px;line-height:1.12}.content{flex:1;overflow:hidden}.box{background:#142237;border:1px solid #36516a;border-radius:14px;padding:20px 25px;margin-bottom:18px}h2{font-size:19px;color:#aec6dc;margin:0 0 12px;font-weight:normal}pre{font:25px/1.42 Menlo,monospace;white-space:pre-wrap;overflow-wrap:anywhere;margin:0}.command pre{color:#9edac2;font-size:22px}.result pre{font-size:23px}.hero{font-size:55px;line-height:1.3;margin:27px 0}.hero em{font-style:normal;color:#a7e5c9}.note{font-size:24px;line-height:1.5;color:#aec6dc}.controls{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin:25px 0}.control{border:1px solid #36516a;border-radius:14px;padding:28px;background:#142237}.control strong{display:block;font-size:76px;color:#a7e5c9;margin:18px 0}.control p{font-size:23px}.download{font-size:30px;line-height:1.6;color:#c8d5e3}.url{font-size:25px;color:#a7e5c9;margin-top:40px}.footer{border-top:1px solid #36516a;padding-top:17px;font-size:18px;color:#a2b8ce;display:flex;justify-content:space-between}.badge{color:#f5ce84}'
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width':1440, 'height':960}, device_scale_factor=1)
    for i, (beat, body) in enumerate(zip(plan['beats'], items)):
        doc = f'<!doctype html><meta charset="utf-8"><style>{css}</style><div class="frame"><div class="top"><span>TERRAPHIM · LEARNING AND HOOKS</span><span class="badge">AGENT 1.21.19 · OPENCODE 2.0.20</span></div><h1 class="title">{esc(beat["title"])}</h1><div class="content">{body}</div><div class="footer"><span>Actual saved outputs · readable excerpt view · synthetic narration</span><span>{i+1:02d} / 07</span></div></div>'
        (OUT / f'scene-{i}.html').write_text(doc)
        page.set_content(doc)
        assert page.locator('.content').evaluate('(e)=>e.scrollHeight<=e.clientHeight'), f'overflow in scene {i}'
        page.screenshot(path=str(OUT / f'scene-{i}.png'))
        if i in (0,3,5):
            name = {0:'poster',3:'hook-output',5:'executed-result'}[i]
            page.screenshot(path=str(OUT / 'screenshots' / f'{name}.jpg'), type='jpeg', quality=92)
    browser.close()
concat=[]
for i,beat in enumerate(plan['beats']):
    concat += [f"file 'scene-{i}.png'", f"duration {beat['end']-beat['start']}"]
concat.append("file 'scene-6.png'")
(OUT / 'frames.txt').write_text('\n'.join(concat)+'\n')
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(OUT/'frames.txt'),'-i',str(ROOT/'narration.wav'),'-t',str(plan['durationSeconds']),'-vf','fps=25,format=yuv420p','-c:v','libx264','-preset','medium','-crf','19','-c:a','aac','-b:a','160k','-movflags','+faststart',str(OUT/'agent-hooks.mp4')],check=True)
(OUT/'render-receipt.json').write_text(json.dumps({'qualification':'released-binary','identities':identity,'durationSeconds':plan['durationSeconds'],'source':'evidence/fresh-run','outputPresentation':'Readable excerpts preserving actual source values; no simulated terminal execution.','manualPromotion':True,'adapterRequired':True},indent=2)+'\n')
print(OUT/'agent-hooks.mp4')

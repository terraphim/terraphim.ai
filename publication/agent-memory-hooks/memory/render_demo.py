#!/usr/bin/env python3
"""Render a labelled walkthrough from actual CLI receipts, never invented outputs."""
import argparse
import html
import json
from pathlib import Path
import subprocess
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--run', required=True, type=Path)
parser.add_argument('--output', required=True, type=Path)
parser.add_argument('--candidate-preview', action='store_true')
args = parser.parse_args()
run = args.run.resolve()
out = args.output.resolve()
out.mkdir(parents=True, exist_ok=True)
(out / 'screenshots').mkdir(exist_ok=True)
verification = json.loads((run / 'verification.json').read_text())
assert verification['status'] == 'PASS' and all(verification['checks'].values())
assert args.candidate_preview or verification['qualification'] == 'released-binary'
plan = json.loads((ROOT / 'storyboard.json').read_text())
read = lambda name: json.loads((run / 'outputs' / (name + '.stdout.json')).read_text())
capture, shown, found = read('capture'), read('reopened'), read('retrieved')
lesson = shown['memory_item']['content']
assert found['items'][0]['content'] == lesson
assert found['items'][0]['id'] == capture['memory_id']
esc = html.escape

def box(label, value, kind=''):
    return f'<section class="box {kind}"><h2>{esc(label)}</h2><pre>{esc(value)}</pre></section>'

def terminal(command, result):
    return box('Command excerpt · runner supplies JSON format, config and isolated store', '$ ' + command, 'command') + box('Actual saved output', result, 'result')

brief = (run / 'fixture/brief.md').read_text()
items = [
    box('The public Harbour brief', brief) + '<p class="hero">Keep the instruction.<br><em>Find it next time.</em></p>',
    box('lesson.md · authored instruction', lesson) + terminal('terraphim-agent memory capture --file lesson.md\n  --provenance-tag harbour-public-brief-v1', json.dumps(capture, indent=2)),
    terminal('terraphim-agent memory show ' + capture['memory_id'], json.dumps({'id': shown['id'], 'content': lesson, 'tags': shown['memory_item']['tags']}, indent=2)) + '<p class="note">Capture has exited. This is a new process reading the saved item.</p>',
    box('Brief validation · concept note', (run / 'fixture/kg/brief/brief-validation.md').read_text()) + box('Project brief · concept note', (run / 'fixture/kg/brief/project-brief.md').read_text()) + '<p class="note">Explicit project terminology · two connected concepts in the saved lesson</p>',
    terminal('terraphim-agent memory retrieve "validate brief" --role "Brief Reviewer"', json.dumps({'role': found['role'], 'count': found['count'], 'content': found['items'][0]['content'], 'matched_concepts': found['items'][0]['matched_concepts'], 'tags': found['items'][0]['tags']}, indent=2)),
    '<div class="controls">' + ''.join(f'<section class="control"><h2>{esc(label)}</h2><strong>{count}</strong><p>{esc(detail)}</p></section>' for label,count,detail in [('Brief Reviewer', found['count'], 'validate brief'), ('Unrelated question', read('unrelated-query')['count'], 'volcanic eruption'), ('Finance Reviewer', read('other-role')['count'], 'validate brief'), ('Separate empty store', read('separate-store')['count'], 'validate brief')]) + '</div><p class="note">Actual retrieved-item counts. Roles filter concepts; separate folders hold separate stores.</p>',
    '<p class="hero">One lesson.<br><em>Ready for the next run.</em></p><div class="download">Public brief + lesson + graph<br>Commands + saved outputs + checksums</div><p class="url">terraphim.ai/posts/cold-start-tax-agentic-memory/</p>'
]
css = '''*{box-sizing:border-box}body{margin:0;background:#0c1422;color:#f5f7fa;font-family:Arial,sans-serif}.frame{width:1440px;height:960px;padding:38px 64px;display:flex;flex-direction:column}.top{font-size:19px;letter-spacing:.06em;color:#a2b8ce;display:flex;justify-content:space-between}.title{font-size:42px;margin:30px 0 24px;line-height:1.12}.content{flex:1;overflow:hidden}.box{background:#142237;border:1px solid #36516a;border-radius:14px;padding:20px 25px;margin-bottom:18px}h2{font-size:19px;color:#aec6dc;margin:0 0 12px;font-weight:normal}pre{font:25px/1.42 Menlo,monospace;white-space:pre-wrap;overflow-wrap:anywhere;margin:0}.command pre{color:#9edac2;font-size:22px}.result pre{font-size:23px}.hero{font-size:55px;line-height:1.3;margin:27px 0}.hero em{font-style:normal;color:#a7e5c9}.note{font-size:24px;line-height:1.5;color:#aec6dc}.controls{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin:25px 0}.control{border:1px solid #36516a;border-radius:14px;padding:28px;background:#142237}.control strong{display:block;font-size:76px;color:#a7e5c9;margin:18px 0}.control p{font-size:23px}.download{font-size:30px;line-height:1.6;color:#c8d5e3}.url{font-size:25px;color:#a7e5c9;margin-top:40px}.footer{border-top:1px solid #36516a;padding-top:17px;font-size:18px;color:#a2b8ce;display:flex;justify-content:space-between}.badge{color:#f5ce84}'''
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width':1440,'height':960}, device_scale_factor=1)
    for i,(beat,body) in enumerate(zip(plan['beats'], items)):
        badge = 'CANDIDATE PREVIEW' if args.candidate_preview else 'RELEASED BINARY · ' + verification['binaryVersion']
        doc = f'<!doctype html><meta charset="utf-8"><style>{css}</style><div class="frame"><div class="top"><span>TERRAPHIM · PROJECT MEMORY</span><span class="badge">{esc(badge)}</span></div><h1 class="title">{esc(beat["title"])}</h1><div class="content">{body}</div><div class="footer"><span>Actual CLI outputs · readable excerpt view · synthetic narration</span><span>{i+1:02d} / 07</span></div></div>'
        (out / f'scene-{i}.html').write_text(doc)
        page.set_content(doc)
        assert page.locator('.content').evaluate('(e)=>e.scrollHeight<=e.clientHeight'), f'overflow in scene {i}'
        page.screenshot(path=str(out / f'scene-{i}.png'))
        if i in (0,2,5):
            name = {0:'poster',2:'saved-lesson',5:'retrieval-controls'}[i]
            page.screenshot(path=str(out / 'screenshots' / f'{name}.jpg'), type='jpeg', quality=92)
    browser.close()

concat = []
for i,beat in enumerate(plan['beats']):
    concat += [f"file 'scene-{i}.png'", f"duration {beat['end']-beat['start']}"]
concat.append("file 'scene-6.png'")
(out / 'frames.txt').write_text('\n'.join(concat)+'\n')
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(out/'frames.txt'),'-i',str(ROOT/'narration.wav'),'-t',str(plan['durationSeconds']),'-vf','fps=25,format=yuv420p','-c:v','libx264','-preset','medium','-crf','19','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out/'agent-memory.mp4')],check=True)
(out/'render-receipt.json').write_text(json.dumps({'qualification':verification['qualification'],'sourceRun':str(run),'binarySha256':verification['binarySha256'],'outputPresentation':'Excerpts from actual CLI JSON, preserving source strings and numbers. No simulated terminal execution.','durationSeconds':plan['durationSeconds'],'scenes':7,'candidatePreview':args.candidate_preview},indent=2)+'\n')
print(out/'agent-memory.mp4')

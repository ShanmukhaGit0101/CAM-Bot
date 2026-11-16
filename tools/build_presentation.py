#!/usr/bin/env python3
"""Build an offline, evidence-backed CAM-BOT deck; never alter source captures."""

import argparse
import base64
import hashlib
import html
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
CAPTURE = ROOT / 'experiments/machine_tending/runs/ay10-visual-20261015-03'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect():
    metrics_path = CAPTURE / 'raw_analysis/metrics.json'
    metrics = json.loads(metrics_path.read_text())
    for name, expected in metrics['input_sha256'].items():
        if digest(CAPTURE / 'raw' / name) != expected:
            raise ValueError('raw input differs from qualified analysis: ' + name)
    scenario = metrics['scenarios'][0]
    if len(metrics['scenarios']) != 1 or metrics['ay10']['qualification'] != 'VISUAL_SIMULATION_PASS':
        raise ValueError('expected the single qualified visual scenario')
    rows = [json.loads(line) for line in (CAPTURE / 'raw/trials.events.jsonl').read_text().splitlines()]
    first_trial = rows[0]['trial_id']
    events = [{'t': row['monotonic_elapsed_s'], 'action': row['action'],
               'state': row['state'], 'result': row['result'],
               'workpiece': row['details'].get('workpiece_state', '')}
              for row in rows if row['trial_id'] == first_trial and
              (row['result'] in ('STEP_STARTED', 'STEP_COMPLETED') or
               row['action'] == 'FSM' and row['result'] == 'SUCCESS')]
    if not events or events[-1]['result'] != 'SUCCESS' or events[-1]['workpiece'] != 'FINISHED_AT_S5':
        raise ValueError('recorded replay must retain a complete successful trial')
    if any(b['t'] < a['t'] for a, b in zip(events, events[1:])):
        raise ValueError('recorded replay times are not monotonic')
    images = {
        'rviz': CAPTURE / 'raw/rviz_runtime.png',
        'cycles': CAPTURE / 'raw_analysis/cycle_time_by_trial.png',
        'workspace': ROOT / 'experiments/workspace/runs/model-study-20261107/study/workspace.png',
        'cad': ROOT / 'design/compact_module/generated/preview.png',
    }
    for path in images.values():
        if not path.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'):
            raise ValueError('image missing or still an LFS pointer: ' + str(path))
    sources = [metrics_path, CAPTURE/'raw/trials.csv', CAPTURE/'raw/trials.events.jsonl',
               ROOT/'docs/TASK_ALLOCATION.md', ROOT/'docs/evidence/AY-13/independent_repeat.md',
               ROOT/'design/compact_module/generated/report.json',
               ROOT/'docs/evidence/TASK-08/mock_bimanual_20261115/combined/bimanual/result.json',
               ROOT/'docs/evidence/TASK-08/mock_bimanual_20261115/combined/probe/result.json',
               ROOT/'docs/evidence/TASK-08/mock_bimanual_20261115/combined/benchmark/summary.json',
               *images.values()]
    stats = {'attempts': scenario['attempts'], 'successes': scenario['successful_attempts'],
             'mean_s': scenario['successful_cycle_time']['mean_s'],
             'sd_s': scenario['successful_cycle_time']['sample_stdev_s'],
             'repositions': scenario['carrier_repositions_completed']}
    return stats, {'trial_id': first_trial, 'capture': str(CAPTURE.relative_to(ROOT)),
                   'mode': 'recorded_visual_event_replay', 'events': events}, images, sources


def slides(stats):
    return [
        dict(tag='FINAL PROJECT • TOPS 2026', title='CAM-BOT', subtitle='Global reach. Local manipulation.\nOne coordinated visual workflow.',
             bullets=['Carrier-assisted Adaptive Manipulation with Bimanual Operational Technology',
                      'UR5 carrier + flange-mounted dual-arm concept', 'ROS 2 Humble visual demonstrator'],
             notes='Ayush opens (35 seconds). Our goal is to demonstrate the coordination architecture and make its behavior measurable. This is the completed visual-simulation project. We will show the live workflow or its retained event replay, then evidence and contributions.'),
        dict(tag='01 • MOTIVATION', title='Separate transit from local work', subtitle='A carrier moves between stations; smaller arms represent local handling.',
             bullets=['Global task: reach the raw, staging, machine, output and finished stations.',
                      'Local task: represent approach, grasp, release and handling near each station.',
                      'Research question: how should the two levels coordinate?'],
             notes='Shannu (40 seconds). Explain the carrier-assisted concept before discussing code. We investigate the architecture; we have not measured an efficiency advantage over a controlled conventional baseline.'),
        dict(tag='02 • ARCHITECTURE', title='One task-level coordinator', subtitle='UR5 → carrier flange → bimanual module',
             bullets=['Official UR5 chain preserved; custom module attaches after tool0.',
                      'ROS transforms + geometric workspace check inform local/reposition decisions.',
                      'State machine drives the visual sequence; events record what happened.'],
             diagram=True,
             notes='Shannu (50 seconds). Use the three architecture boxes. Global positioning and local actions meet in the coordinator. The accepted demonstration uses four placeholder joints and a geometric reachability proxy, not collision-aware grasp planning.'),
        dict(tag='03 • WORKCELL', title='Five stations, one visible sequence', subtitle='S1 raw → S2 staging → S3 machine → S4 output → S5 finished',
             bullets=['Start, cancel and reset through ROS services.', 'Workpiece state remains visible throughout the cycle.'],
             image='rviz', caption='Recorded RViz screenshot • qualified visual capture, October 2026',
             notes='Ayush (40 seconds). Point out the carrier, mounted local arms and the five stations. Explain the simulated workpiece. This screenshot is retained evidence; switch to the prepared live RViz window if available.'),
        dict(tag='04 • COORDINATION', title='Reposition only when the proxy requires it', subtitle='Check target → choose motion → observe final TF → recheck',
             bullets=['Locally reachable: use local visual manipulation.',
                      'Outside the local region: reposition the carrier, then check again.',
                      'Unreachable or cancelled: record a specific failure rather than pretend success.'],
             notes='Ayush or Shannu (45 seconds). Explain the actual decision contract. Local workspace checks are geometric proxies. The recorded scenario has five visual repositions per trial; do not call this globally optimal planning.'),
        dict(tag='05 • DEMONSTRATION', title='Watch one complete workflow', subtitle='Live RViz, or the clearly labelled archived-event replay below',
             bullets=['Start once. Follow the state changes. Finish at FINISHED_AT_S5 and HOME.'],
             replay=True,
             notes='Ayush (90 seconds including the demo). For live mode: run bash tools/present_demo.sh in the prepared Humble environment, then the start command in a second terminal. Otherwise use Play recorded trial in the HTML. Say explicitly that this replays event timestamps and states, with a static screenshot—not live ROS or animated robot reconstruction. Let it finish before moving on.'),
        dict(tag='06 • MEASURED RESULTS', title='Repeatable within the fixed visual scenario', subtitle='Five qualified attempts; source data and analysis retained',
             stats=[f"{stats['successes']}/{stats['attempts']} visual successes",f"{stats['mean_s']:.3f} s mean",f"{stats['repositions']} repositions"],
             bullets=[f"Sample SD: {stats['sd_s']:.6f} s. Five visual repositions per trial.",
                      'Timing: first S1 approach through final HOME completion; initial setup excluded.'],
             image='cycles', caption='Published event-derived cycle durations • five trials; no comparative baseline',
             notes='Ayush (55 seconds). State the measurement boundary. The published 19.579117-second mean comes from events; the broader elapsed field in the raw CSV includes additional time. Five successes demonstrate this scenario, not industrial reliability, throughput or grasp accuracy.'),
        dict(tag='07 • ENGINEERING STUDIES', title='Explore the design space', subtitle='Carrier kinematics, placement and historical mass experiments',
             bullets=['20,006 carrier configurations sampled; five assumed placements compared.',
                      'Three archived +10% link-mass experiments analyzed as trajectory statistics.',
                      'Later IK/clearance diagnostics identified limits for future designs.'],
             image='workspace', caption='Preliminary carrier FK sample cloud • assumed layout, collision unchecked in this study',
             notes='Shannu (55 seconds). Show the workspace image as a kinematic study, not a guaranteed collision-free reachable volume. Mass-study recordings were not time-aligned and derived accelerations are not force/torque measurements. These studies show engineering investigation and transparent limits.'),
        dict(tag='08 • VERIFICATION', title='Reproducibility is part of the result', subtitle='Visual acceptance plus separately scoped controller experiments',
             bullets=['AY-01–AY-13 complete in accepted visual scope; independent human reproduction recorded.',
                      'Mock-backed controllers: 8 carrier + 7 bimanual protocol checks passed.',
                      'Separate 20/20 synthetic carrier cycles; one broadcaster and clean shutdown.'],
             notes='Ayush (50 seconds). Distinguish independent visual acceptance from agent-run controller experiments. GenericSystem supplies mock positions. The 20 cycles are carrier protocol benchmarks, not full physical or controller-backed tending cycles. We preserved failed attempts as well as passes.'),
        dict(tag='09 • MECHANICAL DIRECTION', title='From placeholder to an original compact concept', subtitle='A separate design study—not the model used in the accepted live demo',
             bullets=['14 valid solids; mounting plate, pedestals and elbow fork geometry.',
                      'Standalone four-joint model, meshes and explicit mass allocations.',
                      'Manufacture, hardware selection and physical validation remain future work.'],
             image='cad', caption='Original AI-assisted compact-module concept • preliminary design',
             notes='Tanmay presents the mechanical workstream (50 seconds). Explain mounting, local-arm layout and design evolution. The recent original compact model was AI-assisted at Ayush’s direction; do not claim that it was manufactured or individually authored by another member. Do not call the allocated mass a verified UR5 load qualification.'),
        dict(tag='10 • TEAM CONTRIBUTIONS', title='Three workstreams, one integrated deliverable', subtitle='Mechanical design → kinematics → software → validation',
             bullets=['Shannu / Shanmukha — kinematics, control architecture and integration workstream.',
                      'Tanmay — mechanical/carrier design, CAD and structural-concept workstream.',
                      'Ayush Ranjan — software, simulation, repository, integration and presentation.'],
             notes='All members (45 seconds total). These are documented workstreams and suggested speaking roles, not claims that every roadmap checkbox is complete. Use CONTRIBUTIONS.md to identify actual artifacts and attribution. Acknowledge upstream open-source tools and AI-assisted implementation/design support.'),
        dict(tag='FINAL TAKEAWAY', title='An integrated, reproducible visual demonstrator', subtitle='The primary project objective is delivered.',
             bullets=['Demonstrated: carrier/local coordination across a five-station workflow.',
                      'Measured: repeated visual trials with inspectable logs and analysis.',
                      'Next research: qualified grasping, controller-backed tending and physical validation.'],
             notes='Ayush closes (40 seconds). We are wrapping up the visual prototype, not asserting deployment readiness. Tasks 7–15 are future extensions outside this final delivery. The contribution is the integrated architecture, reproducible behavior, transparent measurements and documented engineering studies. Invite discussion.'),
    ]


def html_deck(items, replay, images):
    encoded = {key: 'data:image/png;base64,' + base64.b64encode(path.read_bytes()).decode()
               for key, path in images.items()}
    sections=[]
    for i, slide in enumerate(items):
        visual=''
        if slide.get('image'):
            visual=f'<figure><img src="{encoded[slide["image"]]}" alt="{html.escape(slide["caption"])}"><figcaption>{html.escape(slide["caption"])}</figcaption></figure>'
        if slide.get('diagram'):
            visual='<div class="architecture"><div>UR5 carrier<br><small>Global positioning</small></div><span>→</span><div>Flange interface<br><small>Mechanical connection</small></div><span>→</span><div>Local arms<br><small>Visual manipulation</small></div></div>'
        if slide.get('replay'):
            visual=f'''<div class="replay"><div class="replay-left"><img src="{encoded['rviz']}" alt="Static screenshot from the qualified RViz capture"><small>Recorded RViz screenshot · not animated robot motion</small></div><div class="telemetry"><div class="badge">ARCHIVED EVENT REPLAY · NOT LIVE ROS</div><div id="elapsed">0.000 s</div><strong id="event-state">Ready to replay</strong><div id="event-step">First qualifying trial</div><div id="workpiece">RAW_AT_S1</div><progress id="progress" value="0" max="1" aria-label="Replay progress"></progress><div class="stations">{''.join('<span id="station-'+str(n)+'">S'+str(n)+'</span>' for n in range(1,6))}</div><div class="controls"><button id="play">Play recorded trial</button><button id="reset">Reset</button><label>Speed <select id="speed"><option value="1">1×</option><option value="2">2×</option><option value="4">4×</option></select></label></div><small>Real log times and states · initial HOME included in replay</small></div></div>'''
        stats=''.join('<span>'+html.escape(s)+'</span>' for s in slide.get('stats',[]))
        sections.append(f'''<section class="slide {'active' if i==0 else ''}" aria-label="Slide {i+1}"><div class="tag">{html.escape(slide['tag'])}</div><h1>{html.escape(slide['title'])}</h1><p class="subtitle">{html.escape(slide['subtitle']).replace(chr(10),'<br>')}</p>{'<div class="stats">'+stats+'</div>' if stats else ''}<div class="content {'with-image' if slide.get('image') else ''}"><ul>{''.join('<li>'+html.escape(b)+'</li>' for b in slide['bullets'])}</ul>{visual}</div><aside class="notes">{html.escape(slide['notes'])}</aside><footer><span>CAM-BOT · visual demonstrator / supporting studies</span><span>{i+1:02} / {len(items):02}</span></footer></section>''')
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CAM-BOT — final presentation</title><style>
*{box-sizing:border-box}body{margin:0;background:#07131f;color:#edf4fa;font-family:Arial,Helvetica,sans-serif}button,select{font:inherit;border:1px solid #3d6578;background:#142c3c;color:#edf4fa;border-radius:7px;padding:9px 15px;cursor:pointer}button:hover{background:#245069}button:focus-visible,select:focus-visible{outline:3px solid #f5bd68}.slide{display:none;min-height:100vh;padding:5vh 6vw 90px;position:relative}.slide.active{display:block}.tag{color:#53d6ca;font-size:15px;font-weight:bold;letter-spacing:3px}h1{font-size:clamp(32px,3.8vw,62px);line-height:1.06;max-width:1100px;margin:20px 0} .subtitle{font-size:clamp(19px,1.8vw,29px);line-height:1.35;color:#b4cad7;max-width:1100px;margin:0 0 28px}.content{font-size:clamp(19px,1.65vw,27px);line-height:1.4}ul{margin:0;padding-left:24px;max-width:1080px}li{margin:0 0 22px}.with-image{display:grid;grid-template-columns: .85fr 1.15fr;gap:35px;align-items:center}.with-image ul{font-size:clamp(18px,1.4vw,24px)}figure{margin:0}figure img{width:100%;height:39vh;min-height:200px;object-fit:contain;background:#fff;border-radius:10px}figcaption,small{display:block;font-size:13px;line-height:1.4;color:#a8c1d1;margin-top:9px}.stats{display:flex;gap:16px;flex-wrap:wrap;margin:0 0 24px}.stats span{background:#12313c;border-left:4px solid #53d6ca;padding:12px 22px;font-size:24px;font-weight:bold}.architecture{display:flex;align-items:center;justify-content:center;gap:18px;margin-top:45px}.architecture div{border:1px solid #397186;border-radius:12px;padding:25px;background:#122c3d;text-align:center;font-size:24px}.architecture span{color:#53d6ca}.replay{display:grid;grid-template-columns:1.1fr 1fr;gap:24px;margin-top:22px}.replay-left img{width:100%;height:32vh;object-fit:contain;background:#12202c;border-radius:8px}.telemetry{background:#102839;padding:22px;border-radius:12px}.badge{font-size:12px;color:#f5bd68;letter-spacing:1px}#elapsed{font-size:32px;margin:12px 0;color:#53d6ca}#event-state{font-size:24px}#event-step,#workpiece{font-size:16px;margin-top:8px;overflow-wrap:anywhere}progress{width:100%;margin-top:18px;accent-color:#53d6ca}.stations{display:flex;gap:8px;margin-top:8px}.stations span{padding:5px 10px;border:1px solid #47616e;border-radius:5px;font-size:15px}.stations .selected{background:#53d6ca;color:#07131f}.controls{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:15px;font-size:14px}footer{position:absolute;bottom:26px;left:6vw;right:6vw;display:flex;justify-content:space-between;color:#8aa8bb;font-size:12px;letter-spacing:1px}.nav{position:fixed;right:25px;bottom:12px;display:flex;gap:8px;z-index:5}.notes{display:none;background:#173d46;color:#e2f1ef;padding:18px;font-size:16px;line-height:1.5;margin-top:20px}.show-notes .active .notes{display:block}.hint{position:fixed;left:20px;bottom:8px;font-size:11px;color:#7e9bad;z-index:6}@media(max-width:800px){.with-image,.replay{display:block}figure img{height:26vh}.architecture{flex-wrap:wrap}.slide{padding:30px 25px 100px}.replay-left{display:none}.nav{right:10px}footer{display:none}li{margin-bottom:12px}}@media print{@page{size:13.333in 7.5in;margin:0}body{background:#07131f!important;-webkit-print-color-adjust:exact;print-color-adjust:exact}.slide{display:block!important;width:13.333in;height:7.5in;min-height:0;padding:35px 50px 65px;page-break-after:always;overflow:hidden}.slide:last-of-type{page-break-after:auto}h1{font-size:38px}.tag{font-size:12px}.subtitle{font-size:21px;margin-bottom:20px}.content{font-size:21px}.with-image ul{font-size:18px}figure img{height:280px;min-height:0}.stats span{font-size:20px}.nav,.hint,.notes,.controls{display:none!important}.replay-left img{height:260px}.telemetry{padding:14px}.architecture{margin-top:25px}.slide footer{bottom:20px;left:50px;right:50px}.slide li{margin-bottom:18px}}
</style></head><body>''' + ''.join(sections) + '''<nav class="nav" aria-label="Slide controls"><button id="prev" aria-label="Previous slide">←</button><button id="next" aria-label="Next slide">→</button><button id="notes-toggle">Notes (N)</button></nav><div class="hint">Offline · arrow keys navigate · N toggles notes · print for static PDF</div><script>
const replay = ''' + json.dumps(replay).replace('<','\\u003c') + ''';
const slides=[...document.querySelectorAll('.slide')];let current=0,playing=false,time=0,last=0,raf=null;const end=replay.events[replay.events.length-1].t;
function stop(){playing=false;if(raf!==null)cancelAnimationFrame(raf);raf=null;document.querySelector('#play').textContent='Play recorded trial';}
function show(n){stop();current=Math.max(0,Math.min(slides.length-1,n));slides.forEach((s,i)=>s.classList.toggle('active',i===current));location.hash='slide-'+(current+1);}
document.querySelector('#prev').onclick=()=>show(current-1);document.querySelector('#next').onclick=()=>show(current+1);document.querySelector('#notes-toggle').onclick=()=>document.body.classList.toggle('show-notes');
document.addEventListener('keydown',e=>{if(['INPUT','SELECT','TEXTAREA'].includes(e.target.tagName))return;if(e.key==='ArrowRight'){e.preventDefault();show(current+1)}if(e.key==='ArrowLeft'){e.preventDefault();show(current-1)}if(e.key.toLowerCase()==='n')document.body.classList.toggle('show-notes')});
function render(){let event=replay.events[0];for(const row of replay.events){if(row.t<=time)event=row;else break;}document.querySelector('#elapsed').textContent=time.toFixed(3)+' s';document.querySelector('#event-state').textContent=event.state+(event.result==='SUCCESS'?' · COMPLETE':'');document.querySelector('#event-step').textContent=event.action+' · '+event.result;document.querySelector('#workpiece').textContent=event.workpiece;document.querySelector('#progress').value=time/end;const match=event.action.match(/^S([1-5])/);const station=match?Number(match[1]):(event.action==='MACHINE_DWELL'?3:0);for(let n=1;n<=5;n++)document.querySelector('#station-'+n).classList.toggle('selected',n===station)}
function tick(now){if(!playing)return;time=Math.min(end,time+(now-last)/1000*Number(document.querySelector('#speed').value));last=now;render();if(time>=end){stop();document.querySelector('#play').textContent='Replay complete';return;}raf=requestAnimationFrame(tick)}
document.querySelector('#play').onclick=()=>{if(playing){stop();return}if(time>=end)time=0;playing=true;last=performance.now();document.querySelector('#play').textContent='Pause';raf=requestAnimationFrame(tick)};document.querySelector('#reset').onclick=()=>{stop();time=0;render()};
function hashSlide(){const match=location.hash.match(/^#slide-([0-9]+)$/);if(match&&Number(match[1])-1!==current)show(Number(match[1])-1)}window.addEventListener('hashchange',hashSlide);hashSlide();render();
</script></body></html>'''


def powerpoint(items, images, output):
    # Optional export dependency; provenance tests also run in lean Humble images.
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.util import Inches, Pt

    deck=Presentation();deck.slide_width=Inches(13.333);deck.slide_height=Inches(7.5)
    bg=RGBColor.from_string('07131F');white=RGBColor.from_string('EDF4FA');muted=RGBColor.from_string('B4CAD7');accent=RGBColor.from_string('53D6CA')
    def text(slide,x,y,w,h,value,size=24,color=white,bold=False):
        frame=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h)).text_frame
        frame.word_wrap=True
        for i,line in enumerate(value.split('\n')):
            paragraph=frame.paragraphs[0] if i==0 else frame.add_paragraph()
            paragraph.text=line;paragraph.font.name='Arial';paragraph.font.size=Pt(size);paragraph.font.color.rgb=color;paragraph.font.bold=bold
        font=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
        if font.exists():
            frame.fit_text(font_family='DejaVu Sans',max_size=size,bold=bold,font_file=str(font))
        return frame
    def picture(slide,key,x,y,w,h):
        from PIL import Image
        with Image.open(images[key]) as img:iw,ih=img.size
        ratio=min(w/iw,h/ih);pw,ph=iw*ratio,ih*ratio
        slide.shapes.add_picture(str(images[key]),Inches(x+(w-pw)/2),Inches(y+(h-ph)/2),width=Inches(pw),height=Inches(ph))
    for index,item in enumerate(items):
        slide=deck.slides.add_slide(deck.slide_layouts[6]);slide.background.fill.solid();slide.background.fill.fore_color.rgb=bg
        text(slide,.6,.35,12,.35,item['tag'],13,accent,True)
        text(slide,.6,.92,12,1.15,item['title'],38,white,True)
        text(slide,.6,2.05,12,.85,item['subtitle'],22,muted)
        y=3.05
        if item.get('stats'):
            text(slide,.6,2.82,12,.6,'    |    '.join(item['stats']),22,accent,True);y=3.6
        width=5.25 if item.get('image') else 11.8
        if item.get('replay'):
            picture(slide,'rviz',.65,3.2,7,3.35)
            text(slide,8.1,3.3,4.4,2.5,'Start one live cycle\nor\nOpen CAM-BOT.html\nPlay recorded trial',26,accent,True)
            text(slide,8.1,5.85,4.4,.65,'HTML replay is archived events, not live ROS.',16,muted)
        else:
            for bullet in item['bullets']:
                text(slide,.7,y,width,.95,'• '+bullet,21 if item.get('image') else 24,white);y+=1.08
            if item.get('image'):
                picture(slide,item['image'],6.4,3.05,6.25,3.3)
                text(slide,6.4,6.42,6.25,.45,item['caption'],12,muted)
            if item.get('diagram'):
                for j,label in enumerate(['UR5 carrier','Flange interface','Local arms']):
                    box=slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,Inches(.8+j*4.15),Inches(6.35),Inches(3.7),Inches(.5))
                    box.fill.solid();box.fill.fore_color.rgb=RGBColor.from_string('173D46');box.line.fill.background()
                    text(slide,.9+j*4.15,6.38,3.5,.4,label,17,accent,True)
        text(slide,.65,7.08,10,.25,'CAM-BOT · visual demonstrator / supporting studies',11,muted)
        text(slide,11.7,7.08,1,.25,f'{index+1:02} / {len(items):02}',11,muted)
        slide.notes_slide.notes_text_frame.text=item['notes']
    deck.core_properties.title='CAM-BOT — final visual-demonstrator presentation'
    deck.core_properties.subject='Evidence-backed visual simulation, engineering studies and team workstreams'
    deck.core_properties.author='CAM-BOT team; presentation prepared with AI assistance'
    deck.save(output/'CAM-BOT.pptx')


def main(output):
    if output.exists():raise FileExistsError('choose a new presentation output directory')
    stats,replay,images,sources=collect();items=slides(stats)
    output.mkdir(parents=True)
    (output/'CAM-BOT.html').write_text(html_deck(items,replay,images),encoding='utf-8')
    powerpoint(items,images,output)
    (output/'speaker_notes.md').write_text('# CAM-BOT speaker notes\n\nSuggested running time: 10–12 minutes, including one demonstration.\n\n'+''.join(f"## {i+1}. {s['title']}\n\n{s['notes']}\n\n" for i,s in enumerate(items)),encoding='utf-8')
    (output/'recorded_trial.json').write_text(json.dumps(replay,indent=2)+'\n')
    (output/'sources.json').write_text(json.dumps({'source_commit':subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),
        'scope':'communication package; no new ROS/hardware or independent-review claim','generator_sha256':digest(Path(__file__)),'statistics':stats,
        'sha256':{str(p.relative_to(ROOT)):digest(p) for p in sources},'slide_count':len(items)},indent=2)+'\n')
    print(f'Created {len(items)} slides, editable PowerPoint, offline HTML, notes and recorded-trial data in {output}')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    main(parser.parse_args().output)

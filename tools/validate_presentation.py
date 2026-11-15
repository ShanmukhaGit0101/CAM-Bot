#!/usr/bin/env python3
"""Validate a new generated deck; requires playwright, PyMuPDF and Chromium."""
import json
import http.server
import functools
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright
import argparse
parser = argparse.ArgumentParser(description="Check a generated deck and export PDF in its directory.")
parser.add_argument('directory', type=Path)
parser.add_argument('--chromium', default='/usr/bin/chromium')
args = parser.parse_args()
root = args.directory.resolve()
if not (root / 'CAM-BOT.html').is_file():
    parser.error('directory must contain a generated CAM-BOT.html')
errors=[]
handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(root))
server=http.server.ThreadingHTTPServer(("127.0.0.1",0),handler)
threading.Thread(target=server.serve_forever,daemon=True).start()
url=f"http://127.0.0.1:{server.server_port}/CAM-BOT.html"
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=args.chromium,headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':1600,'height':900})
    page.on('pageerror',lambda e: errors.append(str(e)))
    page.route('http://**/*',lambda route: route.continue_() if route.request.url.startswith(f'http://127.0.0.1:{server.server_port}/') else route.abort())
    page.route('https://**/*',lambda route: route.abort())
    page.goto(url)
    assert page.locator('section.slide').count()==12
    for index in range(12):
        assert page.locator('section.active').count()==1
        assert page.locator('section.active').get_attribute('aria-label')==f'Slide {index+1}'
        assert page.locator('section.active').evaluate('(el)=>el.scrollHeight <= 940'),index+1
        for image in page.locator('section.active img').all():
            assert image.evaluate('(el)=>el.complete && el.naturalWidth>0')
        page.screenshot(path=str(root/f'check-slide-{index+1:02}.png'))
        if index<11:page.keyboard.press('ArrowRight')
    page.keyboard.press('n')
    assert page.locator('section.active .notes').is_visible()
    page.keyboard.press('n')
    page.goto(url+'#slide-6')
    page.locator('#speed').select_option('4')
    page.locator('#play').click()
    page.wait_for_function("document.querySelector('#event-state').textContent.includes('COMPLETE')",timeout=15000)
    assert page.locator('#workpiece').inner_text()=='FINISHED_AT_S5'
    assert page.locator('#progress').get_attribute('value')=='1'
    page.locator('#reset').click()
    assert page.locator('#elapsed').inner_text()=='0.000 s'
    page.locator('#play').click();page.wait_for_timeout(300);page.locator('#play').click()
    paused=page.locator('#elapsed').inner_text();page.wait_for_timeout(300)
    assert page.locator('#elapsed').inner_text()==paused
    page.locator('#reset').click()
    page.emulate_media(media='print')
    page.pdf(path=str(root/'CAM-BOT.pdf'),prefer_css_page_size=True,print_background=True)
    assert not errors,errors
    browser.close()
from pptx import Presentation
presentation=Presentation(root/'CAM-BOT.pptx')
assert len(presentation.slides)==12
assert all(s.notes_slide.notes_text_frame.text.strip() for s in presentation.slides)
import fitz
pdf=fitz.open(root/'CAM-BOT.pdf')
assert len(pdf)==12,len(pdf)
assert all(page.get_text().strip() for page in pdf)
for index in (0,5,6,9):
    pdf[index].get_pixmap(matrix=fitz.Matrix(1,1)).save(root/f'check-pdf-{index+1:02}.png')
report={'slide_count':12,'html_offline_navigation':'PASS','embedded_images':'PASS',
        'recorded_replay_completion_pause_reset':'PASS','speaker_notes_toggle':'PASS',
        'javascript_errors':errors,'pptx_slide_count_and_notes':'PASS','pdf_12_pages_with_text':'PASS',
        'browser_serving':'loopback HTTP; managed Chromium blocks file://; no external resources required','fresh_ros_runtime_pass':False,'scope':'presentation packaging and browser interaction checks only'}
(root/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))

server.shutdown()

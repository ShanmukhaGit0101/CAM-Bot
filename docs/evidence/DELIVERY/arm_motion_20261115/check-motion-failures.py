from pathlib import Path
import os,sys,time,json,signal,subprocess
root=Path('/workspace/CAM-BOT')
sys.path.insert(0,str(root))
from tools.check_ros_shutdown import check_shutdown
base=root/'.cambot-runs/motion-failures'
base.mkdir()
original=json.loads((root/'.cambot-runs/run.ygIYqF/plan.json').read_text())
for scenario in ('unreachable','load_failure','cancelled'):
 out=base/scenario;out.mkdir()
 plan=json.loads(json.dumps(original))
 if scenario=='unreachable':
  for arm in ('left','right'):plan['workspace'][arm]['max_radius_m']=.001
 (out/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
 args=['ros2','launch','carrier_description','dual_arm_demo.launch.py',
       'presentation_view:=true','auto_start:=false','enable_coordination:=true',
       f'config_file:={out}/plan.json',f'results_file:={out}/trials.csv']
 if scenario=='load_failure':args+=['fault_injection_step:=S3_LOAD']
 launch_file=(out/'launch.log').open('w')
 process=subprocess.Popen(args,stdout=launch_file,stderr=subprocess.STDOUT,start_new_session=True)
 try:
  until=time.monotonic()+20
  while 'VISUAL SIMULATION ONLY' not in (out/'launch.log').read_text():
   if process.poll() is not None or time.monotonic()>until:raise RuntimeError('launch failed')
   time.sleep(.1)
  with (out/'probe.jsonl').open('w') as log:
   subprocess.run(['python3','tools/ay05_ros_probe.py','--expect',scenario,'--timeout-s','45'],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=55)
 finally:
  if process.poll() is None:process.send_signal(signal.SIGINT)
  process.wait(timeout=15);launch_file.close()
 assert process.returncode==0,process.returncode
 check_shutdown((out/'launch.log').read_text())
 result=subprocess.run(['ros2','node','list','--no-daemon'],capture_output=True,text=True,check=True,timeout=15)
 (out/'residual_nodes.txt').write_text(result.stdout)
 assert not result.stdout.strip(),result.stdout
 print('PASS',scenario,flush=True)

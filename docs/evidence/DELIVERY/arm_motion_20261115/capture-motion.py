from pathlib import Path
import time,json
import rclpy
from std_msgs.msg import String
from sensor_msgs.msg import JointState
from std_srvs.srv import Trigger
from PyQt5.QtWidgets import QApplication

out=Path('/workspace/CAM-BOT/.cambot-runs/motion-visual')
app=QApplication([])
rclpy.init()
node=rclpy.create_node('arm_view_observer')
events=[]
shots=set()
joint_samples=[]
pending=[]
def callback(message):
 data=json.loads(message.data);events.append(data)
 if data.get('event')=='STEP_COMPLETED' and data.get('step') in ('S1_GRASP','S3_LOAD','S5_PLACE'):
  pending.append((time.monotonic()+.15,data['step']))
node.create_subscription(String,'/cambot/task_state',callback,100)
node.create_subscription(JointState,'/joint_states',lambda msg: joint_samples.append({'t': time.monotonic(), 'names': list(msg.name), 'positions': list(msg.position)}),100)
client=node.create_client(Trigger,'/machine_tending_coordinator/start')
assert client.wait_for_service(timeout_sec=20)
ready=time.monotonic()+2
while time.monotonic()<ready:rclpy.spin_once(node,timeout_sec=.1)
pubs=node.get_publishers_info_by_topic('/joint_states')
assert len(pubs)==1 and pubs[0].node_name=='machine_tending_coordinator'
app.primaryScreen().grabWindow(0).save(str(out/'idle.png'))
future=client.call_async(Trigger.Request())
rclpy.spin_until_future_complete(node,future,timeout_sec=10)
assert future.result().success
limit=time.monotonic()+60
success=False
while time.monotonic()<limit:
 rclpy.spin_once(node,timeout_sec=.05);app.processEvents()
 for at,name in list(pending):
  if time.monotonic()>=at:
   app.primaryScreen().grabWindow(0).save(str(out/(name+'.png')))
   shots.add(name);pending.remove((at,name))
 if any(e.get('event')=='SUCCESS' for e in events):success=True;break
assert success,events[-5:]
assert any(e.get('workpiece_state')=='FINISHED_AT_S5' for e in events)
assert shots=={'S1_GRASP','S3_LOAD','S5_PLACE'},shots
(out/'joint-samples.json').write_text(json.dumps(joint_samples,indent=2)+'\n')
(out/'observed-events.json').write_text(json.dumps(events,indent=2)+'\n')
(out/'result.json').write_text(json.dumps({'success':True,'final_workpiece':'FINISHED_AT_S5','joint_state_publishers':[p.node_name for p in pubs],'screenshots':sorted(shots),'scope':'headless RViz presentation view, visual simulation only'},indent=2)+'\n')
node.destroy_node();rclpy.shutdown()
print('SWAPPED_ARMS_SHORTEST_ROUTE_VISUAL_PASS')

#!/usr/bin/env python3
"""Original compact-module layout with connected pedestals and mating holes.

All dimensions/allocations are assumptions. No reference CAD is imported.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

import cadquery as cq


def build(p):
    numeric = [key for key in p if key not in ('classification','purpose','units','provenance','design_approved','hardware_execution_authorized','gripper_body_xyz')]
    for key in numeric:
        if isinstance(p[key],bool) or not isinstance(p[key],(int,float)) or not math.isfinite(p[key]) or p[key] <= 0:
            raise ValueError(key + ' must be positive and finite')
    if p['mount_hole_count'] != 4:
        raise ValueError('this mounting layout requires four holes')
    if p['shoulder_offset_x'] + p['pedestal_width']/2 >= p['base_length']/2:
        raise ValueError('pedestal must fit on the base plate')
    if p['pedestal_width'] >= p['base_width']:
        raise ValueError('pedestal exceeds base width')
    if p['mount_disc_diameter'] >= min(p['base_length'], p['base_width']):
        raise ValueError('mount disc must fit under the plate')
    if p['mount_hole_pcd'] + p['mount_hole_diameter'] >= p['mount_disc_diameter']:
        raise ValueError('mount holes break through the disc rim')
    if 2*p['wall'] >= min(p['upper_width'],p['forearm_width']):
        raise ValueError('invalid tube wall')
    if 2*p['pedestal_wall'] >= p['pedestal_width']:
        raise ValueError('invalid pedestal wall')
    if p['pedestal_bolt_pitch'] + p['fastener_hole_diameter'] >= p['pedestal_width']:
        raise ValueError('pedestal holes break through plate edges')
    if p['joint_axis_height'] <= p['base_thickness']+p['pedestal_height']+p['upper_width']/2:
        raise ValueError('insufficient rotor/upper-arm clearance above pedestal')
    if p['upper_length'] <= 40 or p['forearm_length'] <= 20 or p['upper_width'] <= p['forearm_width']+1:
        raise ValueError('tube dimensions cannot support this elbow fork')
    if p['joint_pin_diameter']+2*p['joint_radial_clearance'] >= p['forearm_width']:
        raise ValueError('joint pin exceeds forearm')
    if len(p['gripper_body_xyz'])!=3 or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<=0 for v in p['gripper_body_xyz']):
        raise ValueError('invalid gripper envelope')
    parts = {}
    mount_points = [(p['mount_hole_pcd']/2*math.cos(i*math.pi/2),
                     p['mount_hole_pcd']/2*math.sin(i*math.pi/2)) for i in range(4)]
    pedestal_points = [(sign*p['shoulder_offset_x']+dx,dy) for sign in (-1,1)
                       for dx in (-p['pedestal_bolt_pitch']/2,p['pedestal_bolt_pitch']/2)
                       for dy in (-p['pedestal_bolt_pitch']/2,p['pedestal_bolt_pitch']/2)]
    base = cq.Workplane('XY').rect(p['base_length'],p['base_width']).extrude(p['base_thickness'])
    base=base.faces('>Z').workplane().pushPoints(mount_points).hole(p['mount_hole_diameter'])
    base=base.faces('>Z').workplane().pushPoints(pedestal_points).hole(p['fastener_hole_diameter'])
    parts['base_plate'] = base.val()
    disc=cq.Workplane('XY').circle(p['mount_disc_diameter']/2).extrude(-p['mount_disc_thickness'])
    parts['mount_disc']=disc.faces('>Z').workplane().pushPoints(mount_points).hole(p['mount_hole_diameter']).val()
    for side, sign in [('left',-1),('right',1)]:
        x=sign*p['shoulder_offset_x']; z=p['joint_axis_height']; w=p['pedestal_width']
        # Closed bottom/top pads joined by two side webs, with a front service opening.
        pad=cq.Workplane('XY').rect(w,w).extrude(p['pedestal_wall'])
        pad=pad.faces('>Z').workplane().pushPoints([(dx,dy) for dx in (-p['pedestal_bolt_pitch']/2,p['pedestal_bolt_pitch']/2)
              for dy in (-p['pedestal_bolt_pitch']/2,p['pedestal_bolt_pitch']/2)]).hole(p['fastener_hole_diameter'])
        top=cq.Workplane('XY').rect(w,w).extrude(p['pedestal_wall']).translate((0,0,p['pedestal_height']-p['pedestal_wall']))
        pedestal=pad.union(top)
        for sign_y in (-1,1):
            web=cq.Workplane('XY').box(w,p['pedestal_wall'],p['pedestal_height'],centered=(True,True,False)).translate((0,sign_y*(w-p['pedestal_wall'])/2,0))
            pedestal=pedestal.union(web)
        # Provision for a yaw shaft; bearing/actuator interface remains unsized.
        pedestal=pedestal.faces('>Z').workplane().hole(p['joint_pin_diameter']+2*p['joint_radial_clearance'])
        parts[side+'_pedestal']=pedestal.translate((x,0,p['base_thickness'])).val()
        shaft=cq.Workplane('XY').circle(p['joint_pin_diameter']/2).extrude(z-p['base_thickness'])
        parts[side+'_yaw_shaft_envelope']=shaft.translate((x,0,p['base_thickness'])).val()
        # Upper tube ends before the elbow axis. Two external fork ears leave
        # 0.5 mm lateral clearance around the forearm lug throughout X rotation.
        width=p['upper_width']; wall=p['wall']; axis_y=p['upper_length']
        upper=cq.Workplane('XZ').rect(width,width).rect(width-2*wall,width-2*wall).extrude(-(axis_y-12))
        hub=cq.Workplane('XY').circle(16).extrude(10).translate((0,0,-5))
        upper=upper.union(hub)
        yaw_bore=cq.Workplane('XY').circle((p['joint_pin_diameter']+2*p['joint_radial_clearance'])/2).extrude(100,both=True)
        upper=upper.cut(yaw_bore)
        for sx in (-1,1):
            ear=cq.Workplane('XY').box(3,32,width).translate((sx*(p['forearm_width']/2+2),axis_y-4,0))
            upper=upper.union(ear)
        elbow_bore=cq.Workplane('YZ').circle((p['joint_pin_diameter']+2*p['joint_radial_clearance'])/2).extrude(100,both=True).translate((0,axis_y,0))
        upper=upper.cut(elbow_bore)
        parts[side+'_upper']=upper.translate((x,0,z)).val()
        fw=p['forearm_width']
        forearm=cq.Workplane('XZ').rect(fw,fw).rect(fw-2*wall,fw-2*wall).extrude(-p['forearm_length']).translate((0,axis_y+8,0))
        lug=cq.Workplane('YZ').circle(10).extrude(fw/2,both=True).translate((0,axis_y,0))
        forearm=forearm.union(lug).cut(elbow_bore)
        parts[side+'_forearm']=forearm.translate((x,0,z)).val()
        pin=cq.Workplane('YZ').circle(p['joint_pin_diameter']/2).extrude(p['upper_width']+8)
        parts[side+'_elbow_pin_envelope']=pin.translate((x-(p['upper_width']+8)/2,axis_y,z)).val()
        gx,gy,gz=p['gripper_body_xyz']
        body=cq.Workplane('XY').box(gx,gy,gz).translate((x,p['upper_length']+8+p['forearm_length']+gy/2,z))
        parts[side+'_gripper_envelope']=body.val()
    return parts, mount_points, pedestal_points



def export_kinematic_model(parts,p,output):
    """Export separate local link meshes and a provisional, inertia-free URDF."""
    meshes=output/'meshes';meshes.mkdir()
    robot=ET.Element('robot',name='cambot_original_compact_module')
    fixed_names=['base_plate','mount_disc']+[side+suffix for side in ('left','right')
                 for suffix in ('_pedestal','_yaw_shaft_envelope')]
    groups={'compact_module_base':(fixed_names,(0,0,0))}
    for side,sign in [('left',-1),('right',1)]:
        groups[side+'_upper_arm']=([side+'_upper',side+'_elbow_pin_envelope'],
                                  (sign*p['shoulder_offset_x'],0,p['joint_axis_height']))
        groups[side+'_forearm']=([side+'_forearm',side+'_gripper_envelope'],
                                (sign*p['shoulder_offset_x'],p['upper_length'],p['joint_axis_height']))
    for link_name,(names,origin) in groups.items():
        shape=cq.Compound.makeCompound([parts[name].translate(tuple(-v for v in origin)) for name in names])
        cq.exporters.export(shape,str(meshes/(link_name+'.stl')),tolerance=0.05,angularTolerance=0.1)
        link=ET.SubElement(robot,'link',name=link_name)
        for kind in ('visual','collision'):
            element=ET.SubElement(link,kind)
            geometry=ET.SubElement(element,'geometry')
            ET.SubElement(geometry,'mesh',filename='meshes/'+link_name+'.stl',scale='0.001 0.001 0.001')
    for side,sign in [('left',-1),('right',1)]:
        for name,parent,child,origin,axis in [
            (side+'_shoulder_joint','compact_module_base',side+'_upper_arm',
             (sign*p['shoulder_offset_x']/1000,0,p['joint_axis_height']/1000),'0 0 1'),
            (side+'_elbow_joint',side+'_upper_arm',side+'_forearm',
             (0,p['upper_length']/1000,0),'1 0 0')]:
            joint=ET.SubElement(robot,'joint',name=name,type='revolute')
            ET.SubElement(joint,'parent',link=parent);ET.SubElement(joint,'child',link=child)
            ET.SubElement(joint,'origin',xyz=' '.join(str(v) for v in origin),rpy='0 0 0')
            ET.SubElement(joint,'axis',xyz=axis)
            # Study bounds, not rated hardware limits. No control plugin is emitted.
            ET.SubElement(joint,'limit',lower='-1.2',upper='1.2',effort='1',velocity='0.5')
        tip=side+'_gripper_envelope_tip'
        ET.SubElement(robot,'link',name=tip)
        joint=ET.SubElement(robot,'joint',name=side+'_envelope_tip',type='fixed')
        ET.SubElement(joint,'parent',link=side+'_forearm');ET.SubElement(joint,'child',link=tip)
        ET.SubElement(joint,'origin',xyz=f"0 {(8+p['forearm_length']+p['gripper_body_xyz'][1])/1000} 0",rpy='0 0 0')
    ET.indent(robot)
    (output/'compact_module.urdf').write_text(ET.tostring(robot,encoding='unicode')+'\n')


def generate(parameters,output):
    if output.exists(): raise FileExistsError('use a new output directory')
    p=json.loads(parameters.read_text())
    parts,mount_points,pedestal_points=build(p)
    rows=[]
    for name,shape in parts.items():
        if not shape.isValid() or len(shape.Solids())!=1: raise ValueError('invalid/disconnected solid: '+name)
        center=shape.Center()
        mass=(p['gripper_mass_each_kg'] if name.endswith('gripper_envelope') else
              shape.Volume()*1e-9*p['assumed_structure_density_kg_m3'])
        rows.append({'name':name,'volume_mm3':shape.Volume(),'assumed_mass_kg':mass,
                     'mass_basis':'allocation, not geometry' if name.endswith('gripper_envelope') else 'uniform assumed aluminum; pins not material-selected',
                     'center_of_mass_m':[center.x/1000,center.y/1000,center.z/1000]})
    model_mass=sum(r['assumed_mass_kg'] for r in rows)
    allocation=model_mass+4*p['arm_actuator_mass_each_kg']+2*p['payload_each_kg']
    output.mkdir(parents=True)
    assembly=cq.Assembly(name='CAMBOT_original_compact_concept')
    for name,shape in parts.items(): assembly.add(shape,name=name)
    assembly.export(str(output/'compact_module.step'))
    cq.exporters.export(cq.Compound.makeCompound(list(parts.values())),str(output/'compact_module.svg'),
                        opt={'width':1000,'height':750,'projectionDir':(1,-2,1),'showHidden':False})
    export_kinematic_model(parts,p,output)
    report={'classification':'ORIGINAL_PRELIMINARY_DESIGN_NOT_MANUFACTURING_RELEASE',
            'parameter_sha256':hashlib.sha256(parameters.read_bytes()).hexdigest(),
            'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'parts':rows,'all_shapes_valid':True,
            'urdf_scope':'standalone kinematic/mesh study; provisional limits, no inertias, controller or gripper joints; envelope tips are not calibrated TCPs',
            'mount_points_xy_mm':mount_points,'pedestal_points_xy_mm':pedestal_points,
            'modeled_mass_allocation_kg':model_mass,
            'actuator_and_workpiece_allocation_kg':4*p['arm_actuator_mass_each_kg']+2*p['payload_each_kg'],
            'subtotal_allocation_kg':allocation,'target_mass_kg':p['target_complete_module_mass_kg'],
            'unallocated_mass_budget_kg':p['target_complete_module_mass_kg']-allocation,
            'estimated_complete_mass_kg':None,
            'missing_design':['selected actuators, gearboxes and shaft couplings',
                             'selected bearings/bushings, fits, shaft couplings and axial retention',
                             'gripper mechanism and object sensing',
                             'fasteners, bearing fits, cables and guards',
                             'verified flange interface and robot payload/inertia envelope',
                             'stress, fatigue, deflection, dynamic and workspace qualification'],
            'physical_operation_verified':False,'payload_compatibility':'NOT_ESTABLISHED',
            'manufacturing_ready':False,'hardware_execution_authorized':False}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('all_shapes_valid','subtotal_allocation_kg','unallocated_mass_budget_kg','payload_compatibility')},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('parameters',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();generate(args.parameters,args.output)

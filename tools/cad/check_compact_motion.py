#!/usr/bin/env python3
"""Sample exact concept solids for nonadjacent module self-clearance only."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import cadquery as cq

from tools.cad.build_compact_module import build


def solid_clearance_mm(first, second):
    """Distinguish overlap/containment from mere distance between surfaces."""
    if first.intersect(second).Volume() > 1e-6:
        return 0.0
    return first.distance(second)


def link_solids(parts,p,q):
    fixed=['base_plate','mount_disc']+[side+suffix for side in ('left','right')
            for suffix in ('_pedestal','_yaw_shaft_envelope')]
    links={'base':cq.Compound.makeCompound([parts[name] for name in fixed])}
    for index,(side,sign) in enumerate([('left',-1),('right',1)]):
        x=sign*p['shoulder_offset_x'];z=p['joint_axis_height']
        upper=cq.Compound.makeCompound([parts[side+'_upper'],parts[side+'_elbow_pin_envelope']])
        forearm=cq.Compound.makeCompound([parts[side+'_forearm'],parts[side+'_gripper_envelope']])
        forearm=forearm.rotate((x,p['upper_length'],z),(x+1,p['upper_length'],z),q[2*index+1])
        links[side+'_upper']=upper.rotate((x,0,z),(x,0,z+1),q[2*index])
        links[side+'_forearm']=forearm.rotate((x,0,z),(x,0,z+1),q[2*index])
    return links


def analyze(parameters,output):
    if output.exists(): raise FileExistsError('choose a new output directory')
    p=json.loads(parameters.read_text());parts,_,_=build(p)
    excluded={frozenset(pair) for pair in [('base','left_upper'),('base','right_upper'),
               ('left_upper','left_forearm'),('right_upper','right_forearm')]}
    records=[]
    for q in itertools.product((-30,0,30),(-45,0,45),(-30,0,30),(-45,0,45)):
        links=link_solids(parts,p,q)
        pairs=[{'links':[a,b],'clearance_mm':solid_clearance_mm(links[a],links[b])}
               for a,b in itertools.combinations(links,2) if frozenset((a,b)) not in excluded]
        records.append({'joint_degrees':list(q),'pairs':pairs,
                        'minimum_clearance_mm':min(pair['clearance_mm'] for pair in pairs),
                        'passes_5mm_screen':all(pair['clearance_mm'] >=5 for pair in pairs)})
    report={'scope':'81 discrete original-concept joint configurations; module self-clearance only',
            'joint_order':['left_shoulder','left_elbow','right_shoulder','right_elbow'],
            'parameter_sha256':hashlib.sha256(parameters.read_bytes()).hexdigest(),
            'generator_sha256':hashlib.sha256(Path(__file__).with_name('build_compact_module.py').read_bytes()).hexdigest(),
            'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'passed':sum(r['passes_5mm_screen'] for r in records),'attempted':len(records),
            'clearance_margin_mm':5,'records':records,
            'excluded_adjacent_pairs':[sorted(pair) for pair in sorted(excluded,key=lambda pair:sorted(pair))],
            'continuous_path_checked':False,'carrier_or_workcell_checked':False,
            'actual_actuator_cable_or_workpiece_geometry_checked':False,
            'hardware_execution_authorized':False}
    output.mkdir(parents=True)
    (output/'sampled_clearance.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({key:report[key] for key in ('scope','passed','attempted','clearance_margin_mm')},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('parameters',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args();analyze(args.parameters,args.output)

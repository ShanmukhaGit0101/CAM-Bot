#!/usr/bin/env python3
"""Inventory static STEP geometry without inventing articulation or mass."""

import argparse
import hashlib
import json
from pathlib import Path
import re

import cadquery as cq
import OCP


def bounds(shape):
    box = shape.BoundingBox()
    return {key: getattr(box, key) for key in
            ('xmin', 'xmax', 'ymin', 'ymax', 'zmin', 'zmax', 'xlen', 'ylen', 'zlen')}


def inspect(source):
    data = source.read_bytes()
    text = data.decode('ascii', errors='replace')
    if 'SI_UNIT(.MILLI.,.METRE.)' not in text:
        raise ValueError('This intake requires explicit millimetre length units')
    shape = cq.importers.importStep(str(source)).val()
    solids = shape.Solids()
    counts = {name: len(re.findall(r'(?<![A-Z_])' + name + r'\s*\(', text))
              for name in ('PRODUCT', 'NEXT_ASSEMBLY_USAGE_OCCURRENCE',
                           'REVOLUTE_PAIR', 'KINEMATIC_JOINT', 'MANIFOLD_SOLID_BREP')}
    report = {
        'source': source.name, 'sha256': hashlib.sha256(data).hexdigest(),
        'bytes': len(data), 'cadquery_version': cq.__version__, 'ocp_version': OCP.__version__,
        'classification': 'STATIC_CAD_ONLY', 'source_length_unit': 'mm',
        'model_identity': 'SDA_20D filename; STEP product name does not authenticate robot model',
        'entity_counts': counts, 'bbox_mm': bounds(shape),
        'solids': [{'index': i, 'valid': solid.isValid(), 'bbox_mm': bounds(solid),
                    'faces': len(solid.Faces()), 'volume_mm3': solid.Volume()}
                   for i, solid in enumerate(solids)],
        'solid_count': len(solids), 'face_count': len(shape.Faces()),
        'whole_shape_valid': shape.isValid(),
        'volume_interpretation': 'Geometric solid volumes only; may overlap. No density, BOM or mass claim.',
        'mass_kg': None, 'joint_axes': None, 'joint_limits': None,
        'link_tree': None, 'controller_interface': None,
        'mounting_transform_to_ur5': None, 'payload_compatibility': 'NOT_ESTABLISHED',
        'hardware_execution_authorized_by_this_report': False,
        'physical_operation_verified': False, 'grasp_verified': False,
        'task_7_to_15_complete': False,
    }
    report['bbox_extent_m'] = [report['bbox_mm'][key] / 1000 for key in ('xlen', 'ylen', 'zlen')]
    return shape, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--preview', action='store_true', help='export optional SVG; may be slow')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('output must be a new directory')
    shape, report = inspect(args.source)
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / 'geometry.json').write_text(json.dumps(report, indent=2) + '\n')
    # Static engineering preview, not an articulated or collision model.
    if args.preview:
        cq.exporters.export(shape, str(args.output / 'preview.svg'),
                            opt={'width': 1000, 'height': 900, 'showAxes': True,
                                 'projectionDir': (1, -2, 1), 'showHidden': False})
    print(json.dumps({k: report[k] for k in ['classification', 'solid_count', 'bbox_extent_m']}, indent=2))


if __name__ == '__main__':
    main()

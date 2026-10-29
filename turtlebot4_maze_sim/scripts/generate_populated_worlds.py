#!/usr/bin/env python3

import math
from pathlib import Path
import random
import xml.etree.ElementTree as ET


WORLD_DIR = Path(__file__).resolve().parents[1] / 'worlds'


def element(parent, tag, text=None, **attributes):
    child = ET.SubElement(parent, tag, attributes)
    if text is not None:
        child.text = str(text)
    return child


def shape(link, name, kind, dimensions, pose, color, collision=True):
    for tag in ('collision', 'visual') if collision else ('visual',):
        part = element(link, tag, name=f'{name}_{tag}')
        element(part, 'pose', ' '.join(map(str, pose)))
        geometry = element(part, 'geometry')
        solid = element(geometry, kind)
        if kind == 'box':
            element(solid, 'size', ' '.join(map(str, dimensions)))
        elif kind == 'cylinder':
            element(solid, 'radius', dimensions[0])
            element(solid, 'length', dimensions[1])
        elif kind == 'sphere':
            element(solid, 'radius', dimensions[0])
        if tag == 'visual':
            material = element(part, 'material')
            element(material, 'ambient', color)
            element(material, 'diffuse', color)


def box(link, name, size, position, color, collision=True):
    shape(link, name, 'box', size, (*position, 0, 0, 0), color, collision)


def cylinder(link, name, radius, length, position, color, collision=True):
    shape(link, name, 'cylinder', (radius, length), (*position, 0, 0, 0), color, collision)


def sphere(link, name, radius, position, color, collision=True):
    shape(link, name, 'sphere', (radius,), (*position, 0, 0, 0), color, collision)


def add_object(world, kind, index, position):
    model = element(world, 'model', name=f'{kind}_{index:03d}')
    element(model, 'static', 'true')
    element(model, 'pose', f'{position[0]:.2f} {position[1]:.2f} 0 0 0 0')
    link = element(model, 'link', name='link')
    dark = '0.12 0.12 0.12 1'
    metal = '0.35 0.38 0.37 1'
    wood = '0.52 0.29 0.13 1'
    green = '0.12 0.42 0.16 1'

    if kind == 'cola_bottle':
        cylinder(link, 'body', 0.035, 0.18, (0, 0, 0.09), '0.20 0.08 0.04 1')
        cylinder(link, 'label', 0.036, 0.07, (0, 0, 0.10), '0.80 0.03 0.03 1', False)
        cylinder(link, 'neck', 0.018, 0.05, (0, 0, 0.205), '0.25 0.10 0.04 1')
        cylinder(link, 'cap', 0.019, 0.012, (0, 0, 0.236), '0.85 0.04 0.04 1')
    elif kind == 'traffic_cone':
        box(link, 'base', (0.25, 0.25, 0.025), (0, 0, 0.0125), dark)
        for layer in range(5):
            color = '0.95 0.95 0.95 1' if layer == 3 else '1.0 0.30 0.02 1'
            cylinder(link, f'layer_{layer}', 0.095 - layer * 0.017, 0.055,
                     (0, 0, 0.0525 + layer * 0.055), color)
    elif kind == 'can':
        cylinder(link, 'body', 0.035, 0.12, (0, 0, 0.06), '0.12 0.38 0.75 1')
        cylinder(link, 'top', 0.034, 0.004, (0, 0, 0.122), '0.75 0.75 0.75 1', False)
    elif kind == 'small_box':
        box(link, 'body', (0.16, 0.13, 0.12), (0, 0, 0.06), '0.65 0.48 0.25 1')
    elif kind == 'ball':
        sphere(link, 'body', 0.09, (0, 0, 0.09), '0.94 0.68 0.04 1')
    elif kind == 'bucket':
        cylinder(link, 'body', 0.10, 0.20, (0, 0, 0.10), '0.15 0.48 0.75 1')
        cylinder(link, 'rim', 0.105, 0.018, (0, 0, 0.209), '0.12 0.35 0.65 1')
    elif kind == 'toolbox':
        box(link, 'body', (0.24, 0.14, 0.12), (0, 0, 0.06), '0.75 0.12 0.08 1')
        box(link, 'handle', (0.09, 0.025, 0.035), (0, 0, 0.1375), dark)
    elif kind == 'garden_pond':
        box(link, 'basin', (1.6, 1.2, 0.18), (0, 0, 0.09), '0.45 0.45 0.40 1')
        box(link, 'water', (1.38, 0.98, 0.012), (0, 0, 0.186), '0.08 0.42 0.62 1', False)
    elif kind == 'chair':
        box(link, 'seat', (0.55, 0.55, 0.08), (0, 0, 0.48), wood)
        box(link, 'back', (0.55, 0.07, 0.55), (0, 0.24, 0.77), wood)
        for x in (-0.22, 0.22):
            for y in (-0.22, 0.22):
                box(link, f'leg_{x}_{y}', (0.06, 0.06, 0.44), (x, y, 0.22), metal)
    elif kind == 'garden_light':
        cylinder(link, 'base', 0.16, 0.08, (0, 0, 0.04), metal)
        cylinder(link, 'post', 0.045, 1.25, (0, 0, 0.705), dark)
        sphere(link, 'globe', 0.16, (0, 0, 1.45), '1.0 0.88 0.53 1')
        light = element(link, 'light', name='lamp', type='point')
        element(light, 'pose', '0 0 1.45 0 0 0')
        element(light, 'diffuse', '0.8 0.7 0.5 1')
        element(light, 'specular', '0.2 0.2 0.2 1')
        attenuation = element(light, 'attenuation')
        element(attenuation, 'range', '3')
        element(attenuation, 'constant', '0.5')
        element(attenuation, 'linear', '0.2')
        element(attenuation, 'quadratic', '0.1')
    elif kind == 'bench':
        box(link, 'seat', (1.3, 0.45, 0.08), (0, 0, 0.46), wood)
        box(link, 'back', (1.3, 0.08, 0.48), (0, 0.19, 0.72), wood)
        for x in (-0.5, 0.5):
            box(link, f'leg_{x}', (0.08, 0.36, 0.42), (x, 0, 0.21), metal)
    elif kind == 'planter':
        box(link, 'pot', (0.75, 0.75, 0.5), (0, 0, 0.25), '0.62 0.26 0.16 1')
        sphere(link, 'plant', 0.32, (0, 0, 0.67), green)
    elif kind == 'tree':
        cylinder(link, 'trunk', 0.12, 1.4, (0, 0, 0.7), '0.36 0.23 0.12 1')
        sphere(link, 'canopy', 0.7, (0, 0, 1.7), green)
    elif kind == 'garden_table':
        box(link, 'top', (1.0, 0.8, 0.08), (0, 0, 0.75), wood)
        for x in (-0.4, 0.4):
            for y in (-0.3, 0.3):
                box(link, f'leg_{x}_{y}', (0.07, 0.07, 0.71), (x, y, 0.355), metal)
    elif kind == 'bin':
        cylinder(link, 'body', 0.28, 0.75, (0, 0, 0.375), '0.12 0.35 0.27 1')
        cylinder(link, 'lid', 0.30, 0.05, (0, 0, 0.775), dark)
    elif kind == 'crate':
        box(link, 'body', (0.7, 0.7, 0.7), (0, 0, 0.35), wood)
    elif kind == 'rock':
        sphere(link, 'body', 0.4, (0, 0, 0.4), '0.45 0.45 0.42 1')
    elif kind == 'barrel':
        cylinder(link, 'body', 0.32, 0.90, (0, 0, 0.45), '0.28 0.40 0.62 1')
        for height in (0.18, 0.72):
            cylinder(link, f'band_{height}', 0.325, 0.045, (0, 0, height), metal, False)
    elif kind == 'birdbath':
        cylinder(link, 'base', 0.25, 0.10, (0, 0, 0.05), '0.55 0.55 0.50 1')
        cylinder(link, 'pedestal', 0.12, 0.65, (0, 0, 0.425), '0.55 0.55 0.50 1')
        cylinder(link, 'bowl', 0.40, 0.12, (0, 0, 0.81), '0.55 0.55 0.50 1')
        cylinder(link, 'water', 0.33, 0.01, (0, 0, 0.875), '0.08 0.42 0.62 1', False)
    elif kind == 'garden_sign':
        box(link, 'post', (0.09, 0.09, 1.15), (0, 0, 0.575), wood)
        box(link, 'sign', (0.70, 0.08, 0.38), (0, 0, 1.16), '0.88 0.85 0.70 1')
    elif kind == 'picnic_table':
        box(link, 'top', (1.45, 0.72, 0.08), (0, 0, 0.75), wood)
        for x in (-0.55, 0.55):
            box(link, f'leg_{x}', (0.09, 0.66, 0.71), (x, 0, 0.355), wood)
        for y in (-0.62, 0.62):
            box(link, f'bench_{y}', (1.4, 0.25, 0.08), (0, y, 0.44), wood)
            for x in (-0.55, 0.55):
                box(link, f'bench_leg_{x}_{y}', (0.09, 0.12, 0.40), (x, y, 0.20), wood)
    elif kind == 'bollard':
        cylinder(link, 'base', 0.22, 0.08, (0, 0, 0.04), metal)
        cylinder(link, 'post', 0.12, 0.8, (0, 0, 0.48), '0.90 0.70 0.08 1')


def positions(world, size, count, clearance):
    walls = []
    named_walls = {}
    for link in world.findall("./model[@name='maze_walls']/link"):
        pose = [float(value) for value in link.findtext('pose').split()]
        dimensions = [float(value) for value in link.findtext('./collision/geometry/box/size').split()]
        wall = (pose[0], pose[1], dimensions[0] / 2, dimensions[1] / 2)
        walls.append(wall)
        named_walls[link.get('name')] = wall

    if size == 'small':
        west = named_walls['wall_outer_3']
        east = named_walls['wall_outer_4']
        south = named_walls['wall_outer_1']
        north = named_walls['wall_outer_2']
        bounds = (west[0] + west[2], east[0] - east[2],
                  south[1] + south[3], north[1] - north[3])
        samples = []
        for wall_x, wall_y, half_x, half_y in walls:
            horizontal = half_x > half_y
            half_length = half_x if horizontal else half_y
            half_width = half_y if horizontal else half_x
            for index in range(int((2 * half_length - 1.0) / 0.8) + 1):
                along = -half_length + 0.5 + index * 0.8
                for side in (-1, 1):
                    offset = side * (half_width + clearance + 0.03)
                    samples.append((wall_x + along, wall_y + offset) if horizontal else
                                   (wall_x + offset, wall_y + along))
    else:
        coordinates = [-18.0 + 2.4 * index for index in range(16)]
        samples = [(x, y) for x in coordinates for y in coordinates]
    candidates = []
    for x, y in samples:
        if math.hypot(x, y) < 1.2 + clearance:
            continue
        if size == 'small' and not (bounds[0] + clearance <= x <= bounds[1] - clearance and
                                    bounds[2] + clearance <= y <= bounds[3] - clearance):
            continue
        if size == 'large' and 12.7 < x < 15.3 and -16.3 < y < -5.7:
            continue
        if any(abs(x - wall_x) < half_x + clearance and
               abs(y - wall_y) < half_y + clearance
               for wall_x, wall_y, half_x, half_y in walls):
            continue
        if size == 'small' and any(
                math.hypot(x - (wall_x + end_x), y - (wall_y + end_y)) < 0.6
                for wall_x, wall_y, half_x, half_y in walls
                for end_x, end_y in (((-half_x, 0), (half_x, 0)) if half_x > half_y else
                                     ((0, -half_y), (0, half_y)))):
            continue
        candidates.append((x, y))
    random.Random(42).shuffle(candidates)
    selected = []
    for candidate in candidates:
        if size == 'small' and any(math.dist(candidate, other) < 0.65 for other in selected):
            continue
        selected.append(candidate)
        if len(selected) == count:
            return selected
    raise ValueError(f'Only {len(selected)} clear positions available for {count} objects')


def generate(size, kinds, clearance):
    tree = ET.parse(WORLD_DIR / f'maze_world_{size}.sdf')
    world = tree.getroot().find('world')
    for index, (kind, position) in enumerate(zip(kinds, positions(world, size, len(kinds), clearance)), 1):
        add_object(world, kind, index, position)
    ET.indent(tree, space='  ')
    tree.write(WORLD_DIR / f'maze_world_{size}_populated.sdf', encoding='utf-8', xml_declaration=True)


if __name__ == '__main__':
    generate('small', ['cola_bottle'] * 5 + ['traffic_cone'] * 5 +
             ['can'] * 3 + ['small_box'] * 3 + ['ball'] * 3 +
             ['bucket'] * 3 + ['toolbox'] * 3, 0.18)
    large_kinds = ['garden_pond', 'chair', 'garden_light', 'bench', 'planter',
                   'tree', 'garden_table', 'bin', 'crate', 'rock', 'barrel',
                   'birdbath', 'garden_sign', 'picnic_table', 'bollard']
    generate('large', large_kinds * 6 + large_kinds[:10], 0.9)
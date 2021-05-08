import bpy
import bmesh
from mathutils import Vector
import random
import sys
import os
import time

from random import randrange

# Delete default cube
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False, confirm=False)

# Tree Hyperparameters
height = 20
base_radius = 5
layers = 8
low_polyness = 10
seed = time.time()

random.seed(seed)

# TODO: Non Linear function
# TODO: Follow path instead of straight

layer_list = []
for i in range(0, layers+1):
    layer_list.append(i*height/layers)

# Create Tree
bm = bmesh.new()

bmesh.ops.create_circle(
    bm,
    cap_ends=True,
    radius=base_radius,
    segments=low_polyness)

bm.verts.ensure_lookup_table()
last_edges = bm.edges
prev_radius = base_radius
to_pull_down = []

# Bottom pull down
for j in range(len(bm.verts)):
        even_odd = random.choice([0, 1])
        if j%2 == even_odd:
            to_pull_down.append(bm.verts[j])

for i in range(1, layers+1):
    outer_radius = ((height - layer_list[i]) * base_radius) / height
    
    # Extrude up
    extruded = bmesh.ops.extrude_edge_only(bm, edges=last_edges)
    
    # Move extruded geometry
    translate_verts = [v for v in extruded['geom'] if isinstance(v, bmesh.types.BMVert)]

    up = Vector((0, 0, layer_list[i]-layer_list[i-1]))
    bmesh.ops.translate(bm, vec=up, verts=translate_verts)
    
    # Scale down
    dr = 1 - random.uniform(0.15, 0.20)
    scale_factor = dr * outer_radius / prev_radius
    scale = Vector((scale_factor, scale_factor, 1))
    bmesh.ops.scale(bm, vec=scale, verts=translate_verts)
        
    # Extrude out
    last_edges = [e for e in extruded['geom'] if isinstance(e, bmesh.types.BMEdge)]
    extruded = bmesh.ops.extrude_edge_only(bm, edges=last_edges)
    translate_verts = [v for v in extruded['geom'] if isinstance(v, bmesh.types.BMVert)]
    
    # Scale up
    scale_factor = 1/dr
    scale = Vector((scale_factor, scale_factor, 1))
    bmesh.ops.scale(bm, vec=scale, verts=translate_verts)
    
    # Choose to bring down
    for j in range(len(translate_verts)):
        even_odd = random.choice([0, 1])
        if j%2 == even_odd:
            to_pull_down.append(translate_verts[j])
            
    last_edges = [e for e in extruded['geom'] if isinstance(e, bmesh.types.BMEdge)]
    prev_radius = outer_radius
   

# Actually bring down
for vert in to_pull_down:
    dz = random.uniform(0.05, 0.3) * height / layers
    down = Vector((0, 0, -dz))
    bmesh.ops.translate(bm, vec=down, verts=[vert])
    
# Remove doubles
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    
# Finish up, write the bmesh into a new mesh
me = bpy.data.meshes.new("Mesh")
bm.to_mesh(me)
bm.free()

# Add the mesh to the scene
obj = bpy.data.objects.new("Tree", me)
bpy.context.collection.objects.link(obj)

# Trunk Hyperparameters
height *= 0.2
base_radius *= 0.2
layers = 3
low_polyness = 8

# Create trunk
bm = bmesh.new()

bmesh.ops.create_circle(
    bm,
    cap_ends=True,
    radius=base_radius,
    segments=low_polyness)

layer_list = []
for i in range(0, layers+1):
    layer_list.append(-i*height/layers)
    
last_edges = bm.edges
prev_radius = base_radius
for i in range(1, layers+1):
    # Extrude down
    extruded = bmesh.ops.extrude_edge_only(bm, edges=last_edges)
    
    # Move extruded geometry
    translate_verts = [v for v in extruded['geom'] if isinstance(v, bmesh.types.BMVert)]
    down = Vector((random.uniform(-0.3*base_radius, 0.3*base_radius), 
                   random.uniform(-0.3*base_radius, 0.3*base_radius), 
                   layer_list[i]-layer_list[i-1]))
    bmesh.ops.translate(bm, vec=down, verts=translate_verts)
    
    # Scale up
    dr = 1 + random.uniform(0.10, 0.15)
    scale = Vector((dr, dr, 1))
    bmesh.ops.scale(bm, vec=scale, verts=translate_verts)
    
    last_edges = [e for e in extruded['geom'] if isinstance(e, bmesh.types.BMEdge)]

# Fill bottom
bmesh.ops.edgeloop_fill(bm, edges=last_edges)

# Remove doubles
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    
# Finish up, write the bmesh into a new mesh
me = bpy.data.meshes.new("Mesh")
bm.to_mesh(me)
bm.free()
    
# Add the mesh to the scene
obj = bpy.data.objects.new("Trunk", me)
bpy.context.collection.objects.link(obj)
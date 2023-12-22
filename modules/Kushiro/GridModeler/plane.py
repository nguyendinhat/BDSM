# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
# Created by Kushiro



import bpy
#import bmesh

from mathutils import Matrix, Vector, Quaternion
from mathutils import bvhtree
from bpy_extras import view3d_utils
import gpu
from gpu_extras.batch import batch_for_shader
import math
from bpy.props import (
    FloatProperty,
    IntProperty,
    BoolProperty,
    EnumProperty,
)
import bmesh



def get_nearby_vert(loc1, source, loops):        
    vs = [v1.co for f1 in source for v1 in f1.verts]

    loopes = []
    for item in loops:
        for p1 in item.loop:
            loopes.append(p1.co)            

    vs = vs + loopes
    low = 100000
    lowe = vs[0]

    for v1 in vs:        
        m = (loc1 - v1).length
        
        if m <= low:
            low = m
            lowe = v1
    #print('vert', lowe)
    return lowe




def get_nearby(loc1, source, loops):        
    es = [(e.verts[0].co, e.verts[1].co, None) for f1 in source for e in f1.edges]

    #loopes = [(p1, p2) for item in loops for (p1, p2) in item.loop]
    
    es2 = []
    for item in loops:
        pes = []
        loopes1 = [(p1.co, item) for p1 in item.loop]
        
        if len(loopes1) >= 2:
            loopes2 = loopes1[1:] + [loopes1[0]]
            #es = es + list(zip(loopes1, loopes2))
            pes = list(zip(loopes1, loopes2))    
        
        for a1, a2 in pes:
            p1, item = a1
            p2, _ = a2
            es2.append((p1, p2, item))
    es = es + es2

    low = 100000
    lowe = es[0]    

    for e1 in es:        
        p1, p2, item = e1
        #p3 = (p1 + p2) / 2
        if (p1-p2).length == 0:
            continue
        d1 = (loc1-p1).angle(p2-p1)
        d2 = (loc1-p2).angle(p1-p2)
        if d1 <= math.radians(90) and d2 <= math.radians(90):                    
            k1 = loc1 - p1
            k2 = p2 - p1
            k3 = k1.project(k2)
            #edgepos = k3 + p1
            m = (k1 - k3).length                
        else:
            m = min((loc1 - p1).length, (loc1 - p2).length)                
        
        if m <= low:
            low = m
            lowe = e1
            
    #print('vert', lowe)
    p1, p2, item = lowe
    return (p1, p2), item



def get_center(fs):
    total = Vector()
    for s in fs:
        total += s.calc_center_median()        
    return total / len(fs)

def calc_main_edge(source, sn):
    promo = []
    for f1 in source:
        for e1 in f1.edges:
            if len(e1.link_faces) == 1:
                promo.append(e1)
            elif not all([sel for sel in e1.link_faces]):
                promo.append(e1)
    if len(promo) == 0:
        promo = [e1 for f1 in source for e1 in f1.edges]    
    
    maxe = 0
    es = None
    for e1 in promo:
        p = e1.calc_length()
        if p > maxe:
            maxe = p
            es = e1

    if es == None:
        return None #zero length plane edge
    p1 = es.verts[0].co
    p2 = es.verts[1].co
    return (p1, p2)


def extend_main(source, a1):
    verts = []
    for f1 in source:
        verts += f1.verts
    p1, p2 = a1
    main = p2 - p1
    lay = [(v1.co-p1).project(main) for v1 in verts]
    rot = main.rotation_difference(Vector((0,0,1))).to_matrix().to_4x4()
    lay2 = [(e, rot @ e.copy()) for e in lay]
    top = max(lay2, key=lambda e: e[1].z)[0]
    bottom = min(lay2, key=lambda e: e[1].z)[0]
    return (top + p1, bottom + p1)        


def get_matrix(m1, m2, cen):    
    m1 = m1.copy().normalized()
    m2 = m2.copy().normalized()
    z = m1.cross(m2)
    m = Matrix.Identity(4)    
    m[0][0:3] = m1
    m[1][0:3] = m2
    m[2][0:3] = z
    m[3][0:3] = cen
    m = m.transposed()
    return m


def is_colinear(m1, m2):
    deg = abs(m1.angle(m2))
    if deg < math.radians(1):
        return True
    if (math.radians(180) - deg) < math.radians(1):
        return True
    return False
    '''
    print(m1.cross(m2).length)
    if m1.cross(m2).length < 0.1:
        return True
    else:
        return False
    '''


def project_length(v1, ax):
    p1 = v1.project(ax)
    return p1.length

def get_plane(source, sn, main_edge, size, mode_A, scale, scale_rel, shift_e, coord_mode, debug):
    guide = []
    gridlen = None    
    main_x = Vector((1,0,0))
    main_y = Vector((0,1,0))
    main_z = Vector((0,0,1))
    
    cen = get_center(source)        
    #a1 = calc_main_edge(source, sn) if main_edge == None else main_edge

    enable_coord_mode = True

    if main_edge == None:
        if coord_mode:            
            if is_colinear(sn, main_z):                
                a1 = (cen - main_x, cen + main_x)
            elif is_colinear(sn, main_y):
                a1 = (cen - main_z, cen + main_z)
            elif is_colinear(sn, main_x):
                a1 = (cen - main_y, cen + main_y)
            else:
                a1 = calc_main_edge(source, sn)    
                enable_coord_mode = False 
        else:
            a1 = calc_main_edge(source, sn)     
    else:
        a1 = main_edge


    if cen == None or a1 == None:
        return None

    h1, h2 = a1
    a1 = (h2-h1).normalized()
    a2 = sn.cross(a1)
    
    main_hori = extend_main(source, (cen, cen+a1))
    main_vert = extend_main(source, (cen, cen+a2))

    h1, h2 = main_hori
    v1, v2 = main_vert    
    #hori = (h2-h1).normalized()
    #ver = (v2-v1).normalized()

    '''
    if scale != 1:
        h2 = (h2 - cen) * scale + cen
        h1 = (h1 - cen) * scale + cen
        v2 = (v2 - cen) * scale + cen
        v1 = (v1 - cen) * scale + cen
    '''
    
    if mode_A:
        if scale != 0:
            h2 = h2 + (h2 - cen).normalized() * scale * 0.1
            h1 = h1 + (h1 - cen).normalized() * scale * 0.1
            v2 = v2 + (v2 - cen).normalized() * scale * 0.1
            v1 = v1 + (v1 - cen).normalized() * scale * 0.1
    else:
        if scale_rel != 0:
            srp = math.pow(1.1, scale_rel)
            h2 = (h2 - cen) * srp + cen
            h1 = (h1 - cen) * srp + cen
            v2 = (v2 - cen) * srp + cen
            v1 = (v1 - cen) * srp + cen
        

    if mode_A == False:
        if main_edge != None:            
            m1, m2 = main_edge
            length = ((m1-m2).length / 2) / size
        else:
            length = (h2-h1).length / size

        #count = size
        #vcount = math.floor( (v2-v1).length / length)
    else:
        length = 1.0 / size            
        #count = math.floor((h2-h1).length / length)
        #vcount = math.floor((v2-v1).length / length)

    gridlen = length

    v_shift = 0
    h_shift = 0

    hlen = (h1-cen).length
    h_shift = hlen % gridlen
    vlen = (v1-cen).length
    v_shift = vlen % gridlen  

    debug.eng = []     

    if main_edge != None:
        m1, m2 = main_edge
        main_p = m2-m1
        mv2 = v1 - m1
        pj = mv2.project(main_p)
        mlen = ((pj + m1)-v1).length
        #off = (mlen % gridlen) * ((pj + m1)-v1).normalized()
        v_shift = mlen % gridlen
        #debug.eng = [((pj + m1), v2.copy())]
        midcen = (m1+m2)/2
        mh2 = h1 - m1
        pj2 = mh2.project(main_p)
        hlen = ((pj2 + m1) - midcen).length
        h_shift = hlen % gridlen

    elif coord_mode and enable_coord_mode:
        m1 = v2-v1
        if is_colinear(m1, main_x):                        
            if v1.x > v2.x:
                v_shift = v1.x % gridlen
            else:
                v_shift = gridlen - v1.x % gridlen
        elif is_colinear(m1, main_y):
            if v1.y > v2.y:
                v_shift = v1.y % gridlen
            else:
                v_shift = gridlen - v1.y % gridlen
        elif is_colinear(m1, main_z):
            if v1.z > v2.z:
                v_shift = v1.z % gridlen            
            else:
                v_shift = gridlen - v1.z % gridlen

        m1 = h2-h1
        if is_colinear(m1, main_x):
            if h1.x > h2.x:
                h_shift = h1.x % gridlen            
            else:
                h_shift = gridlen - h1.x % gridlen            
        elif is_colinear(m1, main_y):
            if h1.y > h2.y:
                h_shift = h1.y % gridlen            
            else:
                h_shift = gridlen - h1.y % gridlen
        elif is_colinear(m1, main_z):
            if h1.z > h2.z:
                h_shift = h1.z % gridlen
            else:
                h_shift = gridlen - h1.z % gridlen
    
    #debug.eng += [(v1, Vector())]    
    
    if shift_e != None:                
        m1 = shift_e
        #midcen = (m1+m2)/2
        main_p = h2-h1
        mh2 = m1-h1
        pj2 = mh2.project(main_p)
        hlen = pj2.length
        h_shift = hlen % gridlen 
        
    mat = get_matrix(h2-h1, v2-v1, cen)    
    
    pen_x = (h2-h1).length
    pen_y = (v2-v1).length
    sx = (h1-cen).length * -1
    sy = (v1-cen).length * -1

    line_list = []
    #for x in range(count * 2):

    x = 0
    while True:        
        px = sx + x * length + h_shift
        if px > sx+pen_x:
            break
        p1 = Vector((px, sy, 0))
        p2 = Vector((px, sy + pen_y, 0))
        line_list.append((p1, p2))        
        x = x + 1

    y = 0
    #for y in range(vcount * 2):
    while True:        
        py = sy + y * length + v_shift
        if py > sy+pen_y:
            break
        p1 = Vector((sx, py, 0))
        p2 = Vector((sx + pen_x, py, 0))
        line_list.append((p1, p2))
        y = y + 1
    '''
    x = 0
    while True:        
        px = sx + x * length + h_shift
        if px > sx+pen_x:
            break
        p1 = Vector((px, sy, 0))
        p2 = Vector((px, sy + pen_y, 0))
        line_list.append((p1, p2))        
        x = x + 1

    y = 0
    #for y in range(vcount * 2):
    while True:        
        py = sy + y * length + v_shift
        if py > sy+pen_y:
            break
        p1 = Vector((sx, py, 0))
        p2 = Vector((sx + pen_x, py, 0))
        line_list.append((p1, p2))
        y = y + 1
    '''

    line_list.append((Vector((sx, sy, 0)), Vector((sx+pen_x, sy, 0))))
    line_list.append((Vector((sx+pen_x, sy, 0)), Vector((sx+pen_x, sy+pen_y, 0))))
    line_list.append((Vector((sx+pen_x, sy+pen_y, 0)), Vector((sx, sy+pen_y, 0))))
    line_list.append((Vector((sx, sy+pen_y, 0)), Vector((sx, sy, 0))))

    guide = [(mat @ p1, mat @ p2) for (p1, p2) in line_list]


    return guide, gridlen, main_hori, main_vert, cen




'''
def get_plane2(source, sn, main_edge, size, mode_A, debug):
    guide = []
    gridlen = None    
    
    cen = get_center(source)
    a1 = calc_main_edge(source, sn) if main_edge == None else main_edge
    
    h1, h2 = a1
    a1 = (h2-h1).normalized()
    a2 = sn.cross(a1)
    
    main_hori = extend_main(source, (cen, cen+a1))
    main_vert = extend_main(source, (cen, cen+a2))

    h1, h2 = main_hori
    v1, v2 = main_vert

    if mode_A == False:
        length = (h2-h1).length / size            
        count = size
        vcount = math.ceil( (v2-v1).length / length)
    else:
        length = 1.0 / size            
        count = math.ceil((h2-h1).length / length)
        vcount = math.ceil((v2-v1).length / length)

    gridlen = length

    if main_edge != None:
        m1, m2 = main_edge
        main_p = m2-m1
        mv2 = v1 - m1
        pj = mv2.project(main_p)
        mlen = ((pj + m1)-v1).length        
        off = (mlen % gridlen) * ((pj + m1)-v1).normalized()        
        #debug.eng = [((pj + m1), v2.copy())]
        v2 += off
        v1 += off

    ph1 = h1 - cen
    ph2 = h2 - cen
    pv1 = v1 - cen
    pv2 = v2 - cen
                     
    for x in range(count + 1):
        p = (h2 - h1) / count
        #p = (h2 - h1).normalized() * length
        p2 = h1 + (p * x)
        guide.append((p2 + pv1, p2 + pv2))
    
    for y in range(vcount + 1):
        p = (v2 - v1) / vcount
        #p = (v2 - v1).normalized() * length
        p2 = v1 + (p * y)
        guide.append((p2 + ph1, p2 + ph2))

    return guide, gridlen, main_hori, main_vert, cen
'''





# -*- coding: utf-8 -*-
# Project #04: ELLIS-9 // Traversable Wormhole Metric
# Category: Астрофизика и Оптика
# Description: Кротовая нора Эллиса, соединяющая две разные галактики через сферическое горло неевклидова пространства-времени.
# Run in TouchDesigner Textport (Alt + T):
# exec(open(r'C:\Users\hvoha\WORK\Antigravity\td_projects\project_04.py', encoding='utf-8').read())

import td

SHADER_CODE = '// ELLIS-9 // Traversable Wormhole Metric — TouchDesigner GLSL TOP Shader\nuniform vec4 uControl; // x: time, y: mouseX, z: mouseY, w: breath\nout vec4 fragColor;\n\nmat2 rot(float a) {\n    float s = sin(a), c = cos(a);\n    return mat2(c, -s, s, c);\n}\nfloat hash21(vec2 p) {\n    p = fract(p * vec2(234.34, 435.345));\n    p += dot(p, p + 34.23);\n    return fract(p.x * p.y);\n}\nfloat noise2(vec2 p) {\n    vec2 i = floor(p), f = fract(p);\n    f = f * f * (3.0 - 2.0 * f);\n    return mix(mix(hash21(i), hash21(i + vec2(1,0)), f.x),\n               mix(hash21(i + vec2(0,1)), hash21(i + vec2(1,1)), f.x), f.y);\n}\nfloat fbm(vec2 p) {\n    float v = 0.0, a = 0.5;\n    for (int i = 0; i < 5; i++) {\n        v += a * noise2(p);\n        p = rot(0.55) * p * 2.08;\n        a *= 0.5;\n    }\n    return v;\n}\nvec3 aces(vec3 x) {\n    return clamp((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0.0, 1.0);\n}\n\nvoid main() {\n    vec2 res = uTDOutputInfo.res.zw;\n    vec2 uv = (gl_FragCoord.xy - 0.5 * res) / res.y;\n    float t = uControl.x;\n    vec2 m = uControl.yz;\n    float breath = uControl.w;\n\n    vec3 ro = vec3(0.0, m.y * 1.2, -3.6);\n    ro.xz *= rot(m.x * 1.6 + t * 0.1);\n    vec3 ww = normalize(-ro), uu = normalize(cross(ww, vec3(0,1,0))), vv = cross(uu, ww);\n    vec3 rd = normalize(uv.x * uu + uv.y * vv + 1.35 * ww);\n\n    float b0 = 0.78; // throat radius\n    vec3 p = ro, v = rd;\n    float side = 1.0;\n    vec3 glowAcc = vec3(0.0);\n    for (int i = 0; i < 110; i++) {\n        float r = length(p);\n        float dr = r - b0;\n        if (abs(dr) < 0.06) {\n            side = -side; // pass through wormhole throat to parallel universe!\n        }\n        float force = (b0 * b0) / (r * r * r + 0.04);\n        v = normalize(v - (p / (r + 1e-4)) * force * 0.042 * sign(dr));\n        p += v * 0.055;\n        float throatRing = exp(-abs(dr) * 16.0) * 0.015;\n        glowAcc += mix(vec3(0.15, 0.85, 1.0), vec3(1.0, 0.45, 0.15), 0.5 - 0.5 * side) * throatRing;\n        if (r > 6.5 && i > 30) break;\n    }\n    vec2 skyUV = v.xy / (abs(v.z) + 0.5) * 3.5;\n    float neb = fbm(skyUV * 1.8 + side * 4.0 + t * 0.08);\n    vec3 univA = mix(vec3(0.01, 0.02, 0.05), vec3(0.1, 0.65, 1.0), pow(neb, 2.2));\n    vec3 univB = mix(vec3(0.04, 0.01, 0.02), vec3(1.0, 0.38, 0.12), pow(neb, 1.8));\n    vec3 col = (side > 0.0 ? univA : univB) + glowAcc;\n    float stars = smoothstep(0.95, 1.0, hash21(floor(skyUV * 12.0)));\n    col += vec3(0.9, 0.95, 1.0) * stars * 0.6;\n    col = aces(col * 1.15);\n\n    fragColor = TDOutputSwizzle(vec4(col, 1.0));\n}\n'

def build_project():
    root = op('/project1') or op('/')
    keep = {'ag_bridge', 'ag_catalog', 'out1'}
    for child in list(root.children):
        if child.name not in keep:
            child.destroy()

    out1 = root.op('out1')
    if out1 is None:
        out1 = root.create(td.outTOP, 'out1')

    # 1. Interactive Mouse & LFO Controller
    mouse = root.create(td.mouseinCHOP, 'mouse_in')
    mouse.nodeX, mouse.nodeY = -750, 350
    mouse.color = (0.1, 0.65, 0.85)

    lag = root.create(td.lagCHOP, 'lag_mouse')
    lag.nodeX, lag.nodeY = -550, 350
    lag.par.lag1 = 0.32
    lag.par.lag2 = 0.32
    lag.inputConnectors[0].connect(mouse)
    lag.color = (0.1, 0.65, 0.85)

    null_mouse = root.create(td.nullCHOP, 'null_mouse')
    null_mouse.nodeX, null_mouse.nodeY = -350, 350
    null_mouse.inputConnectors[0].connect(lag)
    null_mouse.color = (0.1, 0.65, 0.85)

    lfo = root.create(td.lfoCHOP, 'lfo_breath')
    lfo.nodeX, lfo.nodeY = -750, 200
    lfo.par.frequency = 0.2
    lfo.par.channelname = 'breath'
    lfo.color = (0.1, 0.65, 0.85)

    null_mod = root.create(td.nullCHOP, 'null_mod')
    null_mod.nodeX, null_mod.nodeY = -550, 200
    null_mod.inputConnectors[0].connect(lfo)
    null_mod.color = (0.1, 0.65, 0.85)

    # 2. Core Generative GLSL Shader TOP
    code_dat = root.create(td.textDAT, 'shader_code')
    code_dat.nodeX, code_dat.nodeY = -750, 20
    code_dat.color = (0.55, 0.25, 0.85)
    code_dat.text = SHADER_CODE

    glsl_top = root.create(td.glslTOP, 'glsl_generator')
    glsl_top.nodeX, glsl_top.nodeY = -480, 20
    glsl_top.color = (0.55, 0.25, 0.85)
    glsl_top.par.pixeldat = 'shader_code'
    glsl_top.par.outputresolution = 'custom'
    glsl_top.par.resolutionw = 1280
    glsl_top.par.resolutionh = 720
    glsl_top.par.format = 'rgba16float'
    glsl_top.par.vec0name = 'uControl'
    glsl_top.par.vec0valuex.expr = 'absTime.seconds'
    glsl_top.par.vec0valuey.expr = "op('null_mouse')['tx']"
    glsl_top.par.vec0valuez.expr = "op('null_mouse')['ty']"
    glsl_top.par.vec0valuew.expr = "op('null_mod')['breath']"

    for extra in root.ops('glsl_generator*'):
        if extra != glsl_top:
            extra.destroy()

    # 3. HDR Optical Bloom & Final Output
    blur_bloom = root.create(td.blurTOP, 'blur_bloom')
    blur_bloom.nodeX, blur_bloom.nodeY = -200, -120
    blur_bloom.color = (0.2, 0.8, 0.5)
    blur_bloom.par.size = 18.0
    blur_bloom.inputConnectors[0].connect(glsl_top)

    lvl_bloom = root.create(td.levelTOP, 'level_bloom')
    lvl_bloom.nodeX, lvl_bloom.nodeY = 0, -120
    lvl_bloom.color = (0.2, 0.8, 0.5)
    lvl_bloom.par.blacklevel = 0.2
    lvl_bloom.par.opacity = 0.4
    lvl_bloom.inputConnectors[0].connect(blur_bloom)

    comp_final = root.create(td.compositeTOP, 'comp_final')
    comp_final.nodeX, comp_final.nodeY = 220, 20
    comp_final.color = (0.2, 0.8, 0.5)
    comp_final.par.operand = 'add'
    comp_final.inputConnectors[0].connect(glsl_top)
    comp_final.inputConnectors[1].connect(lvl_bloom)

    out1.nodeX, out1.nodeY = 460, 20
    out1.color = (0.95, 0.2, 0.45)
    out1.inputConnectors[0].connect(comp_final)
    out1.display = True
    out1.viewer = True

    try:
        for pane in ui.panes:
            if pane.type == td.PaneType.NETWORKEDITOR:
                pane.home(zoom=True)
    except Exception:
        pass

    return {
        'id': '04',
        'title': 'ELLIS-9 // Traversable Wormhole Metric',
        'errors': [(c.name, c.errors(recurse=True)) for c in root.children if c.errors(recurse=True)],
    }

result = build_project()

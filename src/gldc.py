from dataclasses import dataclass, field

@dataclass
class anim_bin:
    magic_num: str=""
    version: int=0
    num_elements: int=0
    num_frames: int=0
    num_anims: int=0
    anims: list=field(default_factory=list)
    num_refs: int=0
    refs: dict=field(default_factory=dict)

@dataclass
class animation:
    name: str=""
    name2: str=""
    framerate: float=0
    flag: int=0
    num_frames: int=0
    frames: list=field(default_factory=list)

@dataclass
class aframe:
    x: float=0
    y: float=0
    w: float=0
    h: float=0
    num_elements: int=0
    elements: list=field(default_factory=list)

@dataclass
class element:
    ref: int=0
    ndx: int=0
    layer: int=0
    a: float=0
    b: float=0
    g: float=0
    r: float=0
    uk1: float=0
    uk2: float=0
    uk3: float=0
    uk4: float=0
    m1: float=0
    m2: float=0
    m3: float=0
    m4: float=0
    mx: float=0
    my: float=0
    index: float=0
    x: float=0
    y: float=0
    scale_x: float=0
    scale_y: float=0
    angle: float=0
    spin: float=0

@dataclass
class build_bin:
    magic_num: str=""
    version: int=0
    num_symbols: int=0
    num_frames: int=0
    root: str=""
    num_textures: int=0
    textures: list=field(default_factory=list)
    flag: int=0
    symbols: list=field(default_factory=list)
    num_refs: int=0
    refs: dict=field(default_factory=dict)

@dataclass
class symbol:
    ref1: int=0
    ref2: int=0
    flag: int=0
    num_frames: int=0
    frames: list=field(default_factory=list)

@dataclass
class bframe:
    ndx: int=0
    duration: int=0
    buildIdx: int=0
    x_off: float=0
    y_off: float=0
    w: float=0
    h: float=0
    u1: float=0
    v1: float=0
    u2: float=0
    v2: float=0
    piv_x: float=0
    piv_y: float=0

@dataclass
class pbox:
    u1: float=0
    v1: float=0
    u2: float=0
    v2: float=0
    n_u1: float=0
    n_v1: float=0
    n_u2: float=0
    n_v2: float=0

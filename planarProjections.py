mag=lambda vec:sum([el**2 for el in vec])**.5
def proj_to_v3(vec2d,vmag):
    return tuple(list(vec2d[:2])+[(vmag**2-mag(vec2d[:2])**2)**.5])
def v3_to_proj(vec3d):
    return tuple(vec3d[:2])

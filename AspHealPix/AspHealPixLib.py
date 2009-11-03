#$ID:   $
def generate(env, **kw):
    if not kw.get('depsOnly', 0):
        env.Tool('addLibrary', library = ['AspHealPix'])
    env.Tool('astroLib')
    env.Tool('asp_healpixLib')
    env.Tool('irfInterfaceLib')
    env.Tool('irfLoaderLib')
    env.Tool('map_toolsLib')
    env.Tool('pyASPLib')

def exists(env):
    return 1

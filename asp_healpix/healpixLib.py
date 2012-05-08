#$Id$
def generate(env, **kw):
    if not kw.get('depsOnly',0):
        env.Tool('addLibrary', library = ['healpix'])
    env.Tool('astroLib')
    
def exists(env):
    return 1;

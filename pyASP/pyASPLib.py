# $Header$
def generate(env, **kw):
    if not kw.get('depsOnly', 0):
        env.Tool('addLibrary', library=['pyASP'])
    env.Tool('astroLib')

def exists(env):
    return 1;

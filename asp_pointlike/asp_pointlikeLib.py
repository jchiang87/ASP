# @file asp_pointlikeLib.py
# @brief scons package dependencies
#
#$Id$
def generate(env, **kw):
    if not kw.get('depsOnly',0):
        env.Tool('addLibrary', library = ['asp_pointlike'])
    depends = 'astro asp_healpix asp_skymaps embed_python'.split()
    for pack in depends: env.Tool(pack+'Lib')
    env.Tool('addLibrary', library=env['minuitLibs'])
    
def exists(env):
    return 1

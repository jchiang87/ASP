# @file grbASPLib.py
# @brief scons package dependencies for grbASP
#
#$Header$
def generate(env, **kw):
        if not kw.get('depsOnly',0):
                env.Tool('addLibrary', library=['grpASP'])

        env.Tool('astroLib')
        env.Tool('irfInterfaceLib')
        env.Tool('irfLoaderLib')
        env.Tool('BayesianBlocksLib')
        env.Append(LIBS=[ 'Netx'])
        env.Tool('addLibrary', library=env['rootLibs'])

def exists(env):
        return 1

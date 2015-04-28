# @file asp_skymapsLib.py
# @brief scons package dependencies for asp_skymaps
#
#$Header$
def generate(env, **kw):
	if not kw.get('depsOnly',0):
		env.Tool('addLibrary', library=['asp_skymaps'])
        depends = 'facilities tip st_facilities asp_healpix embed_python'.split()
        for pack in depends: env.Tool(pack+'Lib')

	# why these?
	#env.Tool('addLibrary', library=env['clhepLibs'])
	#env.Tool('addLibrary', library=env['cfitsioLibs'])

def exists(env):
	return 1

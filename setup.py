from distutils.core import Extension, setup
from Cython.Build import cythonize

# define an extension that will be cythonized and compiled
ext = Extension(name="verle_cython", sources=["verle_cython.pyx"])
setup(ext_modules=cythonize(ext))
#from setuptools import setup
import setuptools # I think this is needed for the following
from numpy.distutils.core import Extension,setup
from distutils.spawn import find_executable

ext_modules = []
exec(compile(open('Instruments/version.py', "rb").read(), 'Instruments/version.py', 'exec'))

setup(
        name='francklab_instruments',
        author='Beaton,Betts,Franck',
        version=__version__,
        packages=setuptools.find_packages(),
        license='LICENSE.md',
        author_email='jmfranck@notgiven.com',
        url='http://github.com/jmfrancklab/inst_notebooks',
        description='object-oriented control of various instruments',
        long_description="Bridge12 amplifier, GwInstek AFG and oscilloscope",
        install_requires=[
            "numpy",
            "h5py",
            "pyserial>=3.0",
            ],
        ext_modules = ext_modules,
        entry_points=dict(console_scripts=
            [
                'power_control_server=Instruments.power_control_server:main'
                ]
            )
        )

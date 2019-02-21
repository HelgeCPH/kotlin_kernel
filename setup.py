# from distutils.core import setup
import kotlin_kernel
from setuptools import setup


with open('README.md') as f:
    readme = f.read()

setup(
    name='kotlin_kernel',
    version=kotlin_kernel.__version__,
    packages=['kotlin_kernel'],
    description='A Kotlin kernel for Jupyter',
    long_description=readme,
    author='HelgeCPH',
    author_email='ropf@itu.dk',
    url='https://github.com/HelgeCPH/kotlin_kernel',
    install_requires=[
        'jupyter_client==5.2.3', 'IPython', 'ipykernel', 'requests', 'jinja2'
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
    ],
)

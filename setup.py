from setuptools import setup, find_packages


setup(
    name='fsm_modal_analysis',
    version='1.0.2',
    url='https://bitbucket.org/petar/fsm_modal_analysis',
    license='BSD',
    author='Petar Maric',
    author_email='petarmaric@uns.ac.rs',
    description='Console app and Python API for visualization and modal '\
                'analysis of the parametric model of buckling and free '\
                'vibration in prismatic shell structures, as computed by the '\
                'fsm_eigenvalue project.',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Physics',
    ],
    platforms='any',
    py_modules=['fsm_modal_analysis'],
    entry_points={
        'console_scripts': ['fsm_modal_analysis=fsm_modal_analysis:main'],
    },
    install_requires=open('requirements.txt').read().splitlines(),
)

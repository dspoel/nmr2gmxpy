import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nmr2gmxpy",
    version="1.0.0",
    author="Anna Sinelnikova",
    author_email="anna.sinelnikova@physics.uu.se",
    description="Convert NMR data file (NMR restraints V2 (STAR)) to GROMACS format (.itp-file)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dspoel/nmr2gmxpy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Mac OS",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Science/Research"
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    #python_requires='>=3.6',
)
import setuptools
from pathlib import Path

BASE_DIR = Path(__file__).parent

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = [line.strip() for line in f]

pkginfo = {}
exec((BASE_DIR / "hpargparse" / "pkginfo.py").read_text(), None, pkginfo)

setuptools.setup(
    name="hpargparse",
    version=pkginfo["__version__"],
    author="Xinyu Zhou",
    author_email="zxy@megvii.com",
    description="An argparse extension for hpman",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/megvii-research/hpargparse",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    scripts=["bin/hpcli"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)

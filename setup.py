from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="ncas_amof_netcdf_template",
    version= "2.0.0-beta" ,
    description="Package to create NCAS AMOF netCDF files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/joshua-hampton/ncas_amof_netcdf_template",
    author="Joshua M. Ralph-Hampton",
    author_email="joshua.hampton@ncas.ac.uk",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    keywords="NCAS, AMOF, netcdf, template, standard",
    package_dir={"":"src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7, <4",
    install_requires=["netcdf4",
                      "numpy",
                      "requests",
                      "pandas"
                     ]
)

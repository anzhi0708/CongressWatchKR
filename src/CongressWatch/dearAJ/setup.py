import setuptools

with open("README.md") as f:
    long_description: str = f.read()

with open("./src/dearaj/__init__.py") as f:
    for line in f.readlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            version = line.split(delim)[1]
            break
    else:
        print("Can't find version!")
        exit(1)

setuptools.setup(
    name="dearaj",
    version=version,
    author="Anji Wong",
    author_email="anzhi0708@gmail.com",
    description="Data analysis tool for Korean National Assembly",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["requests", "faker", "tqdm"],
    url="https://github.com/anzhi0708/dearAJ",
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Sociology :: History",
        "Topic :: Sociology :: Genealogy",
        "Topic :: Education :: Testing",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Natural Language :: Korean"
    ],
    python_requires=">=3.6"
)
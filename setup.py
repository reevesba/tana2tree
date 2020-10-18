import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tana2tree",
    version="1.1.7",
    author="Bradley Reeves",
    author_email="bradleyaaronreeeves@gmail.com",
    description="Parses Tanagra description into usable formats.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/reevesba/tana2tree",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
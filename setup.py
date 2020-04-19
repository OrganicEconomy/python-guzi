import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="python-guzi",
    version="0.0.4",
    author="Guillaume Dubus",
    author_email="Guillaume1.dubus@gmail.com",
    description="A light library to use Guzi in python application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GuziEconomy/python-guzi",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['python-dateutil'],
)

# Note : upload command :
# 1. Create dist files
# $ rm dist/*; python3 setup.py sdist bdist_wheel
#
# 2. Push it to pypi
# $ python3 -m twine upload  --repository-url https://upload.pypi.org/legacy/ dist/*
#
# For mor details, see https://packaging.python.org/tutorials/packaging-projects/

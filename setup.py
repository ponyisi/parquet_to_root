import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="parquet_to_root",
    version="0.2.0",
    author="Peter Onyisi",
    author_email="ponyisi@utexas.edu",
    description="Parquet-to-ROOT translator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ponyisi/parquet_to_root",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['pyarrow>=2']
)

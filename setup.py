import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="boxkite",
    version="0.0.5",
    author="Luke Marsden",
    author_email="me@lukemarsden.net",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/boxkite-ml/boxkite",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "fluent-logger>=0.10.0,<0.11",
        "prometheus_client>=0.10.1,<0.12",
        "numpy>=1.16,<2",
        "dataclasses; python_version<'3.7'",
    ],
)

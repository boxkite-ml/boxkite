import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="boxkite",
    version="0.0.3",
    author="Luke Marsden",
    author_email="me@lukemarsden.net",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/basisai/boxkite",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    # TODO: can we relax these requirements at all?
    install_requires=[
        "fluent-logger==0.10.0",
        "prometheus_client==0.9",
        "numpy==1.19.4",
    ],
)

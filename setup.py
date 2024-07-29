import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyiso20022",
    version="0.4.5",
    author="Peter Houghton",
    author_email="pete@investigatingsoftware.co.uk",
    description="pyiso20022 is a library for generating ISO20022 messages in Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/phoughton/pyiso20022",
    packages=setuptools.find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)

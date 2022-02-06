import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gradescope-api",
    version="0.0.2",
    author="CS 161 Staff",
    author_email="cs161-staff@berkeley.edu",
    description="An unofficial Gradescope API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cs161-staff/gradescope-api",
    project_urls={
        "Homepage": "https://cs161.org",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=["requests", "bs4"],
)

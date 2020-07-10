import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="EpiCodeGenerator-Yehor-Dzhurynskyi",
    version="0.0.1",
    author="Yehor-Dzhurynskyi",
    author_email="y.a.dzhurynskyi@gmail.com",
    description="CODE GENERATION TOOL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YehorDzhurynskyi/EpiCodeGenerator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

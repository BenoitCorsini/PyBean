import setuptools
  
with open("README.md", "r") as fh:
    description = fh.read()
  
setuptools.setup(
    name="PyBean",
    version="0.0.1",
    author="Benoit Corsini",
    author_email="benoitcorsini@gmail.com",
    packages=["bean"],
    description="A Python package for creating videos.",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/BenoitCorsini/PyBean",
    license='GNU Lesser General Public License v3 (LGPLv3)',
    python_requires='>=3.8',
    install_requires=[]
)
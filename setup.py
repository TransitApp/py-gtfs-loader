from setuptools import setup, find_packages

setup(name='py-gtfs-loader',
      version='0.1.13',
      description='Load GTFS',
      url='https://github.com/TransitApp/py-gtfs-loader',
      author='Nicholas Paun, Jonathan Milot',
      license='License :: OSI Approved :: MIT License',
      packages=find_packages(),
      zip_safe=False,
      install_requires=[])

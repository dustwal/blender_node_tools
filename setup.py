from setuptools import setup

with open("README.rst", 'r') as readme:
    long_description = readme.read()

setup(
    name='blender_node_tools',
    version='1.0',
    description="",
    license="GPL-3.0",
    long_description=long_description,
    author="Dustin Walde",
    author_email='dustin@arcsineimaging.com',
    packages=['blender_node_tools'],
    )
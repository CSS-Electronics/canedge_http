from setuptools import setup
import versioneer

setup(
    name='CANedge_HTTP',
    author='Christian Steiniche',
    author_email='css@csselectronics.com',
    packages=['CANedge_HTTP'],
    scripts=[],
    url="https://github.com/CSS-Electronics/canedge_http/",
    license='LICENSE',
    description='Python module for accessing the CANEdge2 via HTTP',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    install_requires=[],
    cmdclass=versioneer.get_cmdclass(),
    version=versioneer.get_version(),
)
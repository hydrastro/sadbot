"""Setup"""
import setuptools

setuptools.setup(
    name="sadbot",
    version="0.1",
    py_modules=["sadbot"],
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": ["sadbot = sadbot:run"]},
)

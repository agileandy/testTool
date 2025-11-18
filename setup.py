from setuptools import setup, find_packages

setup(
    name="testTool",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "testtool = testTool.main:main"
        ]
    },
)

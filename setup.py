from setuptools import setup, find_packages

setup(
    name="testTool",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "playwright>=1.40.0",
        "pydantic>=2.5.0",
        "pyyaml>=6.0.1",
        "click>=8.1.0",
        "rich>=13.7.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "testtool = testTool.main:main"
        ]
    },
)

from setuptools import setup, find_packages

setup(
    name="pyjavawrap",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "requests",
        "pydantic",
        "pydantic-settings",
        "jinja2",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "pyjavawrap=pyjavawrap.main:main",
        ],
    },
)

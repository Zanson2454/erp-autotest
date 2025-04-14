from setuptools import setup, find_packages

setup(
    name="erp_autotest",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pytest",
        "requests",
        "pymysql",
    ],
    python_requires=">=3.6",
) 
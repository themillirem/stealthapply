from setuptools import setup, find_packages

setup(
    name="stealthapply",
    version="1.0.0",
    description="Privacy-first stealth resume submission tool for SolidWorks engineers",
    author="StealthApply",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "requests>=2.31.0",
        "PyPDF2>=3.0.1",
        "python-docx>=1.1.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
    ],
    entry_points={
        "console_scripts": [
            "stealthapply=stealthapply.main:main",
        ],
    },
)

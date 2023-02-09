from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")


setup(
    name="charset_mnbvc",
    version="0.0.2",
    description="本项目旨在对大量文本文件进行快速编码检测以辅助mnbvc语料集项目的数据清洗工作",
    url="https://github.com/alanshi/charset_mnbvc",
    author="Alan Shi",
    author_email="alan.shi86@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3"
    ],
    packages=['charset_mnbvc'],
    python_requires=">=3.7",
    project_urls={  # Optional
        "Bug Reports": "https://github.com/alanshi/charset_mnbvc/issues",
        "Source": "https://github.com/alanshi/charset_mnbvc/",
    },
)
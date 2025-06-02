"""Setup configuration for Talisik Short URL library"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="talisik-short-url",
    version="0.1.0",
    author="Erick Luna",
    author_email="erick.luna@seven-gen.com",
    description="Privacy-focused URL shortener library and service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",  # For environment variables
        "xata>=1.0.0",           # Xata Python client
    ],
    extras_require={
        "api": ["fastapi>=0.100.0", "uvicorn[standard]>=0.20.0"],
        "dev": ["pytest>=7.0.0", "pytest-cov>=4.0.0", "black>=23.0.0", "ruff>=0.1.0"],
        "xata": ["xata>=1.0.0"],  # Optional Xata dependency group
    },
) 
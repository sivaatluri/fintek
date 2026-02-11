"""Setup configuration for finops-config package."""
from setuptools import find_packages, setup

setup(
    name="finops-config",
    version="0.1.0",
    description="Configuration management for FinOps services",
    author="FinOps Team",
    python_requires=">=3.11",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
        ],
    },
)

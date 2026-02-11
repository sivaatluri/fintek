"""Setup configuration for finops-common package."""
from setuptools import setup, find_packages

setup(
    name="finops-common",
    version="0.1.0",
    description="Common utilities for FinOps SaaS services",
    author="FinOps Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "python-json-logger>=2.0.7",
        "opentelemetry-api>=1.22.0",
        "opentelemetry-sdk>=1.22.0",
        "opentelemetry-instrumentation-fastapi>=0.43b0",
        "opentelemetry-exporter-otlp>=1.22.0",
        "python-multipart>=0.0.6",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "httpx>=0.26.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
        ],
    },
)

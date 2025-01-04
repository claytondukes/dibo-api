"""Setup configuration for DIBO API."""

from setuptools import setup, find_packages

setup(
    name="api",
    version="0.1.0",
    description="Diablo Immortal Build Optimizer API",
    author="Charles Dukes",
    author_email="me@csdukes.com",
    package_dir={"": "."},
    packages=find_packages(where="."),
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "python-jose[cryptography]>=3.3.0",
        "httpx>=0.25.2",
        "python-dotenv>=1.0.0",
        "pydantic[email]>=2.5.2",
        "pydantic-settings>=2.1.0",
        "email-validator>=2.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.23.2",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "isort>=5.12.0",
            "mypy>=1.7.1",
            "ruff>=0.1.6",
        ]
    },
    entry_points={
        "console_scripts": [
            "api=api.main:main",
        ],
    },
)

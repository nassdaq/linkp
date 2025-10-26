from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="linkp",
    version="1.0.2",
    author="nassdaq",
    description="AI-powered tool for daily LinkedIn developer progress posts, with git tracking, AI summarization, and visual generation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nassdaq/linkp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "click>=8.0.0",
        "openai>=1.0.0",
        "requests>=2.28.0",
        "Pillow>=9.0.0",
        "python-dotenv>=0.19.0",
    ],
    entry_points={
        "console_scripts": [
            "linkp=linkp.cli:main",
        ],
    },
)

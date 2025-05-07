#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="audio_upscale",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "librosa>=0.9.0",
        "soundfile>=0.10.0",
        "tqdm>=4.62.0",
        "click>=8.0.0",
        "matplotlib>=3.4.0",
    ],
    entry_points={
        "console_scripts": [
            "audio-upscale=audio_upscale.cli:cli",
        ],
    },
    author="Faycal Amrouche",
    author_email="your.email@example.com",
    description="A tool for enhancing audio quality using FFT-based processing",
    keywords="audio, enhancement, fft, upscaling, processing",
    url="https://github.com/yourusername/audio-upscale",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/audio-upscale/issues",
        "Source Code": "https://github.com/yourusername/audio-upscale",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Multimedia :: Sound/Audio :: Conversion",
    ],
) 
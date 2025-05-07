# Audio Upscaler CLI

A command-line tool for upscaling audio quality using FFT (Fast Fourier Transform) processing.

## Features

- Enhance audio quality using advanced spectral processing
- Multiple enhancement algorithms: harmonics, stereo widening, exciter, transient detection
- Save and load custom presets for different audio sources
- Visualize before/after spectral differences
- Support for common audio formats (WAV, MP3, FLAC)
- Process mono and stereo files
- Progress visualization during processing

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/audio-upscale.git
cd audio-upscale

# Install in development mode
pip install -e .
```

## Usage

After installation, you can use the `audio-upscale` command:

```bash
# Basic usage
audio-upscale upscale input.mp3 output.wav

# With custom parameters
audio-upscale upscale input.mp3 output.wav --intensity 2.0 --harmonics-boost 0.5

# Use spectral enhancers
audio-upscale upscale input.mp3 output.wav --enhancers "harmonic,exciter"

# Save your settings as a preset
audio-upscale upscale input.mp3 output.wav --intensity 1.8 --harmonics-boost 0.6 --save-preset "my_preset"

# Use a saved preset
audio-upscale upscale input.mp3 output.wav --preset "my_preset"

# Generate visualizations
audio-upscale upscale input.mp3 output.wav --visualize
```

Alternatively, you can run the script directly:

```bash
python upscale.py upscale input.mp3 output.wav
```

## Available Commands

```
Commands:
  delete-preset           Delete a preset.
  enhancer-info           Show information about enhancers or a specific...
  list-available-enhancers  List all available spectral enhancers.
  show-preset             Show details of a specific preset.
  show-presets            List all available presets.
  upscale                 Upscale audio quality using FFT processing.
  visualize               Visualize the difference between original and...
```

## Project Structure

```
audio-upscale/
├── audio_upscale/            # Main package
│   ├── __init__.py           # Package initialization
│   ├── cli.py                # Command line interface
│   ├── core/                 # Core functionality
│   │   ├── __init__.py
│   │   └── upscaler.py       # Main upscaler implementation
│   ├── enhancers/            # Spectral enhancement modules
│   │   ├── __init__.py
│   │   └── spectral.py       # FFT-based enhancers
│   ├── utils/                # Utility functions
│   │   ├── __init__.py
│   │   └── preset_manager.py # Preset management
│   └── visualization/        # Visualization tools
│       ├── __init__.py
│       └── visualize.py      # Visualization functions
├── tests/                    # Test suite
│   ├── __init__.py           # Test package initialization
│   ├── run_tests.py          # Test runner script
│   └── test_audio_upscaler.py # Test cases for audio upscaler
├── .gitignore                # Git ignore file
├── README.md                 # Project documentation
├── requirements.txt          # Dependencies
├── setup.py                  # Package setup
└── upscale.py                # Main executable
```

## How It Works

This tool uses the Fast Fourier Transform (FFT) to convert audio signals from the time domain to the frequency domain, applies various enhancements to the frequency spectrum, and then converts back to the time domain using the Inverse FFT (IFFT).

The process includes:
- Spectral analysis
- Harmonic enhancement
- Dynamic range adjustment
- Noise reduction
- Transient enhancement
- Stereo widening
- Harmonic excitation

## Advanced Features

### Spectral Enhancers

The tool includes several specialized spectral enhancers:

- **Harmonic Enhancer**: Boosts harmonics to create a richer sound
- **Spectral Widener**: Creates a wider stereo image using phase manipulation
- **Exciter**: Adds harmonic excitement similar to audio exciter hardware
- **Transient Enhancer**: Detects and enhances transients for better clarity

### Presets

Save your favorite settings as presets to quickly apply them to different audio files:

```bash
# List available presets
audio-upscale show-presets

# View a specific preset
audio-upscale show-preset my_preset

# Delete a preset
audio-upscale delete-preset my_preset
```

## Development

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests:
   ```bash
   # Run all tests
   python tests/run_tests.py
   
   # Or use unittest directly
   python -m unittest discover tests
   ```
5. Submit a pull request

## Running Tests

The project includes a comprehensive test suite to ensure functionality:

```bash
# Run all tests with the test runner
cd audio-upscale
python tests/run_tests.py

# Run specific test file
python -m unittest tests/test_audio_upscaler.py

# Run specific test case
python -m unittest tests.test_audio_upscaler.TestAudioUpscaler.test_process_file
```

 
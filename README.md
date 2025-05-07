# Audio Upscaler

A simple tool to make your audio sound better using some fancy signal processing.

## What it does

- Makes your audio sound clearer and fuller
- Works with MP3, WAV, and other common formats
- Shows progress as it works
- Lets you save your favorite settings

## Quick start

```bash
# Clone it
git clone https://github.com/Faycall1l/audio-upscaler.git
cd audio-upscale

# Install stuff
pip install -r requirements.txt

# Run it
python upscale.py upscale your-audio.mp3 your-audio-improved.mp3
```

## Basic commands

```bash
# Simple upscale
python upscale.py upscale input.mp3 output.mp3

# Make it more intense
python upscale.py upscale input.mp3 output.mp3 --intensity 2.0

# Add some special effects
python upscale.py upscale input.mp3 output.mp3 --enhancers "harmonic,exciter"

# Save settings you like
python upscale.py upscale input.mp3 output.mp3 --intensity 1.8 --save-preset "my_preset"

# Use saved settings
python upscale.py upscale input.mp3 output.mp3 --preset "my_preset"
```

## What's in the box

- **Harmonic enhancer**: Makes your audio sound richer
- **Stereo widener**: Makes the stereo image wider
- **Exciter**: Adds some sparkle to the high end
- **Transient enhancer**: Makes drums and other percussive sounds pop

## Testing

If you want to run the tests:

```bash
python tests/run_tests.py
```

## Project structure

```
├── audio_upscale/       # Main code
├── tests/               # Tests
├── requirements.txt     # Dependencies
├── setup.py            # Setup script
└── upscale.py          # Main script
```

That's it! Have fun making your audio sound better! 🎵
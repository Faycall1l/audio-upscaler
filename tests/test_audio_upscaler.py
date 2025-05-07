#!/usr/bin/env python3
"""
Tests for Audio Upscaler

This module contains tests for the Audio Upscaler functionality.
"""

import os
import sys
import unittest
import tempfile
import numpy as np
import soundfile as sf
from pathlib import Path

# Add parent directory to path to import audio_upscale
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from audio_upscale.core.upscaler import AudioUpscaler
from audio_upscale.enhancers import create_enhancer_chain, get_available_enhancers


class TestAudioUpscaler(unittest.TestCase):
    """Test cases for the AudioUpscaler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a simple test audio file (sine wave)
        self.sample_rate = 22050
        self.duration = 1.0  # 1 second
        self.test_audio = np.sin(2 * np.pi * 440 * np.linspace(0, self.duration, int(self.sample_rate * self.duration)))
        
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_input_path = os.path.join(self.temp_dir.name, "test_input.wav")
        self.test_output_path = os.path.join(self.temp_dir.name, "test_output.wav")
        
        # Save the test audio
        sf.write(self.test_input_path, self.test_audio, self.sample_rate)
        
        # Create a default upscaler
        self.upscaler = AudioUpscaler()
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    def test_upscaler_initialization(self):
        """Test that the upscaler initializes with default parameters."""
        upscaler = AudioUpscaler()
        self.assertIsNotNone(upscaler)
        self.assertEqual(upscaler.intensity, 1.5)
        self.assertEqual(upscaler.harmonics_boost, 0.3)
        self.assertEqual(upscaler.noise_reduction, 0.2)
        self.assertEqual(upscaler.dynamic_boost, 1.2)
        self.assertTrue(upscaler.clarity_enhance)
    
    def test_upscaler_custom_parameters(self):
        """Test that the upscaler initializes with custom parameters."""
        upscaler = AudioUpscaler(
            intensity=2.0,
            harmonics_boost=0.5,
            noise_reduction=0.1,
            dynamic_boost=1.5,
            clarity_enhance=False
        )
        self.assertEqual(upscaler.intensity, 2.0)
        self.assertEqual(upscaler.harmonics_boost, 0.5)
        self.assertEqual(upscaler.noise_reduction, 0.1)
        self.assertEqual(upscaler.dynamic_boost, 1.5)
        self.assertFalse(upscaler.clarity_enhance)
    
    def test_process_file(self):
        """Test processing a file."""
        # Process the test audio file
        stats = self.upscaler.process_file(self.test_input_path, self.test_output_path)
        
        # Check that the output file exists
        self.assertTrue(os.path.exists(self.test_output_path))
        
        # Check that stats were returned
        self.assertIn('duration', stats)
        self.assertIn('processing_time', stats)
        
        # Load the processed audio
        processed_audio, sr = sf.read(self.test_output_path)
        
        # Check that the processed audio has the same sample rate
        self.assertEqual(sr, self.sample_rate)
        
        # Check that the processed audio has the same length
        self.assertEqual(len(processed_audio), len(self.test_audio))
    
    def test_enhancer_chain(self):
        """Test creating and using an enhancer chain."""
        # Create an enhancer chain
        enhancer_config = [
            {'name': 'harmonic'},
            {'name': 'widener'}
        ]
        enhancer_chain = create_enhancer_chain(enhancer_config)
        
        # Create an upscaler with the enhancer chain
        upscaler = AudioUpscaler(enhancer_chain=enhancer_chain)
        
        # Process the test audio file
        upscaler.process_file(self.test_input_path, self.test_output_path)
        
        # Check that the output file exists
        self.assertTrue(os.path.exists(self.test_output_path))


class TestEnhancers(unittest.TestCase):
    """Test cases for the enhancers module."""
    
    def test_available_enhancers(self):
        """Test that enhancers are available."""
        enhancers = get_available_enhancers()
        self.assertIsNotNone(enhancers)
        self.assertIsInstance(enhancers, dict)
        
        # Check for expected enhancers
        expected_enhancers = ['harmonic', 'widener', 'exciter', 'transient']
        for enhancer in expected_enhancers:
            self.assertIn(enhancer, enhancers)


if __name__ == '__main__':
    unittest.main()

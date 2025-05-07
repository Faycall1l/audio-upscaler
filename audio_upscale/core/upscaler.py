#!/usr/bin/env python3
"""
Core Audio Upscaler implementation
"""

import os
import time
import numpy as np
import librosa
import soundfile as sf
from tqdm import tqdm
from scipy import signal

from audio_upscale.enhancers import (
    get_available_enhancers,
    create_enhancer_chain,
    apply_enhancer_chain
)
from audio_upscale.utils.preset_manager import load_preset, save_preset


class AudioUpscaler:
    """FFT-based audio upscaler with various enhancement techniques"""
    
    def __init__(self, intensity=1.5, harmonics_boost=0.3, noise_reduction=0.2, 
                 dynamic_boost=1.2, clarity_enhance=True, enhancer_chain=None):
        """
        Initialize the upscaler with enhancement parameters
        
        Args:
            intensity: Overall intensity of the effect (1.0 = normal)
            harmonics_boost: Level of harmonic enhancement (0.0 = none)
            noise_reduction: Strength of noise floor reduction (0.0 = none)
            dynamic_boost: Dynamic range enhancement (1.0 = no change)
            clarity_enhance: Whether to apply clarity enhancement
            enhancer_chain: List of spectral enhancer objects to apply
        """
        self.intensity = intensity
        self.harmonics_boost = harmonics_boost
        self.noise_reduction = noise_reduction
        self.dynamic_boost = dynamic_boost
        self.clarity_enhance = clarity_enhance
        self.enhancer_chain = enhancer_chain or []
        
    def _process_frame(self, frame):
        """Process a single frame of audio using FFT"""
        # Apply FFT to convert to frequency domain
        fft_data = np.fft.rfft(frame)
        magnitudes = np.abs(fft_data)
        phases = np.angle(fft_data)
        
        # Create a copy for processing
        enhanced_magnitudes = magnitudes.copy()
        enhanced_phases = phases.copy()
        
        # Noise floor reduction
        if self.noise_reduction > 0:
            noise_floor = np.mean(enhanced_magnitudes[-len(enhanced_magnitudes)//5:])
            mask = enhanced_magnitudes > (noise_floor * (1 + self.noise_reduction * 3))
            enhanced_magnitudes = enhanced_magnitudes * mask
        
        # Harmonic enhancement
        if self.harmonics_boost > 0:
            # Focus on the first half of the spectrum (most important harmonics)
            harmonic_region = len(enhanced_magnitudes) // 2
            boost_curve = np.linspace(1.0, 0.1, harmonic_region)
            boost_amount = 1.0 + (boost_curve * self.harmonics_boost)
            enhanced_magnitudes[:harmonic_region] *= boost_amount
        
        # Overall intensity scaling
        enhanced_magnitudes = enhanced_magnitudes * self.intensity
        
        # Dynamic range enhancement
        if self.dynamic_boost != 1.0:
            # Compress or expand the dynamic range
            mean_magnitude = np.mean(enhanced_magnitudes)
            enhanced_magnitudes = mean_magnitude + (enhanced_magnitudes - mean_magnitude) * self.dynamic_boost
            enhanced_magnitudes = np.maximum(0, enhanced_magnitudes)  # Ensure no negative values
        
        # Clarity enhancement
        if self.clarity_enhance:
            # Enhance mid-range frequencies for better clarity
            mid_start = len(enhanced_magnitudes) // 8
            mid_end = len(enhanced_magnitudes) // 3
            enhanced_magnitudes[mid_start:mid_end] *= 1.2
        
        # Apply spectral enhancer chain if available
        if self.enhancer_chain:
            enhanced_magnitudes, enhanced_phases = apply_enhancer_chain(
                enhanced_magnitudes, enhanced_phases, self.enhancer_chain)
        
        # Reconstruct the signal
        enhanced_fft = enhanced_magnitudes * np.exp(1j * enhanced_phases)
        enhanced_frame = np.fft.irfft(enhanced_fft)
        
        return enhanced_frame
    
    def process_audio(self, audio_data, sr, frame_size=2048, hop_length=1024, progress_callback=None):
        """
        Process the entire audio file
        
        Args:
            audio_data: Input audio as numpy array
            sr: Sample rate
            frame_size: FFT frame size
            hop_length: Hop length between frames
            progress_callback: Optional callback for progress updates
            
        Returns:
            Enhanced audio data
        """
        # Handle mono/stereo
        is_stereo = len(audio_data.shape) > 1 and audio_data.shape[1] == 2
        
        if is_stereo:
            # Process each channel separately
            left_channel = audio_data[:, 0]
            right_channel = audio_data[:, 1]
            
            print("Processing left channel...")
            enhanced_left = self._process_channel(left_channel, sr, frame_size, hop_length, progress_callback)
            
            print("Processing right channel...")
            enhanced_right = self._process_channel(right_channel, sr, frame_size, hop_length, progress_callback)
            
            # Combine channels
            enhanced_audio = np.column_stack((enhanced_left, enhanced_right))
        else:
            enhanced_audio = self._process_channel(audio_data, sr, frame_size, hop_length, progress_callback)
        
        return enhanced_audio
    
    def _process_channel(self, channel_data, sr, frame_size=2048, hop_length=1024, progress_callback=None):
        """Process a single audio channel"""
        # Pad audio to ensure complete processing
        pad_length = frame_size
        padded_audio = np.pad(channel_data, (pad_length, pad_length), mode='reflect')
        
        # Prepare output array
        enhanced_audio = np.zeros_like(padded_audio)
        
        # Process in frames with overlap
        total_frames = 1 + (len(padded_audio) - frame_size) // hop_length
        
        with tqdm(total=total_frames, desc="Upscaling audio") as pbar:
            for i in range(0, len(padded_audio) - frame_size, hop_length):
                frame = padded_audio[i:i+frame_size]
                enhanced_frame = self._process_frame(frame)
                
                # Overlap-add to output
                enhanced_audio[i:i+frame_size] += enhanced_frame * signal.windows.hann(frame_size)
                pbar.update(1)
                
                if progress_callback:
                    progress_callback(i / (len(padded_audio) - frame_size))
        
        # Normalize for the overlap
        num_overlaps = frame_size // hop_length
        enhanced_audio /= num_overlaps
        
        # Remove padding
        enhanced_audio = enhanced_audio[pad_length:-pad_length]
        
        # Normalize audio level
        max_val = np.max(np.abs(enhanced_audio))
        if max_val > 0:
            target_level = 0.95
            current_level = max_val
            gain = target_level / current_level
            enhanced_audio = enhanced_audio * gain
        
        return enhanced_audio
    
    def process_file(self, input_file, output_file, frame_size=2048):
        """
        Process an audio file and save the result
        
        Args:
            input_file: Path to input audio file
            output_file: Path to save enhanced audio
            frame_size: FFT frame size
            
        Returns:
            dict: Processing statistics
        """
        start_time = time.time()
        
        # Load audio file
        print(f"Loading audio file: {input_file}")
        try:
            audio_data, sr = librosa.load(input_file, sr=None, mono=False)
        except Exception as e:
            raise RuntimeError(f"Error loading audio file: {e}")
        
        duration = librosa.get_duration(y=audio_data, sr=sr)
        print(f"Loaded audio: {sr}Hz, {duration:.2f} seconds")
        
        # Process audio
        enhanced_audio = self.process_audio(audio_data, sr, frame_size=frame_size)
        
        # Save enhanced audio
        print(f"Saving enhanced audio to: {output_file}")
        sf.write(output_file, enhanced_audio, sr)
        
        elapsed_time = time.time() - start_time
        print(f"Processing completed in {elapsed_time:.2f} seconds")
        
        # Return processing stats
        return {
            "input_file": input_file,
            "output_file": output_file,
            "sample_rate": sr,
            "duration": duration,
            "processing_time": elapsed_time,
            "frame_size": frame_size
        }
    
    def save_preset(self, preset_name):
        """Save current settings as a preset"""
        preset_data = {
            "intensity": self.intensity,
            "harmonics_boost": self.harmonics_boost,
            "noise_reduction": self.noise_reduction,
            "dynamic_boost": self.dynamic_boost,
            "clarity_enhance": self.clarity_enhance,
            "enhancers": [{"name": e.name.lower().replace("enhancer", "")} for e in self.enhancer_chain]
        }
        
        return save_preset(preset_name, preset_data)
    
    @classmethod
    def from_preset(cls, preset_name):
        """Create upscaler from a preset"""
        preset_data = load_preset(preset_name)
        
        # Create enhancer chain if specified
        enhancer_chain = None
        if "enhancers" in preset_data:
            enhancer_chain = create_enhancer_chain(preset_data["enhancers"])
            
        # Remove enhancers from the preset data
        if "enhancers" in preset_data:
            del preset_data["enhancers"]
            
        # Create upscaler with preset settings
        return cls(enhancer_chain=enhancer_chain, **preset_data)


def get_enhancer_params(enhancer_type):
    """Return the available parameters for a given enhancer type"""
    enhancers = get_available_enhancers()
    if enhancer_type not in enhancers:
        return {}
        
    # This is a simplistic approach - in a production environment,
    # you'd want to use introspection to get the actual parameters
    if enhancer_type == 'harmonic':
        return {
            'harmonic_boost': 1.5,
            'harmonic_decay': 0.5
        }
    elif enhancer_type == 'widener':
        return {
            'width': 1.5
        }
    elif enhancer_type == 'exciter':
        return {
            'drive': 1.5
        }
    elif enhancer_type == 'transient':
        return {
            'sensitivity': 0.5,
            'attack_boost': 2.0
        }
    
    return {} 
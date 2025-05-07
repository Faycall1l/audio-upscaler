#!/usr/bin/env python3
"""
Spectral Enhancement Plugins for Audio Upscaler
"""

import numpy as np
from abc import ABC, abstractmethod


class SpectralEnhancer(ABC):
    """Base class for spectral enhancement algorithms"""
    
    @abstractmethod
    def process(self, magnitudes, phases):
        """
        Process the spectral components
        
        Args:
            magnitudes: FFT magnitude spectrum
            phases: FFT phase spectrum
            
        Returns:
            enhanced_magnitudes: Enhanced magnitude spectrum
            enhanced_phases: Modified or original phase spectrum
        """
        pass
    
    @property
    def name(self):
        """Return the name of the enhancer"""
        return self.__class__.__name__


class HarmonicEnhancer(SpectralEnhancer):
    """Enhance harmonics in the audio spectrum"""
    
    def __init__(self, harmonic_boost=1.5, harmonic_decay=0.5, preserve_phases=True):
        """
        Initialize harmonic enhancer
        
        Args:
            harmonic_boost: Amount to boost harmonics
            harmonic_decay: How quickly harmonic boosting decreases for higher harmonics
            preserve_phases: Whether to preserve original phases
        """
        self.harmonic_boost = harmonic_boost
        self.harmonic_decay = harmonic_decay
        self.preserve_phases = preserve_phases
    
    def process(self, magnitudes, phases):
        """Enhance harmonics in the frequency spectrum"""
        enhanced_magnitudes = magnitudes.copy()
        enhanced_phases = phases
        
        # Find the fundamental frequency (simplistic approach - looking for peak in lower freq)
        # For more accurate results, consider implementing a proper pitch detection algorithm
        lower_region = min(len(magnitudes) // 5, 100)
        if lower_region > 0:
            fundamental_idx = np.argmax(magnitudes[:lower_region])
            if fundamental_idx > 0:  # Found a potential fundamental frequency
                # Enhance harmonics
                for harmonic in range(2, 8):  # Process up to 7th harmonic
                    harmonic_idx = fundamental_idx * harmonic
                    if harmonic_idx < len(magnitudes):
                        # Calculate boost that decreases with higher harmonics
                        boost = self.harmonic_boost * (1 / (harmonic ** self.harmonic_decay))
                        
                        # Apply boost to a small region around the harmonic frequency
                        window_size = max(3, min(5, len(magnitudes) // 1000))
                        start_idx = max(0, harmonic_idx - window_size)
                        end_idx = min(len(magnitudes), harmonic_idx + window_size + 1)
                        
                        # Apply graduated boost (stronger in center, weaker at edges)
                        window = np.hanning(end_idx - start_idx)
                        boost_factors = 1 + (window * (boost - 1))
                        enhanced_magnitudes[start_idx:end_idx] *= boost_factors
        
        return enhanced_magnitudes, enhanced_phases


class SpectralWidener(SpectralEnhancer):
    """Widen the stereo image using spectral techniques"""
    
    def __init__(self, width=1.5, focus_region=(300, 5000)):
        """
        Initialize stereo widener
        
        Args:
            width: Stereo width factor (1.0 = unchanged)
            focus_region: Frequency range to focus on (Hz)
        """
        self.width = width
        self.focus_region = focus_region
    
    def process(self, magnitudes, phases):
        """Apply stereo widening effect"""
        # This enhancer is designed to work on a single channel
        # The actual stereo widening happens when processing both channels
        # and applying different phase shifts to each
        
        enhanced_magnitudes = magnitudes.copy()
        
        # Generate phase shift (normally would be applied differently to L and R channels)
        # For mono signals, this just adds some extra harmonics/overtones
        phase_shift = np.linspace(0, np.pi/4 * (self.width - 1), len(phases))
        enhanced_phases = phases + phase_shift
        
        return enhanced_magnitudes, enhanced_phases


class ExciterEnhancer(SpectralEnhancer):
    """Add harmonic excitement/saturation to the audio"""
    
    def __init__(self, drive=1.5, freq_range=(1000, 16000)):
        """
        Initialize harmonic exciter
        
        Args:
            drive: Drive/intensity of the effect (1.0 = subtle)
            freq_range: Frequency range to target (Hz)
        """
        self.drive = drive
        self.freq_range = freq_range
    
    def process(self, magnitudes, phases):
        """Add harmonic excitement to the spectrum"""
        enhanced_magnitudes = magnitudes.copy()
        
        # Simple saturation effect - creates gentle harmonics
        # For real-world implementation, use true waveshaping algorithms
        enhanced_magnitudes = np.tanh(enhanced_magnitudes * self.drive) / self.drive
        
        # Apply frequency targeting - focus on the specified range
        # This would require knowledge of the frequency resolution (sample_rate / n_fft)
        # For demonstration, we'll use a simple bandpass-like approach
        
        # Create a simple bandpass-like mask
        mask = np.ones_like(enhanced_magnitudes)
        mid_point = len(mask) // 2
        
        # Apply very gentle boost to the target range (simplified version)
        boost_region = slice(len(mask) // 8, len(mask) // 2)
        mask[boost_region] = 1.1
        
        enhanced_magnitudes *= mask
        
        return enhanced_magnitudes, phases


class TransientEnhancer(SpectralEnhancer):
    """Enhance transients in the audio signal"""
    
    def __init__(self, sensitivity=0.5, attack_boost=2.0):
        """
        Initialize transient enhancer
        
        Args:
            sensitivity: How sensitive the detection should be (0.0-1.0)
            attack_boost: How much to boost detected transients
        """
        self.sensitivity = sensitivity
        self.attack_boost = attack_boost
        self._prev_magnitudes = None
    
    def process(self, magnitudes, phases):
        """Enhance audio transients using spectral flux"""
        enhanced_magnitudes = magnitudes.copy()
        
        # We need previous frame for transient detection
        if self._prev_magnitudes is None:
            self._prev_magnitudes = magnitudes
            return enhanced_magnitudes, phases
        
        # Calculate spectral flux (increase in magnitudes compared to previous frame)
        flux = magnitudes - self._prev_magnitudes
        
        # Only boost positive flux (increases in energy = potential transients)
        positive_flux = np.maximum(0, flux)
        
        # Detect actual transients (simplistic threshold-based approach)
        threshold = np.mean(positive_flux) * (1 + self.sensitivity * 5)
        transient_mask = positive_flux > threshold
        
        # Apply boost to transients
        boost_amount = 1.0 + (transient_mask * (self.attack_boost - 1.0))
        enhanced_magnitudes *= boost_amount
        
        # Store current magnitudes for next frame
        self._prev_magnitudes = magnitudes
        
        return enhanced_magnitudes, phases


def get_available_enhancers():
    """Return a dictionary of available enhancers"""
    return {
        'harmonic': HarmonicEnhancer,
        'widener': SpectralWidener,
        'exciter': ExciterEnhancer,
        'transient': TransientEnhancer
    }


def create_enhancer_chain(config):
    """
    Create a chain of enhancers from configuration
    
    Args:
        config: List of dicts with enhancer name and params
        Example: [
            {'name': 'harmonic', 'params': {'harmonic_boost': 1.5}},
            {'name': 'exciter', 'params': {'drive': 2.0}}
        ]
    
    Returns:
        List of initialized enhancers
    """
    available = get_available_enhancers()
    enhancers = []
    
    for item in config:
        name = item['name']
        params = item.get('params', {})
        
        if name in available:
            enhancer = available[name](**params)
            enhancers.append(enhancer)
    
    return enhancers


def apply_enhancer_chain(magnitudes, phases, enhancers):
    """
    Apply a chain of enhancers to the spectral data
    
    Args:
        magnitudes: FFT magnitude spectrum
        phases: FFT phase spectrum
        enhancers: List of enhancer instances
    
    Returns:
        enhanced_magnitudes: Processed magnitude spectrum
        enhanced_phases: Processed phase spectrum
    """
    enhanced_magnitudes = magnitudes
    enhanced_phases = phases
    
    for enhancer in enhancers:
        enhanced_magnitudes, enhanced_phases = enhancer.process(
            enhanced_magnitudes, enhanced_phases)
    
    return enhanced_magnitudes, enhanced_phases 
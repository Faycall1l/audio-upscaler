#!/usr/bin/env python3
"""
Visualization module for the audio upscaler
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import click


def plot_waveform_comparison(original, enhanced, sr, title="Waveform Comparison"):
    """Plot original vs enhanced waveform"""
    plt.figure(figsize=(12, 6))
    
    # Ensure we're comparing the same length
    min_len = min(len(original), len(enhanced))
    original = original[:min_len]
    enhanced = enhanced[:min_len]
    
    time = np.linspace(0, min_len/sr, min_len)
    
    plt.subplot(2, 1, 1)
    plt.plot(time, original)
    plt.title("Original Waveform")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    
    plt.subplot(2, 1, 2)
    plt.plot(time, enhanced)
    plt.title("Enhanced Waveform")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    
    plt.tight_layout()
    return plt.gcf()


def plot_spectrum_comparison(original, enhanced, sr, title="Spectrum Comparison"):
    """Plot original vs enhanced frequency spectrum"""
    plt.figure(figsize=(12, 6))
    
    # Ensure we're comparing the same length
    min_len = min(len(original), len(enhanced))
    original = original[:min_len]
    enhanced = enhanced[:min_len]
    
    # Compute FFT
    n_fft = 2048
    original_fft = np.abs(librosa.stft(original, n_fft=n_fft))
    enhanced_fft = np.abs(librosa.stft(enhanced, n_fft=n_fft))
    
    # Convert to dB scale
    original_db = librosa.amplitude_to_db(original_fft, ref=np.max)
    enhanced_db = librosa.amplitude_to_db(enhanced_fft, ref=np.max)
    
    plt.subplot(2, 1, 1)
    librosa.display.specshow(original_db, sr=sr, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title("Original Spectrogram")
    
    plt.subplot(2, 1, 2)
    librosa.display.specshow(enhanced_db, sr=sr, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title("Enhanced Spectrogram")
    
    plt.tight_layout()
    return plt.gcf()


def plot_spectral_difference(original, enhanced, sr, title="Spectral Enhancement"):
    """Plot the difference between original and enhanced spectrum"""
    plt.figure(figsize=(12, 4))
    
    # Ensure we're comparing the same length
    min_len = min(len(original), len(enhanced))
    original = original[:min_len]
    enhanced = enhanced[:min_len]
    
    # Compute FFT
    n_fft = 2048
    original_fft = np.abs(librosa.stft(original, n_fft=n_fft))
    enhanced_fft = np.abs(librosa.stft(enhanced, n_fft=n_fft))
    
    # Compute difference
    diff = enhanced_fft - original_fft
    
    # Convert to dB scale
    diff_db = librosa.amplitude_to_db(np.abs(diff), ref=np.max(original_fft))
    
    librosa.display.specshow(diff_db, sr=sr, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title("Spectral Enhancement Difference")
    
    plt.tight_layout()
    return plt.gcf()


def visualize_comparison(original_file, enhanced_file, output=None, sample_duration=10.0):
    """Visualize the difference between original and enhanced audio files."""
    
    # Load audio files
    print("Loading audio files...")
    y_orig, sr_orig = librosa.load(original_file, sr=None, duration=sample_duration)
    y_enh, sr_enh = librosa.load(enhanced_file, sr=None, duration=sample_duration)
    
    # Ensure same sample rate
    if sr_orig != sr_enh:
        print(f"Warning: Sample rates differ ({sr_orig} vs {sr_enh}). Resampling...")
        if sr_orig > sr_enh:
            y_enh = librosa.resample(y_enh, orig_sr=sr_enh, target_sr=sr_orig)
            sr = sr_orig
        else:
            y_orig = librosa.resample(y_orig, orig_sr=sr_orig, target_sr=sr_enh)
            sr = sr_enh
    else:
        sr = sr_orig
    
    # For stereo, use the first channel
    if len(y_orig.shape) > 1:
        y_orig = y_orig[0]
    if len(y_enh.shape) > 1:
        y_enh = y_enh[0]
    
    # Create visualizations
    print("Generating waveform comparison...")
    fig1 = plot_waveform_comparison(y_orig, y_enh, sr)
    
    print("Generating spectrum comparison...")
    fig2 = plot_spectrum_comparison(y_orig, y_enh, sr)
    
    print("Generating spectral difference...")
    fig3 = plot_spectral_difference(y_orig, y_enh, sr)
    
    # Save or display
    if output:
        output_base = output.rsplit('.', 1)[0] if '.' in output else output
        
        waveform_out = f"{output_base}_waveform.png"
        spectrum_out = f"{output_base}_spectrum.png"
        diff_out = f"{output_base}_difference.png"
        
        print(f"Saving visualizations to {output_base}_*.png")
        fig1.savefig(waveform_out, dpi=300, bbox_inches='tight')
        fig2.savefig(spectrum_out, dpi=300, bbox_inches='tight')
        fig3.savefig(diff_out, dpi=300, bbox_inches='tight')
    else:
        plt.show() 
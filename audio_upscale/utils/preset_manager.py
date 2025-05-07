#!/usr/bin/env python3
"""
Preset management utilities for audio upscaler
"""

import os
import json


PRESETS_DIR = os.path.expanduser("~/.audio_upscale/presets")


def ensure_presets_dir():
    """Ensure the presets directory exists"""
    os.makedirs(PRESETS_DIR, exist_ok=True)
    return PRESETS_DIR


def list_presets():
    """List all available presets"""
    presets_dir = ensure_presets_dir()
    if not os.path.exists(presets_dir):
        return []
        
    return [f.replace(".json", "") for f in os.listdir(presets_dir) 
            if f.endswith(".json")]


def get_preset_path(preset_name):
    """Get the full path to a preset file"""
    return os.path.join(PRESETS_DIR, f"{preset_name}.json")


def load_preset(preset_name):
    """
    Load a preset from file
    
    Args:
        preset_name: Name of the preset
        
    Returns:
        dict: Preset data
        
    Raises:
        ValueError: If preset doesn't exist
    """
    preset_path = get_preset_path(preset_name)
    
    if not os.path.exists(preset_path):
        raise ValueError(f"Preset '{preset_name}' not found")
    
    with open(preset_path, 'r') as f:
        return json.load(f)


def save_preset(preset_name, preset_data):
    """
    Save a preset to file
    
    Args:
        preset_name: Name of the preset
        preset_data: Dictionary of preset settings
        
    Returns:
        str: Path to the saved preset
    """
    presets_dir = ensure_presets_dir()
    preset_path = get_preset_path(preset_name)
    
    with open(preset_path, 'w') as f:
        json.dump(preset_data, f, indent=2)
    
    return preset_path


def delete_preset(preset_name):
    """
    Delete a preset
    
    Args:
        preset_name: Name of the preset
        
    Returns:
        bool: True if deleted, False if not found
    """
    preset_path = get_preset_path(preset_name)
    
    if not os.path.exists(preset_path):
        return False
    
    os.remove(preset_path)
    return True


def get_preset_info(preset_name):
    """
    Get information about a preset
    
    Args:
        preset_name: Name of the preset
        
    Returns:
        dict: Preset information
        
    Raises:
        ValueError: If preset doesn't exist
    """
    preset_data = load_preset(preset_name)
    
    # Format the preset data for display
    info = {
        "name": preset_name,
        "parameters": {},
        "enhancers": []
    }
    
    # Extract enhancers
    if "enhancers" in preset_data:
        info["enhancers"] = preset_data["enhancers"]
        del preset_data["enhancers"]
    
    # Everything else is parameters
    info["parameters"] = preset_data
    
    return info 
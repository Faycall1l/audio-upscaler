#!/usr/bin/env python3
"""
Command Line Interface for Audio Upscaler
"""

import os
import time
import json
import click

from audio_upscale.core.upscaler import AudioUpscaler, get_enhancer_params
from audio_upscale.enhancers import get_available_enhancers, create_enhancer_chain
from audio_upscale.utils.preset_manager import (
    list_presets, load_preset, save_preset, delete_preset, get_preset_info
)


def list_enhancers():
    """List all available enhancers with descriptions"""
    enhancers = {
        'harmonic': 'Enhances harmonic content for richer sound',
        'widener': 'Creates a wider stereo image',
        'exciter': 'Adds harmonic saturation for brightness',
        'transient': 'Enhances transients for better clarity'
    }
    return enhancers


# Create a group for all commands
@click.group()
@click.version_option(package_name='audio_upscale')
def cli():
    """Audio Upscaler - Enhance audio quality using FFT processing."""
    pass


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.option('--intensity', type=float, default=1.5, help='Overall effect intensity')
@click.option('--harmonics-boost', type=float, default=0.3, help='Harmonic enhancement level')
@click.option('--noise-reduction', type=float, default=0.2, help='Noise reduction strength')
@click.option('--dynamic-boost', type=float, default=1.2, help='Dynamic range enhancement')
@click.option('--clarity/--no-clarity', default=True, help='Apply clarity enhancement')
@click.option('--frame-size', type=int, default=2048, help='FFT frame size')
@click.option('--preset', type=str, help='Use a saved preset')
@click.option('--enhancers', type=str, help='Comma-separated list of enhancers to apply')
@click.option('--save-preset', type=str, help='Save settings as a preset')
@click.option('--visualize/--no-visualize', default=False, help='Generate visualizations')
def upscale(input_file, output_file, intensity, harmonics_boost, noise_reduction, 
            dynamic_boost, clarity, frame_size, preset, enhancers, save_preset, visualize):
    """Upscale audio quality using FFT processing."""
    
    start_time = time.time()
    
    # Handle preset loading
    if preset:
        try:
            click.echo(f"Loading preset: {preset}")
            upscaler = AudioUpscaler.from_preset(preset)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            return
    else:
        # Create enhancer chain if specified
        enhancer_chain = []
        if enhancers:
            enhancer_list = [e.strip() for e in enhancers.split(',')]
            for e_name in enhancer_list:
                click.echo(f"Adding enhancer: {e_name}")
                enhancer_config = [{'name': e_name}]
                enhancer_chain.extend(create_enhancer_chain(enhancer_config))
        
        # Create upscaler
        upscaler = AudioUpscaler(
            intensity=intensity, 
            harmonics_boost=harmonics_boost,
            noise_reduction=noise_reduction,
            dynamic_boost=dynamic_boost,
            clarity_enhance=clarity,
            enhancer_chain=enhancer_chain
        )
    
    # Save preset if requested
    if save_preset:
        preset_path = upscaler.save_preset(save_preset)
        click.echo(f"Saved preset to {preset_path}")
    
    try:
        # Process file
        stats = upscaler.process_file(input_file, output_file, frame_size=frame_size)
    except Exception as e:
        click.echo(f"Error processing file: {e}", err=True)
        return
    
    # Show processing stats
    elapsed_time = time.time() - start_time
    click.echo(f"Total processing time: {elapsed_time:.2f} seconds")
    click.echo(f"Audio duration: {stats['duration']:.2f} seconds")
    click.echo(f"Processing speed: {stats['duration']/stats['processing_time']:.2f}x realtime")
    
    # Generate visualizations if requested
    if visualize:
        try:
            click.echo("Generating visualizations...")
            from audio_upscale.visualization import visualize_comparison
            
            # For visualization, we'll use a short sample (max 30 seconds)
            sample_duration = min(30.0, stats['duration'])
            
            # Generate visualizations
            vis_dir = os.path.splitext(output_file)[0] + "_vis"
            os.makedirs(vis_dir, exist_ok=True)
            
            output_base = os.path.join(vis_dir, "comparison")
            visualize_comparison(input_file, output_file, output=output_base, sample_duration=sample_duration)
            
            click.echo(f"Visualizations saved to {vis_dir}")
        except Exception as e:
            click.echo(f"Error generating visualizations: {e}", err=True)


@cli.command()
def list_available_enhancers():
    """List all available spectral enhancers."""
    enhancers = list_enhancers()
    click.echo("Available spectral enhancers:")
    for name, desc in enhancers.items():
        click.echo(f"  • {name}: {desc}")


@cli.command()
@click.argument('enhancer_type', required=False)
def enhancer_info(enhancer_type):
    """Show information about enhancers or a specific enhancer."""
    if enhancer_type:
        enhancers = list_enhancers()
        if enhancer_type not in enhancers:
            click.echo(f"Enhancer '{enhancer_type}' not found", err=True)
            return
            
        click.echo(f"Enhancer: {enhancer_type}")
        click.echo(f"Description: {enhancers[enhancer_type]}")
        
        params = get_enhancer_params(enhancer_type)
        if params:
            click.echo("Parameters:")
            for param, default in params.items():
                click.echo(f"  • {param}: {default} (default)")
    else:
        list_available_enhancers()


@cli.command()
def show_presets():
    """List all available presets."""
    presets = list_presets()
    if not presets:
        click.echo("No presets found.")
        return
        
    click.echo("Available presets:")
    for preset in presets:
        click.echo(f"  • {preset}")


@cli.command()
@click.argument('preset_name')
def show_preset(preset_name):
    """Show details of a specific preset."""
    try:
        info = get_preset_info(preset_name)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        return
        
    click.echo(f"Preset: {info['name']}")
    
    click.echo("\nParameters:")
    for key, value in info["parameters"].items():
        click.echo(f"  • {key}: {value}")
    
    if info["enhancers"]:
        click.echo("\nEnhancers:")
        for enhancer in info["enhancers"]:
            click.echo(f"  • {enhancer['name']}")


@cli.command()
@click.argument('preset_name')
def delete_preset(preset_name):
    """Delete a preset."""
    success = delete_preset(preset_name)
    if success:
        click.echo(f"Preset '{preset_name}' deleted")
    else:
        click.echo(f"Preset '{preset_name}' not found", err=True)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.option('--output-dir', type=click.Path(), help='Directory to save visualizations')
@click.option('--sample-duration', type=float, default=10.0, help='Duration (seconds) to analyze')
def visualize(input_file, output_file, output_dir, sample_duration):
    """Visualize the difference between original and enhanced audio files."""
    from audio_upscale.visualization import visualize_comparison
    
    output_path = output_file
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        basename = os.path.basename(output_file)
        output_path = os.path.join(output_dir, basename)
    
    visualize_comparison(input_file, output_file, output=output_path, sample_duration=sample_duration)


if __name__ == '__main__':
    cli() 
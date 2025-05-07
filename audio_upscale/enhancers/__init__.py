"""Spectral enhancement modules for audio processing."""

from audio_upscale.enhancers.spectral import (
    get_available_enhancers,
    create_enhancer_chain,
    apply_enhancer_chain
)

__all__ = [
    'get_available_enhancers',
    'create_enhancer_chain',
    'apply_enhancer_chain'
] 
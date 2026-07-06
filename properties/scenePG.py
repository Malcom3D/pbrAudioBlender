# Copyright (C) 2025 Malcom3D <malcom3d.gpl@gmail.com>
#
# This file is part of pbrAudio.
#
# pbrAudio is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pbrAudio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pbrAudio.  If not, see <https://www.gnu.org/licenses/>.
# SPDX-License-Identifier: GPL-3.0-or-later

import bpy
from bpy.types import PropertyGroup
from bpy.props import EnumProperty, IntProperty, BoolProperty, StringProperty, PointerProperty, FloatProperty

classes = []

class PBRAudioSceneProperties(PropertyGroup):
    def set_quality(self, context):
        if 'LOW' in self.audio_quality:
            self.sample_rate = 24000
            self.bit_depth = '16BIT'
        if 'MEDIUM' in self.audio_quality:
            self.sample_rate = 48000
            self.bit_depth = '24BIT'
        if 'HIGH' in self.audio_quality:
            self.sample_rate = 96000
            self.bit_depth = '24BIT'
        if 'ULTRA' in self.audio_quality:
            self.sample_rate = 192000
            self.bit_depth = '32BIT'

    def set_preview_sample_rate(self, context):
        if 'LOW' in self.preview_audio_quality:
            self.preview_sample_rate = 24000
        if 'MEDIUM' in self.preview_audio_quality:
            self.preview_sample_rate = 48000
        if 'HIGH' in self.preview_audio_quality:
            self.preview_sample_rate = 96000
        if 'ULTRA' in self.preview_audio_quality:
            self.preview_sample_rate = 192000

    # Define the first property
    def update_value(self, context):
        if self.surround_LFE > self.surround_channels:
            self.surround_LFE = self.surround_channels

#    """Scene properties for pbrAudio NodeTree"""
#    acoustic_shader_type = EnumProperty(
#        name="AcousticShaderType",
#        items=[
#            ('OBJECT', "Object", "Edit Shader Node from Object"),
#            ('WORLD', "World", "Edit Shader Node from World"),
#            ('SOUND', "Sound", "Edit Shader Node from Sound"),
#        ],
#        default='OBJECT'
#    )

    """Scene properties for pbrAudio"""
    device: EnumProperty(
        name="Device",
        items=[
            ('CPU', "CPU", "Use CPU device for rendering"),
            ('GPU', "GPU Compute", "Use GPU Compute device for rendering, configured in the system tab in the user preferences"),
        ],
        default='CPU'
    )

    audio_quality: EnumProperty(
        name="Audio Quality",
        items=[
            ('LOW', "Low", "Low quality, fast rendering"),
            ('MEDIUM', "Medium", "Balanced quality and speed"),
            ('HIGH', "High", "High quality, slow rendering"),
            ('ULTRA', "Ultra", "Ultra quality, very slow rendering"),
        ],
        default='MEDIUM',
        update=set_quality
    )

    sample_rate: FloatProperty(
        name="Sample Rate",
        description="Audio sample rate in Hz",
        default=48000,
        min=12000,
        max=192000
    )

    output_format = EnumProperty(
        name="Output Format",
        description="Output Format to save the rendered audio",
        items=[
            ('AMBISONIC', "Ambisonic", "Output Audio in ambisonic format"),
            ('SURROUND', "Surround", "Output Audio in surround format"),
            ('STEREO', "Stereo", "Output Audio in stereo format"),
        ],
        default='AMBISONIC'
    )

    ambisonic_order: IntProperty(
        name="Ambisonic order of rendered audio",
        description="Audio sample rate in Hz",
        default=1,
        min=0,
        max=3 
    )

    surround_channels: IntProperty(
        name="Number of channels",
        description="Number of full range channels of rendered audio",
        default=5,
        min=2,
        max=256 
    )

    surround_LFE: IntProperty(
        name="Number of LFE channels",
        description="Number of low-frequency effect dedicated audio tracks (120Hz limited)",
        default=1,
        min=0,
        max=256 
        update=update_value
    )

    stereo_hrtf: BoolProperty(
        name="Enable HRTF process",
        description="Enable rendering of ambisonic sound tracks to HRTF stereo",
        default=False
    )

    hrtf_file: StringProperty( 
        name="HRTF",
        description="Select the HRTF file for rendering",
        subtype='FILE_PATH',
        default='',
        options={'PATH_SUPPORTS_BLEND_RELATIVE', 'ANIMATABLE'}
    )

    file_format: EnumProperty(
        name="File Format",
        items=[
            ('RAW', "RAW: un-containerized and uncompressed RAW Waveform Audio File Format", "RAW Waveform Audio File Format"),
            ('PCM', "WAV: PCM Waveform Audio File Format", "PCM Waveform Audio File Format"),
        ],
        default='PCM',
    )

    output_path: StringProperty(
        name="Output",
        description="Path to save audio files",
        subtype='FILE_PATH',
        options={'PATH_SUPPORTS_BLEND_RELATIVE'},
        default='/tmp/'
    )

    bit_depth: EnumProperty(
        name="Bit Depth",
        items=[
            ('16BIT', "16 bit", "16-bit Depth per Channel"),
            ('24BIT', "24 bit", "24-bit Depth per Channel"),
            ('32BIT', "32 bit", "32-bit Depth per Channel"),
            ('FLOAT', "32 bit float", "32-bit float Depth per Channel"),
            ('DOUBLE', "64 bit float", "32-bit float Depth per Channel"),
        ],
        default='24BIT',
    )

    enable_graphical_preview: BoolProperty(
        name="Enable Graphical Preview",
        description="Enable graphical preview",
        default=False
    )

    viewRays_collection: StringProperty(
        name="Rays Graphical Preview Collection Name",
        default='viewRays'
    )

    enable_acoustic_preview: BoolProperty(
        name="Acoustic Preview",
        description="Enable acoustic preview",
        default=False
    )

    preview_sample_rate: IntProperty(
        name="Sample Rate For Acoustic Preview",
        description="Audio sample rate in Hz",
        default=48000,
        min=12000,
        max=192000
    )

    preview_audio_quality: EnumProperty(
        name="Audio Quality",
        items=[
            ('LOW', "Low", "Low quality, fast rendering"),
            ('MEDIUM', "Medium", "Balanced quality and speed"),
            ('HIGH', "High", "High quality, slow rendering"),
            ('ULTRA', "Ultra", "Ultra quality, very slow rendering"),
        ],
        default='MEDIUM',
        update=set_preview_sample_rate
    )

    preview_bit_depth: EnumProperty(
        name="Bit Depth",
        items=[
            ('16BIT', "16 bit", "16-bit Depth per Channel"),
            ('24BIT', "24 bit", "24-bit Depth per Channel"),
            ('32BIT', "32 bit", "32-bit Depth per Channel"),
            ('FLOAT', "32 bit float", "32-bit float Depth per Channel"),
            ('DOUBLE', "64 bit float", "32-bit float Depth per Channel"),
        ],
        default='24BIT',
    )

    collision_collection: PointerProperty(
        name="Collision Collection",
        description="Collection for collision",
        type=bpy.types.Collection
    )

    collision_margin: FloatProperty(
        name="Collision Margin",
        default=1E-1,
        min=0,
        max=1
    ) 

    samples_per_object: IntProperty(
        name="Samples per Object",
        default=1000,
        min=0,
        max=99999999
    )

    modal_modes: IntProperty(
        name="Modal modes",
        description="Number of Modal Modes",
        default=20,
        min=1,
        max=100
    )

    fracture: BoolProperty(
        name="fracture",
        description="Bake fracture data for sound synthesis",
        default=False
    )

    bake: BoolProperty(
        name="bake",
        description="Bake prebaked data for sound synthesis",
        default=False
    )

    prebake: BoolProperty(
        name="prebake",
        description="Prebake baked physics dynamics for sound synthesis",
        default=False
    )

    physics: BoolProperty( 
        name="physics", 
        description="Bake physics dynamics",
        default=False
    )

    shader_processing: BoolProperty(
        name="Shader Processing",
        description="Indicates if shaders is currently being processed",
        default=False
    )
    
    status_progress: FloatProperty(
        name="Status Progress",
        description="Progress of processing",
        default=0.0,
        min=0.0,
        max=1.0,
        subtype='PERCENTAGE'
    )

    cache_path: StringProperty(
        name="Cache",
        description="Path to save cache files",
        subtype='DIR_PATH',
        options={'PATH_SUPPORTS_BLEND_RELATIVE'},
        default='//pbrAudioCache'
    )

    cache_status: BoolProperty(
        name="Cache Status",
        description="True if cache is initialized",
        default=False
    )

    """Scene properties for pbrAudio AudioForcesDenoiser"""

    enable_forces_denoiser: BoolProperty(
        name="AudioForces Denoiser",
        default=False
    )

    enable_dc_blocker: BoolProperty(
        name="DC Blocker",
        default=False
    )

    dc_blocker_alpha: FloatProperty(
        name="Alpha",
        description="DC blocker coefficient (higher = more aggressive)",
        default=0.999
    )

    # Adaptive Noise Gate parameters
    enable_noise_gate: BoolProperty(
        name="Adaptive Noise Gate",
        default=False
    )

    gate_threshold_db: FloatProperty( 
        name="dB Threshold",
        description="Noise gate threshold in dB",
        default=-60.0
    )

    gate_attack_ms: FloatProperty(
        name="Attack ms",
        description="Attack time in ms",
        default=2.0
    )

    gate_release_ms: FloatProperty(
        name="Release ms",
        description="Release time in ms",
        default=50.0
    )

    gate_hold_ms: FloatProperty(
        name="Hold ms",
        description="Hold time in ms",
        default=10.0
    )

    # Temporal Smoothing parameters
    enable_temporal_smoothing: BoolProperty(
        name="Temporal Smoothing",
        default=False
    )

    temporal_smoothing_window: IntProperty(
        name="Window size",
        description="Window size for temporal smoothing (samples)",
        default=5
    )

    # Spectral Noise Reduction parameters
    enable_spectral_noise_reduction: BoolProperty(
        name="Spectral Noise Reduction",
        default=False
    )

    spectral_fft_size: IntProperty(
        name="FFT size",
        description="FFT size for spectral processing",
        default=2048
    )

    spectral_hop_size: IntProperty(
        name="Hop size",
        description="Hop size for spectral processing",
        default=512
    )

    spectral_noise_floor_db: FloatProperty(
        name="Noise floor dB",
        description="Noise floor estimate in dB",
        default=-80.0
    )

    spectral_reduction_strength: FloatProperty(
        name="Reduction strength",
        description="Reduction strength (0-1)",
        default=0.8
    )

    spectral_smoothing: FloatProperty(
        name="Smoothing",
        description="Spectral smoothing factor",
        default=0.3
    )

    # Envelope Shaping parameters
    enable_envelope_shaping: BoolProperty(
        name="Envelope Shaping",
        default=False
    )

    envelope_attack_ms: FloatProperty(
        name="Attack",
        description="Attack time for envelope",
        default=1.0
    )

    envelope_release_ms: FloatProperty(
        name="Release",
        description="Release time for envelope",
        default=20.0
    )

    envelope_smoothing: FloatProperty(
        name="Smoothing",
        description="Envelope smoothing factor",
        default=0.5
    )

    # Gaussian Adaptive Smoothing parameters
    enable_gaussian_adaptive_smoothing: BoolProperty(
        name="Gaussian Adaptive Smoothing",
        default=False
    )

    gaussian_sigma_min: FloatProperty(
        name="Minimum sigma",
        description="Minimum Gaussian sigma",
        default=0.5
    )

    gaussian_sigma_max: FloatProperty(
        name="Maximum sigma",
        description="Maximum Gaussian sigma",
        default=3.0
    )

    gaussian_force_threshold: FloatProperty(
        name="Force threshold",
        description="Force threshold for adaptive smoothing",
        default=0.1
    )


    """Configuration for pbrAudio post-processing parameters."""

    enable_postprocess: BoolProperty(
        name="PostProcessing",
        default=True
    )

    postprocess_dynamic_denoise_enabled: BoolProperty(
        name="Dynamic Denoise",
        description="Enable PostProcess Dynamic Denoise",
        default=False
    ) 

    postprocess_noise_gate_threshold_db: FloatProperty(
        name="Noise Gate Threshold",
        description="PostProcess Noise Gate Threshold in dB",
        default=-60.0
    )

    postprocess_noise_floor_estimate_db: FloatProperty(
        name="Noise Floor",
        description="PostProcess Estimated Noise Floor in dB",
        default=-80.0
    )

    postprocess_spectral_reduction_strength: FloatProperty(
        name="Spectral Reduction strength",
        description="PostProcess Spectral Reduction strength (0-1)",
        default=0.7,
        min=0,
        max=1
    )

    postprocess_temporal_smoothing_window: IntProperty(
        name="Window size",
        description="PostProcess Temporal Smoothing Window size for temporal smoothing in samples",
        default=5
    )
    
    # Dynamic reference weighting
    postprocess_force_reference_weight: FloatProperty(
        name="Reduction strength",
        description="PostProcess Force Reference Weighting",
        default=0.3
    )

    postprocess_min_force_threshold: FloatProperty( 
        name="Minimum Force",
        description="PostProcess Minimum Force Threshold",
        default=1e-6
    )
    
    # Smoothing parameters
    postprocess_smoothing_enabled: BoolProperty(
        name="Smoothing",
        description="Enable PostProcess Dynamic Smoothing",
        default=False
    )

    postprocess_smoothing_window_ms: FloatProperty(  
        name="Smoothing Window",
        description="PostProcess Smoothing Window in milliseconds",
        default=2.0
    )

    postprocess_adaptive_smoothing: BoolProperty(
        name="Adaptive Smoothing",
        description="Enable PostProcess Dynamic Adaptive Smoothing",
        default=False
    )
    
    # Phase alignment
    postprocess_phase_align_enabled: BoolProperty(    
        name="Phase Align",
        description="Enable PostProcess Dynamic Phase Alignment",
        default=False
    )

    postprocess_crossfade_samples: IntProperty(
        name="Crossfade Length",
        description="PostProcess Crossfade Length in samples",
        default=5
    )
    
    # Audio-Force drived dynamic Amplification
    postprocess_target_rms: FloatProperty(
        name="Target RMS",
        description="PostProcess Target RMS Dynamic Amplification Level in dB",
        default=0.15
    )

    postprocess_max_gain_db: FloatProperty(
        name="Maximum Gain",
        description="PostProcess Maximum Dynamic Amplification Gain in dB",
        default=20.0
    )

    postprocess_dynamic_range_compression: FloatProperty(
        name="DRC Compression",
        description="PostProcess Dynamic Range Compression",
        default=0.5,
        min=0,
        max=1
    )
    
    # Blending
    postprocess_blend_enabled: BoolProperty(
        name="Tracks Blend",
        description="Enable PostProcess Dynamic Tracks Blending",
        default=False
    )

    postprocess_dry_wet_mix: FloatProperty(
        name="Dry/Wet Level",
        description="PostProcess Dry/Wet Mix Level",
        default=0.85,
        min=0,
        max=1
    )

    postprocess_normalize_output: BoolProperty(
        name="Normalize output",
        description="Normalize PostProcessed Output",
        default=False
    )

classes.append(PBRAudioSceneProperties)

import numpy as np
import soundfile as sf
from scipy.spatial.transform import Rotation
import json
import os
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import warnings


class AmbisonicDecoder:
    """
    Decode ambisonic files to multiple audio channels based on spherical positions.
    Supports ambisonic orders 0-3 (FuMa and ACN formats).
    """
    
    def __init__(self, json_config_path: str = None, config_data: Dict = None):
        """
        Initialize the decoder with configuration.
        
        Args:
            json_config_path: Path to JSON configuration file
            config_data: Direct configuration data (alternative to file path)
        """
        if json_config_path:
            with open(json_config_path, 'r') as f:
                self.config = json.load(f)
        elif config_data:
            self.config = config_data
        else:
            raise ValueError("Either json_config_path or config_data must be provided")
        
        # Validate configuration
        self._validate_config()
        
        # Initialize decoder
        self.order = self._detect_ambisonic_order()
        self.num_channels = (self.order + 1) ** 2
        self.sample_rate = None
        self.audio_data = None
        
    def _validate_config(self):
        """Validate the configuration structure."""
        required_fields = ['file_path', 'channels', 'center_location', 'boundaries']
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Missing required field in config: {field}")
        
        if len(self.config['boundaries']) != self.config['channels']:
            warnings.warn(f"Number of boundaries ({len(self.config['boundaries'])}) "
                         f"doesn't match channels count ({self.config['channels']})")
    
    def _detect_ambisonic_order(self) -> int:
        """
        Detect ambisonic order from the number of channels.
        For N channels, order = sqrt(N) - 1
        """
        ambisonic_file = self.config['file_path']
        
        # Try to detect from file if it exists
        if os.path.exists(ambisonic_file):
            try:
                info = sf.info(ambisonic_file)
                num_channels = info.channels
                
                # Calculate order from channel count
                order = int(np.sqrt(num_channels)) - 1
                if (order + 1) ** 2 != num_channels:
                    warnings.warn(f"Channel count {num_channels} doesn't match standard ambisonic layout")
                
                # Check if it matches config channels
                if num_channels != self.config['channels']:
                    warnings.warn(f"File has {num_channels} channels, config expects {self.config['channels']}")
                
                return order
            except Exception as e:
                warnings.warn(f"Could not detect order from file: {e}")
        
        # Fallback: infer from boundaries count
        num_boundaries = len(self.config['boundaries'])
        order = int(np.sqrt(num_boundaries)) - 1
        
        if (order + 1) ** 2 != num_boundaries:
            warnings.warn(f"Boundaries count {num_boundaries} doesn't match standard ambisonic layout")
        
        return order
    
    def load_ambisonic_file(self):
        """Load the ambisonic audio file."""
        ambisonic_file = self.config['file_path']
        
        if not os.path.exists(ambisonic_file):
            raise FileNotFoundError(f"Ambisonic file not found: {ambisonic_file}")
        
        self.audio_data, self.sample_rate = sf.read(ambisonic_file)
        
        # Ensure audio data has correct shape
        if len(self.audio_data.shape) == 1:
            # Mono file - not valid for ambisonics
            raise ValueError("Ambisonic file should have multiple channels")
        
        if self.audio_data.shape[1] != self.num_channels:
            warnings.warn(f"Audio file has {self.audio_data.shape[1]} channels, "
                         f"expected {self.num_channels} for order {self.order}")
    
    def spherical_harmonics(self, azimuth: float, elevation: float, order: int = 3) -> np.ndarray:
        """
        Calculate spherical harmonics for a given direction (ACN/SN3D normalization).
        
        Args:
            azimuth: Azimuth angle in radians (0 to 2π)
            elevation: Elevation angle in radians (-π/2 to π/2)
            order: Ambisonic order
        
        Returns:
            Array of spherical harmonic coefficients for channels 0 to (order+1)^2-1
        """
        # Convert to spherical coordinates
        theta = azimuth  # azimuth
        phi = np.pi/2 - elevation  # inclination (0 at north pole, π at south pole)
        
        # Pre-calculate trigonometric functions
        cos_phi = np.cos(phi)
        sin_phi = np.sin(phi)
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)
        
        harmonics = []
        
        for n in range(order + 1):  # n = order
            for m in range(-n, n + 1):  # m = degree
                # Calculate normalization factor (SN3D)
                if m == 0:
                    norm = np.sqrt((2 * n + 1) / (4 * np.pi))
                else:
                    norm = np.sqrt((2 * n + 1) / (2 * np.pi) * 
                                  np.math.factorial(n - abs(m)) / np.math.factorial(n + abs(m)))
                
                # Associated Legendre polynomial
                if n == 0:
                    P = 1.0
                elif n == 1:
                    if m == -1:
                        P = sin_phi
                    elif m == 0:
                        P = cos_phi
                    elif m == 1:
                        P = sin_phi
                elif n == 2:
                    if m == -2:
                        P = 3 * sin_phi**2
                    elif m == -1:
                        P = 3 * sin_phi * cos_phi
                    elif m == 0:
                        P = (3 * cos_phi**2 - 1) / 2
                    elif m == 1:
                        P = 3 * sin_phi * cos_phi
                    elif m == 2:
                        P = 3 * sin_phi**2
                elif n == 3:
                    if m == -3:
                        P = 15 * sin_phi**3
                    elif m == -2:
                        P = 15 * sin_phi**2 * cos_phi
                    elif m == -1:
                        P = sin_phi * (15 * cos_phi**2 - 3) / 2
                    elif m == 0:
                        P = cos_phi * (5 * cos_phi**2 - 3) / 2
                    elif m == 1:
                        P = sin_phi * (15 * cos_phi**2 - 3) / 2
                    elif m == 2:
                        P = 15 * sin_phi**2 * cos_phi
                    elif m == 3:
                        P = 15 * sin_phi**3
                else:
                    # For higher orders, we'd need a more general implementation
                    P = 0.0
                    warnings.warn(f"Spherical harmonic for order {n}, degree {m} not implemented")
                
                # Apply cosine/sine modulation based on m
                if m < 0:
                    harmonic = norm * P * np.sin(abs(m) * theta)
                elif m == 0:
                    harmonic = norm * P
                else:  # m > 0
                    harmonic = norm * P * np.cos(m * theta)
                
                harmonics.append(harmonic)
        
        return np.array(harmonics)
    
    def decode_to_position(self, azimuth: float, elevation: float) -> np.ndarray:
        """
        Decode ambisonic audio to a specific direction.
        
        Args:
            azimuth: Azimuth angle in degrees
            elevation: Elevation angle in degrees
        
        Returns:
            Decoded mono audio signal for the specified direction
        """
        if self.audio_data is None:
            self.load_ambisonic_file()
        
        # Convert degrees to radians
        azimuth_rad = np.radians(azimuth)
        elevation_rad = np.radians(elevation)
        
        # Calculate decoding coefficients (spherical harmonics)
        coeffs = self.spherical_harmonics(azimuth_rad, elevation_rad, self.order)
        
        # Ensure we have enough coefficients
        if len(coeffs) != self.num_channels:
            raise ValueError(f"Number of coefficients ({len(coeffs)}) doesn't match "
                           f"number of channels ({self.num_channels})")
        
        # Decode by weighted sum of ambisonic channels
        decoded = np.zeros(len(self.audio_data))
        for i in range(self.num_channels):
            decoded += coeffs[i] * self.audio_data[:, i]
        
        return decoded
    
    def decode_all_boundaries(self, normalize: bool = True) -> Dict[str, np.ndarray]:
        """
        Decode audio for all boundary positions.
        
        Args:
            normalize: Whether to normalize output to prevent clipping
        
        Returns:
            Dictionary mapping boundary names to decoded audio arrays
        """
        if self.audio_data is None:
            self.load_ambisonic_file()
        
        results = {}
        
        for boundary in self.config['boundaries']:
            name = boundary['name']
            
            # Calculate azimuth and elevation from relative position
            rel_pos = boundary['relative_position']
            x, y, z = rel_pos['x'], rel_pos['y'], rel_pos['z']
            
            # Convert Cartesian to spherical coordinates
            r = np.sqrt(x**2 + y**2 + z**2)
            
            if r == 0:
                # At center, use default direction
                azimuth = 0
                elevation = 0
            else:
                # Azimuth: angle in XY plane
                azimuth = np.degrees(np.arctan2(y, x))
                # Elevation: angle from XY plane
                elevation = np.degrees(np.arcsin(z / r))
            
            # Ensure azimuth is in [0, 360)
            azimuth = azimuth % 360
            
            # Decode for this direction
            audio = self.decode_to_position(azimuth, elevation)
            
            # Normalize if requested
            if normalize and len(audio) > 0:
                max_val = np.max(np.abs(audio))
                if max_val > 0:
                    audio = audio / max_val * 0.95  # Leave some headroom
            
            results[name] = audio
        
        return results
    
    def save_decoded_files(self, output_dir: str = None, normalize: bool = True):
        """
        Decode and save all boundary audio files.
        
        Args:
            output_dir: Directory to save files (default: use paths from config)
            normalize: Whether to normalize output
        """
        # Decode all boundaries
        decoded_audio = self.decode_all_boundaries(normalize=normalize)
        
        # Save each boundary's audio
        for boundary in self.config['boundaries']:
            name = boundary['name']
            audio = decoded_audio[name]
            
            # Determine output path
            if output_dir:
                # Use custom output directory
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f"{name}.wav")
            else:
                # Use path from config
                output_path = boundary['audio_file']
                # Ensure directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save as WAV file (FLOAT format)
            sf.write(output_path, audio, self.sample_rate, subtype='FLOAT')
            
            print(f"Saved: {output_path}")
    
    def create_virtual_speaker_setup(self, num_speakers: int = 8) -> List[Tuple[float, float]]:
        """
        Create a virtual speaker setup for decoding.
        
        Args:
            num_speakers: Number of virtual speakers
        
        Returns:
            List of (azimuth, elevation) tuples in degrees
        """
        # Create a basic speaker layout (e.g., ring at ear level)
        positions = []
        
        for i in range(num_speakers):
            azimuth = 360 * i / num_speakers
            elevation = 0  # Ear level
            
            positions.append((azimuth, elevation))
        
        return positions
    
    def decode_to_virtual_speakers(self, speaker_positions: List[Tuple[float, float]], 
                                  normalize: bool = True) -> Dict[Tuple[float, float], np.ndarray]:
        """
        Decode to a custom virtual speaker setup.
        
        Args:
            speaker_positions: List of (azimuth, elevation) tuples in degrees
            normalize: Whether to normalize output
        
        Returns:
            Dictionary mapping positions to decoded audio
        """
        results = {}
        
        for azimuth, elevation in speaker_positions:
            audio = self.decode_to_position(azimuth, elevation)
            
            if normalize and len(audio) > 0:
                max_val = np.max(np.abs(audio))
                if max_val > 0:
                    audio = audio / max_val * 0.95
            
            results[(azimuth, elevation)] = audio
        
        return results


# Example usage function
def decode_environment_from_json(json_path: str, output_dir: str = None):
    """
    Convenience function to decode an environment from JSON config.
    
    Args:
        json_path: Path to JSON configuration file
        output_dir: Optional custom output directory
    """
    decoder = AmbisonicDecoder(json_config_path=json_path)
    
    print(f"Decoding ambisonic file: {decoder.config['file_path']}")
    print(f"Ambisonic order: {decoder.order}")
    print(f"Number of channels: {decoder.num_channels}")
    print(f"Number of boundaries: {len(decoder.config['boundaries'])}")
    
    # Decode and save files
    decoder.save_decoded_files(output_dir=output_dir)
    
    print("Decoding complete!")


# Batch processing function
def batch_decode_environments(json_files: List[str], output_base_dir: str = None):
    """
    Batch decode multiple environment configurations.
    
    Args:
        json_files: List of JSON configuration file paths
        output_base_dir: Base directory for outputs
    """
    for json_file in json_files:
        print(f"\nProcessing: {json_file}")
        
        try:
            if output_base_dir:
                env_name = Path(json_file).stem
                output_dir = os.path.join(output_base_dir, env_name)
                decode_environment_from_json(json_file, output_dir)
            else:
                decode_environment_from_json(json_file)
        except Exception as e:
            print(f"Error processing {json_file}: {e}")
            continue


if __name__ == "__main__":
    # Example usage
    json_path = "WorldEnvironment.001.json"
    
    if os.path.exists(json_path):
        decode_environment_from_json(json_path)
    else:
        print(f"JSON file not found: {json_path}")
        print("Creating example usage...")
        
        # Example with direct configuration
        example_config = {
            "file_path": "/path/to/ambambisonic/file.wav",
            "channels": 16,  # 3rd order ambisonics (4^2 = 16 channels)
            "center_location": {"x": 0, "y": 0, "z": 0},
            "boundaries": [
                {
                    "name": "Speaker_00",
                    "relative_position": {"x": 1, "y": 0, "z": 0},
                    "audio_file": "/output/path/Speaker_00.wav"
                },
                # ... more boundaries
            ]
        }
        
        decoder = AmbisonicDecoder(config_data=example_config)
        print(f"Created decoder for order {decoder.order}")

"""
decoder = AmbisonicDecoder(json_config_path="WorldEnvironment.001.json")
decoder.save_decoded_files()
"""

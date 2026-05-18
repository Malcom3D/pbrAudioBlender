import subprocess
import numpy as np
import soundfile as sf
import tempfile
import os

def convert_51_to_prologic2(input_ac3_file, output_wav_file, sample_rate=48000):
    """
    Convert 5.1 AC3 file to stereo Pro Logic II encoded audio.
    
    Pro Logic II encoding matrix:
    Lt = L + 0.707*C - 0.707*(Ls + Rs) - 0.707*LFE
    Rt = R + 0.707*C + 0.707*(Ls + Rs) - 0.707*LFE
    
    Where:
    - Lt, Rt = Left total, Right total (stereo output)
    - L, R = Front left, Front right
    - C = Center
    - Ls, Rs = Surround left, Surround right
    - LFE = Low Frequency Effects (subwoofer)
    
    Args:
        input_ac3_file: Path to input 5.1 AC3 file
        output_wav_file: Path to output stereo WAV file
        sample_rate: Output sample rate (default 48000)
    """
    
    # Create temporary directory for intermediate files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Step 1: Extract 5.1 channels to separate WAV files using FFmpeg
        channel_files = []
        channel_names = ['FL', 'FR', 'FC', 'LFE', 'BL', 'BR']
        
        for i, name in enumerate(channel_names):
            temp_file = os.path.join(temp_dir, f'ch_{name}.wav')
            channel_files.append(temp_file)
            
            # FFmpeg command to extract individual channel
            cmd = [
                'ffmpeg', '-i', input_ac3_file,
                '-map_channel', f'0.0.{i}',
                '-ac', '1',
                '-ar', str(sample_rate),
                '-sample_fmt', 's16',
                '-y', temp_file
            ]
            subprocess.run(cmd, check=True, capture_output=True)
        
        # Step 2: Read all channel WAV files
        channels = []
        for ch_file in channel_files:
            data, rate = sf.read(ch_file)
            channels.append(data.astype(np.float32))
        
        # Step 3: Pro Logic II encoding
        # Normalize factors (applied during matrix encoding)
        front_gain = 1.0
        center_gain = 0.7071  # -3dB
        surround_gain = 0.7071  # -3dB
        lfe_gain = 0.7071  # -3dB (reduced LFE)
        
        # Extract individual channels
        L = channels[0] * front_gain
        R = channels[1] * front_gain
        C = channels[2] * center_gain
        LFE = channels[3] * lfe_gain
        Ls = channels[4] * surround_gain
        Rs = channels[5] * surround_gain
        
        # Apply phase shift to surround channels for Pro Logic II
        # Surround channels are phase-shifted by 90 degrees (Hilbert transform)
        # and have a 180-degree phase relationship between Ls and Rs
        
        # Simple phase shift using all-pass filter approximation
        # For proper Pro Logic II, surround channels should be:
        # Ls shifted by -90°, Rs shifted by +90°
        
        # Apply Hilbert transform approximation for phase shift
        def hilbert_phase_shift(signal, shift_degrees=90):
            """Apply approximate phase shift using FFT"""
            n = len(signal)
            spectrum = np.fft.fft(signal)
            
            # Create phase shift array
            freqs = np.fft.fftfreq(n)
            phase_shift = np.exp(1j * np.pi * shift_degrees / 180 * np.sign(freqs))
            
            # Apply phase shift
            spectrum_shifted = spectrum * phase_shift
            
            # Inverse FFT
            shifted_signal = np.fft.ifft(spectrum_shifted).real
            return shifted_signal
        
        # Apply phase shifts
        Ls_shifted = hilbert_phase_shift(Ls, -90)  # Ls shifted -90°
        Rs_shifted = hilbert_phase_shift(Rs, 90)   # Rs shifted +90°
        
        # Pro Logic II encoding matrix
        Lt = L + C - 0.707 * (Ls_shifted + Rs_shifted) - LFE
        Rt = R + C + 0.707 * (Ls_shifted + Rs_shifted) - LFE
        
        # Step 4: Normalize to prevent clipping
        max_val = max(np.max(np.abs(Lt)), np.max(np.abs(Rt)))
        if max_val > 0:
            Lt = Lt / max_val * 0.95  # Leave some headroom
            Rt = Rt / max_val * 0.95
        
        # Step 5: Convert to int16 and create stereo interleaved array
        Lt_int16 = (Lt * 32767).astype(np.int16)
        Rt_int16 = (Rt * 32767).astype(np.int16)
        
        stereo_data = np.column_stack((Lt_int16, Rt_int16))
        
        # Step 6: Save stereo WAV file
        sf.write(output_wav_file, stereo_data, sample_rate, subtype='FLOAT')
        
        print(f"Successfully converted {input_ac3_file} to Pro Logic II stereo")
        print(f"Output saved to {output_wav_file}")

# Example usage
#if __name__ == "__main__":
#    # Using the Python implementation
#    convert_51_to_prologic2("input.ac3", "output_prologic2.wav")

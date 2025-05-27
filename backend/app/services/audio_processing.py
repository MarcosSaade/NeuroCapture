# backend/app/services/audio_processing.py

import numpy as np
import librosa
import noisereduce as nr
import parselmouth
from parselmouth.praat import call
import scipy.signal
import scipy.stats
import webrtcvad
import os
import warnings
from typing import Dict, Tuple, List
from uuid import uuid4

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# --- Preprocessing Functions ---

def load_audio(file_path: str, target_sr: int = 16000) -> Tuple[np.ndarray, int]:
    """Load audio file, convert to mono, and resample to supported sample rate."""
    audio_data, sr = librosa.load(file_path, sr=target_sr, mono=True)
    return audio_data, target_sr

def normalize_audio(audio_data: np.ndarray) -> np.ndarray:
    """Normalize audio to a consistent RMS."""
    rms_target = 0.1
    current_rms = np.sqrt(np.mean(audio_data**2))
    scaling_factor = rms_target / current_rms if current_rms > 0 else 1
    return audio_data * scaling_factor

def reduce_noise(audio_data: np.ndarray, sr: int) -> np.ndarray:
    """Reduce background noise in the audio."""
    reduced_audio = nr.reduce_noise(y=audio_data, sr=sr)
    return reduced_audio

def remove_extreme_peaks(audio_data: np.ndarray, k: int = 7, reduction_ratio: float = 0.99) -> np.ndarray:
    """
    Remove extreme peaks from audio data.
    
    Parameters:
    - audio_data: 1D NumPy array of audio samples.
    - k: Multiplier for standard deviation to set the peak threshold.
    - reduction_ratio: Proportion to reduce the amplitude of detected peaks.

    Returns:
    - Processed audio data with extreme peaks reduced.
    """
    # Calculate standard deviation (mean is 0)
    std_dev = np.std(audio_data)
    
    # Define threshold for peak detection
    threshold = k * std_dev

    # Create a copy of the audio data to modify
    processed_audio = np.copy(audio_data)
    
    # Identify peaks above the threshold
    peaks = np.abs(processed_audio) > threshold
    
    # Reduce the amplitude of peaks
    processed_audio[peaks] *= (1 - reduction_ratio)

    return processed_audio

def convert_to_int16(audio_data: np.ndarray) -> np.ndarray:
    """Convert float audio data to 16-bit integers."""
    audio_int16 = np.clip(audio_data * 32768, -32768, 32767).astype(np.int16)
    return audio_int16

def extract_silences(audio_data: np.ndarray, sr: int, frame_duration: int = 30, 
                    aggressiveness: int = 3, min_silence_duration: float = 0.5, 
                    min_speech_duration: float = 0.2) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
    """
    Perform Voice Activity Detection using WebRTC VAD with minimum duration thresholds.

    Args:
        audio_data: numpy array of audio samples
        sr: sample rate (must be 8000, 16000, 32000, or 48000)
        frame_duration: frame duration in ms (10, 20, or 30)
        aggressiveness: VAD aggressiveness (0-3)
        min_silence_duration: minimum duration in seconds for a silence segment to be counted
        min_speech_duration: minimum duration in seconds for a speech segment to be counted

    Returns:
        silence_segments (list of tuples): List of (start_time, end_time) for silences
        speech_segments (list of tuples): List of (start_time, end_time) for speech
    """
    if sr not in [8000, 16000, 32000, 48000]:
        raise ValueError("Sample rate must be 8000, 16000, 32000, or 48000")
    if frame_duration not in [10, 20, 30]:
        raise ValueError("Frame duration must be 10, 20, or 30 ms")
    if not (0 <= aggressiveness <= 3):
        raise ValueError("Aggressiveness must be between 0 and 3")

    # Convert to int16 if needed
    if audio_data.dtype != np.int16:
        audio_data = convert_to_int16(audio_data)

    vad = webrtcvad.Vad(aggressiveness)
    frame_size = int(sr * frame_duration / 1000)
    num_frames = len(audio_data) // frame_size

    # Use temporary lists to store all segments before filtering
    temp_speech_segments = []
    temp_silence_segments = []
    voiced = False
    start_time = 0

    for i in range(num_frames):
        start_idx = i * frame_size
        end_idx = start_idx + frame_size

        frame = audio_data[start_idx:end_idx]
        if len(frame) != frame_size:
            frame = np.pad(frame, (0, frame_size - len(frame)), 'constant')

        try:
            is_speech = vad.is_speech(frame.tobytes(), sr)
        except Exception as e:
            print(f"Error processing frame {i}: {e}")
            continue

        current_time = start_idx / sr

        if is_speech != voiced:
            if is_speech:
                start_time = current_time
                if len(temp_silence_segments) == 0 and start_time > 0:
                    temp_silence_segments.append((0, start_time))
            else:
                temp_speech_segments.append((start_time, current_time))
            voiced = is_speech

    # Handle the final segment
    if voiced:
        temp_speech_segments.append((start_time, len(audio_data) / sr))
    elif len(temp_speech_segments) > 0:
        temp_silence_segments.append((temp_speech_segments[-1][1], len(audio_data) / sr))
    elif len(temp_speech_segments) == 0:
        temp_silence_segments.append((0, len(audio_data) / sr))

    # Add intermediate silence segments
    if len(temp_speech_segments) > 1:
        for i in range(1, len(temp_speech_segments)):
            temp_silence_segments.append((temp_speech_segments[i-1][1], temp_speech_segments[i][0]))

    # Filter segments based on duration thresholds
    speech_segments = []
    silence_segments = []

    for start, end in temp_speech_segments:
        duration = end - start
        if duration >= min_speech_duration:
            speech_segments.append((start, end))

    for start, end in temp_silence_segments:
        duration = end - start
        if duration >= min_silence_duration:
            silence_segments.append((start, end))

    # Sort the filtered segments
    speech_segments.sort(key=lambda x: x[0])
    silence_segments.sort(key=lambda x: x[0])

    # Merge adjacent silence segments if any gaps were created by filtering
    if len(silence_segments) > 1:
        merged_silence = []
        current_start, current_end = silence_segments[0]

        for start, end in silence_segments[1:]:
            if start <= current_end:  # Overlapping or adjacent segments
                current_end = max(current_end, end)
            else:
                merged_silence.append((current_start, current_end))
                current_start, current_end = start, end

        merged_silence.append((current_start, current_end))
        silence_segments = merged_silence

    return silence_segments, speech_segments

# --- Prosodic Feature Extraction Functions ---

def _extract_timing_features(audio_data: np.ndarray, sr: int) -> Dict[str, float]:
    """Extract timing-related features using VAD."""
    features = {}

    # Prepare audio for VAD
    vad_audio = librosa.resample(audio_data, orig_sr=sr, target_sr=16000) if sr != 16000 else audio_data

    # Get speech and silence segments
    silence_segments, speech_segments = extract_silences(vad_audio, 16000)

    # Filter silence segments between speech
    filtered_silence_segments = [
        (start, end) for start, end in silence_segments
        if speech_segments and start > speech_segments[0][0] and end < speech_segments[-1][1]
    ]

    # Calculate pause durations
    pause_durations = [end - start for start, end in filtered_silence_segments]

    # Calculate speech segment durations
    speech_durations = [end - start for start, end in speech_segments]

    total_duration = len(audio_data) / sr
    total_speech_duration = sum(speech_durations)

    features.update({
        'total_duration': total_duration,
        'silence_count': len(filtered_silence_segments),
        'speech_segment_count': len(speech_segments),
        'total_silence_duration': sum(pause_durations),
        'total_speech_duration': total_speech_duration,
        'speech_rate': len(speech_segments) / total_duration,
        'articulation_rate': len(speech_segments) / total_speech_duration if total_speech_duration > 0 else 0,

        # Pause-related features
        'mean_pause_duration': np.mean(pause_durations) if pause_durations else 0,
        'std_pause_duration': np.std(pause_durations) if pause_durations else 0,
        'max_pause_duration': np.max(pause_durations) if pause_durations else 0,
        'min_pause_duration': np.min(pause_durations) if pause_durations else 0,
        'pause_rate': len(pause_durations) / total_speech_duration if total_speech_duration > 0 else 0,
        'pause_ratio': sum(pause_durations) / total_speech_duration if total_speech_duration > 0 else 0,

        # Speech features
        'mean_speech_duration': np.mean(speech_durations) if speech_durations else 0,
        'std_speech_duration': np.std(speech_durations) if speech_durations else 0,
        'max_speech_duration': np.max(speech_durations) if speech_durations else 0,
        'speech_duration_range': (np.max(speech_durations) - np.min(speech_durations)) if speech_durations else 0,
        'speech_duration_coefficient_of_variation': (np.std(speech_durations) / np.mean(speech_durations)) if speech_durations and np.mean(speech_durations) > 0 else 0,
        'speech_to_pause_ratio': total_speech_duration / sum(pause_durations) if pause_durations and sum(pause_durations) > 0 else float('inf')
    })

    return features

def _extract_rhythm_features(sound) -> Dict[str, float]:
    """Extract rhythm-related features including PVI measures."""
    features = {}
    try:
        intensity = sound.to_intensity()
        intensity_values = intensity.values[0]
        time_step = intensity.get_time_step()

        peaks, _ = scipy.signal.find_peaks(
            intensity_values,
            height=np.mean(intensity_values),
            distance=int(0.06 / time_step)
        )

        if len(peaks) > 1:
            intervals = np.diff(peaks) * time_step
            differences = np.abs(np.diff(intervals))
            means = np.mean([intervals[:-1], intervals[1:]], axis=0)

            features.update({
                'rPVI': np.mean(differences),
                'nPVI': np.mean((differences / means) * 100)
            })
        else:
            features.update({'rPVI': 0, 'nPVI': 0})

    except Exception as e:
        print(f"Error in rhythm analysis: {e}")
        features.update({'rPVI': 0, 'nPVI': 0})

    return features

def _extract_tempo_beat_features(audio_data: np.ndarray, sr: int) -> Dict[str, float]:
    """Extract tempo and beat-related features."""
    features = {}
    try:
        # Estimate tempo and beat frames
        tempo, beat_frames = librosa.beat.beat_track(y=audio_data, sr=sr, hop_length=512, trim=False)

        # Convert beat frames to time
        beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=512)

        # Number of beats
        num_beats = len(beat_frames)
        features['tempo_bpm'] = tempo
        features['num_beats'] = num_beats

        if num_beats > 1:
            # Inter-beat intervals (IBI)
            ibi = np.diff(beat_times)
            features['ibi_mean'] = np.mean(ibi)
            features['ibi_std'] = np.std(ibi)
            features['ibi_variance'] = np.var(ibi)
            features['ibi_skewness'] = scipy.stats.skew(ibi)
            features['ibi_kurtosis'] = scipy.stats.kurtosis(ibi)
        else:
            features.update({
                'ibi_mean': 0,
                'ibi_std': 0,
                'ibi_variance': 0,
                'ibi_skewness': 0,
                'ibi_kurtosis': 0
            })

    except Exception as e:
        print(f"Error in tempo and beat analysis: {e}")
        features.update({
            'tempo_bpm': 0,
            'num_beats': 0,
            'ibi_mean': 0,
            'ibi_std': 0,
            'ibi_variance': 0,
            'ibi_skewness': 0,
            'ibi_kurtosis': 0
        })

    return features

def _extract_energy_temporal_features(audio_data: np.ndarray, sr: int) -> Dict[str, float]:
    """Extract energy-based temporal features."""
    features = {}
    try:
        # Compute Short-Time Energy (STE)
        frame_length = 1024
        hop_length = 512
        energy = np.array([
            np.sum(np.abs(audio_data[i:i+frame_length]**2))
            for i in range(0, len(audio_data), hop_length)
        ])

        # Mean Energy
        features['energy_mean'] = np.mean(energy) if len(energy) > 0 else 0

        # Standard Deviation of Energy
        features['energy_std'] = np.std(energy) if len(energy) > 0 else 0

        # Energy Variability (Coefficient of Variation)
        features['energy_cv'] = (features['energy_std'] / features['energy_mean']) if features['energy_mean'] > 0 else 0

        # Energy Entropy
        energy_norm = energy / np.sum(energy) if np.sum(energy) > 0 else energy
        energy_entropy = -np.sum(energy_norm * np.log2(energy_norm + 1e-12))  # Add epsilon to avoid log(0)
        features['energy_entropy'] = energy_entropy

    except Exception as e:
        print(f"Error in energy temporal analysis: {e}")
        features.update({
            'energy_mean': 0,
            'energy_std': 0,
            'energy_cv': 0,
            'energy_entropy': 0
        })

    return features

def extract_prosodic_features(audio_data: np.ndarray, sr: int) -> Dict[str, float]:
    """
    Extract comprehensive prosodic features from audio data.

    Args:
        audio_data (array): Audio signal
        sr (int): Sampling rate

    Returns:
        dict: Dictionary containing all extracted features
    """

    features = {}
    sound = parselmouth.Sound(audio_data, sr)
        
    # 1. Timing and Speech/Silence Features
    features.update(_extract_timing_features(audio_data, sr))

    # 2. Rhythm Features
    features.update(_extract_rhythm_features(sound))

    # 3. Tempo and Beat Features
    features.update(_extract_tempo_beat_features(audio_data, sr))

    # 4. Energy-Based Temporal Features
    features.update(_extract_energy_temporal_features(audio_data, sr))

    return features

# --- Acoustic Feature Extraction Functions ---

def _extract_voice_quality_features(sound) -> Dict[str, float]:
    """Extract voice quality features including jitter, shimmer, and CPPS."""
    features = {}

    try:
        # Jitter and Shimmer
        point_process = call(sound, "To PointProcess (periodic, cc)", 75, 500)
        features.update({
            'jitter_local': call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3),
            'jitter_ppq5': call(point_process, "Get jitter (ppq5)", 0, 0, 0.0001, 0.02, 1.3),
            'shimmer_local': call([sound, point_process], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6),
            'shimmer_apq5': call([sound, point_process], "Get shimmer (apq5)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
        })

        # CPPS Analysis
        spectrum = sound.to_spectrum()
        power_spectrum = np.abs(spectrum.values[0])**2
        cepstrum = np.fft.ifft(np.log(power_spectrum + 1e-10)).real

        quefrency = np.arange(len(cepstrum)) / sound.sampling_frequency
        valid_range = (quefrency >= 0.002) & (quefrency <= 0.025)

        window_size = int(0.001 * sound.sampling_frequency)
        if window_size % 2 == 0:
            window_size += 1
        smoothed_cepstrum = scipy.signal.savgol_filter(cepstrum, window_size, 2)

        peak_index = np.argmax(smoothed_cepstrum[valid_range])
        background = np.mean(smoothed_cepstrum[valid_range])
        features['CPPS'] = smoothed_cepstrum[valid_range][peak_index] - background

    except Exception as e:
        print(f"Error in voice quality analysis: {e}")
        features.update({
            'jitter_local': 0, 'jitter_ppq5': 0,
            'shimmer_local': 0, 'shimmer_apq5': 0,
            'CPPS': 0
        })
    return features

def _extract_amplitude_features(sound) -> Dict[str, float]:
    """Extract average amplitude, peak amplitude, and amplitude variance features."""
    features = {}
    try:
        amplitude_values = sound.values[0]

        # Calculate Average Amplitude
        features['average_amplitude'] = np.mean(amplitude_values)

        # Calculate Peak Amplitude
        features['peak_amplitude'] = np.max(np.abs(amplitude_values))

        # Calculate Amplitude Variance
        features['amplitude_variance'] = np.var(amplitude_values)

    except Exception as e:
        print(f"Error in amplitude feature calculation: {e}")
        features['average_amplitude'] = 0
        features['peak_amplitude'] = 0
        features['amplitude_variance'] = 0

    return features

def _extract_formant_features(sound) -> Dict[str, float]:
    """Extract formant features (F1-F4) and their dynamics."""
    features = {}
    try:
        formant = sound.to_formant_burg(
            time_step=0.01,
            max_number_of_formants=5,
            maximum_formant=6500
        )

        formant_values = {i: [] for i in range(1, 5)}  # F1-F4
        formant_deltas = {i: [] for i in range(1, 5)}  # Derivatives of F1-F4
        f3_b3_values = []  # Bandwidth of F3

        times = np.arange(0, sound.duration, 0.01)

        for t in times:
            for formant_number in range(1, 5):
                try:
                    value = formant.get_value_at_time(formant_number, t)
                    if value > 0:
                        formant_values[formant_number].append(value)
                        if len(formant_values[formant_number]) > 1:
                            # Compute delta (difference between consecutive formant values)
                            delta = value - formant_values[formant_number][-2]
                            formant_deltas[formant_number].append(delta)
                    if formant_number == 3:
                        bandwidth = formant.get_bandwidth_at_time(formant_number, t)
                        if bandwidth > 0:
                            f3_b3_values.append(bandwidth)
                except:
                    continue

        for formant_number, values in formant_values.items():
            if values:
                prefix = f'F{formant_number}'
                features.update({
                    f'{prefix}_mean': np.mean(values),
                    f'{prefix}_std': np.std(values),
                    f'{prefix}_range': np.max(values) - np.min(values),
                    f'{prefix}_median': np.median(values),
                    f'{prefix}_skewness': scipy.stats.skew(values),
                    f'{prefix}_kurtosis': scipy.stats.kurtosis(values)
                })
                if formant_number == 4:  # Additional F4 features
                    features[f'{prefix}_coefficient_of_variation'] = np.std(values) / np.mean(values)
                # Formant delta statistics
                deltas = formant_deltas[formant_number]
                if deltas:
                    features.update({
                        f'{prefix}_delta_mean': np.mean(deltas),
                        f'{prefix}_delta_std': np.std(deltas),
                        f'{prefix}_delta_range': np.max(deltas) - np.min(deltas)
                    })
            else:
                prefix = f'F{formant_number}'
                features.update({
                    f'{prefix}_mean': 0,
                    f'{prefix}_std': 0,
                    f'{prefix}_range': 0,
                    f'{prefix}_median': 0,
                    f'{prefix}_skewness': 0,
                    f'{prefix}_kurtosis': 0,
                    f'{prefix}_delta_mean': 0,
                    f'{prefix}_delta_std': 0,
                    f'{prefix}_delta_range': 0
                })
                if formant_number == 4:
                    features[f'{prefix}_coefficient_of_variation'] = 0

        # F3 Bandwidth (F3_B3)
        features['F3_B3'] = np.mean(f3_b3_values) if f3_b3_values else 0

        # F1 Standard Deviation (F1_sd)
        if formant_values[1]:
            features['F1_sd'] = np.std(formant_values[1])
        else:
            features['F1_sd'] = 0

    except Exception as e:
        print(f"Error in formant analysis: {e}")
        for i in range(1, 5):
            prefix = f'F{i}'
            features.update({
                f'{prefix}_mean': 0,
                f'{prefix}_std': 0,
                f'{prefix}_range': 0,
                f'{prefix}_median': 0,
                f'{prefix}_skewness': 0,
                f'{prefix}_kurtosis': 0,
                f'{prefix}_delta_mean': 0,
                f'{prefix}_delta_std': 0,
                f'{prefix}_delta_range': 0
            })
            if i == 4:
                features[f'{prefix}_coefficient_of_variation'] = 0
        features['F3_B3'] = 0
        features['F1_sd'] = 0

    return features

def _extract_complexity_features(audio_data: np.ndarray) -> Dict[str, float]:
    """Extract complexity features including Higuchi Fractal Dimension."""
    features = {}
    try:
        window_sizes = [128, 256, 512, 1024]
        hfd_values = []

        for window_size in window_sizes:
            num_windows = len(audio_data) // window_size
            for i in range(num_windows):
                start_idx = i * window_size
                end_idx = start_idx + window_size
                window_data = audio_data[start_idx:end_idx]
                hfd = _calculate_hfd(window_data)
                if not np.isnan(hfd):
                    hfd_values.append(hfd)

        if hfd_values:
            features.update({
                'HFD_mean': np.mean(hfd_values),
                'HFD_max': np.max(hfd_values),
                'HFD_min': np.min(hfd_values),
                'HFD_std': np.std(hfd_values),
                'HFD_var': np.var(hfd_values)
            })
        else:
            features.update({
                'HFD_mean': 0, 'HFD_max': 0,
                'HFD_min': 0, 'HFD_std': 0,
                'HFD_var': 0
            })

    except Exception as e:
        print(f"Error in complexity analysis: {e}")
        features.update({
            'HFD_mean': 0, 'HFD_max': 0,
            'HFD_min': 0,
            'HFD_std': 0,
            'HFD_var': 0
        })

    return features

def _calculate_hfd(signal: np.ndarray, kmax: int = 10) -> float:
    """
    Calculate the Higuchi Fractal Dimension of a signal.

    Args:
        signal (array): Input signal
        kmax (int): Maximum delay/lag (default=10)

    Returns:
        float: Higuchi Fractal Dimension
    """
    N = len(signal)
    L = np.zeros((kmax,))
    x = np.zeros((kmax,))

    for k in range(1, kmax + 1):
        Lk = 0
        for m in range(k):
            indices = np.arange(1, int((N-m)/k))
            Lmk = np.abs(signal[m + k*indices] - signal[m + k*(indices-1)]).sum()
            Lmk = (Lmk * (N - 1) / (((N-m)/k)*k)) / k
            Lk += Lmk

        L[k-1] = Lk / k
        x[k-1] = np.log(1.0 / k)

    p = np.polyfit(x, np.log(L), 1)
    return p[0]

def _extract_spectral_features(sound, sr: int) -> Dict[str, float]:
    """Extract spectral features including MFCCs, spectral slope, centroid, flux, roll-off, zero-crossing rate, and energy entropy."""
    features = {}
    try:
        # Convert sound to spectrum
        spectrum = sound.to_spectrum()
        spectral_values = spectrum.values[0]
        frequencies = np.linspace(0, sr / 2, len(spectral_values))
        
        # Spectral Slope Calculation (Original)
        slope, intercept = np.polyfit(frequencies, spectral_values, 1)
        features['spectral_slope'] = slope

        # Spectral Centroid Calculation (Original)
        spectral_centroid = np.sum(frequencies * np.abs(spectral_values)) / np.sum(np.abs(spectral_values))
        features['spectral_centroid'] = spectral_centroid

        # MFCCs (using librosa)
        audio_signal = sound.values[0]
        n_mfcc = 30  # Increased number of MFCCs
        mfccs = librosa.feature.mfcc(y=audio_signal, sr=sr, n_mfcc=n_mfcc, hop_length=512)
        # Delta coefficients
        delta_mfccs = librosa.feature.delta(mfccs)
        # Delta-Delta coefficients
        delta2_mfccs = librosa.feature.delta(mfccs, order=2)
        
        # Collect statistics for MFCCs and their deltas
        for i in range(mfccs.shape[0]):
            # MFCCs
            features[f'mfcc_{i+1}_mean'] = np.mean(mfccs[i])
            features[f'mfcc_{i+1}_std'] = np.std(mfccs[i])
            # Delta MFCCs
            features[f'delta_mfcc_{i+1}_mean'] = np.mean(delta_mfccs[i])
            features[f'delta_mfcc_{i+1}_std'] = np.std(delta_mfccs[i])
            # Delta-Delta MFCCs
            features[f'delta2_mfcc_{i+1}_mean'] = np.mean(delta2_mfccs[i])
            features[f'delta2_mfcc_{i+1}_std'] = np.std(delta2_mfccs[i])
        
        # Spectral Flux
        spectral_flux = librosa.onset.onset_strength(y=audio_signal, sr=sr, hop_length=512)
        features['spectral_flux_mean'] = np.mean(spectral_flux)
        features['spectral_flux_std'] = np.std(spectral_flux)
        
        # Spectral Roll-off
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_signal, sr=sr, hop_length=512)
        features['spectral_rolloff_mean'] = np.mean(spectral_rolloff)
        features['spectral_rolloff_std'] = np.std(spectral_rolloff)
        
        # Zero-Crossing Rate
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y=audio_signal, hop_length=512)
        features['zero_crossing_rate_mean'] = np.mean(zero_crossing_rate)
        features['zero_crossing_rate_std'] = np.std(zero_crossing_rate)
        
        # Energy Entropy
        stft = np.abs(librosa.stft(audio_signal, n_fft=2048, hop_length=512))
        energy = np.sum(stft ** 2, axis=0)
        energy_norm = energy / np.sum(energy)
        energy_entropy = -np.sum(energy_norm * np.log2(energy_norm + 1e-12))  # Add epsilon to avoid log(0)
        features['energy_entropy'] = energy_entropy
        
    except Exception as e:
        print(f"Error in spectral analysis: {e}")
        # Initialize all features to zero in case of error
        n_mfcc = 30 # Define n_mfcc for error handling
        feature_names = ['spectral_slope',
                         'spectral_centroid',
                         'spectral_flux_mean', 'spectral_flux_std',
                         'spectral_rolloff_mean', 'spectral_rolloff_std',
                         'zero_crossing_rate_mean', 'zero_crossing_rate_std',
                         'energy_entropy']
        feature_names += [f'mfcc_{i+1}_mean' for i in range(n_mfcc)]
        feature_names += [f'mfcc_{i+1}_std' for i in range(n_mfcc)]
        feature_names += [f'delta_mfcc_{i+1}_mean' for i in range(n_mfcc)]
        feature_names += [f'delta_mfcc_{i+1}_std' for i in range(n_mfcc)]
        feature_names += [f'delta2_mfcc_{i+1}_mean' for i in range(n_mfcc)]
        feature_names += [f'delta2_mfcc_{i+1}_std' for i in range(n_mfcc)]
        features.update({name: 0 for name in feature_names})
    return features

def _extract_hnr_features(sound) -> Dict[str, float]:
    """Extract Harmonics-to-Noise Ratio (HNR) using autocorrelation method with required parameters."""
    features = {}
    pitch_floor = 60  # Adjusted pitch floor for elderly speakers
    silence_threshold = 0.1  # Typical silence threshold value
    periods_per_window = 3.0  # Periods per window

    try:
        # Use autocorrelation method with silence threshold and periods per window
        hnr = call(sound, "To Harmonicity (ac)", 0.01, pitch_floor, silence_threshold, periods_per_window)

        if hnr:
            frame_count = hnr.get_number_of_frames()

            if frame_count > 0:
                hnr_mean = call(hnr, "Get mean", 0, 0)

                if hnr_mean is None or isinstance(hnr_mean, float) and np.isnan(hnr_mean):
                    hnr_mean = 0
                features['hnr_mean'] = hnr_mean
            else:
                features['hnr_mean'] = 0
        else:
            features['hnr_mean'] = 0

    except Exception as e:
        features['hnr_mean'] = 0

    return features

def _extract_pitch_features(sound) -> Dict[str, float]:
    """Extract pitch features including mean and standard deviation of pitch."""
    features = {}
    try:
        pitch = call(sound, "To Pitch", 0.01, 75, 500)
        features['pitch_mean'] = call(pitch, "Get mean", 0, 0, "Hertz")
        features['pitch_std'] = call(pitch, "Get standard deviation", 0, 0, "Hertz")
    except Exception as e:
        print(f"Error in pitch analysis: {e}")
        features['pitch_mean'] = 0
        features['pitch_std'] = 0
    return features

def _extract_additional_features(audio_data: np.ndarray) -> Dict[str, float]:
    """Extract additional features such as Asymmetry and TrajIntra."""
    features = {}
    try:
        # Asymmetry Feature Calculation
        features['Asymmetry'] = np.mean((audio_data - np.mean(audio_data))**3) / (np.std(audio_data)**3)

        # TrajIntra Feature Calculation
        features['TrajIntra'] = np.mean(np.abs(np.diff(audio_data)))

    except Exception as e:
        print(f"Error in additional feature calculation: {e}")
        features['Asymmetry'] = 0
        features['TrajIntra'] = 0
    return features

def _extract_avqi_hnr_sd(audio_data: np.ndarray, sr: int) -> Dict[str, float]:
    """Extract AVQI HNR_sd feature using RMS of the audio signal."""
    features = {}
    try:
        # Calculate RMS energy using librosa
        rms = librosa.feature.rms(y=audio_data)
        features['AVQI_HNR_sd'] = np.std(rms)
    except Exception as e:
        print(f"Error in AVQI HNR_sd calculation: {e}")
        features['AVQI_HNR_sd'] = 0
    return features

def _extract_amplitude_maximum_difference_mean(audio_data: np.ndarray) -> Dict[str, float]:
    """Extract Amplitude Maximum Difference Mean."""
    features = {}
    try:
        features['Amplitude_Maximum_Difference_mean'] = np.mean(np.abs(np.diff(audio_data)))
    except Exception as e:
        print(f"Error in Amplitude Maximum Difference Mean calculation: {e}")
        features['Amplitude_Maximum_Difference_mean'] = 0
    return features

def _extract_amplitude_minimum(audio_data: np.ndarray) -> Dict[str, float]:
    """Extract Amplitude Minimum."""
    features = {}
    try:
        features['Amplitude_Minimum'] = np.min(audio_data)
    except Exception as e:
        print(f"Error in Amplitude Minimum calculation: {e}")
        features['Amplitude_Minimum'] = 0
    return features

def extract_acoustic_features(audio_data: np.ndarray, sr: int, original_audio_data: np.ndarray = None) -> Dict[str, float]:
    """
    Extract comprehensive acoustic features from audio data.

    Args:
        audio_data (array): Preprocessed audio signal
        sr (int): Sampling rate
        original_audio_data (array, optional): Original audio signal before normalization

    Returns:
        dict: Dictionary containing all extracted features
    """
    features = {}
    sound = parselmouth.Sound(audio_data, sr)

    # Voice Quality Features (Jitter, Shimmer, CPPS)
    features.update(_extract_voice_quality_features(sound))

    # Formant Features (Updated)
    features.update(_extract_formant_features(sound))

    # Spectral Features (Updated)
    features.update(_extract_spectral_features(sound, sr))

    # Harmonics-to-Noise Ratio (HNR)
    features.update(_extract_hnr_features(sound))

    # Amplitude Features (Extracted from original audio data)
    if original_audio_data is not None:
        original_sound = parselmouth.Sound(original_audio_data, sr)
        features.update(_extract_amplitude_features(original_sound))
    else:
        features.update(_extract_amplitude_features(sound))

    # Complexity Features (HFD)
    features.update(_extract_complexity_features(audio_data))

    # Pitch Features
    features.update(_extract_pitch_features(sound))

    # Additional Features (e.g., TrajIntra, Asymmetry)
    features.update(_extract_additional_features(audio_data))

    # AVQI HNR_sd Feature
    features.update(_extract_avqi_hnr_sd(audio_data, sr))

    # Amplitude Maximum Difference Mean
    features.update(_extract_amplitude_maximum_difference_mean(audio_data))

    # Amplitude Minimum
    features.update(_extract_amplitude_minimum(audio_data))

    return features

def extract_all_features(audio_data: np.ndarray, sr: int, original_audio_data: np.ndarray = None) -> Dict[str, float]:
    """
    Extract both acoustic and prosodic features from audio data.

    Args:
        audio_data (array): Preprocessed audio signal
        sr (int): Sampling rate
        original_audio_data (array, optional): Original audio signal before normalization

    Returns:
        dict: Dictionary containing all extracted features
    """

    # Get acoustic features
    features = extract_acoustic_features(audio_data, sr, original_audio_data)

    # Get prosodic features
    prosodic_features = extract_prosodic_features(audio_data, sr)

    # Update features with prosodic features
    features.update(prosodic_features)

    return features

def clean_and_extract_features(input_file_path: str, output_file_path: str = None) -> Tuple[Dict[str, float], str]:
    """
    Main function to clean audio and extract features.
    
    Args:
        input_file_path: Path to the input audio file
        output_file_path: Optional path to save cleaned audio
        
    Returns:
        Tuple of (features dict, cleaned audio file path)
    """
    # Load and preprocess audio
    audio_data, sr = load_audio(input_file_path, target_sr=16000)
    original_audio_data = audio_data.copy()
    
    # Apply preprocessing steps
    audio_data = normalize_audio(audio_data)
    audio_data = reduce_noise(audio_data, sr)
    audio_data = remove_extreme_peaks(audio_data)
    
    # Save cleaned audio if output path is provided
    if output_file_path is None:
        # Generate a new filename with "cleaned" suffix
        base, ext = os.path.splitext(input_file_path)
        output_file_path = f"{base}_cleaned{ext}"
    
    # Save cleaned audio
    import soundfile as sf
    sf.write(output_file_path, audio_data, sr)
    
    # Extract features
    features = extract_all_features(audio_data, sr, original_audio_data)
    
    return features, output_file_path

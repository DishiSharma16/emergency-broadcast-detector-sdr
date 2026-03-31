# fm_mod.py
import numpy as np
from scipy.signal import resample

def nbfm_modulate(audio, fs_audio, fs_tx=1_000_000, fdev=5000, amplitude=0.6):
    """
    audio: float32 in [-1,1]
    fs_audio: audio sample rate
    fs_tx: desired complex sample rate to feed Pluto (e.g., 1e6)
    fdev: frequency deviation in Hz
    returns complex64 IQ samples and actual fs_tx
    """
    # resample audio to fs_tx length
    target_len = int(round(len(audio) * (fs_tx / fs_audio)))
    audio_rs = resample(audio, target_len).astype(np.float32)
    # normalize
    audio_rs = audio_rs / (np.max(np.abs(audio_rs)) + 1e-12)
    dt = 1.0 / fs_tx
    # integrate audio to phase
    phase = 2.0 * np.pi * fdev * np.cumsum(audio_rs) * dt
    iq = amplitude * np.exp(1j * phase).astype(np.complex64)
    return iq, int(fs_tx)

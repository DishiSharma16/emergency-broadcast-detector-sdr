#pluto_tx_morse.py  
import soundfile as sf
import adi
import numpy as np
from fm_mod import nbfm_modulate      # FM mod function
import time
from scipy.signal import butter, filtfilt

TX_FREQ = 433.92e6       
FS_TX = int(1e6)          # Pluto sample_rate 
FDEV = 15000              # FM deviation (Hz), narrow
TX_GAIN_DB = -10          # keeping it very low for safety
CHUNK = 32768             # choose a chunk 

# 1) Read WAV
audio, fs_audio = sf.read("morse_sos.wav")
if audio.ndim > 1:
    audio = audio.mean(axis=1)
audio = audio.astype(np.float32)
audio = audio / (np.max(np.abs(audio)) + 1e-12)
audio *= 2.5 


# 2) Low-pass to audio_band 
b, a = butter(4, 3000/(fs_audio/2), btype='low')   
audio = filtfilt(b, a, audio)

# 3) FM-modulate
iq, fs_iq = nbfm_modulate(audio, fs_audio, fs_tx=FS_TX, fdev=FDEV)
iq = iq.astype(np.complex64)

# 4) Connect to Pluto
try:
    sdr = adi.Pluto("ip:192.168.2.1")  
except Exception:
    sdr = adi.Pluto("usb:")            


sdr.sample_rate = int(fs_iq)
sdr.tx_lo = int(TX_FREQ)

try:
    sdr.tx_hardwaregain_chan0 = TX_GAIN_DB
except Exception:
    try:
        sdr.tx_buffer_size = CHUNK
    except Exception:
        pass

print(f"Transmitting on {TX_FREQ/1e6:.6f} MHz  sample_rate={fs_iq}")
try:
    try:
        sdr.tx_destroy_buffer()
    except Exception:
        pass

    total = len(iq)
    idx = 0
    while idx < total:
        end = min(idx + CHUNK, total)
        seg = iq[idx:end]
      
        if len(seg) != CHUNK:
            pad = np.zeros(CHUNK - len(seg), dtype=np.complex64)
            seg = np.concatenate((seg, pad))
        sdr.tx(seg)    
        idx = end
    print("Finished TX")
finally:
    try:
        sdr.tx_destroy_buffer()
    except Exception:
        pass
    time.sleep(0.2)

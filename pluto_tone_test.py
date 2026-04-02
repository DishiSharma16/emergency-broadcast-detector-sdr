# pluto_tone_test.py  -> runs continuous tone for testing (low power)
import adi, numpy as np, time
TX_FREQ = int(433.92e6)
FS = 1_000_000
sdr = adi.Pluto("ip:192.168.2.1")   # or "usb:" if you use USB
sdr.sample_rate = FS
sdr.tx_lo = TX_FREQ
try:
    sdr.tx_hardwaregain_chan0 = -20
except:
    pass

# 1 second tone sample at FS
t = np.arange(0, 1.0, 1/FS)
tone = 0.6 * np.exp(2j*np.pi*1000*t).astype(np.complex64)

# pad to chunk multiple
CH = 32768
pad = (-len(tone)) % CH
if pad:
    tone = np.concatenate([tone, np.zeros(pad, dtype=np.complex64)])

print("Transmitting tone... CTRL-C to stop.")
try:
    while True:
        # send in chunks
        for i in range(0, len(tone), CH):
            sdr.tx(tone[i:i+CH])
        # small sleep to be nice
        time.sleep(0.01)
finally:
    try:
        sdr.tx_destroy_buffer()
    except:
        pass

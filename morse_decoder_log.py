import numpy as np
import scipy.io.wavfile as wav
import noisereduce as nr
from scipy.signal import butter, filtfilt
from sklearn.cluster import KMeans
import csv
import os
from datetime import datetime

CSV_FILE = "morse_dataset.csv"

# ============================================================
# Ensure CSV exists with correct header
# ============================================================
def ensure_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "morse_code",
                "decoded_text",
                "avg_dot_duration",
                "avg_dash_duration",
                "avg_gap_duration"
            ])
        print(f"[+] Created new CSV: {CSV_FILE}")

ensure_csv()

# ============================================================
# Loading WAV from GNU Radio
# ============================================================
sr, audio = wav.read("morse_rx.wav")
audio = audio.astype(float)

# Noise reduction
audio = nr.reduce_noise(y=audio, sr=sr)

# Bandpass filter (Morse tone)
b, a = butter(4, [300/(sr/2), 1200/(sr/2)], btype="band")
filtered = filtfilt(b, a, audio)

# Envelope detection
win = int(0.01 * sr)
env = np.convolve(np.abs(filtered), np.ones(win)/win, mode="same")

# Adaptive threshold
thr = np.mean(env) + 1.0*np.std(env)
tone = env > thr

# Find ON/OFF transitions
diff = np.diff(tone.astype(int))
starts = np.where(diff == 1)[0]
ends   = np.where(diff == -1)[0]

if len(starts) == 0 or len(ends) == 0:
    print("[-] No tone detected!")
    morse = ""
    decoded = ""
else:
    if ends[0] < starts[0]:
        ends = ends[1:]
    if len(starts) > len(ends):
        starts = starts[:-1]

    dur_on = (ends - starts) / sr
    dur_off = (starts[1:] - ends[:-1]) / sr

    # Cluster for dot vs dash
    kmeans = KMeans(n_clusters=2, n_init=10).fit(dur_on.reshape(-1, 1))
    labels = kmeans.labels_
    means = kmeans.cluster_centers_.flatten()

    dot_cluster = np.argmin(means)
    dash_cluster = np.argmax(means)

    morse = ""

    for i, d in enumerate(dur_on):
        morse += "." if labels[i] == dot_cluster else "-"

        if i < len(dur_off):
            g = dur_off[i]
            if g > 0.7:
                morse += "   "
            elif g > 0.25:
                morse += " "

    # Morse dictionary
    MORSE_DICT = {
        '.-': 'A','-...': 'B','-.-.': 'C','-..': 'D','.': 'E','..-.': 'F',
        '--.': 'G','....': 'H','..': 'I','.---': 'J','-.-': 'K','.-..': 'L',
        '--': 'M','-.': 'N','---': 'O','.--.': 'P','--.-': 'Q','.-.': 'R',
        '...': 'S','-': 'T','..-': 'U','...-': 'V','.--': 'W','-..-': 'X',
        '-.--': 'Y','--..': 'Z',
        '-----': '0','.----': '1','..---': '2','...--': '3','....-': '4',
        '.....': '5','-....': '6','--...': '7','---..': '8','----.': '9'
    }

    decoded = ""
    for word in morse.split("   "):
        for letter in word.split(" "):
            decoded += MORSE_DICT.get(letter, "?")
        decoded += " "

    decoded = decoded.strip()


    avg_dot = float(np.mean(dur_on[labels == dot_cluster])) if np.any(labels == dot_cluster) else 0
    avg_dash = float(np.mean(dur_on[labels == dash_cluster])) if np.any(labels == dash_cluster) else 0
    avg_gap = float(np.mean(dur_off)) if len(dur_off) > 0 else 0

    # ============================================================
    # Append a row to CSV
    # ============================================================
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            morse,
            decoded,
            avg_dot,
            avg_dash,
            avg_gap
        ])

    print("\n[✓] Row added to CSV.")
    print("Morse Detected:", morse)
    print("Decoded:", decoded)

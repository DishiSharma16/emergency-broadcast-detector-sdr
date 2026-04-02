# utils_morse.py
import numpy as np
import soundfile as sf

MORSE = {
 'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.',
 'G':'--.','H':'....','I':'..','J':'.---','K':'-.-','L':'.-..',
 'M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.',
 'S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-',
 'Y':'-.--','Z':'--..',
 '1':'.----','2':'..---','3':'...--','4':'....-','5':'.....',
 '6':'-....','7':'--...','8':'---..','9':'----.','0':'-----'
}

def text_to_morse(msg):
    msg = msg.upper()
    words = msg.split()
    out = []
    for wi, w in enumerate(words):
        for ci, c in enumerate(w):
            if c in MORSE:
                out.append(MORSE[c])
                if ci != len(w)-1:
                    out.append(' ')  # inter-letter gap
        if wi != len(words)-1:
            out.append('/')  # word separator
    return ' '.join(out)

def morse_to_tone_sequence(morse_str, wpm=18, fs=48000, tone_freq=800):
    # dot length (seconds) using PARIS standard: 1.2 / WPM
    dot = 1.2 / wpm
    dash = dot * 3
    intra_symbol = dot      # gap between dot/dash within letter
    inter_letter = dot * 3
    inter_word = dot * 7

    def tone(n):
        t = np.arange(n) / fs
        # gentle Hann window to avoid clicks
        sig = np.sin(2*np.pi * tone_freq * t).astype(np.float32)
        win = np.hanning(n) if n>1 else np.array([1.0], dtype=np.float32)
        return 0.8 * sig * win

    def silence(n):
        return np.zeros(n, dtype=np.float32)

    samples = np.array([], dtype=np.float32)
    for token in morse_str.split(' '):
        if token == '/':
            samples = np.concatenate([samples, silence(int(inter_word*fs))])
            continue
        for si, sym in enumerate(token):
            if sym == '.':
                samples = np.concatenate([samples, tone(int(round(dot*fs)))])
            elif sym == '-':
                samples = np.concatenate([samples, tone(int(round(dash*fs)))])
            # intra-symbol gap if not last
            if si != len(token)-1:
                samples = np.concatenate([samples, silence(int(round(intra_symbol*fs)))])
        # after letter
        samples = np.concatenate([samples, silence(int(round(inter_letter*fs)))])
    return samples, fs

def save_wav(path, samples, fs):
    sf.write(path, samples, fs, subtype='PCM_16')

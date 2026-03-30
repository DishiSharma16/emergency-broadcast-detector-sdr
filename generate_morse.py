# generate_morse.py
from utils_morse import text_to_morse, morse_to_tone_sequence, save_wav

msg = "SOS EMERGENCY"
morse = text_to_morse(msg)
print("Morse:", morse)
samples, fs = morse_to_tone_sequence(morse, wpm=18, fs=48000, tone_freq=800)
save_wav("morse_sos.wav", samples, fs)
print("Saved morse_sos.wav (fs=%d)" % fs)

import adi

# Connect to Pluto
sdr = adi.Pluto("usb:")

# Print basic info
print("Connected to PlutoSDR")
print("RX LO:", sdr.rx_lo)
print("Sample Rate:", sdr.sample_rate)

# Receive 1 buffer of IQ data
samples = sdr.rx()
print("Received", len(samples), "samples")

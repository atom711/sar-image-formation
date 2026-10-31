import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Allow imports from the local 'src' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.chirp import generate_lfm_chirp, apply_matched_filter

# --- Physics & Radar System Parameters ---
c = 3e8              # Speed of light in meters per second (m/s)
bandwidth = 150e6    # Transmitted signal bandwidth (150 MHz) -> determines range resolution
pulse_duration = 10e-6 # Duration of one chirp pulse (10 microseconds)
fs = 2 * bandwidth   # Sampling frequency (Nyquist rate: twice the bandwidth)

# --- Generate Reference Transmitted Chirp ---
# This creates the ideal blueprint of the signal you are sending out of the antenna
t_chirp, tx_pulse = generate_lfm_chirp(pulse_duration, bandwidth, fs)
N_chirp = len(tx_pulse)

# --- Build Receive Signal Vector (Simulating Radar Echoes) ---
# Create a time axis long enough for a round-trip out to 3,000 meters and back
t_receive = np.arange(0, 2 * 3000.0 / c, 1 / fs)
rx_signal = np.zeros(len(t_receive), dtype=complex) # Initialize empty container with zeros (dead time / space)

# Define simulated targets: [Range in meters, Radar Cross Section / Amplitude multiplier]
# Target located at 1.5 km with a reflection strength of 1.0
targets = [
    (1500.0, 1.0),
    (1501.5, 0.8)
]

# Inject target echoes into the receive signal vector
for target_range, rcs in targets:
    # Calculate round-trip delay time for this target
    round_trip_time = 2 * target_range / c
    
    # Find the sample index corresponding to that delay time
    start_idx = int(round_trip_time * fs)
    end_idx = start_idx + N_chirp
    
    # Ensure we don't overflow the array boundaries
    if end_idx <= len(rx_signal):
        # Add the scaled transmitted chirp into the receive array at the exact target bin location
        rx_signal[start_idx:end_idx] += rcs * tx_pulse
    else:
        # Handle edge case if target is too close to the end of the window
        valid_len = len(rx_signal) - start_idx
        rx_signal[start_idx:] += rcs * tx_pulse[:valid_len]

# --- OPTIONAL: Diagnostic Plot 1 (Raw Receive Signal) ---
# Uncomment below to inspect the flat zero-region followed by the uncompressed echo wave
# plt.figure(figsize=(10, 4))
# plt.plot(np.abs(rx_signal))
# plt.title("1. Raw Receive Signal (Time Domain Magnitude)")
# plt.xlabel("Sample Index")
# plt.ylabel("Amplitude")
# plt.grid(True)
# plt.show()


# --- Process Matched Filtering (With and Without Windowing) ---
# Run once with a rectangular (no) window
compressed_rect = apply_matched_filter(rx_signal, tx_pulse, window=None)

# Run a second time with a Hamming window to see side-lobe suppression
compressed_hamm = apply_matched_filter(rx_signal, tx_pulse, window='hamming')


# --- Correct Range Axis Mapping ---
# Convert sample indices from the IFFT output back into physical distance (meters)
# Distance = (Sample Index * Speed of Light) / (2 * Sampling Frequency)
N_fft = len(compressed_rect)
range_axis = (np.arange(N_fft) / fs) * (c / 2.0)


# --- Convert to Decibels (dB) for Dynamic Range Visualization ---
# Radar data spans huge amplitude differences, so we scale it logarithmically (20 * log10)
# We normalize against the maximum peak value so the peak sits right at 0 dB.
norm_rect = 20 * np.log10(np.abs(compressed_rect) / np.max(np.abs(compressed_rect)))
# Hamming Window: Tapers pulse edges to trade a slightly wider mainlobe (minor resolution loss) 
# for aggressive sidelobe suppression, preventing strong target reflections from masking weak adjacent targets.
norm_hamm = 20 * np.log10(np.abs(compressed_hamm) / np.max(np.abs(compressed_hamm)))


# --- Plotting Comparison: Windowed vs Unwindowed Matched Filter ---
plt.figure(figsize=(10, 5))
plt.plot(range_axis, norm_rect, label='Rectangular (Unwindowed)', alpha=0.7)
plt.plot(range_axis, norm_hamm, label='Hamming Window', linestyle='--')

# Zoom in tightly around the target peak at 1,500 meters to inspect mainlobe and sidelobes
plt.xlim([1480, 1530])
plt.ylim([-50, 5])
plt.title("Range Compression: Rectangular vs Hamming Windowing")
plt.xlabel("Range (meters)")
plt.ylabel("Normalized Magnitude (dB)")
plt.grid(True)
plt.legend()
plt.tight_layout()

# Save output figure to disk
plt.savefig("figures/chirp_matched_filter_comparison.png", dpi=300, bbox_inches='tight')
plt.show()
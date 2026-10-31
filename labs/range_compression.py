import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Allow imports from src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.chirp import generate_lfm_chirp, apply_matched_filter

# Parameters
c = 3e8
bandwidth = 150e6
pulse_duration = 10e-6
fs = 2 * bandwidth

# Generate reference chirp
t_chirp, tx_pulse = generate_lfm_chirp(pulse_duration, bandwidth, fs)
N_chirp = len(tx_pulse)

# Build receive signal vector
t_receive = np.arange(0, 2 * 3000.0 / c, 1 / fs)
rx_signal = np.zeros(len(t_receive), dtype=complex)

# Define targets: [range_in_meters, rcs_multiplier]
targets = [
    (1500.0, 1.0),
    (1501.5, 0.8)
]

# Safely inject targets into rx_signal
for target_range, rcs in targets:
    round_trip_time = 2 * target_range / c
    start_idx = int(round_trip_time * fs)
    end_idx = start_idx + N_chirp
    
    if end_idx <= len(rx_signal):
        rx_signal[start_idx:end_idx] += rcs * tx_pulse
    else:
        # Handle edge case if target is too close to the end of the window
        valid_len = len(rx_signal) - start_idx
        rx_signal[start_idx:] += rcs * tx_pulse[:valid_len]

# Process matched filtering
compressed_rect = apply_matched_filter(rx_signal, tx_pulse, window=None)
compressed_hamm = apply_matched_filter(rx_signal, tx_pulse, window='hamming')

# Correct range axis mapping
N_fft = len(compressed_rect)
range_axis = (np.arange(N_fft) / fs) * (c / 2.0)

# Normalize safely
norm_rect = 20 * np.log10(np.abs(compressed_rect) / np.max(np.abs(compressed_rect)))
norm_hamm = 20 * np.log10(np.abs(compressed_hamm) / np.max(np.abs(compressed_hamm)))

# Plotting Comparison
plt.figure(figsize=(10, 5))
plt.plot(range_axis, norm_rect, label='Rectangular (Unwindowed)', alpha=0.7)
plt.plot(range_axis, norm_hamm, label='Hamming Window', linestyle='--')

plt.xlim([1480, 1530])
plt.ylim([-50, 5])
plt.title("Range Compression: Rectangular vs Hamming Windowing")
plt.xlabel("Range (meters)")
plt.ylabel("Normalized Magnitude (dB)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("data/chirp_matched_filter_comparison.png", dpi=300, bbox_inches="tight")
plt.show()
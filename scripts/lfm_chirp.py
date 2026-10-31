import numpy as np
import matplotlib.pyplot as plt

# --- 1. Radar & Chirp Parameters ---
c = 3e8                   # Speed of light (m/s)
f0 = 10e9                 # Center frequency: 10 GHz (X-band)
bandwidth = 150e6         # Chirp bandwidth: 150 MHz -> Range res = c / (2*B) ~ 1m
pulse_duration = 10e-6    # Pulse width: 10 microseconds
fs = 2 * bandwidth        # Sampling rate (Hz)

# Target setup
target_range = 1500.0     # Target distance in meters
target_rcs = 1.0          # Target reflectivity multiplier

# --- 2. Time Vectors & Transmitted Chirp (Replica) ---
t_chirp = np.arange(-pulse_duration/2, pulse_duration/2, 1/fs)
K = bandwidth / pulse_duration  # Chirp rate (Hz/s)

# Complex LFM pulse s(t) = exp(j * pi * K * t^2)
tx_pulse = np.exp(1j * np.pi * K * t_chirp**2)

# --- 3. Simulated Received Signal (Time Delay & Noise) ---
time_delay = 2 * target_range / c
max_range = 3000.0
t_receive = np.arange(0, 2 * max_range / c, 1/fs)

# Place delayed chirp into received signal vector
rx_signal = np.zeros(len(t_receive), dtype=complex)
start_idx = int(time_delay * fs)
end_idx = start_idx + len(tx_pulse)

if end_idx < len(rx_signal):
    rx_signal[start_idx:end_idx] += target_rcs * tx_pulse

# Add Gaussian thermal noise (SNR ~ 10 dB)
noise_power = 0.1
noise = (np.random.normal(0, np.sqrt(noise_power/2), len(rx_signal)) + 
         1j * np.random.normal(0, np.sqrt(noise_power/2), len(rx_signal)))
rx_signal += noise

# --- 4. Fast-Time Matched Filtering (Frequency Domain) ---
N_fft = len(rx_signal) + len(tx_pulse) - 1
RX_freq = np.fft.fft(rx_signal, N_fft)
TX_freq = np.fft.fft(tx_pulse, N_fft)

# Matched filter transfer function is the complex conjugate of the TX spectrum
compressed_freq = RX_freq * np.conj(TX_freq)
compressed_signal = np.fft.ifft(compressed_freq)

# Range axis calibration
range_axis = (np.arange(N_fft) / fs) * (c / 2)

# --- 5. Plot Results ---
plt.figure(figsize=(10, 5))
plt.plot(range_axis, 20 * np.log10(np.abs(compressed_signal) / np.max(np.abs(compressed_signal))))
plt.xlim([target_range - 100, target_range + 100])
plt.ylim([-40, 0])
plt.title("Range Compression Peak (Matched Filter Output)")
plt.xlabel("Range (meters)")
plt.ylabel("Normalized Magnitude (dB)")
plt.grid(True)
plt.tight_layout()
plt.show()

# Print metrics
measured_idx = np.argmax(np.abs(compressed_signal))
measured_range = range_axis[measured_idx]
print(f"Target True Range:     {target_range:.2f} m")
print(f"Measured Peak Range:   {measured_range:.2f} m")
print(f"Theoretical Resolution: {c / (2 * bandwidth):.2f} m")
import os
import sys
import matplotlib.pyplot as plt
import numpy as np

# Import the official open-source CPHD reader tool
from sarpy.io.phase_history.cphd import CPHDReader

# file
cphd_file = "2024-01-12-04-09-18_UMBRA-05_CPHD.cphd"

# The reader object opens the file and maps out internal data segment positions
reader = CPHDReader(cphd_file)

# EXTRACT RAW LOGICAL COMPLEX CHANNELS
# Pull a 2048x2048 subset array chip from the raw signal grid safely
# read_chip parameters map to: (pulse_start, pulse_end), (sample_start, sample_end)
phase_matrix = reader.read_chip((0, 2048), (0, 2048))

print(f"Ingested Phase Matrix Shape: {phase_matrix.shape}")
print(f"Data Component Vector Class: {phase_matrix.dtype}") # Verifies true complex numbers

# 2-D MATCHED FILTER; Fast Fourier Transform processing

# Step A: 1D FFT along rows to focus Fast-Time Range chirps
range_compressed = np.fft.fft(phase_matrix, axis=0)

# Step B: 1D FFT along columns to focus Slow-Time Azimuth Doppler history
focused_image = np.fft.fft(range_compressed, axis=1)

# Shift zero-frequency components to the center of the spectrum grid mapping
focused_image = np.fft.fftshift(focused_image)

# COMPRESS LOGARITHMIC SPECTRUM DENSITY TO DECIBELS (dB)
magnitude_matrix = np.abs(focused_image)
normalized_data = magnitude_matrix / np.max(magnitude_matrix)
image_db = 20 * np.log10(normalized_data + 1e-6)

# PLOT
plt.figure(figsize=(10, 8), facecolor="white")

# Apply standard contrast stretching window to reveal ground features
plt.imshow(image_db, cmap="gray", vmin=-45, vmax=0)
plt.colorbar(label="Relative Backscatter Intensity (dB)")

plt.title("Formed Spaceborne Image\nFocused via Custom Python 2D-FFT and SarPy Engine", fontsize=12, fontweight="bold")
plt.xlabel("Cross-Range Azimuth Bins")
plt.ylabel("Slant-Range Pulse Bins")
plt.axis("image")

output_name = "sar_image_formation.png"
plt.savefig(output_name, dpi=300, bbox_inches="tight")
print(f"Process complete! Output successfully saved to disk as '{output_name}'")
plt.show()

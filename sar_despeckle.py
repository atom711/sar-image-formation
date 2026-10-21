
import os
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from scipy.ndimage import uniform_filter

# file path
sar_file_path = "2024-01-12-04-09-18_UMBRA-05_GEC.tif"

# INGEST RASTER DATA VIA RASTERIO 
with rasterio.open(sar_file_path) as src:
    raw_backscatter = src.read(1).astype(float)

# ISOLATE TARGET MATRIX REGION
sar_matrix = raw_backscatter[1999:4047, 1999:4047]
rows, cols = sar_matrix.shape

# PHASE INTENSITY SCALING
print("Executing log-transform intensity compression...")
amplitude_normalized = sar_matrix / np.max(sar_matrix)
sar_db = 20 * np.log10(amplitude_normalized + 1e-6)

# ADAPTIVE DESPECKLING 
print("Applying local variance adaptive noise suppression...")
# Create a moving 5x5 uniform averaging mask (Equivalent to ones(5,5)/25)
local_mean = uniform_filter(sar_matrix, size=5, mode="reflect")
local_sq_mean = uniform_filter(np.square(sar_matrix), size=5, mode="reflect")
local_var = local_sq_mean - np.square(local_mean)

noise_variance = np.mean(local_var) / 2
weight_matrix = local_var / (local_var + noise_variance)
weight_matrix[local_var == 0] = 0

despeckled_matrix = local_mean + weight_matrix * (sar_matrix - local_mean)
despeckled_db = 20 * np.log10(despeckled_matrix / np.max(despeckled_matrix) + 1e-6)

# PLOTS
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), facecolor="white")

# Plot 1: Raw Dynamic Range Radar Field
img1 = ax1.imshow(sar_db, cmap="gray", vmin=-40, vmax=0)
cbar1 = fig.colorbar(img1, ax=ax1, fraction=0.046, pad=0.04)
ax1.set_title("Raw Spaceborne X-Band Amplitude Array", fontweight="bold")
ax1.set_xlabel("Azimuth Coordinates")
ax1.set_ylabel("Slant-Range Bins")

# Plot 2: Processed Signal Field (Adaptive Filtered)
img2 = ax2.imshow(despeckled_db, cmap="gray", vmin=-40, vmax=0)
cbar2 = fig.colorbar(img2, ax=ax2, fraction=0.046, pad=0.04)
ax2.set_title(
    "Despeckled Target Field (Local Variance Windowed)", fontweight="bold"
)
ax2.set_xlabel("Azimuth Coordinates")
ax2.set_ylabel("Slant-Range Bins")

plt.tight_layout()

output_filename = "sar_despeckled_comparison.png"
plt.savefig(output_filename, dpi=300, bbox_inches="tight")
plt.close(fig)

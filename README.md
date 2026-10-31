# SAR Image Formation Toolkit

A modular Python framework for Synthetic Aperture Radar (SAR) signal processing, target simulation, and 2D image formation using real-world Phase History Data (CPHD/SICD).

## Repository Architecture

```text
sar-image-formation/
├── data/       # Local raw SAR phase history and CPHD archives (gitignored)
├── figures/    # Output plots, range profiles, and processing verification images
├── labs/       # Interactive lab scripts for core processing milestones
├── src/        # Core algorithm modules (chirp generation, matched filtering, SAR core)
├── scripts/    # Data fetching and automation utilities
└── tests/      # Verification and unit tests
```

## Daily Milestones & Progress

### Day 1: Range Compression & Signal Windowing
* Implemented Linear Frequency Modulated (LFM) chirp generator.
* Built 1D fast-time matched filtering using time-domain and frequency-domain correlation.
* Evaluated mainlobe width vs. side-lobe suppression trade-offs comparing unwindowed (rectangular) and Hamming windowed functions (~30 dB side-lobe reduction).

### Real-World Data Pipeline Integration
* Integrated native AWS CLI fetching protocols for Umbra CPHD datasets (`s3://umbra-open-data-catalog/`).
* Standardized ingest workflows using `sarpy` for parsing multi-channel complex phase history matrices.

## Quickstart & Setup

### 1. Environment Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install numpy scipy matplotlib sarpy awscli
```

AWS install and data download:

```bash
# Install the official AWS CLI engine natively using classic security permissions
sudo snap install aws-cli --classic

# Verify the binary is successfully compiled and responding to system calls
aws --version

# Stream the raw uncompressed phase history archive (.cphd) down from the open cloud bucket
aws s3 cp --no-sign-request "s3://umbra-open-data-catalog/sar-data/tasks/Bingham Copper Mine/04371d76-7497-425e-b5bc-7206263b622a/2024-01-12-04-09-18_UMBRA-05/2024-01-12-04-09-18_UMBRA-05_CPHD.cphd" .
```

## Theoretical Framework & Radar Physics

Unlike an optical camera that opens a physical shutter and maps incoming light directly onto a geometric grid of pixels where spatial location is already explicitly established, a SAR sensor operates as an echo recorder. It transmits high-power microwave energy pulses and documents the time delay, amplitude, and phase angle of the reflections bouncing back from the earth. Consequently, the data is collected entirely within the time domain. The Fast Fourier Transform (FFT) serves as the primary digital lens in this pipeline, translating the abstract time-domain wave interactions directly into physical frequency-domain spatial coordinates.

The engineering of a SAR system exploits a unique mathematical concept known as separability. Because the physical mechanisms governing how a radar sensor maps the cross-track dimension (Range) are completely independent of how it maps the along-track dimension (Azimuth), the overall 2D image focus problem can be split into two isolated, sequential 1D operations. 

**Range Compression (`axis=0`)** focuses the data vertically down the matrix columns in a timeline called Fast-Time. Because the satellite transmits long, frequency-modulated *Linear FM Chirps*, overlapping reflections from targets at different distances blur together in raw memory. A 1D FFT acts as a matched filter, decoding the chirp modulation to collapse these smeared waveforms into sharp numerical peaks. This operation must run first in the Range-Doppler Algorithm; failing to isolate these distinct range bins beforehand would cause subsequent along-track operations to track completely unlocalized Doppler energy. 

**Azimuth Compression (`axis=1`)** focuses the data horizontally across rows over a longer timeline called Slow-Time. As the satellite travels along its orbital track, it continuously transmits pulses at a rigid Pulse Repetition Frequency (PRF). This relative motion generates a changing physical Doppler shift—a higher pitch as the spacecraft approaches a target and a lower pitch as it recedes. Executing a 1D FFT across this dimension maps these shifting frequency histories directly into precise horizontal cross-range coordinates, completing the 2D spatial grid.

**Frequency Centering and Scaling** transforms the focused output into a viewable map layout. The Discrete Fourier Transform natively outputs frequencies starting at 0Hz before wrapping into aliased negative frequencies, which would visually split the radar beam footprint in half. An `fftshift` operation swaps the matrix quadrants, centering the 0Hz baseline so terrain features align realistically. Finally, because the resulting array consists of complex numbers (I/Q channels), taking the absolute value isolates the raw backscatter magnitude. This data is normalized and converted to a logarithmic decibel (dB) scale via 20 * log10() to compress the massive dynamic range, elevating faint geological textures into viewable gray scales while preventing bright metallic reflections from blowing out the display.


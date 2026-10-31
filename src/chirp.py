import numpy as np

def generate_lfm_chirp(pulse_duration: float, bandwidth: float, fs: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Generates a Linear Frequency Modulated (LFM) pulse (a chirp).
    An LFM chirp sweeps linearly from -bandwidth/2 to +bandwidth/2 over the pulse duration.
    """
    # Create a time array for the duration of a single pulse based on sampling frequency (fs)
    t = np.arange(-pulse_duration / 2, pulse_duration / 2, 1 / fs)
    
    # Calculate the frequency modulation slope (chirp rate), denoted as 'k' or 'gamma'
    # Bandwidth divided by pulse duration gives how fast frequency changes per second
    K = bandwidth / pulse_duration  # Chirp rate (Hz/s)
    
    # Generate the complex exponential chirp signal: exp(j * pi * k * t^2)
    # Using complex numbers (exp(j*theta) = cos(theta) + j*sin(theta)) allows us to represent 
    # quadrature (I/Q) data, avoiding ambiguity in Doppler/frequency shifts.
    tx_pulse = np.exp(1j * np.pi * K * t**2) # CHIRP
    
    return t, tx_pulse


def apply_matched_filter(rx_signal: np.ndarray, tx_pulse: np.ndarray, window: str = None) -> np.ndarray:
    """
    Applies a matched filter to the received signal using the transmitted reference chirp.
    Matched filtering optimizes the Signal-to-Noise Ratio (SNR) and compresses the long chirp into a sharp peak.
    """
    # 1. Optional Windowing: Taper the edges of the reference pulse to reduce frequency sidelobes
    if window == 'hamming':
        win = np.hamming(len(tx_pulse))
        tx_pulse = tx_pulse * win
    elif window == 'taylor':
        # Simple generalized cosine approximation for windowing test
        win = np.blackman(len(tx_pulse))
        tx_pulse = tx_pulse * win
    # If window is None (rectangular), tx_pulse passes through untapered

    # 2. Zero-Padding Length Calculation
    # To avoid circular convolution artifacts when using FFTs, the FFT length (N_fft) 
    # must be at least the length of the signal plus the length of the reference pulse minus 1.
    N_fft = len(rx_signal) + len(tx_pulse) - 1

    # 3. Frequency Domain Transformation (FFT)
    # Convert both the receive signal and the reference pulse into the frequency domain.
    # This turns a slow time-domain convolution into fast frequency-domain multiplication.
    RX_freq = np.fft.fft(rx_signal, N_fft)
    TX_freq = np.fft.fft(tx_pulse, N_fft)

    # 4. Matched Filtering Operation
    # Multiply the received spectrum by the COMPLEX CONJUGATE of the transmitted reference spectrum.
    # Conjugating flips the phase alignment so that the time delays match up and constructively interfere.
    filtered_freq = RX_freq * np.conj(TX_freq)

    # 5. Return to Time Domain (IFFT)
    # Convert the filtered frequency data back into the time domain using the Inverse FFT (IFFT).
    # The result is your compressed range profile (sharp peaks where targets are located).
    # Matched filter transfer function: conjugate of TX spectrum
    compressed_signal = np.fft.ifft(RX_freq * np.conj(TX_freq))
    return compressed_signal
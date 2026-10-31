import numpy as np

def generate_lfm_chirp(pulse_duration: float, bandwidth: float, fs: float) -> tuple[np.ndarray, np.ndarray]:
    """Generates a complex LFM chirp pulse and its time vector."""
    t = np.arange(-pulse_duration / 2, pulse_duration / 2, 1 / fs)
    K = bandwidth / pulse_duration  # Chirp rate (Hz/s)
    tx_pulse = np.exp(1j * np.pi * K * t**2)
    return t, tx_pulse

def apply_matched_filter(rx_signal: np.ndarray, tx_pulse: np.ndarray, window: str = None) -> np.ndarray:
    """Applies fast-time matched filtering in the frequency domain with optional windowing."""
    if window == 'hamming':
        win = np.hamming(len(tx_pulse))
        tx_pulse = tx_pulse * win
    elif window == 'taylor':
        # Simple generalized cosine approximation for windowing test
        win = np.blackman(len(tx_pulse))
        tx_pulse = tx_pulse * win

    N_fft = len(rx_signal) + len(tx_pulse) - 1
    RX_freq = np.fft.fft(rx_signal, N_fft)
    TX_freq = np.fft.fft(tx_pulse, N_fft)
    
    # Matched filter transfer function: conjugate of TX spectrum
    compressed_signal = np.fft.ifft(RX_freq * np.conj(TX_freq))
    return compressed_signal
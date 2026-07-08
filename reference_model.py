"""
Floating-point reference model: 31-tap FIR low-pass, decimate by 2.
Golden standard for validating the Q15 fixed-point C implementation.
"""
import numpy as np
from scipy import signal

FS = 48000        # input sample rate (Hz)
NTAPS = 31        # filter length
CUTOFF = 10000    # passband edge (Hz), below new Nyquist of 12 kHz
DECIM = 2         # decimation factor
N = 4096          # test signal length

# --- 1. Design the filter (Hamming-windowed sinc) ---
taps = signal.firwin(NTAPS, CUTOFF, fs=FS, window="hamming")

# --- 2. Quantize coefficients to Q15 (this is what the C code will use) ---
taps_q15 = np.round(taps * 32768).astype(np.int32)
taps_q15 = np.clip(taps_q15, -32768, 32767)

# --- 3. Test signal: in-band tone + out-of-band tone + noise ---
rng = np.random.default_rng(42)
t = np.arange(N) / FS
x = (0.4 * np.sin(2*np.pi*3000*t)      # 3 kHz  -> must survive
   + 0.4 * np.sin(2*np.pi*18000*t)     # 18 kHz -> must be killed
   + 0.05 * rng.standard_normal(N))    # noise floor
x = np.clip(x, -0.999969, 0.999969)    # keep inside Q15 range

# Quantize input to Q15 — the C code receives EXACTLY these samples
x_q15 = np.round(x * 32768).astype(np.int16)

# --- 4. Reference filtering: float taps on the Q15-quantized input ---
x_float = x_q15.astype(np.float64) / 32768.0
y = np.convolve(x_float, taps, mode="full")[:N]   # causal FIR
y_dec = y[::DECIM]                                 # decimate by 2

# --- 5. Save everything the C program needs ---
np.savetxt("input_q15.txt",  x_q15,    fmt="%d")
np.savetxt("taps_q15.txt",   taps_q15, fmt="%d")
np.savetxt("reference_output.txt", y_dec, fmt="%.10f")

print(f"Filter designed : {NTAPS} taps, cutoff {CUTOFF} Hz at fs {FS} Hz")
print(f"Taps Q15 range  : [{taps_q15.min()}, {taps_q15.max()}]")
print(f"Input samples   : {N}  ->  output after decimation: {len(y_dec)}")
print(f"Output range    : [{y_dec.min():.4f}, {y_dec.max():.4f}]")
print("Files written   : input_q15.txt, taps_q15.txt, reference_output.txt")

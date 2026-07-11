"""
Sample-by-sample comparison: Q15 C implementation vs floating-point
reference. Measures quantization SNR and worst-case error.
Exits nonzero if error exceeds 3 LSBs of Q15, so CI can enforce it.
"""
import sys
import numpy as np

LSB = 1.0 / 32768.0
LIMIT_LSB = 3          # pass/fail threshold in Q15 LSBs

ref = np.loadtxt("reference_output.txt")          # float reference
c_q15 = np.loadtxt("c_output_q15.txt")            # Q15 ints from C
c = c_q15 / 32768.0                                # back to float scale

n = min(len(ref), len(c))
ref, c = ref[:n], c[:n]

err = c - ref
max_abs_err = np.max(np.abs(err))
rms_err = np.sqrt(np.mean(err**2))

signal_power = np.mean(ref**2)
noise_power = np.mean(err**2)
snr_db = 10*np.log10(signal_power / noise_power) if noise_power > 0 else float("inf")

print(f"Samples compared      : {n}")
print(f"Max absolute error    : {max_abs_err:.8f}  ({max_abs_err/LSB:.2f} Q15 LSBs)")
print(f"RMS error             : {rms_err:.8f}")
print(f"Quantization SNR      : {snr_db:.2f} dB")
print(f"Pass threshold        : max error <= {LIMIT_LSB} LSBs")

if max_abs_err <= LIMIT_LSB * LSB:
    print("RESULT: PASS - C implementation matches reference within Q15 precision")
    sys.exit(0)
else:
    print("RESULT: FAIL - divergence exceeds Q15 quantization floor")
    sys.exit(1)

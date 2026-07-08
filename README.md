# q15-fir-validation

Q15 fixed-point FIR decimation filter in embedded C, validated sample-by-sample against a Python/SciPy floating-point reference model.

**Status: in progress.** Reference model done. C implementation and comparison harness next.

## Structure
- `reference_model.py` — designs a 31-tap low-pass FIR (48 kHz, 10 kHz cutoff, decimate by 2), quantizes coefficients to Q15, generates test signals, writes the golden reference output.
- `fixed_point_filter.c` — (coming) pure Q15 implementation, no floating point in the signal path.
- `compare_results.py` — (coming) sample-by-sample error and SNR measurement.

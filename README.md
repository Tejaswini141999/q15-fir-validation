# q15-fir-validation

![validate](https://github.com/Tejaswini141999/q15-fir-validation/actions/workflows/validate.yml/badge.svg)

Q15 fixed-point FIR decimation filter in embedded C, validated sample by sample against a Python/SciPy floating-point reference model. The repository demonstrates a complete numerical validation workflow: golden reference model, hardware-constrained implementation, and automated bit-level comparison with a defined pass/fail criterion.

## Measured results

| Metric | Value |
|---|---|
| Quantization SNR | 79.95 dB |
| Max absolute error | 5.77e-5 (1.89 Q15 LSBs) |
| RMS error | 2.86e-5 |
| Pass criterion | max error below 3 Q15 LSBs |

The validation runs automatically in CI on every commit. The build fails if the C implementation diverges from the reference beyond the defined threshold.

## Filter specification

| Parameter | Value |
|---|---|
| Structure | 31-tap linear-phase FIR, direct form |
| Sample rate | 48 kHz input |
| Passband edge | 10 kHz |
| Decimation factor | 2 |
| Coefficient format | Q15 (int16) |
| Signal path | int16 samples, int64 accumulator, no floating point |

## Reproducing the results

    git clone https://github.com/Tejaswini141999/q15-fir-validation.git
    cd q15-fir-validation
    pip install numpy scipy
    python reference_model.py
    gcc -O2 -Wall -o fir_q15 fixed_point_filter.c
    ./fir_q15
    python compare_results.py

Expected output: PASS with the metrics listed above. Total runtime is under one minute.

## Repository structure

| File | Purpose |
|---|---|
| reference_model.py | Designs the filter (SciPy firwin, Hamming window), quantizes coefficients to Q15, generates a test signal with an in-band tone, an out-of-band tone and noise, and writes the golden reference output. |
| fixed_point_filter.c | Q15 implementation in pure integer arithmetic. Reads the same quantized input and coefficients, writes Q15 output. |
| compare_results.py | Sample-by-sample comparison. Computes SNR, RMS and worst-case error in Q15 LSBs. Exits nonzero on failure, which CI enforces. |
| .github/workflows/validate.yml | CI pipeline: builds the C code, regenerates the reference, runs the filter, runs the comparison. |

## Design decisions

**Q15 format.** One sign bit, 15 fractional bits, range [-1, 1). This is the native format of 16-bit fixed-point DSPs and FPGA multiplier blocks.

**64-bit accumulator.** Each Q15 x Q15 product occupies Q30 (32 bits). Accumulating 31 products can exceed 32 bits, so a 64-bit accumulator removes intermediate overflow as a failure mode. Saturation then needs to be handled only once, at the output stage.

**Round to nearest, not truncation.** Half an LSB is added before the Q30 to Q15 shift. Truncation introduces a DC bias and doubles the error floor relative to rounding.

**Saturation, not wraparound.** Two's-complement wraparound converts a marginal overshoot into a full-scale sample of opposite sign. Saturating arithmetic clips gracefully, matching the behaviour of hardware MAC units.

**Identical quantized input for both implementations.** The reference model filters the Q15-quantized input rather than the ideal float signal. The measured error therefore isolates the arithmetic difference between floating-point and fixed-point processing, independent of input quantization noise.

## Background

This repository is a compact public version of the validation methodology from my M.Sc. thesis (Hochschule Bremen, 2025), which benchmarked five deep learning architectures for acoustic anomaly detection against fixed-point conversion constraints using MATLAB/Simulink, Fixed-Point Designer and auto-code generation for embedded targets. Three of the five architectures passed in floating point and failed after fixed-point conversion. This project applies the same reference-versus-implementation validation pattern in a minimal, fully reproducible form.

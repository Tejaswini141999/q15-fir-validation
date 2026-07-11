/*
 * Q15 fixed-point FIR decimation filter.
 * Reads Q15 input samples and Q15 coefficients from text files,
 * filters with a 31-tap FIR (pure integer arithmetic, no floating
 * point in the signal path), decimates by 2, writes Q15 output.
 *
 * Accumulator: 64-bit to make intermediate overflow impossible
 * (31 taps * int16 * int16 fits easily in 64 bits).
 * Rounding: convergent-free simple rounding, add 0x4000 before >>15.
 * Saturation: clamp to [-32768, 32767] after shift.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define NTAPS 31
#define DECIM 2
#define MAXN  8192

static int16_t taps[NTAPS];
static int16_t x[MAXN];

static int load_i16(const char *path, int16_t *dst, int maxn) {
    FILE *f = fopen(path, "r");
    if (!f) { fprintf(stderr, "cannot open %s\n", path); exit(1); }
    int n = 0; long v;
    while (n < maxn && fscanf(f, "%ld", &v) == 1) {
        dst[n++] = (int16_t)v;
    }
    fclose(f);
    return n;
}

static inline int16_t sat_q15(int64_t acc) {
    /* acc is in Q30 (Q15*Q15). Round and shift back to Q15. */
    acc += (int64_t)1 << 14;      /* rounding */
    acc >>= 15;
    if (acc >  32767) acc =  32767;
    if (acc < -32768) acc = -32768;
    return (int16_t)acc;
}

int main(void) {
    int ntaps = load_i16("taps_q15.txt", taps, NTAPS);
    int n     = load_i16("input_q15.txt", x, MAXN);
    if (ntaps != NTAPS) { fprintf(stderr, "expected %d taps, got %d\n", NTAPS, ntaps); return 1; }

    FILE *out = fopen("c_output_q15.txt", "w");
    if (!out) { fprintf(stderr, "cannot open output file\n"); return 1; }

    int written = 0;
    for (int i = 0; i < n; i += DECIM) {
        int64_t acc = 0;
        for (int k = 0; k < NTAPS; k++) {
            int idx = i - k;
            int16_t xi = (idx >= 0) ? x[idx] : 0;   /* zero initial state */
            acc += (int32_t)xi * (int32_t)taps[k];   /* Q15*Q15 = Q30 */
        }
        fprintf(out, "%d\n", (int)sat_q15(acc));
        written++;
    }
    fclose(out);

    printf("Q15 FIR done: %d input samples -> %d output samples (decimate by %d)\n",
           n, written, DECIM);
    printf("Signal path: int16 in, int64 accumulate, round, saturate, int16 out. Zero floats.\n");
    return 0;
}

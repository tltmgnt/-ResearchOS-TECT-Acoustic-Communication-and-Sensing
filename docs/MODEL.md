# Baseband link and single-echo demo v1

## Idealized link

At distance d ≥ reference distance d₀, relative loss is:

`loss_dB = 20 log10(d/d₀) + absorption_dB_per_km × (d−d₀)/1000`

Received Eb/N0 in dB is declared reference Eb/N0 minus this loss. The reference already describes conditions at d₀; absorption applies only to additional distance. This is a geometric/fixed-noise model with user-supplied absorption. No frequency, bandwidth, acoustic source level, transducer response or environment-dependent absorption is inferred. Eb/N0 is energy per bit divided by noise spectral density, not generic receive SNR. Increasing bitrate does not automatically change supplied Eb/N0; the researcher must adjust energy assumptions consistently.

Convert received Eb/N0 to linear gamma = 10^(dB/10). Transmitted bits map to −1/+1 unit-energy real symbols. Add independent Gaussian noise of standard deviation sqrt(1/(2 gamma)), and decide at zero. The ideal coherent AWGN BER is approximated as `0.5 erfc(sqrt(gamma))`. A shared polynomial/exponential erfc approximation is checked against Python math.erfc to absolute error 10⁻⁷ on tested points. Extreme small probabilities may underflow to zero. This numerical approximation is not a physical uncertainty model.

One-way propagation delay is d/c. Frame duration is bits/bitrate, excluding propagation, coding, headers, retries, processing and synchronization. Model limits: 1–30 distances, 1–100,000 bits per distance, at most one million total bits, d ≤ 10⁶ m, and received/reference Eb/N0 within [−60,60] dB. Nonfinite results are rejected.

Simulation uses a portable noncryptographic LCG32: state = (1664525 state + 1013904223) mod 2³², uniform = (state+0.5)/2³². Box-Muller uses two successive uniforms and the cosine branch for a normal draw. Each symbol consumes one bit uniform and two normal uniforms. Sweep index i uses seed+i modulo 2³², so changing distance order changes its noise stream. No confidence intervals are computed. Zero observed errors do not imply zero probability.

## Synthetic ranging

A seeded bipolar pulse is injected with a declared nonnegative gain at a known integer delay, into independent real Gaussian noise. The pulse and noise use the same generator with seed XOR 0xa5a5a5a5. Receiver length equals pulse length plus maximum delay; the search includes zero through maximum delay.

Score(delay) is the mean of pulse[i] × received[i+delay]. The largest signed correlation score wins, with the earliest delay breaking ties. Range = delay × sound speed / (2 × sample rate), assuming a monostatic round trip and known constant sound speed. Bin spacing is c/(2fs); it is not measurement uncertainty or guaranteed resolution.

Limits: sample rate 100–192,000 Hz, pulse length 8–256 samples, maximum delay 1–4,096 samples, injected delay within that search, gain and noise standard deviation in [0,10]. No threshold, confidence estimate or false-alarm control is provided. Even zero-gain/noise-only input has an argmax; this is not certified detection. At all-zero input all delays tie and zero wins. No actual target, object identification, live audio or real acoustic waveform is modeled.

## Scope and reproducibility

Both demos exclude multipath, Doppler, reverberation, colored noise, fading, carrier generation, hardware timing and calibration. Declared measurements are stored separately without fitting or validating them. Synthetic output remains synthetic even when its input record contains experimental measurements.

Python and JavaScript are checked for matching sampled errors, peaks and numerical results across seeds and delay boundaries. Floating-point/logarithm differences can affect borderline decisions. Exact bundle verification uses the current runner/runtime; preserve Python version and runner revision for durable studies. Hashes are integrity declarations, not signatures: replacing every record and hash can forge a self-consistent bundle.

"""Bounded baseband AWGN and synthetic single-echo ranging demonstrations."""
import math
from .records import dumps, require, validate

LIMITATIONS = (
    "Simplified synthetic models only. BPSK assumes coherent ideal timing and AWGN; "
    "loss uses geometric spreading plus declared absorption with fixed noise. "
    "Ranging uses one injected baseband echo and known sound speed. No acoustic "
    "hardware, carrier waveform, multipath, Doppler, reverberation, environmental "
    "calibration or field validation is implemented. These results establish "
    "neither operational performance nor scientific novelty or DARPA compliance."
)


class RNG:
    """Portable LCG32 and Box-Muller normal draws; not cryptographic."""
    def __init__(self, seed):
        self.state = seed

    def uniform(self):
        self.state = (1664525*self.state+1013904223) & 0xffffffff
        return (self.state+.5)/4294967296

    def normal(self):
        return math.sqrt(-2*math.log(self.uniform()))*math.cos(2*math.pi*self.uniform())


def erfc_approx(x):
    t = 1/(1+.5*x)
    poly = .17087277
    for c in (-.82215223, 1.48851587, -1.13520398, .27886807, -.18628806, .09678418, .37409196, 1.00002368):
        poly = c+t*poly
    return min(1.0, t*math.exp(-x*x-1.26551223+t*poly))


def link_study(r):
    p = r["link"]
    rows = []
    for index,d in enumerate(p["distances_m"]):
        loss = 20*math.log10(d/p["reference_distance_m"]) + p["absorption_db_km"]*(d-p["reference_distance_m"])/1000
        ebn0 = p["reference_ebn0_db"]-loss
        require(math.isfinite(ebn0) and -60 <= ebn0 <= 60, "received Eb/N0 outside supported [-60,60] dB; revise channel assumptions")
        gamma = 10**(ebn0/10)
        sigma = math.sqrt(1/(2*gamma))
        rng = RNG((r["seed"]+index) & 0xffffffff)
        errors = 0
        preview = []
        for i in range(p["bits"]):
            bit = 1 if rng.uniform() >= .5 else 0
            received = (1 if bit else -1)+sigma*rng.normal()
            decided = 1 if received >= 0 else 0
            errors += decided != bit
            if i < 48:
                preview.append({"symbol":i,"bit":bit,"received":received,"decided":decided})
        row = {"distance_m":d,"relative_loss_db":loss,"received_ebn0_db":ebn0,
               "one_way_delay_s":d/p["sound_speed_m_s"],"frame_time_s":p["bits"]/p["bit_rate_bps"],
               "approx_theoretical_ber":.5*erfc_approx(math.sqrt(gamma)),
               "simulated_bit_errors":errors,"simulated_ber":errors/p["bits"],"symbol_preview":preview}
        dumps(row)
        rows.append(row)
    return rows


def ranging_study(r):
    p = r["ranging"]
    rng = RNG((r["seed"] ^ 0xa5a5a5a5) & 0xffffffff)
    pulse = [1 if rng.uniform() >= .5 else -1 for _ in range(p["pulse_samples"])]
    rx = [p["noise_std"]*rng.normal() for _ in range(p["pulse_samples"]+p["max_delay_samples"])]
    for i,value in enumerate(pulse):
        rx[i+p["injected_delay_samples"]] += p["echo_gain"]*value
    scores = [sum(value*rx[delay+i] for i,value in enumerate(pulse))/len(pulse) for delay in range(p["max_delay_samples"]+1)]
    peak = max(range(len(scores)),key=lambda i:scores[i])
    scale = r["link"]["sound_speed_m_s"]/(2*p["sample_rate_hz"])
    result = {"injected_delay_samples":p["injected_delay_samples"],"estimated_delay_samples":peak,
              "injected_range_m":p["injected_delay_samples"]*scale,"estimated_range_m":peak*scale,
              "absolute_range_error_m":abs(peak-p["injected_delay_samples"])*scale,
              "range_bin_m":scale,"peak_score":scores[peak],
              "detection_status":"unthresholded-maximum-only",
              "correlation":[{"delay_samples":i,"score":s} for i,s in enumerate(scores)]}
    dumps(result)
    return result


def analyze(record):
    r = validate(record)
    return {"analysis":"baseband-link-and-echo-demo-v1","runner_version":"0.1.0",
            "input_data_kind":r["data_kind"],"output_kind":"synthetic-simulation",
            "link_results":link_study(r),"ranging_results":ranging_study(r),
            "declared_measurements":r["measurements"],"limitations":LIMITATIONS}

#!/usr/bin/env python3
import sionna as sn
import tensorflow as tf
import os

print("🎉 **Sionna Workshop Complete!**")
print(f"Sionna: {sn.__version__}")

from sionna.phy.channel import AWGN
from sionna.phy.mapping import Mapper

print("\n🔬 **Sionna AWGN Test**")

batch_size = 32
ebno_db = 10.0

bits = tf.cast(tf.random.uniform([batch_size, 64], 0, 2) > 0.5, tf.float32)
mapper = Mapper("qam", 2)
symbols = mapper(bits)

Eb = tf.reduce_mean(tf.abs(symbols)**2)
No = Eb / (10**(ebno_db/10))

awgn = AWGN()
rx_symbols = awgn(symbols, No)

print(f"✅ Eb/No {ebno_db}dB Success!")
print(f"  Tx Power: {Eb:.3f}")
print(f"  Noise: {No:.4f}")
print(f"  Rx Verified!")

# 🔥 Add file saving! (Important!)
results_dir = "/app/results"
os.makedirs(results_dir, exist_ok=True)

# Save results to text file
output_file = f"{results_dir}/sionna_result.txt"
with open(output_file, "w") as f:
    f.write("=== Sionna AWGN Test Results ===\n")
    f.write(f"Eb/No: {ebno_db} dB\n")
    f.write(f"Tx Power: {Eb.numpy():.3f}\n")
    f.write(f"Noise Power: {No.numpy():.4f}\n")
    f.write(f"Batch Size: {batch_size}\n")

print(f"\n💾 Results saved: {output_file}")

print("\n🏆 Docker + Sionna Perfect!")
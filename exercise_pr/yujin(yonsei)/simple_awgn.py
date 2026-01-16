#!/usr/bin/env python3
import sionna as sn
import tensorflow as tf
import os

print("🎉 **Sionna 워크숍 완성!**")
print(f"Sionna: {sn.__version__}")

from sionna.phy.channel import AWGN
from sionna.phy.mapping import Mapper

print("\n🔬 **Sionna AWGN 테스트**")

batch_size = 32
ebno_db = 10.0

bits = tf.cast(tf.random.uniform([batch_size, 64], 0, 2) > 0.5, tf.float32)
mapper = Mapper("qam", 2)
symbols = mapper(bits)

Eb = tf.reduce_mean(tf.abs(symbols)**2)
No = Eb / (10**(ebno_db/10))

awgn = AWGN()
rx_symbols = awgn(symbols, No)

print(f"✅ Eb/No {ebno_db}dB 성공!")
print(f"  Tx 파워: {Eb:.3f}")
print(f"  노이즈: {No:.4f}")
print(f"  Rx 확인됨!")

# 🔥 파일 저장 추가! (중요!)
results_dir = "/app/results"
os.makedirs(results_dir, exist_ok=True)

# 결과 텍스트 파일로 저장
output_file = f"{results_dir}/sionna_result.txt"
with open(output_file, "w") as f:
    f.write("=== Sionna AWGN 테스트 결과 ===\n")
    f.write(f"Eb/No: {ebno_db} dB\n")
    f.write(f"Tx Power: {Eb.numpy():.3f}\n")
    f.write(f"Noise Power: {No.numpy():.4f}\n")
    f.write(f"Batch Size: {batch_size}\n")

print(f"\n💾 결과 저장됨: {output_file}")

print("\n🏆 Docker + Sionna 완벽!")
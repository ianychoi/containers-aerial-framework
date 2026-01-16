---
title: "Dockerfile과 Sionna 실습"
weight: 42
---

# Dockerfile과 Sionna의 만남

**"pip install" 대신 Docker로 Sionna 환경 만들기**

Sionna를 로컬에 직접 설치하지 말고, Dockerfile로 환경을 정의해 봅니다. 간단한 통신 실험 1개를 컨테이너에서 실행하며 Docker의 재사용성을 체험합니다.

## 🎯 실습 단계

1. **제공된 Dockerfile 확인**
2. **이미지 빌드**
3. **컨테이너 실행 + Sionna 테스트**
4. **결과 확인**

**포인트**: 환경을 "코드(Dockerfile)"로 만드는 습관!

## 📋 1단계: 파일 준비 (5분)

- Link1: ![Dockerfile](/static/samples/docker-sionna/Dockerfile)
- Link2: ![simple_awgn.py](/static/samples/docker-sionna/simple_awgn.py)

```bash
mkdir /workshop/docker-sionna
cd /workshop/docker-sionna
curl -o <Link1>
curl -o <Link2>
```

워크숍 폴더 구조:

```
docker-sionna/
├── Dockerfile         # 제공됨 (수정 불필요!)
└── simple_awgn.py     # Sionna 실험 스크립트
```

## 🧐 2단계: Dockerfile 한눈에 보기 (5분)

**제공된 Dockerfile:**

```dockerfile
FROM python:3.10-slim
WORKDIR /app
RUN pip install sionna tensorflow numpy matplotlib
COPY simple_awgn.py .
CMD ["python", "simple_awgn.py"]
```

### 한 줄씩 이해

- `FROM python:3.10-slim`: 가벼운 Python 3.10 베이스 이미지
- `WORKDIR /app`: 작업 디렉토리 설정
- `RUN pip install`: Sionna + TensorFlow 자동 설치
- `COPY simple_awgn.py`: 실험 코드 복사
- `CMD`: 컨테이너 시작 시 자동 실행

### Base 이미지 비교

| Base 이미지 | 크기 | 빌드시간 | GPU | 추천 |
|-------------|------|----------|-----|------|
| `python:3.10-slim` | **1.2GB** | **2분** | CPU | 🏆 **워크숍 최적** |
| `tensorflow/tensorflow:2.16.1` | 3.5GB | 5분 | CPU/GPU | 복잡 |
| `nvidia/cuda:12.4.1` | 10GB | 8분 | GPU | 무거움 |
| `python:3.10-alpine` | 0.8GB | 4분 | CPU | 호환성 문제 |

**워크숍 선택 이유**: `python:3.10-slim`은 가볍고 빠르며 Sionna 1.2.1 완벽 호환!

## 🔨 3단계: 이미지 빌드 (5분)

터미널에서 실행:

```bash
cd docker-sionna
docker build -t sionna-simple .
```

**성공 시 출력 예시:**

```
[+] Building 101.3s (9/9) FINISHED
 => [1/4] FROM python:3.10-slim                      3.4s
 => [2/4] WORKDIR /app                               0.3s
 => [3/4] RUN pip install sionna...                 76.6s
 => [4/4] COPY simple_awgn.py .                      0.0s
 => exporting to image                              18.5s
 => => exporting layers                             18.5s
 => => naming to docker.io/library/sionna-simple     0.0s
 ```

**확인:**

```bash
docker images | grep sionna-simple
```

**예상 결과:**
```
sionna-simple   latest   abc123   2분 전   1.2GB
```

## 🚀 4단계: Sionna 실험 실행 (20분)

### 한 번에 실행 (가장 쉽다!)

```bash
docker run --rm sionna-simple
```

### 예상 결과 (10초 내 출력):

```
🎉 **Sionna 워크숍 완성!**
Sionna: 1.2.1

🔬 **Sionna AWGN 테스트**
✅ Eb/No 10dB 성공!
  Tx 파워: 1.000
  노이즈: 0.1000
  Rx 확인됨!

🏆 Docker + Sionna 완벽!
```

### 자세히 보고 싶다면 (인터랙티브)

```bash
docker run -it --rm sionna-simple bash
```

컨테이너 안에서:

```bash
python simple_awgn.py
ls -la  # 파일 확인
exit
```

## 🖥️ 4.5단계: 인프라 환경 확인 (10분) [Optional]

### GPU 환경 확인

AWS EC2에서 GPU 인스턴스를 사용하는 경우 다음 명령어로 확인:

```bash
# 호스트에서 GPU 확인
nvidia-smi

# Docker 컨테이너에서 GPU 접근 확인 (GPU 인스턴스인 경우)
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
```

**GPU 사용 가능 시 예상 출력:**
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 535.104.05             Driver Version: 535.104.05   CUDA Version: 12.2     |
|-------------------------------+----------------------+----------------------+
| GPU  Name                 Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                               |                      |               MIG M. |
|===============================+======================+======================|
|   0  Tesla T4                   Off  | 00000000:00:1E.0 Off |                    0 |
| N/A   45C    P0    26W /  70W |      0MiB / 15109MiB |      0%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+
```

**GPU가 없는 경우 (CPU 전용):**
```bash
# CPU 정보 확인
lscpu | grep -E "Model name|Architecture|CPU\(s\)"
```

### Graviton (ARM64) 환경 확인

AWS Graviton 프로세서를 사용하는 경우:

```bash
# 아키텍처 확인
uname -m
# 출력: aarch64 (ARM64) 또는 x86_64 (Intel/AMD)

# CPU 상세 정보
lscpu | grep -E "Architecture|Model name|CPU\(s\)"

# Graviton 특화 정보 확인
cat /proc/cpuinfo | grep -E "model name|processor" | head -5
```

**Graviton 인스턴스 예상 출력:**
```
Architecture:        aarch64
CPU(s):              4
Model name:          Neoverse-N1
```

**x86 인스턴스 예상 출력:**
```
Architecture:        x86_64
CPU(s):              2
Model name:          Intel(R) Xeon(R) Platinum 8259CL CPU @ 2.50GHz
```

### Docker 아키텍처 호환성 확인

```bash
# Docker가 현재 아키텍처에서 실행되는지 확인
docker version --format 'Client: {{.Client.Arch}} Server: {{.Server.Arch}}'

# 멀티 아키텍처 이미지 지원 확인
docker buildx version
```

### 성능 벤치마크 (선택사항)

```bash
# CPU 성능 간단 테스트
docker run --rm python:3.10-slim python -c "
import time
start = time.time()
sum(i*i for i in range(1000000))
print(f'CPU 테스트 완료: {time.time()-start:.2f}초')
print(f'아키텍처: {__import__('platform').machine()}')
"
```

**성능 비교 참고:**
- **Graviton3 (ARM64)**: 전력 효율성 우수, 비용 효율적
- **Intel/AMD (x86_64)**: 단일 스레드 성능 우수, 광범위한 소프트웨어 호환성

### 환경별 최적화 팁

| 환경 | 최적화 방법 | 주의사항 |
|------|-------------|----------|
| **GPU 인스턴스** | `--gpus all` 플래그 사용 | CUDA 버전 호환성 확인 |
| **Graviton (ARM64)** | ARM64 네이티브 이미지 사용 | 일부 패키지 호환성 확인 |
| **x86_64** | 표준 이미지 사용 | 메모리 사용량 모니터링 |

## 🎉 5단계: 성공 확인 (5분)

**체크리스트:**

| 항목 | 확인 방법 | 예상 결과 |
|------|-----------|-----------|
| ✅ 빌드 성공 | `docker images` | sionna-simple 보임 |
| ✅ 실행 성공 | `docker run` | 🏆 메시지 출력 |
| ✅ Sionna 동작 | 출력 확인 | "Eb/No 10dB 성공!" |
| ✅ 에러 없음 | 빨간 에러 | 없음 |

## 🔍 simple_awgn.py 코드 살펴보기

**컨테이너가 실행하는 코드:**

```python
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
```

**핵심 포인트:**
- Sionna 1.2.1 API: `sionna.phy.channel.AWGN`
- 수동 노이즈 계산 (utils 불필요)
- 최소 32 batch로 빠른 실행

## 💡 왜 이렇게 하는 게 좋을까?

```
❌ 로컬 설치 (힘듦 😭)
$ pip install sionna tensorflow  # 20분+환경 충돌
$ python simple_awgn.py          # 내 PC에서만 됨

✅ Docker 방식 (편함 😊)  
$ docker build -t sionna-simple .  # 2분 한 번만
$ docker run sionna-simple         # 원할 때 언제든지 재실행이 편리함 + 환경 완벽 재현
```

**재사용성 핵심:**
- 환경 = 코드(Dockerfile)
- `docker build` 1회 → 무한 재실행
- ECR 업로드 → 어디서나 동일 환경

## 🛠️ 만약 에러가 나면?

| 에러 메시지 | 해결법 |
|-------------|--------|
| `no space left` | `docker system prune -af` |
| `ModuleNotFoundError` | `docker build --no-cache .` |
| `Permission denied` | `sudo docker ...` 또는 그룹 추가 |
| 빌드 느림 | 네트워크 확인, 다른 미러 시도 |

## 🎁 보너스: 결과 저장하기

```bash
# 결과 폴더를 호스트에 연결
docker run --rm -v "$(pwd)/results:/app/results" sionna-simple
```

컨테이너 종료 후 `./results/`에 파일 저장됨!

## ✅ 실습 완료!

**축하합니다! 🎉**

이제 다음을 할 수 있습니다:

✅ Dockerfile로 Sionna 환경 정의  
✅ `docker run` 한 번에 실험 실행  
✅ "환경 설치" 시간 0초!  
✅ Base 이미지 선택 기준 이해

**다음 시간**: 이 이미지를 ECR에 올리고, 약간 바꿔서 새 버전 만들기.

---

**[다음: 환경 버전 만들기 →](/40-container-environment/experiment-environment/)**

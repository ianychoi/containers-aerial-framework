---
title: "실험 환경 통합 구축"
weight: 61
---

# 실험 환경 통합 구축

**Docker + Git으로 Sionna PHY Abstraction 실험 환경 만들기**

이제 Docker, Git, 그리고 실제 Sionna 실험을 통합하여 재현 가능한 연구 환경을 구축해봅니다. PHY Abstraction을 사용한 링크 레벨 시뮬레이션을 통해 실제 연구에서 사용하는 워크플로우를 경험합니다.

## 🎯 실습 목표

1. **통합 프로젝트 구조 생성** - Docker + Git + Sionna 실험 환경
2. **PHY Abstraction 실험 실행** - 기본 설정으로 실험 수행
3. **실험 결과 확인** - TBLER, 처리량 분석
4. **환경 재현성 검증** - 동일한 결과 재현 확인

## 📋 1단계: 프로젝트 구조 생성 (10분)

### 디렉토리 구조 만들기

```bash
mkdir sionna-experiments
cd sionna-experiments

# 프로젝트 구조 생성
mkdir -p configs scripts results
touch Dockerfile README.md .gitignore
```

**최종 구조:**
```
sionna-experiments/
├── Dockerfile          # 실험 환경 정의
├── README.md           # 재현 가이드
├── .gitignore          # Git 제외 파일
├── configs/            # 실험 설정 파일
│   ├── baseline.yaml   # 기본 실험 설정
│   └── extras.yaml     # 확장 실험 설정
├── scripts/            # 실험 스크립트
│   └── run_phy_abs.py  # PHY Abstraction 실험
└── results/            # 실험 결과 (Git 제외)
```

## 🐳 2단계: Docker 환경 설정 (5분)

### Dockerfile 작성

```dockerfile
FROM python:3.10-slim
WORKDIR /app

# Sionna 및 필수 패키지 설치
RUN pip install sionna tensorflow numpy matplotlib pyyaml

# 소스 코드 복사
COPY configs/ ./configs/
COPY scripts/ ./scripts/
COPY README.md .

# 실행 권한 설정
RUN chmod +x scripts/*.py

# 결과 저장용 볼륨
VOLUME ["/app/results"]

# 기본 실행 명령
ENTRYPOINT ["python", "scripts/run_phy_abs.py"]
```

### .gitignore 설정

```gitignore
# 실험 결과 및 대용량 파일
results/
data/
raw/
*.log
*.h5
*.png
__pycache__/
*.pyc

# AWS 자격증명
.aws/
*.pem
docker-credential*
.env
*.token

# IDE 설정
.vscode/
.idea/
*.swp

# OS 파일
.DS_Store
Thumbs.db
```

## 🔬 3단계: Sionna PHY Abstraction 실험 스크립트 (15분)

### scripts/run_phy_abs.py 작성

```python
#!/usr/bin/env python3
import os
import sys
import yaml
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import tensorflow as tf

# 결과 디렉토리 생성
os.makedirs("/app/results", exist_ok=True)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

try:
    import sionna
    print(f"🔬 Sionna {sionna.__version__} 실험 시작")
except ImportError:
    print("❌ Sionna 설치 필요: pip install sionna")
    exit(1)

from sionna.sys import PHYAbstraction, InnerLoopLinkAdaptation
from sionna.phy import config
from sionna.phy.utils import db_to_lin

# Sionna 설정
config.precision = 'single'
config.seed = 42

def load_config(path):
    """실험 설정 파일 로드"""
    with open(path) as f:
        return yaml.safe_load(f)

def run_phy_experiment(config):
    """PHY Abstraction 실험 실행"""
    print(f"=== {config['experiment_id']} 실험 ===")
    
    # PHY Abstraction 및 Link Adaptation 초기화
    phy_abs = PHYAbstraction()
    illa = InnerLoopLinkAdaptation(phy_abs, config['bler_target'])
    
    # 실험 결과 저장용 리스트
    all_tbler = []
    all_throughput = []
    
    print(f"📊 {config['num_experiments']}회 실험 수행 중...")
    
    for exp in range(config['num_experiments']):
        # SINR 그리드 생성 (랜덤 채널 조건)
        sinr_db = tf.random.uniform(
            [1, 1, config['num_ut'], 1],
            config['sinr_range'][0], 
            config['sinr_range'][1]
        ) + tf.random.normal(
            [config['num_sym'], config['num_sc'], config['num_ut'], 1], 
            stddev=2.0
        )
        sinr = db_to_lin(sinr_db)
        
        # MCS 선택 (Link Adaptation)
        mcs_index = illa(sinr=sinr, mcs_table_index=config['mcs_table_index'])
        
        # PHY Abstraction 수행
        num_decoded_bits, harq_feedback, sinr_eff, bler, tbler = phy_abs(
            mcs_index, 
            sinr=sinr, 
            mcs_table_index=config['mcs_table_index'],
            mcs_category=config['mcs_category']
        )
        
        # 결과 수집
        all_tbler.append(tbler.numpy().mean())
        all_throughput.append(num_decoded_bits.numpy().sum())
        
        if (exp + 1) % 5 == 0:
            print(f"  진행률: {exp + 1}/{config['num_experiments']}")
    
    # 통계 계산
    results = {
        'tbler_mean': np.mean(all_tbler),
        'throughput_mean': np.mean(all_throughput),
        'tbler_std': np.std(all_tbler),
        'harq_nack_rate': 1 - np.mean(harq_feedback.numpy())
    }
    
    # 결과 저장
    np.savez(f"results/{config['experiment_id']}.npz", **results)
    
    # 결과 출력
    print(f"\n📈 실험 결과:")
    print(f"  TBLER: {results['tbler_mean']:.3f} ± {results['tbler_std']:.3f}")
    print(f"  처리량: {results['throughput_mean']/1024:.1f} kbit")
    print(f"  HARQ NACK 비율: {results['harq_nack_rate']:.3f}")
    
    # 결과 시각화
    create_plots(config, all_tbler, results)
    
    return results

def create_plots(config, all_tbler, results):
    """실험 결과 시각화"""
    plt.figure(figsize=(12, 4))
    
    # TBLER 분포 히스토그램
    plt.subplot(121)
    plt.hist(all_tbler, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
    plt.axvline(config['bler_target'], color='red', linestyle='--', 
                label=f'Target BLER: {config["bler_target"]}')
    plt.xlabel('TBLER')
    plt.ylabel('Frequency')
    plt.title('TBLER Distribution')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 요약 막대 그래프
    plt.subplot(122)
    metrics = ['TBLER', 'Thuroughput (kbit)', 'NACK rate']
    values = [
        results['tbler_mean'], 
        results['throughput_mean']/1024, 
        results['harq_nack_rate']
    ]
    
    bars = plt.bar(metrics, values, color=['lightcoral', 'lightgreen', 'lightsalmon'])
    plt.title(f'{config["experiment_id"]} Summary')
    plt.xticks(rotation=45)
    
    # 막대 위에 값 표시
    for bar, value in zip(bars, values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{value:.3f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(f"results/{config['experiment_id']}.png", 
                dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"📊 그래프 저장: results/{config['experiment_id']}.png")

if __name__ == "__main__":
    # 설정 파일 경로 (기본값: baseline.yaml)
    config_file = sys.argv[1] if len(sys.argv) > 1 else "configs/baseline.yaml"
    
    try:
        config = load_config(config_file)
        results = run_phy_experiment(config)
        print("\n🏆 실험 완료!")
        
    except FileNotFoundError:
        print(f"❌ 설정 파일을 찾을 수 없습니다: {config_file}")
        exit(1)
    except Exception as e:
        print(f"❌ 실험 중 오류 발생: {e}")
        exit(1)
```

## ⚙️ 4단계: 실험 설정 파일 생성 (5분)

### configs/baseline.yaml

```yaml
experiment_id: "phy-abs-baseline"
num_ut: 5              # 사용자 수
num_sym: 7             # OFDM 심볼 수
num_sc: 12             # 서브캐리어 수
bler_target: 0.1       # 목표 BLER
mcs_table_index: 1     # MCS 테이블 인덱스
mcs_category: 0        # 0: uplink, 1: downlink
sinr_range: [-5, 30]   # SINR 범위 (dB)
num_experiments: 10    # 실험 반복 횟수
```

### configs/extras.yaml

```yaml
experiment_id: "phy-abs-extras"
num_ut: 8              # 사용자 수 증가
num_sym: 14            # OFDM 심볼 수 증가
num_sc: 24             # 서브캐리어 수 증가
bler_target: 0.05      # 더 엄격한 목표 BLER
mcs_table_index: 2     # 다른 MCS 테이블
mcs_category: 1        # downlink
sinr_range: [-10, 35]  # 더 넓은 SINR 범위
num_experiments: 20    # 더 많은 실험 반복
```

## 📖 5단계: README.md 작성 (5분)

프로젝트 루트에 `README.md` 파일을 생성하여 실험 재현 방법을 문서화합니다:

```bash
cat > README.md << 'EOF'
# Sionna PHY Abstraction 실험 환경

## 📋 실험 재현 방법

### 1. 환경 준비

git clone [repository-url]

cd sionna-experiments

### 2. Docker 이미지 빌드

docker build -t sionna-phy .

### 3. 실험 실행

- 기본 실험 (baseline)

docker run --rm -v $(pwd)/results:/app/results sionna-phy configs/baseline.yaml

- 확장 실험 (extras)

docker run --rm -v $(pwd)/results:/app/results sionna-phy configs/extras.yaml

### 4. 결과 확인

- results/phy-abs-baseline.npz: 수치 결과
- results/phy-abs-baseline.png: 시각화 결과

## 🔬 실험 설정

- baseline: 기본 5G 링크 레벨 시뮬레이션
- extras: 확장된 다중 사용자 시나리오

## 📊 예상 결과

- TBLER: 목표값 근처 수렴
- 처리량: 채널 조건에 따른 적응적 변화
- HARQ 성능: 재전송 효율성 분석

EOF
```

## 🚀 6단계: 첫 실험 실행 (10분)

### Docker 이미지 빌드

```bash
docker build -t sionna-phy .
```

**예상 출력:**
```
[+] Building 45.2s (10/10) FINISHED
 => [1/6] FROM python:3.10-slim                    2.1s
 => [2/6] WORKDIR /app                             0.1s
 => [3/6] RUN pip install sionna tensorflow...    38.5s
 => [4/6] COPY configs/ ./configs/                 0.1s
 => [5/6] COPY scripts/ ./scripts/                 0.1s
 => [6/6] COPY README.md .                         0.1s
 => exporting to image                             4.2s
```

### 기본 실험 실행

```bash
docker run --rm -v $(pwd)/results:/app/results sionna-phy configs/baseline.yaml
```

**예상 출력:**
```
🔬 Sionna 1.2.1 실험 시작
=== phy-abs-baseline 실험 ===
📊 10회 실험 수행 중...
  진행률: 5/10
  진행률: 10/10

📈 실험 결과:
  TBLER: 0.098 ± 0.012
  처리량: 1247.3 kbit
  HARQ NACK 비율: 0.089

📊 그래프 저장: results/phy-abs-baseline.png
🏆 실험 완료!
```

### 결과 확인

```bash
ls -la results/
```

**예상 결과:**
```
-rw-r--r-- 1 user user  2048 Jan 11 15:30 phy-abs-baseline.npz
-rw-r--r-- 1 user user 45123 Jan 11 15:30 phy-abs-baseline.png
```

## ✅ 실습 체크리스트

| 단계 | 확인 사항 | 상태 |
|------|-----------|------|
| ✅ 프로젝트 구조 | 디렉토리 및 파일 생성 완료 | |
| ✅ Docker 빌드 | `sionna-phy` 이미지 생성 성공 | |
| ✅ 실험 실행 | baseline 실험 정상 완료 | |
| ✅ 결과 생성 | .npz, .png 파일 생성 확인 | |
| ✅ TBLER 수렴 | 목표 BLER(0.1) 근처 결과 | |

## 🛠️ 문제 해결

| 문제 | 해결 방법 |
|------|-----------|
| Docker 빌드 실패 | `docker system prune -f` 후 재시도 |
| Sionna 설치 오류 | Python 3.10 이미지 사용 확인 |
| 결과 파일 없음 | 볼륨 마운트 경로 확인 |
| TBLER 값 이상 | 설정 파일 파라미터 확인 |

## 🎉 완료!

**축하합니다!** 

이제 다음을 할 수 있습니다:

✅ Docker + Git + Sionna 통합 환경 구축  
✅ PHY Abstraction 실험 실행  
✅ 실험 결과 분석 및 시각화  
✅ 재현 가능한 실험 환경 생성

**다음 단계**: 이 환경을 Git으로 관리하고 ECR로 공유하는 협업 워크플로우를 학습합니다.

---

**[다음: 협업 워크플로우 구현 →](/60-integrated-workflow/collaboration-workflow/)**
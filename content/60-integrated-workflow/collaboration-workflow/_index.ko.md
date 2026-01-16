---
title: "협업 워크플로우 구현"
weight: 62
---

# 협업 워크플로우 구현

**Git + ECR을 통한 실험 공유 및 재현성 검증**

이전 단계에서 구축한 Sionna 실험 환경을 이제 Git으로 버전 관리하고, ECR을 통해 팀과 공유하는 완전한 협업 워크플로우를 구현해봅니다. 실험 변경사항 추적부터 팀원 간 결과 재현까지 전체 과정을 실습합니다.

## 🎯 실습 목표

1. **Git 버전 관리** - 실험 변경사항 체계적 추적
2. **ECR 이미지 공유** - 실험 환경 팀 공유
3. **협업 재현성 검증** - 팀원 간 동일 결과 확인
4. **버전별 결과 비교** - 실험 변화에 따른 성능 분석

## 📋 1단계: Git 저장소 초기화 (10분)

### Git 저장소 생성

```bash
cd sionna-experiments

# Git 저장소 초기화
git init
git config user.name "(Your Name)"
git config user.email "your@e-mail_address.com"
```

### 초기 커밋

```bash
# 모든 파일 추가 (.gitignore 적용됨)
git add .

# 초기 커밋
git commit -m "init: Sionna PHY Abstraction 실험 환경 구축

- Docker 기반 Sionna 실험 환경
- PHY Abstraction baseline 설정
- 재현 가능한 실험 스크립트 구성"
```

### 커밋 확인

```bash
git log --oneline
```

**예상 출력:**
```
a1b2c3d (HEAD -> main) init: Sionna PHY Abstraction 실험 환경 구축
```

## 🔄 2단계: 실험 변경사항 추적 (15분)

### extras 실험 설정 수정

기존 `configs/extras.yaml`을 더 도전적인 설정으로 수정:

```yaml
experiment_id: "phy-abs-extras-v2"
num_ut: 12             # 사용자 수 대폭 증가
num_sym: 14            # OFDM 심볼 수
num_sc: 48             # 서브캐리어 수 대폭 증가
bler_target: 0.01      # 매우 엄격한 목표 BLER
mcs_table_index: 2     # 고차 MCS 테이블
mcs_category: 1        # downlink
sinr_range: [-15, 40]  # 매우 넓은 SINR 범위
num_experiments: 30    # 더 많은 실험 반복
```

### 실험 실행 및 결과 확인

```bash
# 새로운 설정으로 실험 실행
docker run --rm -v $(pwd)/results:/app/results sionna-phy configs/extras.yaml
```

**예상 출력:**
```
🔬 Sionna 1.2.1 실험 시작
=== phy-abs-extras-v2 실험 ===
📊 30회 실험 수행 중...
  진행률: 5/30
  진행률: 10/30
  진행률: 15/30
  진행률: 20/30
  진행률: 25/30
  진행률: 30/30

📈 실험 결과:
  TBLER: 0.009 ± 0.003
  처리량: 2847.6 kbit
  HARQ NACK 비율: 0.008

📊 그래프 저장: results/phy-abs-extras-v2.png
🏆 실험 완료!
```

### 변경사항 커밋

```bash
# 변경된 파일 확인
git status

# 설정 파일 변경사항 확인
git diff configs/extras.yaml

# 변경사항 커밋
git add configs/extras.yaml
git commit -m "feat: [extras-v2] 대규모 다중사용자 시나리오 추가

- 사용자 수: 8 → 12명
- 서브캐리어: 24 → 48개  
- 목표 BLER: 0.05 → 0.01 (더 엄격)
- 실험 횟수: 20 → 30회
- 예상 처리량 향상 및 HARQ 성능 개선"
```

### README 업데이트

README.md에 다음 내용과 같이 새로운 실험 설정을 추가:

```markdown
# Sionna PHY Abstraction 실험 환경

## 📋 실험 재현 방법

### 1. 환경 준비
```bash
git clone <repository-url>
cd sionna-experiments
git checkout <commit-hash>  # 특정 버전 재현 시
```

### 2. Docker 이미지 빌드
```bash
docker build -t sionna-phy .
```

### 3. 실험 실행
```bash
# 기본 실험 (baseline)
docker run --rm -v $(pwd)/results:/app/results sionna-phy configs/baseline.yaml

# 확장 실험 v1 (extras)
docker run --rm -v $(pwd)/results:/app/results sionna-phy configs/extras.yaml
```

## 🔬 실험 설정 비교

| 설정 | baseline | extras-v2 |
|------|----------|-----------|
| 사용자 수 | 5 | 12 |
| 서브캐리어 | 12 | 48 |
| 목표 BLER | 0.1 | 0.01 |
| 실험 횟수 | 10 | 30 |
| 예상 처리량 | ~1.2 Mbit | ~2.8 Mbit |

## 📊 재현성 검증

동일한 커밋에서 실행 시 다음 결과 예상:
- baseline: TBLER ~0.098, 처리량 ~1247 kbit
- extras-v2: TBLER ~0.009, 처리량 ~2847 kbit
```

### README 변경사항 커밋

```bash
git add README.md
git commit -m "docs: extras-v2 실험 설정 및 재현 가이드 추가"
```

## ☁️ 3단계: ECR 이미지 공유 (15분)

### ECR 저장소 생성

```bash
# ECR 저장소 생성
aws ecr create-repository \
    --repository-name sionna-experiments \
    --region ap-northeast-2
```

### Docker 이미지 태깅 및 푸시

```bash
# 계정 ID 가져오기
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# ECR 로그인
aws ecr get-login-password --region ap-northeast-2 | \
    docker login --username AWS --password-stdin \
    $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com

# 현재 커밋 해시 가져오기
COMMIT=$(git rev-parse --short HEAD)
echo "현재 커밋: $COMMIT"

# 이미지 태깅
docker tag sionna-phy:latest \
    $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:$COMMIT

docker tag sionna-phy:latest \
    $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:latest

# ECR에 푸시
docker push $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:$COMMIT
docker push $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:latest
```

**예상 출력:**
```
The push refers to repository [123456789012.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments]
a1b2c3d: Pushed
latest: digest: sha256:abc123... size: 1234
```

### 이미지 공유 정보 기록

```bash
# 공유 정보를 README에 추가
cat >> README.md << EOF

## 🐳 Docker 이미지 공유

### ECR에서 이미지 가져오기
\`\`\`bash
# ECR 로그인
aws ecr get-login-password --region ap-northeast-2 | \\
    docker login --username AWS --password-stdin \\
    $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com

# 특정 버전 가져오기
docker pull $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:$COMMIT

# 최신 버전 가져오기
docker pull $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:latest
\`\`\`

### 버전별 실행
\`\`\`bash
# 특정 커밋 버전으로 실행
docker run --rm -v \$(pwd)/results:/app/results \\
    $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:$COMMIT \\
    configs/baseline.yaml
\`\`\`
EOF

# 변경사항 커밋
git add README.md
git commit -m "docs: ECR 이미지 공유 가이드 추가

- 커밋별 이미지 태깅 전략
- ECR 이미지 pull/run 명령어
- 버전별 실험 재현 방법"
```

## 🤝 4단계: 협업 재현성 검증 (20분)

### 이전 버전으로 롤백 테스트

```bash
# 커밋 히스토리 확인
git log --oneline

# 첫 번째 커밋으로 롤백
FIRST_COMMIT=$(git rev-list --max-parents=0 HEAD)
git checkout $FIRST_COMMIT

# 이전 버전으로 이미지 빌드
docker build -t sionna-phy-old .

# 이전 설정으로 실험 실행
mkdir -p results-old
docker run --rm -v $(pwd)/results-old:/app/results sionna-phy-old configs/baseline.yaml
```

### 결과 비교

```bash
# 최신 버전으로 복귀
git checkout main

# 결과 파일 비교
echo "=== 이전 버전 결과 ==="
ls -la results-old/

echo "=== 현재 버전 결과 ==="
ls -la results/

# Python으로 수치 결과 비교
pip install numpy
python3 << EOF
import numpy as np

# 이전 버전 결과 로드
try:
    old_data = np.load('results-old/phy-abs-baseline.npz')
    print("이전 버전 TBLER:", old_data['tbler_mean'])
    print("이전 버전 처리량:", old_data['throughput_mean']/1024, "kbit")
except:
    print("이전 버전 결과 없음")

# 현재 버전 결과 로드
try:
    new_data = np.load('results/phy-abs-baseline.npz')
    print("현재 버전 TBLER:", new_data['tbler_mean'])
    print("현재 버전 처리량:", new_data['throughput_mean']/1024, "kbit")
    
    # extras-v2 결과
    extras_data = np.load('results/phy-abs-extras-v2.npz')
    print("extras-v2 TBLER:", extras_data['tbler_mean'])
    print("extras-v2 처리량:", extras_data['throughput_mean']/1024, "kbit")
except:
    print("현재 버전 결과 없음")
EOF
```

### 팀 협업 시뮬레이션

```bash
# 새로운 디렉토리에서 팀원 관점 시뮬레이션
cd ..
mkdir team-member-test
cd team-member-test

# ECR에서 이미지 가져오기
aws ecr get-login-password --region ap-northeast-2 | \
    docker login --username AWS --password-stdin \
    $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com

docker pull $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:latest

# Git 저장소 클론 (실제로는 GitHub/GitLab에서)
cp -r ../sionna-experiments .
cd sionna-experiments

# 팀원이 동일한 실험 실행
mkdir -p team-results
docker run --rm -v $(pwd)/team-results:/app/results \
    $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:latest \
    configs/baseline.yaml

echo "=== 팀원 재현 결과 ==="
ls -la team-results/
```

## 📊 (고급) 5단계: 버전별 성능 분석 (10분)

### 성능 비교 스크립트 생성

다음 샘플 비교 스크립트를 실행해봅니다. Docker 환경 활용을 하는 것을 추천합니다.

```bash
cd ../sionna-experiments

# 성능 분석 스크립트 생성
cat > scripts/compare_results.py << 'EOF'
#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

def compare_experiments():
    """실험 결과 비교 분석"""
    results_files = glob.glob('results/*.npz')
    
    if not results_files:
        print("❌ 결과 파일이 없습니다.")
        return
    
    experiments = {}
    
    # 모든 결과 파일 로드
    for file in results_files:
        exp_name = os.path.basename(file).replace('.npz', '')
        data = np.load(file)
        experiments[exp_name] = {
            'tbler': data['tbler_mean'],
            'throughput': data['throughput_mean'] / 1024,  # kbit
            'tbler_std': data['tbler_std'],
            'nack_rate': data['harq_nack_rate']
        }
    
    # 결과 출력
    print("📊 실험 결과 비교")
    print("=" * 60)
    print(f"{'실험명':<20} {'TBLER':<10} {'처리량(kbit)':<12} {'NACK율':<8}")
    print("-" * 60)
    
    for exp_name, data in experiments.items():
        print(f"{exp_name:<20} {data['tbler']:.3f}     {data['throughput']:.1f}        {data['nack_rate']:.3f}")
    
    # 시각화
    if len(experiments) > 1:
        create_comparison_plot(experiments)

def create_comparison_plot(experiments):
    """비교 시각화"""
    exp_names = list(experiments.keys())
    tbler_values = [experiments[name]['tbler'] for name in exp_names]
    throughput_values = [experiments[name]['throughput'] for name in exp_names]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # TBLER 비교
    bars1 = ax1.bar(exp_names, tbler_values, color='lightcoral', alpha=0.7)
    ax1.set_ylabel('TBLER')
    ax1.set_title('TBLER Comparison per experiment')
    ax1.tick_params(axis='x', rotation=45)
    
    # 막대 위에 값 표시
    for bar, value in zip(bars1, tbler_values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
                f'{value:.3f}', ha='center', va='bottom')
    
    # 처리량 비교
    bars2 = ax2.bar(exp_names, throughput_values, color='lightgreen', alpha=0.7)
    ax2.set_ylabel('Throughput (kbit)')
    ax2.set_title('Comparing Throughput per Experiment')
    ax2.tick_params(axis='x', rotation=45)
    
    # 막대 위에 값 표시
    for bar, value in zip(bars2, throughput_values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                f'{value:.1f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('results/experiment_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print("📊 비교 그래프 저장: results/experiment_comparison.png")

if __name__ == "__main__":
    compare_experiments()
EOF

chmod +x scripts/compare_results.py
```

### 성능 비교 실행

```bash
python scripts/compare_results.py
```

**예상 출력:**
```
📊 실험 결과 비교
============================================================
실험명                TBLER      처리량(kbit)   NACK율  
------------------------------------------------------------
phy-abs-baseline     0.098      1247.3       0.089
phy-abs-extras-v2    0.009      2847.6       0.008
📊 비교 그래프 저장: results/experiment_comparison.png
```

## ✅ 실습 체크리스트

| 단계 | 확인 사항 | 상태 |
|------|-----------|------|
| ✅ Git 초기화 | 저장소 생성 및 초기 커밋 | |
| ✅ 실험 변경 추적 | extras-v2 설정 변경 및 커밋 | |
| ✅ ECR 이미지 공유 | 커밋별 태깅 및 푸시 성공 | |
| ✅ 재현성 검증 | 이전 버전 롤백 및 실행 | |
| ✅ 팀 협업 테스트 | ECR 이미지로 동일 결과 재현 | |
| ✅ 성능 비교 | 버전별 결과 분석 완료 | |

## 🎯 핵심 워크플로우 요약

### 1. 개발 워크플로우
```bash
# 실험 설정 변경
vim configs/new_experiment.yaml

# 실험 실행 및 검증
docker run --rm -v $(pwd)/results:/app/results sionna-phy configs/new_experiment.yaml

# 변경사항 커밋
git add configs/new_experiment.yaml
git commit -m "feat: 새로운 실험 설정 추가"

# ECR에 푸시
COMMIT=$(git rev-parse --short HEAD)
docker tag sionna-phy:latest $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:$COMMIT
docker push $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:$COMMIT
```

### 2. 협업 워크플로우
```bash
# 팀원: 저장소 클론
git clone <repository-url>
cd sionna-experiments

# 특정 버전 체크아웃
git checkout <commit-hash>

# ECR에서 해당 버전 이미지 가져오기
docker pull $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:<commit-hash>

# 동일한 실험 재현
docker run --rm -v $(pwd)/results:/app/results \
    $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-experiments:<commit-hash> \
    configs/baseline.yaml
```

## 🛠️ 문제 해결

| 문제 | 해결 방법 |
|------|-----------|
| Git 커밋 실패 | 사용자 정보 설정 확인 |
| ECR 푸시 실패 | AWS 자격증명 및 권한 확인 |
| 결과 불일치 | Sionna seed 설정 확인 |
| 이미지 태그 오류 | 커밋 해시 정확성 확인 |

## 🎉 완료!

**축하합니다!** 

완전한 협업 워크플로우를 구현했습니다:

✅ Git을 통한 실험 변경사항 체계적 추적  
✅ ECR을 통한 실험 환경 이미지 공유  
✅ 커밋별 버전 관리 및 재현성 보장  
✅ 팀 협업을 위한 표준화된 워크플로우  
✅ 실험 결과 비교 및 성능 분석

**핵심 가치**: 이제 어떤 팀원이든 특정 커밋의 실험을 100% 동일하게 재현할 수 있습니다!

---

**[워크샵 요약으로 계속 →](/80-summary/)**
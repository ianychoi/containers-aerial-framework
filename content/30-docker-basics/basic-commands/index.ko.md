---
title: "기본 명령어와 실습"
weight: 32
---

# 기본 명령어와 실습

Docker의 기본 명령어를 실습을 통해 학습하고, 컨테이너 생명주기 관리 방법을 익혀보겠습니다.

## 🛠️ Docker 기본 명령어 실습

### 실습 환경 확인

```bash
# Docker 버전 확인
docker --version

# Docker 시스템 정보 확인
docker info

# Docker 디스크 사용량 확인
docker system df
```

### 실습 1: Hello World 컨테이너

가장 기본적인 Docker 명령어를 실행해봅니다.

```bash
# Hello World 컨테이너 실행
docker run hello-world
```

**예상 출력:**
```
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
...
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

**동작 과정:**
```
docker run hello-world
        │
        ▼
┌─────────────────────────────────┐
│ 1. 로컬에서 이미지 검색         │
│    → 없음                       │
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ 2. Docker Hub에서 이미지 다운로드│
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ 3. 이미지로 컨테이너 생성       │
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ 4. 컨테이너 실행 (메시지 출력)  │
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ 5. 컨테이너 종료                │
└─────────────────────────────────┘
```

### 실습 2: Ubuntu 컨테이너 대화형 실행

```bash
# Ubuntu 컨테이너를 대화형 모드로 실행
docker run -it ubuntu:22.04 /bin/bash
```

**컨테이너 내부에서 실행:**
```bash
# 시스템 정보 확인
cat /etc/os-release

# 패키지 업데이트
apt update

# 간단한 패키지 설치
apt install -y curl

# 컨테이너 종료
exit
```

**명령어 옵션 설명:**

| 옵션 | 의미 |
|------|------|
| `-i` | Interactive (표준 입력 유지) |
| `-t` | TTY (터미널 할당) |
| `-it` | 대화형 터미널 모드 |

### 실습 3: 컨테이너 생명주기 관리

```bash
# 백그라운드에서 nginx 컨테이너 실행
docker run -d --name my-nginx -p 5000:80 nginx

# 실행 중인 컨테이너 확인
docker ps

# 모든 컨테이너 확인 (중지된 것 포함)
docker ps -a

# 컨테이너 로그 확인
docker logs my-nginx

# 실시간 로그 스트리밍
docker logs -f my-nginx

# 실행 중인 컨테이너에 접속
docker exec -it my-nginx /bin/bash

# 컨테이너 중지
docker stop my-nginx

# 컨테이너 시작
docker start my-nginx

# 컨테이너 재시작
docker restart my-nginx

# 컨테이너 삭제 (중지 후)
docker stop my-nginx
docker rm my-nginx

# 강제 삭제
docker rm -f my-nginx
```

**명령어 옵션 설명:**

| 옵션 | 의미 |
|------|------|
| `-d` | Detached (백그라운드 실행) |
| `--name` | 컨테이너 이름 지정 |
| `-p 8080:80` | 호스트:컨테이너 포트 매핑 |
| `-f` | Follow (실시간 출력) |

### 실습 4: 이미지 관리

```bash
# Docker Hub에서 이미지 검색
docker search python

# 이미지 다운로드
docker pull python:3.11-slim

# 로컬 이미지 목록 확인
docker images

# 이미지 상세 정보 확인
docker inspect python:3.11-slim

# 이미지 삭제
docker rmi python:3.11-slim

# 사용하지 않는 이미지 정리
docker image prune

# 모든 미사용 리소스 정리
docker system prune -a
```

## 🐍 Python 환경 구성 실습

### 실습 5: Python 개발 환경

Python 컨테이너를 활용한 개발 환경을 구성해봅시다.

```bash
# Python 3.11 컨테이너 실행
docker run -it python:3.11 python

# Python 인터프리터에서 실행
>>> import sys
>>> print(f"Python version: {sys.version}")
>>> print("Hello from containerized Python!")
>>> exit()
```

### 실습 6: 패키지 설치 및 테스트

```bash
# Python 컨테이너에서 패키지 설치 테스트
docker run -it python:3.11 /bin/bash

# 컨테이너 내부에서 실행
pip install numpy matplotlib
python -c "import numpy as np; print(f'NumPy version: {np.__version__}')"
python -c "import matplotlib; print(f'Matplotlib version: {matplotlib.__version__}')"
exit
```

### 실습 7: 간단한 Python 스크립트 실행

**1. 작업 디렉터리 생성:**

```bash
mkdir -p ~/docker-lab/python-demo
cd ~/docker-lab/python-demo
```

**2. Python 스크립트 작성:**

```bash
cat > hello.py << 'EOF'
import datetime

def main():
    now = datetime.datetime.now()
    print(f"Hello from Docker! Current time: {now}")
    
    # 간단한 계산
    numbers = [1, 2, 3, 4, 5]
    total = sum(numbers)
    print(f"Sum of {numbers} = {total}")

if __name__ == "__main__":
    main()
EOF
```

**3. 컨테이너에서 스크립트 실행:**

```bash
# 현재 디렉터리를 컨테이너에 마운트하여 스크립트 실행
docker run --rm -v $(pwd):/app -w /app python:3.11 python hello.py
```

## 📊 matplotlib 설치 실습

### 실습 8: 시각화 환경 구성

matplotlib을 사용한 시각화 환경을 구성해봅시다.

**1. 시각화 스크립트 작성:**

```bash
cat > plot_demo.py << 'EOF'
import matplotlib
matplotlib.use('Agg')  # GUI 없는 환경에서 사용
import matplotlib.pyplot as plt
import numpy as np

# 데이터 생성
x = np.linspace(0, 10, 100)
y = np.sin(x)

# 플롯 생성
plt.figure(figsize=(10, 6))
plt.plot(x, y, 'b-', linewidth=2, label='sin(x)')
plt.xlabel('x')
plt.ylabel('y')
plt.title('Sine Wave')
plt.legend()
plt.grid(True)

# 파일로 저장
plt.savefig('/app/sine_wave.png', dpi=300, bbox_inches='tight')
print("Plot saved as sine_wave.png")
EOF
```

**2. 필요한 패키지와 함께 실행:**

```bash
# matplotlib 설치 후 스크립트 실행
docker run --rm -v $(pwd):/app -w /app python:3.11 bash -c "
pip install matplotlib numpy && 
python plot_demo.py
"

# 생성된 파일 확인
ls -la sine_wave.png
```

## 🔧 실습 과제

### 과제 1: 웹 서버 컨테이너 실행

다음 요구사항을 만족하는 웹 서버를 실행하세요:

1. nginx 이미지 사용
2. 포트 8080으로 접근 가능
3. 컨테이너 이름은 "my-webserver"
4. 백그라운드에서 실행

**해답:**
```bash
docker run -d --name my-webserver -p 8080:80 nginx
```

### 과제 2: 데이터 분석 스크립트 실행

pandas를 사용하여 간단한 데이터 분석을 수행하는 스크립트를 작성하고 실행하세요.

**스크립트 예시:**
```python
import pandas as pd
import numpy as np

# 샘플 데이터 생성
data = {
    'name': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'age': [25, 30, 35, 28],
    'score': [85, 92, 78, 88]
}

df = pd.DataFrame(data)
print("Data:")
print(df)
print(f"\nAverage age: {df['age'].mean()}")
print(f"Average score: {df['score'].mean()}")
```

## 📝 정리

### 학습 내용 체크리스트

✅ **기본 명령어**
- `docker run`, `docker ps`, `docker logs`
- `docker exec`, `docker stop`, `docker rm`
- `docker images`, `docker pull`, `docker rmi`

✅ **컨테이너 생명주기**
- 컨테이너 생성, 시작, 중지, 삭제
- 대화형 모드와 백그라운드 실행
- 포트 매핑과 볼륨 마운트

✅ **Python 환경 활용**
- Python 베이스 이미지 사용법
- 패키지 설치 및 스크립트 실행
- 개발 환경 구성

### 유용한 명령어 모음

```bash
# 컨테이너 관리
docker ps -a                    # 모든 컨테이너 확인
docker rm $(docker ps -aq)      # 모든 컨테이너 삭제
docker logs -f <container>      # 실시간 로그

# 이미지 관리
docker images                   # 이미지 목록
docker rmi $(docker images -q)  # 모든 이미지 삭제
docker image prune -a           # 미사용 이미지 정리

# 시스템 관리
docker system df                # 디스크 사용량
docker system prune -a          # 전체 정리

# 디버깅
docker inspect <container>      # 상세 정보
docker stats                    # 리소스 사용량
docker top <container>          # 프로세스 목록
```

## 🚀 다음 단계

기본 명령어를 익혔으니 이제 Dockerfile 작성, Volume 관리, Multi-stage 빌드 등 고급 기능을 학습해보겠습니다.

---

**[실전 활용과 최적화로 계속 →](/30-docker-basics/practical-application/)**
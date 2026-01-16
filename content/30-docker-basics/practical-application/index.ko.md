---
title: "실전 활용과 최적화"
weight: 33
---

# 실전 활용과 최적화

Docker의 실전 활용 기능인 Dockerfile 작성, Volume 관리, Multi-stage 빌드를 학습하여 효율적인 컨테이너 환경을 구축해보겠습니다.

## 📝 Dockerfile 작성

### Dockerfile 기본 구조

```dockerfile
# 베이스 이미지 지정
FROM python:3.11-slim

# 메타데이터 추가
LABEL maintainer="your-email@example.com"
LABEL description="Python development environment"

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV APP_HOME=/app

# 작업 디렉터리 설정
WORKDIR $APP_HOME

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 실행 명령어
CMD ["python", "app.py"]
```

### 주요 Dockerfile 명령어

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `FROM` | 베이스 이미지 지정 | `FROM python:3.11-slim` |
| `WORKDIR` | 작업 디렉터리 설정 | `WORKDIR /app` |
| `COPY` | 파일/디렉터리 복사 | `COPY . /app` |
| `ADD` | 파일 복사 (URL, tar 지원) | `ADD app.tar.gz /app` |
| `RUN` | 빌드 시 명령어 실행 | `RUN pip install flask` |
| `ENV` | 환경 변수 설정 | `ENV PORT=8000` |
| `EXPOSE` | 포트 문서화 | `EXPOSE 8000` |
| `CMD` | 컨테이너 시작 명령어 | `CMD ["python", "app.py"]` |
| `ENTRYPOINT` | 고정 실행 명령어 | `ENTRYPOINT ["python"]` |

### 실습 1: Python 웹 애플리케이션 컨테이너화

**1. 프로젝트 디렉터리 구조 생성:**

```bash
mkdir -p ~/docker-lab/python-app
cd ~/docker-lab/python-app
```

**2. 간단한 Flask 애플리케이션 작성:**

```bash
cat > app.py << 'EOF'
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({
        "message": "Hello from Docker!",
        "hostname": os.uname().nodename
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF
```

**3. requirements.txt 작성:**

```bash
cat > requirements.txt << 'EOF'
flask==3.0.0
EOF
```

**4. Dockerfile 작성:**

```bash
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# 의존성 먼저 복사 (캐시 활용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
EOF
```

**5. 이미지 빌드 및 실행:**

```bash
# 이미지 빌드
docker build -t my-flask-app:v1 .

# 빌드 과정 확인
docker images my-flask-app

# 컨테이너 실행
docker run -d --name flask-app -p 5000:5000 my-flask-app:v1

# 애플리케이션 테스트
curl http://localhost:5000
curl http://localhost:5000/health

# 로그 확인
docker logs flask-app

# 정리
docker rm -f flask-app
```

## 💾 Docker Volume

### Volume이 필요한 이유

```
┌─────────────────────────────────────────────────────────┐
│                    컨테이너 삭제 시                       │
│                                                         │
│  ┌─────────────────┐          ┌─────────────────┐      │
│  │    Container    │   삭제   │     데이터      │      │
│  │                 │ ───────▶ │     손실!       │      │
│  │  (Container     │          │                 │      │
│  │   Layer R/W)    │          │                 │      │
│  └─────────────────┘          └─────────────────┘      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    Volume 사용 시                        │
│                                                         │
│  ┌─────────────────┐          ┌─────────────────┐      │
│  │    Container    │   삭제   │    Container    │      │
│  │                 │ ───────▶ │     삭제됨      │      │
│  └────────┬────────┘          └─────────────────┘      │
│           │                                             │
│           ▼                                             │
│  ┌─────────────────┐          ┌─────────────────┐      │
│  │     Volume      │ ───────▶ │   데이터 유지!   │      │
│  │  (호스트 저장소) │          │                 │      │
│  └─────────────────┘          └─────────────────┘      │
└─────────────────────────────────────────────────────────┘
```

### Volume 유형

| 유형 | 설명 | 사용 사례 |
|------|------|----------|
| **Named Volume** | Docker가 관리하는 볼륨 | 데이터 영속성 |
| **Bind Mount** | 호스트 경로 직접 마운트 | 개발 환경 |
| **tmpfs Mount** | 메모리에 저장 | 임시 데이터 |

### 실습 2: Volume 사용하기

**Named Volume 사용:**

```bash
# 볼륨 생성
docker volume create my-data

# 볼륨 목록 확인
docker volume ls

# 볼륨 상세 정보
docker volume inspect my-data

# 볼륨과 함께 컨테이너 실행
docker run -d \
  --name db-container \
  -v my-data:/var/lib/data \
  ubuntu:22.04 \
  sleep infinity

# 컨테이너에서 데이터 생성
docker exec db-container bash -c "echo 'Hello Volume' > /var/lib/data/test.txt"

# 데이터 확인
docker exec db-container cat /var/lib/data/test.txt

# 컨테이너 삭제
docker rm -f db-container

# 새 컨테이너에서 데이터 확인 (데이터 유지됨!)
docker run --rm \
  -v my-data:/var/lib/data \
  ubuntu:22.04 \
  cat /var/lib/data/test.txt

# 볼륨 삭제
docker volume rm my-data
```

**Bind Mount 사용 (개발 환경):**

```bash
# 작업 디렉터리 생성
mkdir -p ~/docker-lab/bind-mount-demo
cd ~/docker-lab/bind-mount-demo

# 테스트 파일 생성
echo "Hello from host!" > hello.txt

# Bind Mount로 컨테이너 실행
docker run --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  ubuntu:22.04 \
  cat hello.txt

# 실시간 파일 동기화 확인
docker run -it --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  ubuntu:22.04 \
  /bin/bash

# 컨테이너 내부에서
# ls -la
# echo "Modified in container" >> hello.txt
# exit

# 호스트에서 변경사항 확인
cat hello.txt
```

## 🚀 Multi-stage 빌드

### Multi-stage 빌드의 이점

```
┌─────────────────────────────────────────────────────────────────┐
│                     일반 빌드                                    │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 최종 이미지                                              │   │
│  │ - 빌드 도구 포함                                         │   │
│  │ - 소스 코드 포함                                         │   │
│  │ - 불필요한 파일들                                        │   │
│  │                                                         │   │
│  │ 크기: 수백 MB ~ 수 GB                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   Multi-stage 빌드                               │
│                                                                 │
│  Stage 1: Builder                  Stage 2: Final              │
│  ┌────────────────────┐           ┌────────────────────┐       │
│  │ - 빌드 도구        │  COPY     │ - 실행 환경만      │       │
│  │ - 소스 코드        │ ────────▶ │ - 빌드 결과물만    │       │
│  │ - 컴파일 수행      │  필요한   │                    │       │
│  │                    │  것만     │ 크기: 수십 MB      │       │
│  │ 크기: 수백 MB      │           │                    │       │
│  └────────────────────┘           └────────────────────┘       │
│         (버려짐)                       (최종 이미지)             │
└─────────────────────────────────────────────────────────────────┘
```

### 실습 3: Multi-stage 빌드

```bash
mkdir -p ~/docker-lab/multistage
cd ~/docker-lab/multistage
```

**Go 애플리케이션 작성:**

```bash
cat > main.go << 'EOF'
package main

import (
    "fmt"
    "net/http"
)

func main() {
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "Hello from Multi-stage Build!")
    })
    fmt.Println("Server starting on :8080")
    http.ListenAndServe(":8080", nil)
}
EOF
```

**일반 Dockerfile vs Multi-stage Dockerfile 비교:**

```bash
# 일반 Dockerfile
cat > Dockerfile.single << 'EOF'
FROM golang:1.21

WORKDIR /app
COPY main.go .
RUN go build -o server main.go

EXPOSE 8080
CMD ["./server"]
EOF

# Multi-stage Dockerfile
cat > Dockerfile.multi << 'EOF'
# Stage 1: 빌드 환경
FROM golang:1.21 AS builder

WORKDIR /app
COPY main.go .
RUN CGO_ENABLED=0 GOOS=linux go build -o server main.go

# Stage 2: 실행 환경
FROM alpine:latest

WORKDIR /app
COPY --from=builder /app/server .

EXPOSE 8080
CMD ["./server"]
EOF
```

**이미지 크기 비교:**

```bash
# 일반 빌드
docker build -f Dockerfile.single -t go-app:single .

# Multi-stage 빌드
docker build -f Dockerfile.multi -t go-app:multi .

# 크기 비교
docker images | grep go-app
```

**예상 결과:**
```
go-app    single    xxx    xxx    ~800MB
go-app    multi     xxx    xxx    ~15MB
```

## 🧪 실습 과제

### 과제 1: 데이터 분석 환경 구축

다음 요구사항을 만족하는 Dockerfile을 작성하세요:

**요구사항:**
- Python 3.11 베이스 이미지 사용
- numpy, pandas, matplotlib, seaborn 설치
- Jupyter Notebook 설치 및 설정
- 작업 디렉터리를 `/workspace`로 설정
- 포트 8888 노출

**해답 예시:**

```dockerfile
FROM python:3.11-slim

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉터리 설정
WORKDIR /workspace

# Python 패키지 설치
RUN pip install --no-cache-dir \
    numpy \
    pandas \
    matplotlib \
    seaborn \
    jupyter

# Jupyter 설정
RUN jupyter notebook --generate-config && \
    echo "c.NotebookApp.ip = '0.0.0.0'" >> ~/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.allow_root = True" >> ~/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.open_browser = False" >> ~/.jupyter/jupyter_notebook_config.py

# 포트 노출
EXPOSE 8888

# 시작 명령어
CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--allow-root"]
```

### 과제 2: 개발-프로덕션 환경 분리

개발 환경과 프로덕션 환경을 위한 두 가지 Dockerfile을 작성하세요:

**개발 환경 (Dockerfile.dev):**
```dockerfile
FROM python:3.11

WORKDIR /app

# 개발 도구 설치
RUN pip install --no-cache-dir \
    flask \
    flask-debugtoolbar \
    pytest \
    black \
    flake8

# 개발용 설정
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
```

**프로덕션 환경 (Dockerfile.prod):**
```dockerfile
# Stage 1: 빌드 환경
FROM python:3.11 AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: 실행 환경
FROM python:3.11-slim

# 비루트 사용자 생성
RUN useradd --create-home --shell /bin/bash app

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY app.py .
RUN chown -R app:app /app

USER app

EXPOSE 5000

CMD ["python", "app.py"]
```

## 📝 정리

### 학습 내용 체크리스트

✅ **Dockerfile 작성**
- 기본 구조와 명령어 이해
- 이미지 빌드 과정 최적화
- 레이어 캐싱 활용

✅ **Volume 관리**
- Named Volume과 Bind Mount 차이점
- 데이터 영속성 보장 방법
- 개발 환경에서의 활용법

✅ **Multi-stage 빌드**
- 이미지 크기 최적화 기법
- 빌드 환경과 실행 환경 분리
- 보안 강화 방법

### 모범 사례

```dockerfile
# 1. 적절한 베이스 이미지 선택
FROM python:3.11-slim  # slim 버전 사용

# 2. 레이어 캐싱 최적화
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .  # 코드는 마지막에 복사

# 3. 불필요한 파일 제거
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 4. 비루트 사용자 사용
RUN useradd --create-home app
USER app

# 5. 명시적 포트 노출
EXPOSE 8000
```

## 🚀 다음 단계

Docker 기초를 완전히 마스터했습니다! 이제 NVIDIA Sionna 라이브러리를 활용한 전문적인 통신 시뮬레이션 환경을 컨테이너로 구성하는 방법을 학습해보겠습니다.

---

**[Sionna 환경 구축으로 계속 →](/40-container-environment/)**
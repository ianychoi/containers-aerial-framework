---
title: "실험 환경 버전 만들기"
weight: 43
---

# 실험 환경 버전 만들기

**baseline에 패키지 추가해서 extras 만들기**

이전에 만든 이미지에 패키지 몇 개만 추가해서 새 버전을 만듭니다. 그리고 Amazon ECR에 올려서 팀원과 공유합니다.

## 🎯 모듈 구성

1. **baseline 태그 붙이기** - 이름만 바꾸기
2. **extras 버전 만들기** - 패키지 3개 추가
3. **두 버전 비교** - 뭐가 다른지 확인
4. **ECR 업로드** - 클라우드에 저장
5. **다운로드 테스트** - 진짜 공유되나 확인

## 📋 1단계: 이름표 붙이기

### 현재 이미지 확인

```bash
docker images | grep sionna
```

**결과:**
```
sionna-simple   latest   abc123   1.2GB
```

### baseline 태그 추가 (복사 아님!)

```bash
docker tag sionna-simple:latest sionna-simple:baseline
docker images | grep sionna
```

**결과:**
```
sionna-simple   baseline   abc123   1.2GB
sionna-simple   latest     abc123   1.2GB
```

**설명**: 같은 이미지에 이름표 2개 붙인 것!

## 🔨 2단계: extras 버전 만들기

### Dockerfile.extras 만들기

**새 파일: `Dockerfile.extras`**

```dockerfile
FROM python:3.10-slim
WORKDIR /app

# baseline 패키지 + 추가 3개!
RUN pip install sionna==1.2.1 tensorflow numpy matplotlib \
    pandas plotly tqdm

COPY simple_awgn.py .
CMD ["python", "simple_awgn.py"]
```

**추가된 패키지:**
- `pandas`: 데이터 분석
- `plotly`: 예쁜 그래프
- `tqdm`: 진행바

### 빌드하기

```bash
docker build -f Dockerfile.extras -t sionna-simple:extras .
```

**3분 대기...**

### 확인

```bash
docker images | grep sionna
```

**결과:**
```
sionna-simple   extras     def456   1.4GB   방금
sionna-simple   baseline   abc123   1.2GB   30분 전
sionna-simple   latest     abc123   1.2GB   30분 전
```

## 🔍 3단계: 뭐가 다른지 확인

### 크기 비교

| 버전 | 크기 | 차이 |
|------|------|------|
| baseline | 1.2GB | 기본 |
| extras | 1.4GB | +약 200MB (패키지 3개, 환경에 따라 용량 차이가 있음) |

### 실행 비교

```bash
# baseline 실행
docker run --rm sionna-simple:baseline
# 🏆 Docker + Sionna 완벽!

# extras 실행
docker run --rm sionna-simple:extras
# 🏆 Docker + Sionna 완벽! (동일)
```

**차이점**: 실행 결과는 같지만, extras는 pandas/plotly 쓸 수 있음!

### 패키지 확인

```bash
# extras에만 pandas 있나?
docker run --rm sionna-simple:extras python -c "import pandas; print('pandas OK')"
# pandas OK

# baseline에는?
docker run --rm sionna-simple:baseline python -c "import pandas"
# ModuleNotFoundError (정상!)
```

## ☁️ 4단계: ECR에 업로드

### ECR 저장소 만들기 (처음 1회만)

```bash
aws ecr create-repository \
    --repository-name sionna-workshop \
    --region ap-northeast-2
```

**성공 메시지:**
```json
{
    "repository": {
        "repositoryName": "sionna-workshop",
        "repositoryUri": "<ACCOUNT_ID>.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-workshop"
    }
}
```

### Docker - ECR 로그인 정보 보기

```bash
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com
```

**성공:**
```
Login Succeeded
```

### 태그 변경 (ECR 주소 붙이기)

```bash
# 계정 ID 자동 가져오기
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export ECR=$ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-workshop

# baseline 태그
docker tag sionna-simple:baseline $ECR:baseline

# extras 태그
docker tag sionna-simple:extras $ECR:extras
```

### 업로드!

```bash
# baseline 업로드 (5분)
docker push $ECR:baseline

# extras 업로드 (6분)
docker push $ECR:extras
```

**업로드 중:**
```
baseline: digest: sha256:abc123... size: 1234
```

### AWS 콘솔 확인

1. AWS 콘솔 로그인
2. ECR → Repositories → sionna-workshop
3. 이미지 태그 확인:
   - `baseline` ✅
   - `extras` ✅

## 🧪 5단계: 다운로드 테스트 (10분)

### 로컬 이미지 삭제

```bash
docker rmi sionna-simple:baseline sionna-simple:extras
docker images | grep sionna
# 태깅된 이미지 등이 있을 수도 있음
# 모든 이미지 ID를 가져옴
docker images -a -q
# 해당 결과로 모든 이미지를 삭제
docker rmi -f $(docker images -a -q)
# 결과 확인
docker images | grep sionna
# (없음 - 깨끗!)
```

### ECR에서 가져오기

```bash
# baseline 다운로드
docker pull $ECR:baseline
```

```
$ docker pull $ECR:baseline
baseline: Pulling from sionna-workshop
47d2daa5f323: Already exists 
8715e552fa13: Already exists 
9c27bc7ba63d: Already exists 
7da4424a1132: Already exists 
e443f9ce3564: Already exists 
f54f78ac8903: Already exists 
72642c29014c: Already exists 
Digest: sha256:738b2b54f9e3c8947428212c0903a4b8c216665e354a04fc03d85565e5ee0f33
Status: Downloaded newer image for <ACCOUNT_ID>.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-workshop:baseline
<ACCOUNT_ID>.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-workshop:baseline
```

### 깨끗하게 삭제 후 다시 가져오기 실행

```bash
# 컨테이너 + 이미지 + 볼륨 모두 삭제
docker system prune -a --volumes -f
# baseline 다운로드
docker pull $ECR:baseline
```

```
baseline: Pulling from sionna-workshop
47d2daa5f323: Pull complete 
8715e552fa13: Pull complete 
9c27bc7ba63d: Pull complete 
7da4424a1132: Pull complete 
e443f9ce3564: Pull complete 
f54f78ac8903: Pull complete 
72642c29014c: Pull complete 
Digest: sha256:738b2b54f9e3c8947428212c0903a4b8c216665e354a04fc03d85565e5ee0f33
Status: Downloaded newer image for <ACCOUNT_ID>.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-workshop:baseline
<ACCOUNT_ID>.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-workshop:baseline
```

### 가져온 이미지 실행

```bash
# 실행
docker run --rm $ECR:baseline
```

**성공:**
```
🎉 **Sionna 워크숍 완성!**
...
```

## 🎁 팀원 공유 방법

**팀원에게 알려주기:**

```bash
# 1. 계정 ID 가져오기
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# 2. ACCOUNT ID 및 credential 공유
echo $ACCOUNT_ID
aws ecr get-login-password --region ap-northeast-2 > docker-credential

# 3. ECR 로그인
cat docker-credential | \
    docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com

# 3. 다운로드
docker pull $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-workshop:baseline

# 4. 실행
docker run --rm $ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/sionna-workshop:baseline
```

**끝! 팀원도 똑같은 환경에서 실행됨!** 🎉

## ✅ 실습 체크리스트

| 할 일 | 확인 |
|------|------|
| ✅ baseline 태그 | `docker images` 확인 |
| ✅ extras 빌드 | Dockerfile.extras 사용 |
| ✅ 크기 차이 확인 | 200MB 증가 |
| ✅ ECR 업로드 | AWS 콘솔에서 보임 |
| ✅ 다운로드 성공 | pull → run 성공 |

## 🛠️ 에러 해결

| 문제 | 해결 |
|------|------|
| ECR 로그인 안 됨 | `aws configure` 설정 확인 |
| 푸시 권한 없음 | AWS 관리자에게 ECR 권한 요청 |
| 이미지 너무 큼 | `docker system prune -a` |

## 🎉 완료!

**축하합니다!**

이제 할 수 있는 것:

✅ 환경에 패키지 추가 (Dockerfile 수정)  
✅ 버전별 태그 (baseline, extras)  
✅ ECR 업로드 (팀 공유)  
✅ 어디서나 동일 환경 실행

**핵심:**
- Dockerfile 수정 = 환경 변경
- 태그 = 버전 이름
- ECR = 클라우드 저장소

---

**[Git 사용을 통한 버전 관리로 계속 →](/50-git-management/)**

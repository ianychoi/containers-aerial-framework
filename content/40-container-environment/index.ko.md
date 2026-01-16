---
title: "컨테이너 기반 실험 격리 환경"
weight: 40
---

# 컨테이너 기반 실험 격리 환경

**재현 가능한 연구 환경 구축**

이전 모듈에서 Docker의 기본 개념을 학습했다면, 이제 격리된 컨테이너 환경을 사용하여 실험하는 환경에 대해 살펴보겠습니다.
GPU 가속 통신 시뮬레이션 연구에서 재현 가능한 환경 구축은 핵심입니다. 이 모듈에서는 [NVIDIA Sionna](https://developer.nvidia.com/sionna)를 컨테이너로 격리하여 연구 워크플로우를 표준화하는 방법을 배워봅니다.

## 🎯 학습 목표

이 모듈을 완료하면 다음을 할 수 있습니다:

- NVIDIA Sionna의 핵심 기능과 Docker 통합 이해
- baseline/extras 태깅 전략으로 환경 버전 관리
- Amazon ECR을 통한 이미지 공유 및 배포

## 📚 모듈 구성

이 Sionna 컨테이너 환경 모듈은 다음과 같이 구성되어 있습니다:

### [1. Sionna 개념 소개](concepts/)
- NVIDIA Sionna 라이브러리 개요와 6G 연구 활용
- 왜 Docker로 Sionna 환경을 격리해야 하는지
- 링크 수준 시뮬레이션 워크플로우 이해

### [2. Dockerfile과 Sionna 실습](docker-and-sionna/)
- Sionna 설치 Dockerfile 템플릿 작성
- 컨테이너 빌드 및 Sionna 예제 실행
- 아키텍처 및 GPU 가속 환경 검증

### [3. 실험 환경 버전 관리](experiment-environment/)
- baseline vs extras 환경 비교
- 환경 변경사항 Dockerfile로 관리
- ECR 업로드 및 버전 배포 실습

## 🚀 시작하기

Docker를 통해 "로컬 라이브러리 설치"에서 벗어나 재사용 가능한 Sionna 연구 환경을 구축합니다. 첫 번째 섹션인 [Sionna 개념 소개](concepts/)부터 시작하세요.

---

**[Git 버전 관리로 계속 →](/50-git-management/)**
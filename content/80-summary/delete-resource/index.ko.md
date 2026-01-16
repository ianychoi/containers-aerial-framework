---
title: "리소스 삭제"
weight: 81
---

# 🧹 리소스 정리

워크샵 완료 후 비용 발생을 방지하기 위해 생성된 리소스를 정리하세요.

## AWS 콘솔을 통한 리소스 삭제

### 1. Amazon EKS 클러스터 삭제

Amazon EKS 콘솔에서 클러스터를 삭제해 주세요:

![Delete Cluster](/static/delete-cluster.png)

## 명령어를 통한 리소스 정리

### **로컬 환경 정리**

```bash
# Docker 컨테이너 및 이미지 정리
docker system prune -a

# 불필요한 이미지 제거
docker rmi $(docker images -q)
```

### **AWS 리소스 정리**

```bash
# ECR 이미지 삭제
aws ecr batch-delete-image \
  --repository-name sionna-research \
  --image-ids imageTag=latest

# EKS 클러스터 삭제 (확장 환경 구축한 경우)
eksctl delete cluster --name eks-automode
```

## 주의사항

- 리소스 삭제 전에 중요한 데이터나 설정이 백업되어 있는지 확인하세요
- EKS 클러스터 삭제 시 연결된 모든 리소스(노드 그룹, 로드 밸런서 등)도 함께 삭제됩니다
- ECR 이미지 삭제는 되돌릴 수 없으므로 신중하게 진행하세요


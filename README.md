# Containers Aerial Framework Workshop

컨테이너를 활용한 Aerial Framework 및 Sionna 통신 연구 워크샵 사이트입니다.

## 프로젝트 구조

```
.
├── content/              # 마크다운 콘텐츠 파일
│   ├── _index.en.md     # 영문 홈페이지
│   ├── _index.ko.md     # 한글 홈페이지
│   ├── 10-prerequisites/
│   ├── 20-introduction/
│   ├── 30-docker-basics/
│   ├── 40-container-environment/
│   ├── 50-git-management/
│   ├── 60-integrated-workflow/
│   ├── 70-eks/
│   ├── 80-summary/
│   └── 90-credits/
├── static/              # 정적 파일 (이미지, CSS 등)
│   ├── css/
│   ├── images/
│   ├── samples/
│   └── aws-logo.png
├── layouts/             # Hugo 템플릿 파일
│   ├── _default/
│   │   ├── baseof.html
│   │   ├── single.html
│   │   └── list.html
│   ├── index.html
│   └── 404.html
└── hugo.toml           # Hugo 설정 파일
```

## 사용 방법

### 1. Hugo 설치

```bash
# macOS
brew install hugo

# Windows (Chocolatey)
choco install hugo-extended

# Linux (Snap)
snap install hugo
```

### 2. 개발 서버 실행

```bash
hugo server -D
```

사이트가 `http://localhost:1313`에서 실행됩니다.

### 3. 다국어 지원

- 영문: `http://localhost:1313/en/`
- 한글: `http://localhost:1313/ko/`

### 4. 정적 사이트 빌드

```bash
hugo
```

빌드된 파일은 `public/` 디렉토리에 생성됩니다.

## 콘텐츠 작성

### 이미지 사용

이미지는 `static/` 폴더에 저장하고, 마크다운에서 다음과 같이 참조합니다:

```markdown
![설명](/images/폴더명/이미지명.png)
```

예시:
```markdown
![Docker Architecture](/images/docker-basics/architecture.png)
```

### 새 페이지 추가

```bash
hugo new content/섹션명/페이지명.en.md
hugo new content/섹션명/페이지명.ko.md
```

### Front Matter 예시

```yaml
---
title: "페이지 제목"
weight: 10
description: "페이지 설명"
---
```

## 배포

### AWS Amplify

1. GitHub 저장소 연결
2. 빌드 설정:
   - Build command: `hugo`
   - Output directory: `public`

### Netlify

1. GitHub 저장소 연결
2. 빌드 설정:
   - Build command: `hugo`
   - Publish directory: `public`

### GitHub Pages

```bash
hugo
cd public
git init
git add .
git commit -m "Deploy"
git push -f git@github.com:username/repo.git main:gh-pages
```

## 라이선스

이 워크샵 자료는 AWS에서 제공합니다.

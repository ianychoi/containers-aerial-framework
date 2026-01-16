# 배포 가이드

## 로컬 개발 서버 실행

```bash
hugo server -D
```

브라우저에서 다음 주소로 접속:
- 영문: http://localhost:1313/en/
- 한글: http://localhost:1313/ko/

## 프로덕션 빌드

```bash
hugo
```

빌드된 파일은 `public/` 디렉토리에 생성됩니다.

## AWS Amplify 배포

### 1. amplify.yml 생성

프로젝트 루트에 `amplify.yml` 파일을 생성합니다:

```yaml
version: 1
frontend:
  phases:
    build:
      commands:
        - hugo
  artifacts:
    baseDirectory: public
    files:
      - '**/*'
  cache:
    paths: []
```

### 2. Amplify Console에서 설정

1. AWS Amplify Console 접속
2. "New app" > "Host web app" 선택
3. GitHub 저장소 연결
4. 빌드 설정 확인 (amplify.yml 자동 감지)
5. 배포 시작

## Netlify 배포

### 1. netlify.toml 생성

```toml
[build]
  publish = "public"
  command = "hugo"

[build.environment]
  HUGO_VERSION = "0.154.5"

[context.production.environment]
  HUGO_ENV = "production"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### 2. Netlify에서 배포

1. Netlify 대시보드 접속
2. "Add new site" > "Import an existing project"
3. GitHub 저장소 연결
4. 빌드 설정 확인
5. 배포 시작

## GitHub Pages 배포

### GitHub Actions 워크플로우

`.github/workflows/hugo.yml` 파일 생성:

```yaml
name: Deploy Hugo site to Pages

on:
  push:
    branches: ["main"]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

defaults:
  run:
    shell: bash

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        
      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v2
        with:
          hugo-version: '0.154.5'
          extended: true
          
      - name: Build
        run: hugo --minify
        
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./public

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### GitHub 저장소 설정

1. Settings > Pages
2. Source: "GitHub Actions" 선택
3. 코드를 main 브랜치에 푸시하면 자동 배포

## 커스텀 도메인 설정

### AWS Amplify

1. Amplify Console > Domain management
2. "Add domain" 클릭
3. 도메인 입력 및 DNS 설정

### Netlify

1. Site settings > Domain management
2. "Add custom domain" 클릭
3. DNS 설정 또는 Netlify DNS 사용

### GitHub Pages

1. Settings > Pages > Custom domain
2. 도메인 입력
3. DNS에 CNAME 레코드 추가

## 환경별 설정

### 개발 환경
```bash
hugo server -D --environment development
```

### 스테이징 환경
```bash
hugo --environment staging
```

### 프로덕션 환경
```bash
hugo --environment production --minify
```

## 성능 최적화

### 이미지 최적화
```bash
# ImageMagick 사용
find static/images -name "*.png" -exec convert {} -quality 85 {} \;
find static/images -name "*.jpg" -exec convert {} -quality 85 {} \;
```

### 빌드 최적화
```bash
hugo --minify --gc
```

## 문제 해결

### 빌드 실패 시
```bash
# 상세 로그 확인
hugo --verbose

# 캐시 정리
hugo --gc
rm -rf public/ resources/
```

### 이미지가 표시되지 않을 때
- 이미지 경로가 `/images/...` 형식인지 확인
- `static/` 폴더에 이미지가 있는지 확인
- 대소문자 구분 확인

### 다국어 페이지가 작동하지 않을 때
- 파일명이 `.en.md`, `.ko.md` 형식인지 확인
- `hugo.toml`의 언어 설정 확인

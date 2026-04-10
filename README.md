# DIGOUT — 자동화 시스템

인스타그램 컬처 매거진 **DIGOUT**의 트렌드 분석 + 콘텐츠 기획 자동화 시스템입니다.

---

## 시스템 구조

```
매일 오전 8시
GitHub Actions 자동 실행
       ↓
트렌드 수집 (멜론/네이버)
       ↓
Claude가 DIGOUT 관점으로 분석
       ↓
이메일로 트렌드 브리프 수신
       ↓
[내가 주제 선택]
       ↓
GitHub Actions 수동 실행 (주제 입력)
       ↓
Claude가 기획안 완성
(카드 구성 + 캡션 + 해시태그)
       ↓
이메일로 기획안 수신
       ↓
[내가 편집 후 업로드]
```

---

## 파일 구조

```
digout/
├── .github/
│   └── workflows/
│       ├── daily_trend.yml      # 매일 아침 트렌드 브리프
│       └── content_planner.yml  # 기획안 생성 (수동)
├── scripts/
│   ├── trend_analyzer.py        # 트렌드 수집 + 분석 + 발송
│   └── content_planner.py       # 기획안 생성 + 발송
├── requirements.txt
└── README.md
```

---

## 설정 방법

### 1단계 — GitHub Secrets 등록

GitHub 레포 → Settings → Secrets and variables → Actions → New repository secret

| Secret 이름 | 값 |
|------------|---|
| `ANTHROPIC_API_KEY` | Anthropic API 키 |
| `GMAIL_USER` | 보내는 Gmail 주소 (예: yourname@gmail.com) |
| `GMAIL_APP_PW` | Gmail 앱 비밀번호 (아래 참고) |
| `TO_EMAIL` | 받는 이메일 주소 |

### 2단계 — Gmail 앱 비밀번호 발급

1. Google 계정 → 보안 → 2단계 인증 활성화
2. 보안 → 앱 비밀번호 → 앱 선택: 메일 → 기기: 기타 → "DIGOUT" 입력
3. 생성된 16자리 비밀번호를 `GMAIL_APP_PW`에 등록

### 3단계 — 완료

- 매일 오전 8시에 트렌드 브리프 이메일이 자동으로 옵니다
- 기획안은 아래 방법으로 수동 실행하면 됩니다

---

## 기획안 요청 방법

### 방법 A — GitHub 웹에서 실행

1. 레포 → Actions 탭
2. **"DIGOUT — 기획안 생성"** 워크플로우 선택
3. **Run workflow** 클릭
4. 주제 입력 (예: `이번 달 놓치면 안 되는 내한공연`, `필름카메라 입문 추천 3종`)
5. Run workflow 실행 → 1~2분 후 이메일 수신

### 방법 B — 주제 예시

```
# SOUND
이번 달 들어야 할 앨범 3장
힙합 입문자를 위한 플레이리스트
[아티스트명] 내한 전 알아야 할 것들

# WEAR  
요즘 거리에서 보이는 빈티지 룩
이번 시즌 레이어링 스타일링 팁

# PLACE
서울 성수동 숨겨진 카페 5곳
혼자 가기 좋은 서울 공간 추천

# GEAR
필름카메라 입문 추천 3종
LP 플레이어 처음 사는 법

# SCENE
[공연/전시명] 가기 전 알아야 할 것들
이번 달 놓치면 안 되는 팝업 정리
```

---

## 수동 실행 (테스트)

```bash
# 로컬에서 테스트 실행
export ANTHROPIC_API_KEY="sk-..."
export GMAIL_USER="your@gmail.com"
export GMAIL_APP_PW="xxxx xxxx xxxx xxxx"
export TO_EMAIL="receive@email.com"

# 트렌드 브리프
python scripts/trend_analyzer.py

# 기획안 생성
export TOPIC="필름카메라 입문 추천 3종"
python scripts/content_planner.py
```

---

## DIGOUT 시리즈 분류

| 시리즈 | 카테고리 | 키워드 |
|--------|---------|--------|
| DIGOUT SOUND | 음악 | 앨범, 아티스트, 장르, 내한, 차트 |
| DIGOUT WEAR | 패션 | 룩, 스타일, 브랜드, 스트리트 |
| DIGOUT PLACE | 장소 | 카페, 공간, 스팟, 서울, 골목 |
| DIGOUT GEAR | 빈티지 기기 | 카메라, 오디오, 레트로, LP |
| DIGOUT SCENE | 공연/전시 | 내한, 전시, 팝업, 이벤트 |
| DIGOUT NOW | 컬처 이슈 | 트렌드, 이슈, 바이럴, 요즘 |

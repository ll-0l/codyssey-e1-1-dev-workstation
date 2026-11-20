# 동료평가 대비 정리

> 평가 항목(과제 목표 · 기능 요구사항 · 보너스)마다 **한 줄 답 → 쉬운 설명 → 증거 위치 → 바로 보여줄 명령** 순서로 정리했습니다.
> 증거 링크는 모두 [README](../README.md) 안의 해당 절로 연결됩니다.

## 목차

- [0. 30초 자기소개 (내가 한 일)](#0-30초-자기소개-내가-한-일)
- [A. 과제 목표 (설명할 수 있어야 하는 6가지)](#a-과제-목표-설명할-수-있어야-하는-6가지)
- [B. 기능 요구사항 (수행 증거)](#b-기능-요구사항-수행-증거)
- [C. 보너스 과제](#c-보너스-과제)
- [D. 실시간 시연 순서 (5분)](#d-실시간-시연-순서-5분)
- [E. 예상 꼬리 질문](#e-예상-꼬리-질문)
- [F. 핵심 용어 한 줄 사전](#f-핵심-용어-한-줄-사전)

---

## 0. 30초 자기소개 (내가 한 일)

> "터미널로 작업 폴더와 권한을 정리했고, Docker 를 설치해 기본 명령을 익혔습니다.
> `nginx:alpine` 을 베이스로 **내 페이지·설정·헬스체크를 넣은 커스텀 이미지**를 만들고, 같은 이미지를 **8080 / 8081 두 포트**로 띄워 접속했습니다.
> **바인드 마운트**로 호스트 수정이 즉시 반영되는 것, **볼륨**으로 컨테이너를 지워도 데이터가 남는 것을 확인했습니다.
> 보너스로 Compose 로 **nginx + Python API 두 컨테이너**를 띄워 서비스 이름으로 통신시키고, **환경 변수만 바꿔 포트/모드를 변경**했으며, **SSH 키로 push** 했습니다."

**환경 특이사항 (먼저 말하기)** — 과제 안내는 OrbStack 이지만 내 Mac 은 **macOS 12** 이고 OrbStack 은 **macOS 14 이상** 만 지원합니다. 그래서 macOS 12 를 지원하는 마지막 버전인 **Docker Desktop 4.41.2** 를 사용했습니다. `docker` 명령은 똑같습니다. → [트러블슈팅 #1](../README.md#ts1)

---

## A. 과제 목표 (설명할 수 있어야 하는 6가지)

### A1. 절대 경로 vs 상대 경로

| | 한 줄 답 |
|---|---|
| **절대 경로** | `/` (루트) 부터 시작하는 **전체 주소**. 내가 어디 있든 항상 같은 파일 |
| **상대 경로** | **지금 위치(`pwd`) 기준** 주소. `.` = 현재 폴더, `..` = 상위 폴더 |

- **비유**: 절대 경로 = "서울시 ○○구 ○○로 12", 상대 경로 = "여기서 옆 건물"
- **내 실습 예시**: `practice/backup` 폴더에서
  - 상대: `cat ../docs/memo.txt`
  - 절대: `cat /Users/.../E1-1-dev-workstation/practice/docs/memo.txt`
  - → 둘 다 같은 파일 `터미널 실습 메모` 출력
- **실무 포인트**: 문서/스크립트에 내 PC 절대 경로를 박으면 남의 PC 에서 안 돌아감 → 바인드 마운트에서 `"$(pwd)/mount-demo"` 를 사용한 이유
- 증거: [README 6.1](../README.md#61-터미널-기본-조작)

### A2. 파일 권한 r/w/x 와 755 / 644

- **한 줄 답**: 권한은 **소유자 / 그룹 / 기타** 3묶음이고, 각 묶음은 `r=4, w=2, x=1` 을 더한 숫자 하나로 쓴다.

| 표기 | 계산 | 의미 | 주로 쓰는 곳 |
|---|---|---|---|
| `755` | 7(rwx) 5(r-x) 5(r-x) | 나는 다 됨, 남은 읽기·실행만 | 실행 스크립트, 디렉토리 |
| `644` | 6(rw-) 4(r--) 4(r--) | 나는 읽기·쓰기, 남은 읽기만 | 일반 파일 |
| `600` | 6(rw-) 0 0 | 나만 읽기·쓰기 | 개인키 같은 비밀 파일 |

- **파일 vs 디렉토리에서 의미가 다름** (꼭 말하기!)

| | 파일 | 디렉토리 |
|---|---|---|
| r | 내용 읽기 | 안에 뭐가 있는지 **목록 보기** |
| w | 내용 수정 | 안에 파일 **만들기/지우기** |
| x | **실행** | 안으로 **들어가기/접근** |

- **내 실험 결과**
  - `hello.sh` 644 → `./hello.sh` **permission denied** → `chmod 755` → 실행 성공
  - `greeting.txt` 444 → 내용 추가 **실패** → 644 → 성공
  - `docs/` 555 → 파일 생성 실패 / 311 → `ls` 실패지만 이름 알면 `cat` 가능 / 644 → `x` 없어서 `cat` 실패
- 증거: [README 6.2](../README.md#62-권한-실습) · [로그](logs/04-permission.log)

### A3. 기존 Dockerfile 기반 커스텀 이미지

- **한 줄 답**: 검증된 공식 이미지(`nginx:alpine`)를 `FROM` 으로 가져오고, **바꾸고 싶은 것만 위에 덧씌워** 내 이미지를 만들었다. (방식 A)

| 줄 | 왜 넣었나 |
|---|---|
| `FROM nginx:alpine` | nginx 설치·실행은 공식 이미지에 맡김. alpine 이라 가벼움 |
| `LABEL ...` | 이미지 이름/설명/출처 메타데이터 |
| `ENV APP_ENV=dev` | 실행 환경 구분값 (컨테이너 안에서 `printenv APP_ENV` → `dev`) |
| `COPY nginx/default.conf` | `/health` 추가, nginx 버전 숨김, `X-Served-By` 헤더(어느 컨테이너가 응답했는지) |
| `COPY site/` | 기본 Welcome 페이지를 내 페이지로 교체 |
| `HEALTHCHECK` | `docker ps` 에 `(healthy)` 표시 → 살아 있는지 자동 확인 |
| `EXPOSE 80` | "이 컨테이너는 80 을 씀" 문서화 (실제 공개는 `-p` 가 함) |

- **이미지 vs 컨테이너**: 이미지 = 붕어빵 틀(읽기 전용 설계도), 컨테이너 = 틀로 찍은 붕어빵(실행 중인 인스턴스). 하나의 이미지로 컨테이너 여러 개 가능 (8080/8081)
- **레이어**: Dockerfile 한 줄 = 레이어 하나. 바뀐 줄부터만 다시 빌드 → 빌드가 빠름
- 증거: [README 6.6](../README.md#66-dockerfile-기반-커스텀-이미지) · [Dockerfile](../app/Dockerfile) · [빌드 로그](logs/08-build-run.log)

### A4. 포트 매핑이 필요한 이유

- **한 줄 답**: 컨테이너는 **자기만의 격리된 네트워크**를 가져서 밖에서 바로 못 들어간다. `-p 호스트포트:컨테이너포트` 는 **"호스트의 이 문으로 오면 컨테이너의 저 문으로 연결"** 하는 규칙이다.
- **비유**: 아파트(호스트) 공동현관 호수(8080) → 각 집 안의 방문(80)
- **내 실습**: 컨테이너 안은 둘 다 80 인데 호스트 포트만 8080 / 8081 로 다르게 → **충돌 없이 동시에 실행**
  - `X-Served-By` 헤더 값이 서로 달라 **다른 컨테이너가 응답한 것**까지 확인
- **반대 사례**: Compose 의 api(5000)는 일부러 매핑 안 함 → 외부에서 `localhost:5000` 접속 실패 = **필요한 것만 공개하는 보안 습관**
- 증거: [README 6.7](../README.md#67-포트-매핑-및-접속-증거) (curl + 브라우저 스크린샷)

### A5. Docker 볼륨 (영속 데이터)

- **한 줄 답**: 컨테이너 안에 쓴 데이터는 **컨테이너를 지우면 같이 사라진다**. 볼륨은 Docker 가 관리하는 **컨테이너 밖 저장소**라서 컨테이너를 지워도 남고, 새 컨테이너에 다시 붙이면 그대로 보인다.
- **내 실험 (전/후 비교)**
  1. `docker volume create codyssey-data`
  2. `vol-test` 컨테이너에 연결해 `/data/hello.txt` 작성
  3. `docker rm -f vol-test` (컨테이너 삭제) → `docker volume ls` 에 볼륨은 **남아 있음**
  4. 새 컨테이너 `vol-test2` 에 같은 볼륨 연결 → **이전 내용 그대로**
  5. **대조 실험**: 볼륨 없이 `/tmp` 에 쓴 파일은 삭제 후 `No such file`
- **바인드 마운트와 차이**

| | 바인드 마운트 | 볼륨 |
|---|---|---|
| 어디에 저장 | **내 PC 의 특정 폴더** | Docker 관리 영역 |
| 언제 쓰나 | 개발 중 코드 수정 **즉시 반영** | DB 등 **데이터 보존** |
| 단점/장점 | PC 경로에 의존 | 이름만으로 사용, 이식성 좋음 |

- 바인드 마운트 실험: 호스트에서 `mount-demo/index.html` 을 v1 → v2 로 고치자 **재시작 없이** `curl` 결과가 바로 v2. `:ro`(읽기 전용)라서 컨테이너 안에서 쓰기는 거부됨
- 증거: [README 6.8](../README.md#68-바인드-마운트-호스트-변경-즉시-반영) · [README 6.9](../README.md#69-docker-볼륨-영속성) · [로그](logs/10-mount-volume.log)

### A6. Git vs GitHub

- **한 줄 답**: **Git** 은 내 PC 에서 돌아가는 **버전 관리 프로그램**, **GitHub** 는 Git 저장소를 올려 두는 **온라인 협업 서비스**.

| | Git | GitHub |
|---|---|---|
| 어디서 | 내 컴퓨터 (오프라인 가능) | 인터넷 (원격 서버) |
| 하는 일 | commit, branch, log, diff | 백업·공유, PR/코드리뷰, 이슈, Actions(CI/CD) |
| 연결 | `git remote add origin ...` → `git push / pull` | |

- **비유**: Git = 내 노트의 "변경 기록", GitHub = 그 노트를 팀과 같이 보는 "공유 드라이브"
- 증거: [README 6.10](../README.md#610-git-설정-및-githubvscode-연동)

---

## B. 기능 요구사항 (수행 증거)

| # | 평가 항목 | 한 줄 답변 | 증거 |
|---|---|---|---|
| B1 | **저장소 · 기술 문서** | 공개 저장소, README 하나에 개요/환경/체크리스트/검증 방법/트러블슈팅 모두 포함, 원본 로그는 `docs/logs/` | [README 목차](../README.md#목차) |
| B2 | **실행 환경 기록** | macOS 12.7.6 / zsh / VSCode 터미널 / Docker 28.1.1 (Desktop 4.41.2) / Git 2.37.1 | [README 2](../README.md#2-실행-환경) |
| B3 | **터미널 조작** | `pwd`, `ls -la`(숨김 포함), `cd`, `mkdir -p`, `cp`(-r), `mv`(이동·이름변경), `rm`(-r), `cat`, `touch`(빈 파일) 모두 수행 | [README 6.1](../README.md#61-터미널-기본-조작) |
| B4 | **권한 실습** | 파일 2개(`hello.sh`, `greeting.txt`) + 디렉토리 1개(`docs`) 전/후 비교, 성공/실패 결과까지 기록 | [README 6.2](../README.md#62-권한-실습) |
| B5 | **Docker 설치 · 점검** | `docker --version` + `docker version`(Client/Server 둘 다 나옴) + `docker info` | [README 6.3](../README.md#63-docker-설치-및-점검) |
| B6 | **Docker 기본 운영** | `pull`, `images`, `ps`, `ps -a`, `start/stop`, `logs`, `stats --no-stream` | [README 6.4](../README.md#64-docker-기본-운영-명령) |
| B7 | **hello-world / ubuntu** | hello-world 성공, ubuntu 진입 후 `ls`, `echo`, `cat /etc/os-release` | [README 6.5](../README.md#65-컨테이너-실행-실습-hello-world--ubuntu) |
| B8 | **attach vs exec 관찰** | 아래 표 참고 | [README 6.5](../README.md#65-컨테이너-실행-실습-hello-world--ubuntu) |
| B9 | **커스텀 이미지** | 베이스 `nginx:alpine`, 커스텀 포인트 6개 + 목적, 빌드/실행/inspect 결과 | [README 6.6](../README.md#66-dockerfile-기반-커스텀-이미지) |
| B10 | **포트 매핑 접속** | 8080, 8081 두 번 실행, curl 200 OK + 브라우저(주소창 포함) 스크린샷 | [README 6.7](../README.md#67-포트-매핑-및-접속-증거) |
| B11 | **바인드 마운트** | 실행 명령 + 호스트 수정 전(v1)/후(v2) curl 비교 + `:ro` 쓰기 거부 | [README 6.8](../README.md#68-바인드-마운트-호스트-변경-즉시-반영) |
| B12 | **볼륨 영속성** | 생성 → 연결 → 쓰기 → 컨테이너 삭제 → 새 컨테이너에서 확인 + 대조 실험 | [README 6.9](../README.md#69-docker-볼륨-영속성) |
| B13 | **Git 설정** | `user.name`, `user.email`, `init.defaultBranch=main`, `git config --list --show-origin` | [README 6.10](../README.md#610-git-설정-및-githubvscode-연동) |
| B14 | **GitHub · VSCode 연동** | VSCode 계정 메뉴에 `ll-0l (GitHub)`, Source Control 에 `main` + 원격 연동 스크린샷 | [README 6.10](../README.md#610-git-설정-및-githubvscode-연동) |
| B15 | **트러블슈팅 2건 이상** | 3건: ① OrbStack macOS 버전 ② `$(hostname)` 이 호스트에서 치환 ③ `docker stop` 10초 + Exit 137 | [README 8](../README.md#8-트러블슈팅) |
| B16 | **보안 · 개인정보** | 저장소 전용 noreply 이메일, 개인 이메일/SSH 지문 `<masked>`, 개인키 미노출, `.env` 에 비밀 없음 | [README 11](../README.md#11-보안-및-개인정보-처리) |
| B17 | **재현성** | README 5 의 명령만 따라 하면 동일 결과. 실행 전 `lsof` 로 포트 확인, 경로는 `$(pwd)`, Windows 대체 경로 안내 | [README 5](../README.md#5-빠른-재현-방법) |
| B18 | **포트 충돌 진단 · 해제** | `lsof -nP -iTCP:8080 -sTCP:LISTEN` → PID 확인, `netstat -anv` 교차 확인, Docker 면 `docker ps --filter publish=8080` → `rm -f` 또는 대체 포트, 일반 프로세스면 `ps -p PID` 확인 후 `kill` | [README 6.11](../README.md#611-포트-충돌-진단-및-해결) · [로그](logs/15-port-conflict.log) |
| B19 | **볼륨 백업 / 복원** | 임시 컨테이너로 볼륨을 `tar czf` → 새 볼륨에 `tar xzf` → `sha256sum` 일치 확인 | [README 6.9](../README.md#69-docker-볼륨-영속성) · [로그](logs/16-volume-backup.log) |
| B20 | **정리 · 재빌드** | 컨테이너 → 이미지 순서로 `rm` / `rmi` (반대로 하면 conflict 에러), 캐시 문제는 `--no-cache --pull` | [README 6.4](../README.md#64-docker-기본-운영-명령) · [로그](logs/17-rebuild-cleanup.log) |

### B8 보충 — `run -it` / `exec` / `attach` 차이 (자주 물어봄)

| 명령 | 어디에 붙나 | `exit` 하면 | 언제 쓰나 |
|---|---|---|---|
| `docker run -it` | 새 컨테이너의 **메인 프로세스(PID 1)** | 컨테이너 **종료** | 한 번 들어가 보고 끝낼 때 |
| `docker exec -it` | 실행 중 컨테이너에 **새 프로세스 추가** | 그 셸만 종료, 컨테이너 **계속 실행** | 운영 중 점검·디버깅 ✅ |
| `docker attach` | 실행 중 컨테이너의 **PID 1** 에 직접 연결 | PID 1 종료 → 컨테이너 **종료** | 메인 출력 보기 (`Ctrl+P, Ctrl+Q` 로 빠지면 유지) |

> 결론: **운영 중인 서비스에 들어갈 땐 `exec`** — 서비스를 멈추지 않는다.

### B15 보충 — 트러블슈팅 말하는 법 (문제 → 가설 → 확인 → 해결)

1. **OrbStack 설치 불가** → 최소 OS 버전 문제일 것 → `Info.plist` 의 `LSMinimumSystemVersion = 14.0` 확인 → Docker Desktop 4.41.2 로 대체, 자동 업데이트 끔
2. **`docker exec ... echo "$(hostname)"` 에 Mac 이름이 나옴** → 큰따옴표 안 `$( )` 를 **내 Mac 의 zsh 가 먼저** 바꿔버림 → 출력이 Mac 이름과 같음 → **작은따옴표**로 감싸 `sh -c '...'` 로 컨테이너 안에서 해석
3. **`docker stop` 이 10초 걸리고 Exit 137** → PID 1 인 bash 가 종료 신호(SIGTERM)를 무시 → 10초 후 강제 종료(SIGKILL, 128+9=137) → 테스트는 `stop -t 1`, 서비스는 신호 처리하는 프로세스나 `--init` 사용

---

## C. 보너스 과제

| # | 항목 | 한 줄 답변 | 배움 포인트 | 증거 |
|---|---|---|---|---|
| C1 | **Compose 기초** | `docker run -d -p 8085:80 ...` 을 `compose/single/docker-compose.yml` 로 옮겨 `docker compose up -d` 한 줄로 실행 | 긴 명령어가 **저장소에 남는 실행 문서**가 됨 → 누구나 같은 구성 재현 | [README 7.1](../README.md#71-compose-기초-단일-서비스) |
| C2 | **멀티 컨테이너 + 통신** | web(nginx) + api(Python) 를 같은 네트워크로 실행. `web → http://api:5000`, `api → http://web` 양방향 성공 | **서비스 이름 = DNS 이름**. IP 가 바뀌어도 이름으로 찾음 (서비스 디스커버리) | [README 7.2](../README.md#72-compose-멀티-컨테이너--서비스-간-통신) |
| C3 | **운영 명령** | `up -d --build` → `ps` → `logs` → `down` → `ps -a` 로 정리 확인 | **상태 확인 루틴**: 띄우고 → 상태 → 로그 → 내리고 → 남은 것 확인 | [README 7.3](../README.md#73-compose-운영-루틴) |
| C4 | **환경 변수** | `.env` 기본값(8090/5000/dev) → `WEB_PORT=8091 API_PORT=7000 APP_MODE=prod docker compose up -d` 로 코드 수정 없이 변경 | **설정과 코드 분리** → 같은 이미지를 개발/운영에 그대로 사용 | [README 7.4](../README.md#74-환경-변수로-포트모드-변경) |
| C5 | **SSH 키** | `ssh -T git@github.com` → `Hi ll-0l!`, remote 가 `git@github.com:...` 형식, push 성공 | 비밀번호/토큰을 보내지 않고 **개인키(내 PC) + 공개키(GitHub 등록)** 쌍으로 인증 | [README 7.5](../README.md#75-github-ssh-키) |

### C2 보충 — 구조 그림으로 설명하기

```text
브라우저 ──► localhost:8090 ──► [web: nginx] ──/api/──► [api: python :5000]
                                   └──── backend 네트워크 ────┘
       (호스트에는 web 만 공개 / api 는 내부에서만 접근 가능)
```

- `depends_on: condition: service_healthy` → api 가 **healthy 가 된 다음에** web 시작
- nginx 템플릿의 `${API_PORT}` 가 컨테이너 시작 시 실제 값으로 치환됨 → `proxy_pass http://api:7000;` 확인

### C4 보충 — 환경 변수 우선순위

`셸에서 직접 준 값` > `.env 파일` > `compose 파일의 기본값 ${VAR:-기본}` > `Dockerfile 의 ENV`

### C5 보충 — HTTPS vs SSH

| | HTTPS | SSH |
|---|---|---|
| 인증 | 아이디 + 토큰(PAT) | 공개키/개인키 쌍 |
| 주소 | `https://github.com/...` | `git@github.com:...` |
| 주의 | 토큰 만료·유출 관리 | **개인키는 절대 공유 금지** (공개키 `.pub` 만 GitHub 에 등록) |

---

## D. 실시간 시연 순서 (5분)

평가자가 "직접 보여 달라" 고 할 때 그대로 따라 하면 됩니다. (Docker Desktop 실행 후)

```bash
cd codyssey-e1-1-dev-workstation

# 0) 데몬 동작 확인 + 이전 실습 컨테이너 정리 (이름 충돌 방지)
docker --version && docker info --format '{{.ServerVersion}}'
docker rm -f web-8080 web-8081 web-bind 2>/dev/null

# 1) 커스텀 이미지 빌드 → 두 포트로 실행
docker build -t codyssey-web:1.0 ./app
docker run -d -p 8080:80 --name web-8080 codyssey-web:1.0
docker run -d -p 8081:80 --name web-8081 codyssey-web:1.0
docker ps                                   # (healthy) 확인
curl -sI http://localhost:8080 | grep -i x-served-by
curl -sI http://localhost:8081 | grep -i x-served-by   # 값이 다름 = 다른 컨테이너

# 2) 바인드 마운트: 호스트 수정 → 즉시 반영
docker run -d -p 8082:80 --name web-bind -v "$(pwd)/mount-demo":/usr/share/nginx/html:ro codyssey-web:1.0
curl -s http://localhost:8082 | grep 'Page version'
sed -i '' 's/v2 (호스트에서 수정됨)/v3 (시연)/' mount-demo/index.html
curl -s http://localhost:8082 | grep 'Page version'    # v3 로 바뀜
git checkout mount-demo/index.html                     # 원상복구

# 3) 볼륨: 컨테이너 지워도 데이터 유지
docker volume create demo-data
docker run --rm -v demo-data:/data ubuntu:22.04 bash -c 'echo hi > /data/a.txt'
docker run --rm -v demo-data:/data ubuntu:22.04 cat /data/a.txt   # hi (다른 컨테이너)

# 4) (보너스) Compose
cd compose && docker compose up -d --build
curl -s http://localhost:8090/api/info
docker compose exec web wget -qO- http://api:5000/api/info
docker compose down && cd ..

# 정리
docker rm -f web-8080 web-8081 web-bind; docker volume rm demo-data
```

> 💡 포트가 이미 사용 중이라는 에러(`port is already allocated`)가 나오면: `docker ps` 로 같은 포트를 쓰는 컨테이너를 찾아 `docker rm -f <이름>` 하거나 다른 호스트 포트를 사용.

---

## E. 예상 꼬리 질문

| 질문 | 답변 |
|---|---|
| `EXPOSE` 만 쓰면 접속되나요? | 안 됩니다. `EXPOSE` 는 **문서용 표시**이고, 실제로 호스트에 여는 건 `docker run -p` 입니다. |
| `-p 8080:80` 에서 앞/뒤 숫자는? | **앞 = 호스트(내 PC)**, **뒤 = 컨테이너 안**. |
| 같은 호스트 포트를 두 컨테이너에 쓰면? | 두 번째 실행이 `port is already allocated` 로 실패합니다. 그래서 8080/8081 로 나눴습니다. |
| 포트를 누가 쓰는지 어떻게 찾나요? | `lsof -nP -iTCP:<포트> -sTCP:LISTEN` 으로 PID 확인 (Linux 는 `ss -ltnp`). `com.docker.backend` 로 나오면 Docker 컨테이너이므로 `docker ps --filter publish=<포트>` 로 찾아 `docker rm -f`. **com.docker 프로세스를 kill 하면 Docker 전체가 멈춥니다.** |
| `kill` 과 `kill -9` 차이? | `kill` = SIGTERM(정리하고 종료해 달라는 요청), `kill -9` = SIGKILL(즉시 강제 종료). 먼저 `kill`, 안 될 때만 `-9`. |
| `-p 8080:80` 과 `-p 127.0.0.1:8080:80` 차이? | 앞은 모든 인터페이스(0.0.0.0) → 같은 네트워크 다른 기기도 접속 가능, 뒤는 내 PC 에서만. 직접 확인함 ([README 6.7](../README.md#67-포트-매핑-및-접속-증거)) |
| 볼륨은 어떻게 백업하나요? | 볼륨과 호스트 폴더를 함께 마운트한 임시 컨테이너에서 `tar czf` 로 묶어 꺼내고, 복원은 새 볼륨에 `tar xzf`. 해시로 같은지 확인했습니다. |
| setuid / sticky 비트는? | setuid(4000): 소유자 권한으로 실행 (`/usr/bin/sudo` 의 `s`). sticky(1000): 공용 디렉토리에서 자기 파일만 삭제 (`/tmp` 의 `t`). |
| 이미지를 지우면 실행 중 컨테이너는? | 사용 중인 이미지는 바로 못 지웁니다(`-f` 필요). 이미지는 설계도, 컨테이너는 실행 인스턴스라 관계가 있습니다. |
| `docker ps` 와 `docker ps -a` 차이? | `ps` 는 **실행 중**만, `-a` 는 **종료된 것까지 전부**. |
| `docker stop` 과 `docker rm` 차이? | `stop` 은 멈추기(다시 `start` 가능), `rm` 은 컨테이너 자체 삭제. |
| 볼륨은 어디에 저장되나요? | Docker 관리 영역 `/var/lib/docker/volumes/<이름>/_data`. Mac 에선 Docker Desktop 의 리눅스 VM 안에 있습니다. |
| 볼륨을 지우려면? | `docker volume rm <이름>` (사용 중인 컨테이너가 없어야 함). `docker rm -v` 는 익명 볼륨만 함께 삭제. |
| 바인드 마운트에 `:ro` 는 왜? | 컨테이너가 호스트 파일을 **실수로 바꾸지 못하게** 읽기 전용으로 연결. |
| `$(pwd)` 에 왜 큰따옴표? | 내 경로에 **공백**(`Codyssey all-in-one Pre-course`)이 있어 따옴표 없으면 경로가 쪼개집니다. |
| HEALTHCHECK 는 뭘 하나요? | 10초마다 `/health` 를 호출해 실패 3번이면 `unhealthy`. Compose 의 `service_healthy` 조건에도 쓰입니다. |
| `alpine` 은 왜 썼나요? | 매우 작은 리눅스(수 MB) → 이미지가 가볍고 받는 속도가 빠름. |
| api 를 root 가 아닌 사용자로 실행한 이유? | `USER appuser` — 컨테이너가 뚫려도 피해 범위를 줄이는 보안 습관. |
| Exit code 137 은? | 128 + 9(SIGKILL) = **강제 종료**됨. 0 은 정상 종료. |
| `git config` 전역 vs 저장소? | `--global` 은 내 PC 전체(`~/.gitconfig`), 옵션 없으면 이 저장소만(`.git/config`). 저장소 설정이 우선. 그래서 이 저장소 커밋엔 noreply 이메일만 남음. |
| 기본 브랜치를 main 으로 바꾼 이유? | GitHub 기본값과 맞춰 push 시 브랜치 혼동(master/main)을 방지. |
| 민감정보가 커밋되면? | 파일에서 지워도 **히스토리에 남음** → 히스토리 정리(`git filter-repo` 등) + **토큰/키 즉시 폐기·재발급**이 핵심. |
| 왜 컨테이너를 쓰나요? | "내 PC 에선 되는데" 문제 해결. 실행 환경을 이미지로 묶어 **누가 어디서 실행해도 같은 결과**. |
| 컨테이너 vs 가상머신? | VM 은 OS 전체를 통째로 띄움(무겁고 느림), 컨테이너는 **호스트 커널을 공유**하고 프로세스만 격리(가볍고 빠름). |

---

## F. 핵심 용어 한 줄 사전

| 용어 | 한 줄 |
|---|---|
| 이미지 | 실행 환경을 담은 읽기 전용 설계도 |
| 컨테이너 | 이미지로 만든 격리된 실행 인스턴스 |
| Dockerfile | 이미지를 만드는 레시피 |
| 레이어 | Dockerfile 한 줄마다 쌓이는 변경분 (캐시되어 재빌드 빠름) |
| 데몬(dockerd) | 실제로 컨테이너를 만들고 관리하는 백그라운드 서버. `docker` CLI 는 클라이언트 |
| 포트 매핑 | 호스트 포트 → 컨테이너 포트 연결 규칙 (`-p`) |
| 바인드 마운트 | 호스트 폴더를 컨테이너에 그대로 연결 |
| 볼륨 | Docker 가 관리하는 영속 저장소 |
| 브리지 네트워크 | 컨테이너끼리 통신하는 가상 네트워크 |
| Compose | 여러 컨테이너 실행 설정을 YAML 하나로 관리하는 도구 |
| 헬스체크 | 서비스가 정상인지 주기적으로 확인하는 명령 |
| remote / origin | 원격 저장소 주소 / 그 기본 이름 |
| SSH 키 | 공개키(서버 등록) + 개인키(내 PC 보관) 쌍으로 하는 인증 |

# Codyssey E1-1 · 개발 워크스테이션 구축

> 터미널 · Docker · Git/GitHub 를 직접 세팅하고, **실행 결과(로그 · 접속 · 데이터 유지)** 로 동작을 검증한 기록입니다.
> 이 README 하나만 읽어도 전체 수행 내용과 재현 방법을 파악할 수 있도록 작성했습니다. 전체 원본 로그는 [`docs/logs/`](docs/logs/) 에 있습니다.

## 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [실행 환경](#2-실행-환경)
3. [저장소 구조](#3-저장소-구조)
4. [수행 체크리스트](#4-수행-체크리스트)
5. [빠른 재현 방법](#5-빠른-재현-방법)
6. [수행 로그 및 검증](#6-수행-로그-및-검증)
7. [보너스 과제](#7-보너스-과제)
8. [트러블슈팅](#8-트러블슈팅)
9. [개념 정리 (과제 목표)](#9-개념-정리-과제-목표)
10. [검증 방법 요약표](#10-검증-방법-요약표)
11. [보안 및 개인정보 처리](#11-보안-및-개인정보-처리)

---

## 1. 프로젝트 개요

| 목표 | 이 저장소에서 한 일 |
|---|---|
| 터미널로 작업 공간 정리 | 디렉토리 생성 · 복사 · 이동 · 삭제, 숨김 파일 확인, 절대/상대 경로 비교 |
| 권한 이해 | 파일 1개 · 디렉토리 1개에 대해 `chmod` 전/후 동작 비교 |
| Docker 설치 · 점검 · 운영 | Docker Desktop 설치, `version/info/images/ps/logs/stats` 실행 |
| 컨테이너 실행 | `hello-world`, `ubuntu` 실행, `run -it` / `exec` / `attach` 차이 관찰 |
| 커스텀 이미지 | `nginx:alpine` 기반 Dockerfile 직접 작성 → `codyssey-web:1.0` |
| 포트 매핑 | 같은 이미지를 `8080`, `8081` 두 포트로 실행 후 접속 |
| 바인드 마운트 / 볼륨 | 호스트 수정 즉시 반영, 컨테이너 삭제 후에도 데이터 유지 증명 |
| Git / GitHub | 사용자 정보 · 기본 브랜치 설정, VSCode GitHub 연동, SSH 푸시 |
| 보너스 | Compose 단일/멀티 컨테이너, 서비스 간 통신, 환경 변수로 포트·모드 변경, SSH 키 |

**핵심 메시지** — 이미지는 "실행 환경의 설계도", 컨테이너는 "그 설계도로 만든 격리된 실행 인스턴스" 입니다.
포트 매핑으로 바깥과 연결하고, 마운트/볼륨으로 데이터를 컨테이너 수명과 분리하면 **같은 서비스를 몇 번을 실행해도 같은 결과가 재현** 됩니다.

---

## 2. 실행 환경

| 항목 | 값 |
|---|---|
| OS | macOS 12.7.6 Monterey (Build 21H1320), Intel x86_64 |
| Shell | zsh (`/bin/zsh`) |
| Terminal | VSCode 통합 터미널 |
| Docker | Docker Desktop **4.41.2** (191736) · Docker Engine **28.1.1** · Compose **v2.35.1** |
| Git | **2.37.1** (Apple Git-137.1) |
| GitHub CLI | gh (계정 `ll-0l`) |

```bash
$ sw_vers
ProductName:	macOS
ProductVersion:	12.7.6
BuildVersion:	21H1320

$ echo $SHELL
/bin/zsh

$ docker --version
Docker version 28.1.1, build 4eba377

$ git --version
git version 2.37.1 (Apple Git-137.1)
```

> ⚠️ **환경 관련 주의 (재현성)**
> 과제 안내의 OrbStack 은 현재 버전이 **macOS 14 이상** 에서만 실행되어, macOS 12 에서는 **Docker Desktop 4.41.2** (Monterey 지원 마지막 버전) 를 사용했습니다. → [트러블슈팅 #1](#ts1)
> macOS 14 이상 / 캠퍼스 환경에서는 OrbStack 을 실행한 뒤 아래 명령을 **그대로** 사용하면 됩니다. (`docker` CLI 는 동일)

---

## 3. 저장소 구조

```text
codyssey-e1-1-dev-workstation/
├── README.md                    # 기술 문서 (이 파일)
├── app/                         # [필수] 커스텀 웹 서버 이미지
│   ├── Dockerfile               #   nginx:alpine 기반
│   ├── nginx/default.conf       #   /health, server_tokens off, X-Served-By 헤더
│   └── site/index.html          #   정적 페이지
├── mount-demo/index.html        # [필수] 바인드 마운트 실습용 (호스트에서 수정한 결과 v2)
├── practice/                    # [필수] 터미널·권한 실습 결과물
├── compose/                     # [보너스]
│   ├── single/docker-compose.yml    # 단일 서비스
│   ├── docker-compose.yml           # web + api 멀티 컨테이너
│   ├── .env                         # 포트/모드 설정 (민감정보 없음)
│   ├── api/ (Dockerfile, app.py)    # Python 표준 라이브러리 API
│   └── web/default.conf.template    # api 로 프록시하는 nginx 템플릿
└── docs/
    ├── logs/                    # 단계별 전체 터미널 로그 (명령 + 출력)
    └── images/                  # 스크린샷 (브라우저 · VSCode)
```

---

## 4. 수행 체크리스트

| # | 항목 | 상태 | 증거 |
|---|---|---|---|
| 1 | 터미널 기본 조작 (pwd/ls -la/cd/mkdir/cp/mv/rm/cat/touch) | ✅ | [6.1](#61-터미널-기본-조작) · [log](docs/logs/03-terminal.log) |
| 2 | 권한 변경 실습 (파일 + 디렉토리, 전/후 비교) | ✅ | [6.2](#62-권한-실습) · [log](docs/logs/04-permission.log) |
| 3 | Docker 설치 / 데몬 점검 | ✅ | [6.3](#63-docker-설치-및-점검) · [log](docs/logs/05-docker-check.log) |
| 4 | Docker 기본 운영 (images/ps/logs/stats) | ✅ | [6.4](#64-docker-기본-운영-명령) · [log](docs/logs/09-ops.log) |
| 5 | hello-world 실행 | ✅ | [6.5](#65-컨테이너-실행-실습-hello-world--ubuntu) |
| 6 | ubuntu 진입 · attach/exec 차이 정리 | ✅ | [6.5](#65-컨테이너-실행-실습-hello-world--ubuntu) · [log](docs/logs/07-ubuntu.log) |
| 7 | Dockerfile 커스텀 이미지 빌드/실행 | ✅ | [6.6](#66-dockerfile-기반-커스텀-이미지) · [log](docs/logs/08-build-run.log) |
| 8 | 포트 매핑 접속 (8080, 8081 두 번) | ✅ | [6.7](#67-포트-매핑-및-접속-증거) |
| 9 | 바인드 마운트 반영 | ✅ | [6.8](#68-바인드-마운트-호스트-변경-즉시-반영) · [log](docs/logs/10-mount-volume.log) |
| 10 | Docker 볼륨 영속성 | ✅ | [6.9](#69-docker-볼륨-영속성) · [log](docs/logs/10-mount-volume.log) |
| 11 | Git 설정 (`git config --list`) | ✅ | [6.10](#610-git-설정-및-githubvscode-연동) · [log](docs/logs/02-git.log) |
| 12 | VSCode GitHub 로그인 · 저장소 연동 | ✅ | [6.10](#610-git-설정-및-githubvscode-연동) |
| B1 | Compose 기초 (단일 서비스) | ✅ | [7.1](#71-compose-기초-단일-서비스) |
| B2 | Compose 멀티 컨테이너 + 네트워크 통신 | ✅ | [7.2](#72-compose-멀티-컨테이너--서비스-간-통신) |
| B3 | Compose 운영 명령 (up/down/ps/logs) | ✅ | [7.3](#73-compose-운영-루틴) |
| B4 | 환경 변수로 포트/모드 변경 | ✅ | [7.4](#74-환경-변수로-포트모드-변경) |
| B5 | GitHub SSH 키로 푸시 | ✅ | [7.5](#75-github-ssh-키) |

---

## 5. 빠른 재현 방법

> 사전 조건: Docker 엔진이 실행 중이어야 합니다 (`docker info` 가 에러 없이 출력되면 OK).

```bash
git clone https://github.com/ll-0l/codyssey-e1-1-dev-workstation.git
cd codyssey-e1-1-dev-workstation

# 1) 커스텀 이미지 빌드 → 두 포트로 실행
docker build -t codyssey-web:1.0 ./app
docker run -d -p 8080:80 --name web-8080 codyssey-web:1.0
docker run -d -p 8081:80 --name web-8081 codyssey-web:1.0
curl http://localhost:8080/health      # ok

# 2) 바인드 마운트 (현재 디렉토리 기준 상대 경로를 $(pwd) 로 절대 경로화)
docker run -d -p 8082:80 --name web-bind -v "$(pwd)/mount-demo":/usr/share/nginx/html:ro codyssey-web:1.0

# 3) 볼륨 영속성
docker volume create codyssey-data
docker run -d --name vol-test -v codyssey-data:/data ubuntu:22.04 sleep infinity
docker exec vol-test bash -lc 'echo hi > /data/hello.txt'
docker rm -f vol-test
docker run --rm -v codyssey-data:/data ubuntu:22.04 cat /data/hello.txt   # hi

# 4) (보너스) Compose
cd compose && docker compose up -d --build && curl http://localhost:8090/api/info

# 정리
docker compose down; cd ..
docker rm -f web-8080 web-8081 web-bind
docker volume rm codyssey-data
```

> 📌 포트 `8080~8082`, `8085`, `8090` 이 이미 사용 중이면 `-p <다른포트>:80` 또는 `compose/.env` 의 `WEB_PORT` 를 바꿔 실행하세요.

---

## 6. 수행 로그 및 검증

### 6.1 터미널 기본 조작

현재 위치 확인 → 생성 → 빈 파일/숨김 파일 생성 → 목록(숨김 포함) → 내용 확인 → 복사 → 이름변경/이동 → 상대·절대 경로 → 삭제 순으로 수행했습니다. ([전체 로그](docs/logs/03-terminal.log))

```bash
$ pwd
/Users/sin-uilyeong/Desktop/Codyssey/all-in-one/E1-1-dev-workstation

$ mkdir -p practice/docs practice/backup      # -p : 중간 경로까지 한 번에 생성
$ cd practice
$ pwd
/Users/sin-uilyeong/Desktop/Codyssey/all-in-one/E1-1-dev-workstation/practice

$ touch empty.txt                             # 빈 파일 생성
$ echo 'Hello, Codyssey!' > hello.txt
$ echo '터미널 실습 메모' > docs/memo.txt
$ touch .hidden_config                        # 숨김 파일 (.으로 시작)

$ ls                                          # 숨김 파일은 보이지 않음
backup
docs
empty.txt
hello.txt

$ ls -la                                      # -a : 숨김 파일 포함, -l : 상세
total 8
drwxr-xr-x  7 sin-uilyeong  staff  224 Nov 19 15:12 .
drwxr-xr-x  4 sin-uilyeong  staff  128 Nov 19 15:12 ..
-rw-r--r--  1 sin-uilyeong  staff    0 Nov 19 15:12 .hidden_config
drwxr-xr-x  2 sin-uilyeong  staff   64 Nov 19 15:12 backup
drwxr-xr-x  3 sin-uilyeong  staff   96 Nov 19 15:12 docs
-rw-r--r--  1 sin-uilyeong  staff    0 Nov 19 15:12 empty.txt
-rw-r--r--  1 sin-uilyeong  staff   17 Nov 19 15:12 hello.txt

$ cat hello.txt
Hello, Codyssey!
$ wc -c empty.txt                             # 빈 파일 = 0 byte
       0 empty.txt

$ cp hello.txt backup/hello_copy.txt          # 파일 복사
$ cp -r docs docs_copy                        # 디렉토리 복사 (-r 재귀)
$ mv hello.txt greeting.txt                   # 이름 변경
$ mv docs_copy backup/                        # 이동

$ cd backup
$ cat ../docs/memo.txt                        # 상대 경로 (현재 위치 기준)
터미널 실습 메모
$ cat /Users/sin-uilyeong/Desktop/Codyssey/all-in-one/E1-1-dev-workstation/practice/docs/memo.txt   # 절대 경로 (/ 부터)
터미널 실습 메모
$ cd ..

$ rm backup/hello_copy.txt                    # 파일 삭제
$ rm -r backup/docs_copy                      # 디렉토리 삭제
$ ls -la backup
total 0
drwxr-xr-x  2 sin-uilyeong  staff   64 Nov 19 15:12 .
drwxr-xr-x  7 sin-uilyeong  staff  224 Nov 19 15:12 ..
```

### 6.2 권한 실습

**권한 읽는 법** — `-rwxr-xr-x` = [종류][소유자 rwx][그룹 r-x][기타 r-x], 숫자는 `r=4, w=2, x=1` 의 합 → `755`. ([전체 로그](docs/logs/04-permission.log))

#### (1) 파일: `hello.sh` 실행 권한 644 → 755 → 600 → 644

```bash
$ ls -l hello.sh
-rw-r--r--  1 sin-uilyeong  staff  46 Nov 19 15:13 hello.sh
$ ./hello.sh
(eval):1: permission denied: ./hello.sh          # x 권한 없음 → 실행 불가

$ chmod 755 hello.sh
$ stat -f "%Sp %Lp %N" hello.sh
-rwxr-xr-x 755 hello.sh
$ ./hello.sh
script executed by sin-uilyeong                  # 실행 성공

$ chmod u-x,go-rx hello.sh                       # 기호 방식으로 변경
$ stat -f "%Sp %Lp %N" hello.sh
-rw------- 600 hello.sh                          # 소유자만 읽기/쓰기
```

#### (2) 파일: `greeting.txt` 쓰기 권한 644 → 444 → 644

```bash
$ chmod 444 greeting.txt
$ stat -f "%Sp %Lp %N" greeting.txt
-r--r--r-- 444 greeting.txt
$ echo 'append' >> greeting.txt
(eval):1: permission denied: greeting.txt        # w 없음 → 수정 불가
$ chmod 644 greeting.txt
$ echo 'append' >> greeting.txt && cat greeting.txt
Hello, Codyssey!
append
```

#### (3) 디렉토리: `docs` 755 → 555 → 311 → 644 → 755

| 권한 | `ls docs` (r: 목록) | `touch docs/new.txt` (w: 생성) | `cat docs/memo.txt` (x: 진입/접근) |
|---|---|---|---|
| `755` drwxr-xr-x | ✅ | ✅ | ✅ |
| `555` dr-xr-xr-x | ✅ | ❌ Permission denied | ✅ |
| `311` d-wx--x--x | ❌ Permission denied | – | ✅ (이름을 알면 접근 가능) |
| `644` drw-r--r-- | – | – | ❌ Permission denied |

```bash
$ chmod 555 docs
$ touch docs/new.txt
touch: docs/new.txt: Permission denied
$ chmod 311 docs
$ ls docs
ls: docs: Permission denied
$ cat docs/memo.txt
터미널 실습 메모
$ chmod 644 docs
$ cat docs/memo.txt
cat: docs/memo.txt: Permission denied
$ chmod 755 docs
$ touch docs/new.txt && ls -la docs
-rw-r--r--  1 sin-uilyeong  staff   24 Nov 19 15:12 memo.txt
-rw-r--r--  1 sin-uilyeong  staff    0 Nov 19 15:13 new.txt
```

> **관찰**: 디렉토리에서 `r` 은 "목록 보기", `w` 는 "안에 파일 만들기/지우기", `x` 는 "들어가서 안의 파일에 접근하기" 입니다. `x` 가 없으면 `r` 이 있어도 파일을 열 수 없습니다.

### 6.3 Docker 설치 및 점검

([전체 로그](docs/logs/05-docker-check.log))

```bash
$ docker --version
Docker version 28.1.1, build 4eba377

$ docker version
Client:
 Version:           28.1.1
 OS/Arch:           darwin/amd64
 Context:           desktop-linux
Server: Docker Desktop 4.41.2 (191736)
 Engine:
  Version:          28.1.1
  OS/Arch:          linux/amd64
 containerd:
  Version:          1.7.27
 runc:
  Version:          1.2.5

$ docker info --format '...'          # 데몬 응답 = 동작 중
Server Version: 28.1.1
Operating System: Docker Desktop
OSType/Arch: linux/x86_64
Kernel: 6.10.14-linuxkit
CPUs: 8  Memory: 8220110848
Storage Driver: overlayfs
Docker Root Dir: /var/lib/docker
```

> `docker version` 의 **Server** 항목과 `docker info` 가 정상 출력되면 CLI(클라이언트)가 데몬(서버)과 통신 중이라는 뜻입니다. 데몬이 꺼져 있으면 `Cannot connect to the Docker daemon` 에러가 납니다.

### 6.4 Docker 기본 운영 명령

([로그1](docs/logs/06-docker-basic.log) · [로그2](docs/logs/09-ops.log))

```bash
$ docker pull ubuntu:22.04
$ docker pull nginx:alpine
$ docker images
REPOSITORY    TAG       IMAGE ID       CREATED        SIZE
nginx         alpine    0563c36f94a6   14 hours ago   93.6MB
ubuntu        22.04     9abcaffc92a5   8 days ago     118MB
hello-world   latest    1e4c05b897a7   8 months ago   20.4kB

$ docker ps
CONTAINER ID   IMAGE              COMMAND                  CREATED          STATUS                    PORTS                  NAMES
775dd0cdf020   codyssey-web:1.0   "/docker-entrypoint.…"   12 seconds ago   Up 12 seconds (healthy)   0.0.0.0:8081->80/tcp   web-8081
7748f7cec1cb   codyssey-web:1.0   "/docker-entrypoint.…"   13 seconds ago   Up 12 seconds (healthy)   0.0.0.0:8080->80/tcp   web-8080

$ docker ps -a --filter name=ubuntu      # 종료된 컨테이너까지
CONTAINER ID   IMAGE          COMMAND   CREATED          STATUS                       NAMES
5506f113455a   ubuntu:22.04   "bash"    11 seconds ago   Exited (137) Less than a second ago   ubuntu-lab
569f5dafeff9   ubuntu:22.04   "bash"    12 seconds ago   Exited (0) 11 seconds ago             ubuntu-it

$ docker logs --tail 3 web-8080
2026/11/19 06:14:26 [notice] 1#1: start worker process 35
2026/11/19 06:14:26 [notice] 1#1: start worker process 36
192.168.65.1 - - [19/Nov/2026:06:14:38 +0000] "GET / HTTP/1.1" 200 964 "-" "curl/8.7.1" "-"

$ docker stats --no-stream
CONTAINER ID   NAME       CPU %     MEM USAGE / LIMIT     MEM %     NET I/O           BLOCK I/O     PIDS
775dd0cdf020   web-8081   0.00%     7.688MiB / 7.656GiB   0.10%     2.05kB / 1.18kB   0B / 8.19kB   9
7748f7cec1cb   web-8080   0.00%     7.617MiB / 7.656GiB   0.10%     1.97kB / 1.77kB   0B / 8.19kB   9

$ docker start ubuntu-lab     # 중지된 컨테이너 재시작
$ docker stop ubuntu-lab      # 실행 중 컨테이너 중지
```

### 6.5 컨테이너 실행 실습 (hello-world / ubuntu)

#### hello-world

```bash
$ docker run hello-world
Unable to find image 'hello-world:latest' locally
latest: Pulling from library/hello-world
...
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

#### ubuntu 내부 진입 후 명령 실행

([전체 로그](docs/logs/07-ubuntu.log))

```bash
$ docker run -it --name ubuntu-it ubuntu:22.04 bash
root@569f5dafeff9:/# cat /etc/os-release | head -2
PRETTY_NAME="Ubuntu 22.04.5 LTS"
NAME="Ubuntu"
root@569f5dafeff9:/# ls /
bin   dev  home  lib32  libx32  mnt  proc  run   srv  tmp  var
boot  etc  lib   lib64  media   opt  root  sbin  sys  usr
root@569f5dafeff9:/# echo "hello from container"
hello from container
root@569f5dafeff9:/# exit

$ docker ps -a --filter name=ubuntu-it
STATUS: Exited (0) Less than a second ago              # bash(PID 1) 종료 → 컨테이너 종료
```

#### attach vs exec 관찰

```bash
# 백그라운드로 bash 를 PID 1 로 띄워 둠
$ docker run -dit --name ubuntu-lab ubuntu:22.04 bash

# (1) exec : 새 프로세스를 추가로 실행
$ docker exec ubuntu-lab sh -c 'echo "exec works: $(hostname)"'
exec works: 5506f113455a
$ docker exec -it ubuntu-lab bash
root@5506f113455a:/# echo inside exec shell, PID1=$(cat /proc/1/comm)
inside exec shell, PID1=bash
root@5506f113455a:/# exit
$ docker ps --filter name=ubuntu-lab
STATUS: Up Less than a second                          # ✅ exec 셸을 나가도 컨테이너 유지

# (2) attach : PID 1 (메인 bash) 의 입출력에 직접 연결
$ docker attach ubuntu-lab
root@5506f113455a:/# echo attached to PID1 shell
attached to PID1 shell
root@5506f113455a:/# exit
$ docker ps -a --filter name=ubuntu-lab
STATUS: Exited (0) Less than a second ago              # ❌ attach 셸에서 exit → 컨테이너 종료
```

| 구분 | 연결 대상 | `exit` 시 | 용도 |
|---|---|---|---|
| `docker run -it` | 새로 만든 컨테이너의 PID 1 | 컨테이너 **종료** | 일회성 대화형 실행 |
| `docker exec -it` | 실행 중 컨테이너에 **추가 프로세스** | 그 프로세스만 종료, 컨테이너 **유지** | 운영 중 점검·디버깅 |
| `docker attach` | 실행 중 컨테이너의 **PID 1** | PID 1 종료 → 컨테이너 **종료** (`Ctrl+P, Ctrl+Q` 로 분리하면 유지) | 메인 프로세스 출력 확인 |

> 결론: 운영 중인 컨테이너에 들어갈 때는 **`exec`** 를 써야 서비스를 멈추지 않습니다.

### 6.6 Dockerfile 기반 커스텀 이미지

- **선택한 방식**: (A) 웹 서버 베이스 이미지 활용
- **기존 베이스**: 공식 [`nginx:alpine`](https://hub.docker.com/_/nginx) (경량 Alpine Linux + NGINX)

[`app/Dockerfile`](app/Dockerfile)

```dockerfile
FROM nginx:alpine

LABEL org.opencontainers.image.title="codyssey-web" \
      org.opencontainers.image.description="Codyssey E1-1 custom NGINX static site" \
      org.opencontainers.image.source="https://github.com/ll-0l/codyssey-e1-1-dev-workstation"
ENV APP_ENV=dev
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY site/ /usr/share/nginx/html/
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1/health || exit 1
EXPOSE 80
```

| 커스텀 포인트 | 목적 |
|---|---|
| `LABEL` (OCI 표준 키) | 이미지 이름·설명·소스 저장소를 메타데이터로 남겨 출처 추적 |
| `ENV APP_ENV=dev` | 실행 환경 구분값을 이미지에 기본값으로 포함 |
| `COPY nginx/default.conf` | `/health` 엔드포인트 추가, `server_tokens off`(버전 숨김), `X-Served-By` 헤더(응답한 컨테이너 식별) |
| `COPY site/` | 기본 "Welcome to nginx" 페이지를 내 정적 페이지로 교체 |
| `HEALTHCHECK` | `docker ps` 에서 `healthy/unhealthy` 로 서비스 상태 확인 |
| `EXPOSE 80` | 컨테이너가 사용하는 포트를 문서화 |

빌드 및 결과 확인 ([전체 로그](docs/logs/08-build-run.log))

```bash
$ docker build -t codyssey-web:1.0 ./app
#5 [1/3] FROM docker.io/library/nginx:alpine@sha256:0563c36f...
#7 [2/3] COPY nginx/default.conf /etc/nginx/conf.d/default.conf
#8 [3/3] COPY site/ /usr/share/nginx/html/
#9 exporting to image
#9 naming to docker.io/library/codyssey-web:1.0 done

$ docker images codyssey-web
REPOSITORY     TAG       IMAGE ID       CREATED                  SIZE
codyssey-web   1.0       eede143e5884   Less than a second ago   93.7MB

$ docker image inspect codyssey-web:1.0 --format '...'
Labels: {..."org.opencontainers.image.title":"codyssey-web"}
Env: [..., "APP_ENV=dev"]
Healthcheck: ["CMD-SHELL","wget -qO- http://127.0.0.1/health || exit 1"]
ExposedPorts: {"80/tcp":{}}

$ docker exec web-8080 printenv APP_ENV
dev
```

### 6.7 포트 매핑 및 접속 증거

`-p <호스트포트>:<컨테이너포트>` — 같은 이미지(컨테이너 내부는 둘 다 80)를 호스트의 **8080, 8081** 두 포트로 연결했습니다.

```bash
$ docker run -d -p 8080:80 --name web-8080 codyssey-web:1.0
$ docker run -d -p 8081:80 --name web-8081 codyssey-web:1.0

$ docker port web-8080
80/tcp -> 0.0.0.0:8080

$ curl -i http://localhost:8080
HTTP/1.1 200 OK
Server: nginx                       # 버전 숨김 (server_tokens off)
Content-Type: text/html
X-Served-By: 7748f7cec1cb           # web-8080 컨테이너 ID
...
<h1>Hello, Codyssey! 🐳</h1>

$ curl -sI http://localhost:8081 | grep -iE 'HTTP|Server|X-Served-By'
HTTP/1.1 200 OK
Server: nginx
X-Served-By: 775dd0cdf020           # web-8081 컨테이너 ID (다른 컨테이너가 응답)

$ curl -s http://localhost:8081/health
ok
```

**브라우저 접속 (주소창 포함)**

| `http://localhost:8080` | `http://localhost:8081` |
|---|---|
| ![8080 접속](docs/images/browser-8080.png) | ![8081 접속](docs/images/browser-8081.png) |

### 6.8 바인드 마운트 (호스트 변경 즉시 반영)

호스트 디렉토리 `mount-demo/` 를 컨테이너의 웹 루트에 **읽기 전용(`:ro`)** 으로 연결했습니다.

```bash
$ grep 'Page version' mount-demo/index.html
    <p>Page version: <span class="ver">bind-mount v1</span></p>

$ docker run -d -p 8082:80 --name web-bind \
    -v "$(pwd)/mount-demo":/usr/share/nginx/html:ro codyssey-web:1.0

$ docker inspect web-bind --format '{{range .Mounts}}{{.Type}}: {{.Source}} -> {{.Destination}} (RW={{.RW}}){{end}}'
bind: /Users/sin-uilyeong/Desktop/Codyssey/all-in-one/E1-1-dev-workstation/mount-demo -> /usr/share/nginx/html (RW=false)

# ── 변경 전 ──
$ curl -s http://localhost:8082 | grep 'Page version'
    <p>Page version: <span class="ver">bind-mount v1</span></p>

# 호스트에서 파일 수정 (컨테이너 재시작/재빌드 없음)
$ sed -i '' 's/bind-mount v1/bind-mount v2 (호스트에서 수정됨)/' mount-demo/index.html

# ── 변경 후 ──
$ curl -s http://localhost:8082 | grep 'Page version'
    <p>Page version: <span class="ver">bind-mount v2 (호스트에서 수정됨)</span></p>
$ docker exec web-bind grep 'Page version' /usr/share/nginx/html/index.html
    <p>Page version: <span class="ver">bind-mount v2 (호스트에서 수정됨)</span></p>

# :ro 이므로 컨테이너 안에서는 쓰기 불가
$ docker exec web-bind sh -c 'echo hack > /usr/share/nginx/html/x.txt'
sh: can't create /usr/share/nginx/html/x.txt: Read-only file system
```

| 구분 | 호스트 파일 | `curl :8082` 응답 |
|---|---|---|
| 변경 전 | `bind-mount v1` | `bind-mount v1` |
| 변경 후 | `bind-mount v2 (호스트에서 수정됨)` | `bind-mount v2 (호스트에서 수정됨)` ← 즉시 반영 |

> ⚠️ 바인드 마운트 경로는 PC 마다 다르므로 절대 경로를 하드코딩하지 않고 `"$(pwd)/mount-demo"` 를 사용했습니다. (경로에 공백이 있을 수 있어 큰따옴표 필수)

### 6.9 Docker 볼륨 영속성

```bash
# 1) 생성
$ docker volume create codyssey-data
codyssey-data
$ docker volume inspect codyssey-data
[
    {
        "Driver": "local",
        "Mountpoint": "/var/lib/docker/volumes/codyssey-data/_data",
        "Name": "codyssey-data",
        "Scope": "local"
    }
]

# 2) 연결 + 데이터 쓰기
$ docker run -d --name vol-test -v codyssey-data:/data ubuntu:22.04 sleep infinity
$ docker exec vol-test bash -lc 'echo "persisted at $(date -u +%FT%TZ) from $(hostname)" > /data/hello.txt && cat /data/hello.txt'
persisted at 2026-11-19T06:15:07Z from dcdaa81d579c

# 3) 컨테이너 삭제
$ docker rm -f vol-test
$ docker ps -a --filter name=vol-test
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES       # 컨테이너 없음
$ docker volume ls
DRIVER    VOLUME NAME
local     codyssey-data                                                      # 볼륨은 남아 있음

# 4) 새 컨테이너에 같은 볼륨 연결 → 데이터 유지 확인
$ docker run -d --name vol-test2 -v codyssey-data:/data ubuntu:22.04 sleep infinity
$ docker exec vol-test2 bash -lc 'hostname; cat /data/hello.txt'
d75cd493eb25                                         # 다른 컨테이너
persisted at 2026-11-19T06:15:07Z from dcdaa81d579c  # 이전 컨테이너가 쓴 데이터 그대로
```

**대조 실험 — 볼륨 없이 컨테이너 내부에 쓴 경우**

```bash
$ docker run -d --name novol-test ubuntu:22.04 sleep infinity
$ docker exec novol-test bash -lc 'echo temp > /tmp/temp.txt && cat /tmp/temp.txt'
temp
$ docker rm -f novol-test
$ docker run -d --name novol-test ubuntu:22.04 sleep infinity
$ docker exec novol-test bash -lc 'cat /tmp/temp.txt'
cat: /tmp/temp.txt: No such file or directory        # 컨테이너와 함께 사라짐
```

### 6.10 Git 설정 및 GitHub/VSCode 연동

([전체 로그](docs/logs/02-git.log))

```bash
$ git config --global init.defaultBranch main
$ git init
Initialized empty Git repository in .../E1-1-dev-workstation/.git/
$ git config user.email "299768439+ll-0l@users.noreply.github.com"   # 공개 저장소용 noreply 이메일 (이 저장소에만)

$ git branch --show-current
main

$ git config --list --show-origin     # (개인 이메일은 마스킹, Sourcetree 관련 항목 제외)
file:/Library/Developer/CommandLineTools/usr/share/git-core/gitconfig	credential.helper=osxkeychain
file:/Users/sin-uilyeong/.gitconfig	user.name=ryeong
file:/Users/sin-uilyeong/.gitconfig	user.email=<masked>@gmail.com
file:/Users/sin-uilyeong/.gitconfig	init.defaultbranch=main
file:.git/config	core.repositoryformatversion=0
file:.git/config	core.filemode=true
file:.git/config	core.bare=false
file:.git/config	core.logallrefupdates=true
file:.git/config	user.email=299768439+ll-0l@users.noreply.github.com
file:.git/config	remote.origin.url=git@github.com:ll-0l/codyssey-e1-1-dev-workstation.git
```

> `--show-origin` 으로 보면 같은 키(`user.email`)가 **전역(~/.gitconfig)** 과 **저장소(.git/config)** 에 모두 있는데, 저장소 설정이 우선합니다. 그래서 이 저장소의 커밋에는 noreply 이메일만 기록됩니다.

**VSCode GitHub 로그인 및 저장소 연동**

| VSCode 계정 (GitHub 로그인) | Source Control (원격 저장소 연동) |
|---|---|
| ![VSCode GitHub 로그인](docs/images/vscode-github-login.png) | ![VSCode 저장소 연동](docs/images/vscode-source-control.png) |

---

## 7. 보너스 과제

### 7.1 Compose 기초 (단일 서비스)

`docker run -d -p 8085:80 --name single-web codyssey-web:1.0` 을 파일로 옮긴 것입니다. → [`compose/single/docker-compose.yml`](compose/single/docker-compose.yml)

```yaml
name: codyssey-single
services:
  web:
    build: ../../app
    image: codyssey-web:1.0
    container_name: single-web
    ports:
      - "8085:80"
    restart: unless-stopped
```

```bash
$ cd compose/single
$ docker compose up -d
 Network codyssey-single_default  Created
 Container single-web  Started
$ docker compose ps
NAME         IMAGE              SERVICE   STATUS                                     PORTS
single-web   codyssey-web:1.0   web       Up Less than a second (health: starting)   0.0.0.0:8085->80/tcp
$ curl -s http://localhost:8085/health
ok
$ docker compose down
 Container single-web  Removed
 Network codyssey-single_default  Removed
```

> **배움 포인트** — 긴 `docker run` 옵션은 사람이 기억해서 매번 다시 입력해야 하지만, Compose 파일은 **저장소에 커밋되는 "실행 설정 문서"** 가 됩니다. 누구나 `docker compose up` 한 줄로 같은 구성을 재현할 수 있습니다. ([로그](docs/logs/11-compose-single.log))

### 7.2 Compose 멀티 컨테이너 + 서비스 간 통신

```text
 Browser ──► localhost:8090 ──► [web: nginx]  ──/api/──►  [api: python]
                                     │    codyssey_backend    │
                                     └──── (bridge network) ──┘
             호스트에는 web 만 공개, api(5000)는 내부 네트워크에서만 접근 가능
```

[`compose/docker-compose.yml`](compose/docker-compose.yml)

```yaml
name: codyssey
services:
  web:
    build: ../app                 # 본 과제의 커스텀 이미지 재사용
    image: codyssey-web:1.0
    ports:
      - "${WEB_PORT:-8090}:80"
    environment:
      API_PORT: ${API_PORT:-5000}
      NGINX_ENVSUBST_OUTPUT_DIR: /etc/nginx/conf.d
    volumes:
      - ./web/default.conf.template:/etc/nginx/templates/default.conf.template:ro
    depends_on:
      api:
        condition: service_healthy   # api 가 healthy 가 된 후 web 시작
    networks: [backend]
  api:
    build: ./api
    image: codyssey-api:1.0
    environment:
      PORT: ${API_PORT:-5000}
      APP_MODE: ${APP_MODE:-dev}
    expose:
      - "${API_PORT:-5000}"
    networks: [backend]
networks:
  backend: {}
```

```bash
$ docker compose up -d --build
 Container codyssey-api-1  Healthy
 Container codyssey-web-1  Started

$ docker compose ps
NAME             IMAGE              SERVICE   STATUS                    PORTS
codyssey-api-1   codyssey-api:1.0   api       Up 11 seconds (healthy)   5000/tcp
codyssey-web-1   codyssey-web:1.0   web       Up Less than a second     0.0.0.0:8090->80/tcp

# 호스트 → web → api (프록시)
$ curl -s http://localhost:8090/api/info
{"service": "api", "hostname": "4027929fedc5", "port": 5000, "mode": "dev", "time": "2026-11-19T06:16:07+00:00"}

# web 컨테이너 → api (서비스 이름으로 접근)
$ docker compose exec web wget -qO- http://api:5000/api/info
{"service": "api", "hostname": "4027929fedc5", "port": 5000, "mode": "dev", ...}

# api 컨테이너 → web (반대 방향)
$ docker compose exec api python -c "import urllib.request as u; print(u.urlopen('http://web/health').read().decode())"
ok

# 서비스 이름이 내부 DNS 로 IP 에 매핑됨
$ docker compose exec web nslookup api
Name:	api
Address: 172.18.0.2
$ docker network inspect codyssey_backend --format '{{range .Containers}}{{.Name}} {{.IPv4Address}}{{println}}{{end}}'
codyssey-web-1 172.18.0.3/16
codyssey-api-1 172.18.0.2/16

# api 는 호스트에 포트를 공개하지 않았으므로 직접 접근 불가
$ curl -s -m 3 http://localhost:5000/api/info || echo 'connection failed (expected)'
connection failed (expected)
```

> **배움 포인트** — 컨테이너 IP 는 실행할 때마다 바뀔 수 있지만, 같은 Compose 네트워크 안에서는 **서비스 이름(`api`, `web`)이 DNS 이름** 으로 등록되어 IP 를 몰라도 통신할 수 있습니다 (서비스 디스커버리). ([로그](docs/logs/12-compose-multi.log))

### 7.3 Compose 운영 루틴

| 단계 | 명령 | 확인 내용 |
|---|---|---|
| 기동 | `docker compose up -d --build` | 의존 순서대로 생성/시작 (api healthy → web) |
| 상태 | `docker compose ps` | STATUS(healthy 여부), PORTS |
| 로그 | `docker compose logs --tail 5 api` | 요청 처리/에러 여부 |
| 종료 | `docker compose down` | 컨테이너 + 네트워크 정리 |
| 확인 | `docker compose ps -a` | 남은 컨테이너 없음 |

```bash
$ docker compose logs --tail 5 api
api-1  | api server listening on 0.0.0.0:5000 (mode=dev)
api-1  | [dev] 127.0.0.1 "GET /health HTTP/1.1" 200 -
api-1  | [dev] 172.18.0.3 "GET /api/info HTTP/1.1" 200 -       # 요청자 = web 컨테이너 IP

$ docker compose down
 Container codyssey-web-1  Removed
 Container codyssey-api-1  Removed
 Network codyssey_backend  Removed
$ docker compose ps -a
NAME      IMAGE     COMMAND   SERVICE   CREATED   STATUS    PORTS
```

### 7.4 환경 변수로 포트/모드 변경

코드 · 이미지 수정 없이 **환경 변수만** 바꿔 재실행했습니다. ([로그](docs/logs/13-compose-env.log))

| 변수 | 기본값 (`.env`) | 변경값 | 영향 |
|---|---|---|---|
| `WEB_PORT` | 8090 | 8091 | 호스트 공개 포트 |
| `API_PORT` | 5000 | 7000 | api 리슨 포트 + nginx `proxy_pass` 대상 |
| `APP_MODE` | dev | prod | prod 에서는 요청 로그 미출력 |

```bash
$ cat .env
WEB_PORT=8090
API_PORT=5000
APP_MODE=dev

$ docker compose exec api printenv PORT APP_MODE
5000
dev
$ docker compose down

# 셸 환경 변수가 .env 보다 우선
$ WEB_PORT=8091 API_PORT=7000 APP_MODE=prod docker compose up -d
$ docker compose ps
codyssey-api-1   ...   Up 11 seconds (healthy)   7000/tcp
codyssey-web-1   ...   Up Less than a second     0.0.0.0:8091->80/tcp

$ curl -s http://localhost:8091/api/info
{"service": "api", "hostname": "09c57ae2fe1f", "port": 7000, "mode": "prod", "time": "2026-11-19T06:16:38+00:00"}

$ docker compose exec web grep proxy_pass /etc/nginx/conf.d/default.conf
        proxy_pass http://api:7000;           # nginx 템플릿이 시작 시 치환됨

$ docker compose logs api
api-1  | api server listening on 0.0.0.0:7000 (mode=prod)     # prod: 요청 로그 없음

$ curl -s -m 3 http://localhost:8090/health || echo '8090: connection failed (이제 8091 사용)'
8090: connection failed (이제 8091 사용)
```

> **배움 포인트** — "어디서 어떻게 실행할지"(포트·모드)는 **설정**, "무엇을 할지"는 **코드** 입니다. 둘을 분리하면 같은 이미지를 개발/운영 환경에 그대로 쓰고 설정만 바꿀 수 있습니다.

### 7.5 GitHub SSH 키

([로그](docs/logs/14-github-ssh.log))

```bash
$ ls ~/.ssh/*.pub
/Users/sin-uilyeong/.ssh/ll-0l-GitHub.pub          # 공개키만 표시 (개인키는 절대 공유 X)

$ ssh-keygen -lf ~/.ssh/ll-0l-GitHub.pub
4096 SHA256:<masked> Generated by Sourcetree on macOS for ll-0l-GitHub (RSA)

$ ssh -T git@github.com
Hi ll-0l! You've successfully authenticated, but GitHub does not provide shell access.

$ git remote -v                                   # HTTPS 가 아닌 SSH 주소
origin	git@github.com:ll-0l/codyssey-e1-1-dev-workstation.git (fetch)
origin	git@github.com:ll-0l/codyssey-e1-1-dev-workstation.git (push)

$ git push -u origin main
To github.com:ll-0l/codyssey-e1-1-dev-workstation.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
```

| 방식 | 인증 수단 | 특징 |
|---|---|---|
| HTTPS | 사용자 + **토큰(PAT)** / 자격 증명 관리자 | 방화벽 친화적, 토큰 만료·유출 관리 필요 |
| SSH | **공개키(GitHub 등록) + 개인키(로컬 보관)** | 비밀번호/토큰 전송 없음, 개인키만 안전하면 됨 |

> 기존에 등록해 둔 RSA 4096 키를 재사용했습니다. 새로 만든다면 `ssh-keygen -t ed25519 -C "<설명>"` 로 생성 후 `~/.ssh/<키>.pub` 내용을 GitHub → Settings → SSH and GPG keys 에 등록합니다.

---

## 8. 트러블슈팅

<a id="ts1"></a>
### #1 OrbStack 이 macOS 12 에서 설치되지 않음

| 단계 | 내용 |
|---|---|
| **문제** | 과제 안내대로 OrbStack 을 설치하려 했으나 macOS 12.7.6 (Monterey) 에서 실행 불가 |
| **원인 가설** | 최신 OrbStack 의 최소 지원 macOS 버전이 12 보다 높다 |
| **확인** | 설치 파일의 `Info.plist` 에서 최소 OS 버전 확인 → `LSMinimumSystemVersion = 14.0` |
| **해결/대안** | Monterey 를 지원하는 마지막 **Docker Desktop 4.41.2** 설치 (4.42 부터 macOS 13.3+ 필요). 서명(Team ID `9BNSXJN65R`, Docker Inc.) 확인 후 설치. **자동 업데이트를 끔** (업데이트 시 실행 불가 버전으로 올라가는 것 방지) |

```bash
$ curl -sSL -o OrbStack.dmg https://orbstack.dev/download/stable/latest/amd64
$ hdiutil attach -nobrowse -readonly -mountpoint ./mnt OrbStack.dmg
$ /usr/libexec/PlistBuddy -c "Print :LSMinimumSystemVersion" -c "Print :CFBundleShortVersionString" ./mnt/OrbStack.app/Contents/Info.plist
14.0          # 최소 macOS 14.0
2.2.5         # OrbStack 버전

$ codesign -dv ./mnt/Docker.app 2>&1 | grep TeamIdentifier      # Docker Desktop 4.41.2 서명 확인
TeamIdentifier=9BNSXJN65R
```

### #2 `docker exec` 결과에 컨테이너가 아니라 Mac 의 hostname 이 출력됨

| 단계 | 내용 |
|---|---|
| **문제** | 컨테이너 안의 hostname 을 출력하려 했는데 Mac 의 이름이 출력됨 |
| **원인 가설** | `$(hostname)` 이 컨테이너에 전달되기 **전에** 호스트 셸(zsh)에서 먼저 치환되었다 |
| **확인** | 큰따옴표 안의 `$( )` 는 호스트 셸이 해석함. 출력값이 Mac 이름과 동일 |
| **해결** | 명령 전체를 **작은따옴표** 로 감싸 컨테이너 안의 `sh -c` 가 해석하도록 변경 |

```bash
# ❌ 호스트에서 치환됨
$ docker exec ubuntu-lab echo "exec works: $(hostname)"
exec works: sin-uilyeong-ui-MacBookPro.local

# ✅ 컨테이너 안에서 치환됨
$ docker exec ubuntu-lab sh -c 'echo "exec works: $(hostname)"'
exec works: 5506f113455a
```

### #3 `docker stop` 이 10초나 걸리고 Exit code 137 로 종료됨

| 단계 | 내용 |
|---|---|
| **문제** | `docker stop ubuntu-lab` 이 약 10초 걸린 뒤 `Exited (137)` 상태가 됨 (nginx 컨테이너는 즉시 `Exited (0)`) |
| **원인 가설** | PID 1 로 실행된 `bash` 가 `SIGTERM` 을 무시 → 10초 유예 후 `SIGKILL` 로 강제 종료 (137 = 128 + 9(SIGKILL)) |
| **확인** | 리눅스에서 PID 1 은 시그널 핸들러가 없으면 기본 동작(종료)이 적용되지 않음. `docker ps -a` 에서 `Exited (137)` 확인 |
| **해결/대안** | 테스트용 컨테이너는 `docker stop -t 1` 로 유예 시간 단축. 실제 서비스는 시그널을 처리하는 프로세스(nginx 등)를 PID 1 로 두거나 `docker run --init` 사용 |

```bash
$ docker stop ubuntu-lab
$ docker ps -a --filter name=ubuntu
5506f113455a   ubuntu:22.04   "bash"   11 seconds ago   Exited (137) Less than a second ago   ubuntu-lab
```

---

## 9. 개념 정리 (과제 목표)

### 절대 경로 vs 상대 경로
- **절대 경로**: 루트(`/`)부터 시작. 현재 위치와 무관하게 항상 같은 대상
  `cat /Users/sin-uilyeong/Desktop/Codyssey/all-in-one/E1-1-dev-workstation/practice/docs/memo.txt`
- **상대 경로**: 현재 위치(`pwd`) 기준. `.` = 현재, `..` = 상위
  `practice/backup` 에서 `cat ../docs/memo.txt` → 같은 파일
- 실무 팁: 스크립트/문서에는 PC 마다 다른 절대 경로를 하드코딩하지 말고 `$(pwd)` 나 상대 경로를 사용 (이 README 의 바인드 마운트 예시)

### 파일 권한 r/w/x 와 755 / 644
- 3자리 숫자 = **소유자 / 그룹 / 기타**, 각 자리는 `r(4) + w(2) + x(1)` 의 합
- `755` = `rwx`(7) `r-x`(5) `r-x`(5) → 소유자만 수정, 모두 읽기·실행 (스크립트, 디렉토리)
- `644` = `rw-`(6) `r--`(4) `r--`(4) → 소유자만 수정, 모두 읽기 (일반 파일)
- 디렉토리에서는 r=목록, w=생성/삭제, x=진입/접근 ([6.2 표](#62-권한-실습) 참고)

### 기존 Dockerfile 기반 커스텀 이미지
- `FROM` 으로 검증된 베이스(`nginx:alpine`)를 그대로 가져오고, **바꾸고 싶은 부분만 레이어로 덧씌움** (`COPY` 설정/콘텐츠, `ENV`, `LABEL`, `HEALTHCHECK`)
- 베이스가 하는 일(nginx 설치·실행)을 다시 만들 필요가 없고, 내 변경점만 Dockerfile 에 명확히 남음

### 포트 매핑이 필요한 이유
- 컨테이너는 **격리된 네트워크** 를 갖기 때문에, 컨테이너의 80 포트는 호스트에서 바로 보이지 않음
- `-p 8080:80` 은 "호스트 8080 으로 들어온 요청을 컨테이너 80 으로 전달" 하는 연결 규칙
- 그래서 **같은 이미지(내부 80)를 여러 개 띄워도 호스트 포트만 다르게** 주면 충돌 없이 동시에 실행 가능 (8080/8081 실습)
- 반대로 공개할 필요가 없는 서비스(api)는 매핑하지 않아 외부 노출을 줄임 (7.2)

### Docker 볼륨 (영속 데이터)
- 컨테이너의 쓰기 레이어는 **컨테이너와 수명이 같아서** 삭제하면 데이터도 사라짐 (6.9 대조 실험)
- **볼륨** 은 Docker 가 관리하는 별도 저장 공간(`/var/lib/docker/volumes/...`)으로, 컨테이너를 지우고 새로 만들어도 다시 연결하면 데이터 유지
- **바인드 마운트** 는 호스트의 특정 경로를 그대로 연결 → 개발 중 소스 수정을 즉시 반영할 때 유용, 대신 호스트 경로에 의존

| | 바인드 마운트 | 볼륨 |
|---|---|---|
| 위치 | 호스트의 지정 경로 | Docker 관리 영역 |
| 주 용도 | 개발 중 코드/설정 실시간 반영 | DB 등 운영 데이터 영속화 |
| 이식성 | 호스트 경로 의존 | 이름만으로 사용 (이식성 ↑) |

### Git vs GitHub
- **Git**: 내 PC 에서 동작하는 **분산 버전 관리 도구**. 커밋/브랜치/이력 관리는 인터넷 없이도 가능
- **GitHub**: Git 저장소를 호스팅하는 **원격 협업 플랫폼**. 백업, 공유, PR/리뷰, 이슈, Actions(CI/CD) 등 제공
- 연결 고리: `git remote` 로 GitHub 주소를 등록하고 `git push/pull` 로 동기화 (인증은 HTTPS 토큰 또는 SSH 키)

---

## 10. 검증 방법 요약표

| 검증 대상 | 사용한 명령 | 기대 결과 (확인 포인트) | 증거 |
|---|---|---|---|
| 숨김 파일 | `ls -la` | `.hidden_config` 표시 | [6.1](#61-터미널-기본-조작) |
| 권한 변경 | `chmod` + `stat -f "%Sp %Lp"` | 전/후 권한 값 변화 + 실행/쓰기 성공·실패 | [6.2](#62-권한-실습) |
| 데몬 동작 | `docker info` | Server Version 등 출력 | [6.3](#63-docker-설치-및-점검) |
| 이미지 빌드 | `docker build`, `docker images`, `image inspect` | 태그 생성, LABEL/ENV/HEALTHCHECK 반영 | [6.6](#66-dockerfile-기반-커스텀-이미지) |
| 컨테이너 상태 | `docker ps` | `Up (healthy)` | [6.4](#64-docker-기본-운영-명령) |
| 포트 매핑 | `docker port`, `curl -i`, 브라우저 | 200 OK, 포트별 다른 `X-Served-By` | [6.7](#67-포트-매핑-및-접속-증거) |
| 바인드 마운트 | `sed` 수정 후 `curl` | v1 → v2 즉시 반영, `:ro` 쓰기 거부 | [6.8](#68-바인드-마운트-호스트-변경-즉시-반영) |
| 볼륨 영속성 | `rm -f` 후 새 컨테이너에서 `cat` | 이전 컨테이너가 쓴 내용 유지 | [6.9](#69-docker-볼륨-영속성) |
| Git 설정 | `git config --list --show-origin` | user.name/email, defaultbranch=main | [6.10](#610-git-설정-및-githubvscode-연동) |
| 서비스 간 통신 | `compose exec web wget http://api:5000` | api JSON 응답 | [7.2](#72-compose-멀티-컨테이너--서비스-간-통신) |
| 환경 변수 | `VAR=... docker compose up` + `printenv` | port 7000, mode prod | [7.4](#74-환경-변수로-포트모드-변경) |
| SSH 인증 | `ssh -T git@github.com`, `git push` | `Hi ll-0l!`, push 성공 | [7.5](#75-github-ssh-키) |

---

## 11. 보안 및 개인정보 처리

- **커밋 이메일**: 공개 저장소이므로 저장소 단위로 GitHub noreply 이메일 사용 (`git config user.email`), 문서 내 개인 이메일은 `<masked>` 처리
- **토큰**: `gh auth status` 출력의 토큰 값, SSH 키 지문(fingerprint)은 문서에 남기지 않음 (`<masked>`)
- **SSH 개인키**: 공개키(`.pub`) 경로만 표시, 개인키 내용은 다루지 않음
- **`.env`**: 포트/모드 같은 실행 설정만 포함. 비밀번호·API 키 등 민감정보는 넣지 않음 (넣어야 한다면 `.gitignore` 처리 후 `.env.example` 만 커밋)
- **스크린샷**: 계정 아이디 외 이메일·토큰·인증 코드가 보이지 않도록 확인 후 첨부
- 커밋 전 점검: `grep -rniE "ghp_|gho_|password|PRIVATE KEY" .` 로 민감 문자열 검사

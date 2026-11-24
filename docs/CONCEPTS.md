# 개념 정리 (과제 목표)

> ← [README 로 돌아가기](../README.md)

## 절대 경로 vs 상대 경로
- **절대 경로**: 루트(`/`)부터 시작. 현재 위치와 무관하게 항상 같은 대상
  `cat /Users/sin-uilyeong/Desktop/Codyssey/all-in-one/Codyssey all-in-one Pre-course/E1-1-dev-workstation/practice/docs/memo.txt`
- **상대 경로**: 현재 위치(`pwd`) 기준. `.` = 현재, `..` = 상위
  `practice/backup` 에서 `cat ../docs/memo.txt` → 같은 파일
- 실무 팁: 스크립트/문서에는 PC 마다 다른 절대 경로를 하드코딩하지 말고 `$(pwd)` 나 상대 경로를 사용 ([6.8 바인드 마운트](VERIFICATION.md#68-바인드-마운트-호스트-변경-즉시-반영) 예시)

<a id="os별-경로-차이"></a>
### OS별 경로 차이

| | macOS / Linux | Windows (PowerShell / CMD) |
|---|---|---|
| 절대 경로 예 | `/Users/me/project` , `/home/me/project` | `C:\Users\me\project` |
| 구분자 | `/` | `\` (PowerShell 은 `/` 도 허용) |
| 홈 디렉토리 | `~` , `$HOME` | `$HOME` / `%USERPROFILE%` |
| 현재 위치 | `$(pwd)` | PowerShell `${PWD}` , CMD `%cd%` |
| 대소문자 | Linux 는 구분, macOS 기본은 구분 안 함 | 구분 안 함 |
| 바인드 마운트 | `-v "$(pwd)/mount-demo":/usr/share/nginx/html` | `-v "${PWD}/mount-demo:/usr/share/nginx/html"` |

- **컨테이너 안쪽 경로는 OS 와 무관하게 항상 리눅스 형식**(`/usr/share/nginx/html`)입니다. 바뀌는 건 콜론 왼쪽의 호스트 경로뿐입니다.
- 경로에 공백이 있으면(이 저장소의 `Codyssey all-in-one Pre-course` 처럼) 반드시 따옴표로 감쌉니다.
- WSL2 를 쓰면 리눅스 경로(`/home/...`)에 프로젝트를 두는 편이 파일 I/O 와 변경 감지가 빠릅니다.

## 파일 권한 r/w/x 와 755 / 644
- 3자리 숫자 = **소유자 / 그룹 / 기타**, 각 자리는 `r(4) + w(2) + x(1)` 의 합
- `755` = `rwx`(7) `r-x`(5) `r-x`(5) → 소유자만 수정, 모두 읽기·실행 (스크립트, 디렉토리)
- `644` = `rw-`(6) `r--`(4) `r--`(4) → 소유자만 수정, 모두 읽기 (일반 파일)
- 디렉토리에서는 r=목록, w=생성/삭제, x=진입/접근 ([6.2 표](VERIFICATION.md#62-권한-실습) 참고)

### 특수 권한 비트 (4자리 표기의 맨 앞자리)

| 비트 | 숫자 | 표시 위치 | 의미 | 이 Mac 에서 확인한 예 |
|---|---|---|---|---|
| **setuid** | `4000` | 소유자 x 자리 → `s` | 실행하는 사람과 무관하게 **파일 소유자 권한**으로 실행 | `-r-s--x--x root /usr/bin/sudo` |
| **setgid** | `2000` | 그룹 x 자리 → `s` | 파일: **소유 그룹 권한**으로 실행 / 디렉토리: 안에 생기는 파일이 디렉토리 그룹을 상속 | `-rwxr-sr-x root _postdrop /usr/sbin/postdrop` |
| **sticky** | `1000` | 기타 x 자리 → `t` | 누구나 쓸 수 있는 디렉토리에서 **자기 파일만 삭제** 가능 | `drwxrwxrwt root /private/tmp` |

```bash
$ ls -l /usr/bin/sudo /usr/bin/login
-r-sr-xr-x  1 root  wheel   172000 Jul 17  2024 /usr/bin/login
-r-s--x--x  1 root  wheel  1461920 Jul 17  2024 /usr/bin/sudo
$ ls -l /usr/sbin/postdrop
-rwxr-sr-x  1 root  _postdrop  602144 Jul 17  2024 /usr/sbin/postdrop
$ ls -ld /private/tmp
drwxrwxrwt  39 root  wheel  1248 Nov 20 18:29 /private/tmp
```

- 예: `chmod 4755 file` → `-rwsr-xr-x`, `chmod 1777 dir` → `drwxrwxrwt`
- 대문자 `S`/`T` 는 특수 비트는 켜졌는데 해당 x 권한이 없는 상태입니다.
- setuid 는 권한 상승 경로가 될 수 있어 보안 점검 대상입니다 (`find / -perm -4000` 으로 목록 확인).

## 기존 Dockerfile 기반 커스텀 이미지
- `FROM` 으로 검증된 베이스(`nginx:alpine`)를 그대로 가져오고, **바꾸고 싶은 부분만 레이어로 덧씌움** (`COPY` 설정/콘텐츠, `ENV`, `LABEL`, `HEALTHCHECK`)
- 베이스가 하는 일(nginx 설치·실행)을 다시 만들 필요가 없고, 내 변경점만 Dockerfile 에 명확히 남음

### 이미지 빌드 vs 컨테이너 실행

| 관점 | 이미지 (`docker build`) | 컨테이너 (`docker run`) |
|---|---|---|
| 정체 | 읽기 전용 **레이어 묶음** (설계도) | 이미지 레이어 + **쓰기 가능한 레이어 1장** (실행 인스턴스) |
| 만들어지는 시점 | 빌드할 때 1번 | 실행할 때마다 새로 |
| 변경 | **불변**. 바꾸려면 Dockerfile 수정 → 재빌드 → 새 이미지 ID | 실행 중 파일 변경 가능, 단 **컨테이너 삭제 시 사라짐** |
| 개수 관계 | 1개 | 같은 이미지로 N개 (`web-8080`, `web-8081`) |
| 식별 | `codyssey-web:1.0` (태그) / IMAGE ID | 이름 (`web-8080`) / CONTAINER ID |
| 확인 명령 | `docker images`, `docker image inspect`, `docker history` | `docker ps -a`, `docker inspect`, `docker logs` |
| 삭제 | `docker rmi` (사용 중인 컨테이너가 있으면 거부, [6.4](VERIFICATION.md#64-docker-기본-운영-명령)) | `docker rm` |

- 실습 근거: `--no-cache` 재빌드 후 이미지 ID 가 `faca3eb4f6dd` 로 새로 생겼지만, 이미 실행 중이던 `web-8080` 은 **이전 이미지(4540c71ee18e)를 계속 사용** → 이미지를 바꿔도 컨테이너는 다시 만들어야 반영됨 ([로그](logs/17-rebuild-cleanup.log))
- 컨테이너 안에서 바꾼 내용이 사라지는 것: [6.9 대조 실험](VERIFICATION.md#69-docker-볼륨-영속성)

## 포트 매핑이 필요한 이유
- 컨테이너는 **격리된 네트워크** 를 갖기 때문에, 컨테이너의 80 포트는 호스트에서 바로 보이지 않음
- `-p 8080:80` 은 "호스트 8080 으로 들어온 요청을 컨테이너 80 으로 전달" 하는 연결 규칙
- 그래서 **같은 이미지(내부 80)를 여러 개 띄워도 호스트 포트만 다르게** 주면 충돌 없이 동시에 실행 가능 (8080/8081 실습)
- 반대로 공개할 필요가 없는 서비스(api)는 매핑하지 않아 외부 노출을 줄임 (7.2)

```text
                     호스트 (macOS)                                  컨테이너 (각자 별도 네트워크 네임스페이스)
 브라우저/curl ──► 0.0.0.0:8080 ─┐                               ┌─► web-8080  eth0:80  (nginx)
                                 ├─ Docker 포트 포워딩 (-p) ─────┤
 브라우저/curl ──► 0.0.0.0:8081 ─┘                               └─► web-8081  eth0:80  (nginx)
                    127.0.0.1:8084 ──────────────────────────────────► web-local eth0:80  (내 PC 에서만 접근)
                   (매핑 없음) ✕ ─────────────────────────────────────  api       :5000    (Compose 내부망 전용)
```

```bash
$ docker port web-8080                 # 매핑 규칙 확인
80/tcp -> 0.0.0.0:8080
$ docker port web-local
80/tcp -> 127.0.0.1:8084               # 바인딩 IP 까지 지정 가능 → 접근 범위 제한
```

- `0.0.0.0` = 호스트의 **모든 네트워크 인터페이스**에서 받음 (LAN 의 다른 기기도 접근 가능), `127.0.0.1` = **내 PC 에서만** ([6.7 상세 확인](VERIFICATION.md#67-포트-매핑-및-접속-증거))
- 포트가 이미 사용 중일 때의 진단은 [6.11](VERIFICATION.md#611-포트-충돌-진단-및-해결)

## Docker 볼륨 (영속 데이터)
- 컨테이너의 쓰기 레이어는 **컨테이너와 수명이 같아서** 삭제하면 데이터도 사라짐 (6.9 대조 실험)
- **볼륨** 은 Docker 가 관리하는 별도 저장 공간(`/var/lib/docker/volumes/...`)으로, 컨테이너를 지우고 새로 만들어도 다시 연결하면 데이터 유지
- **바인드 마운트** 는 호스트의 특정 경로를 그대로 연결 → 개발 중 소스 수정을 즉시 반영할 때 유용, 대신 호스트 경로에 의존

| | 바인드 마운트 | 볼륨 |
|---|---|---|
| 위치 | 호스트의 지정 경로 | Docker 관리 영역 |
| 주 용도 | 개발 중 코드/설정 실시간 반영 | DB 등 운영 데이터 영속화 |
| 이식성 | 호스트 경로 의존 | 이름만으로 사용 (이식성 ↑) |

## Git vs GitHub
- **Git**: 내 PC 에서 동작하는 **분산 버전 관리 도구**. 커밋/브랜치/이력 관리는 인터넷 없이도 가능
- **GitHub**: Git 저장소를 호스팅하는 **원격 협업 플랫폼**. 백업, 공유, PR/리뷰, 이슈, Actions(CI/CD) 등 제공
- 연결 고리: `git remote` 로 GitHub 주소를 등록하고 `git push/pull` 로 동기화 (인증은 HTTPS 토큰 또는 SSH 키)

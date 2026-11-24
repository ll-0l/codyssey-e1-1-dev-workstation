# 트러블슈팅

> ← [README 로 돌아가기](../README.md)
>
> 각 문제를 **문제 → 원인 가설 → 확인 → 해결 → 증거** 순서로 정리했습니다.

<a id="ts1"></a>
## #1 OrbStack 이 macOS 12 에서 설치되지 않음

| 단계 | 내용 |
|---|---|
| **문제** | 과제 안내대로 OrbStack 을 설치하려 했으나 macOS 12.7.6 (Monterey) 에서 실행 불가 |
| **원인 가설** | 최신 OrbStack 의 최소 지원 macOS 버전이 12 보다 높다 |
| **확인** | 설치 파일의 `Info.plist` 에서 최소 OS 버전 확인 → `LSMinimumSystemVersion = 14.0` |
| **해결/대안** | Monterey 를 지원하는 마지막 **Docker Desktop 4.41.2** 설치 (4.42 부터 macOS 13.3+ 필요). 서명(Team ID `9BNSXJN65R`, Docker Inc.) 확인 후 설치. **자동 업데이트를 끔** (업데이트 시 실행 불가 버전으로 올라가는 것 방지) |
| **증거** | 설치 후 버전·데몬 확인: [05-docker-check.log](logs/05-docker-check.log) · [6.3](VERIFICATION.md#63-docker-설치-및-점검) |

```bash
$ curl -sSL -o OrbStack.dmg https://orbstack.dev/download/stable/latest/amd64
$ hdiutil attach -nobrowse -readonly -mountpoint ./mnt OrbStack.dmg
$ /usr/libexec/PlistBuddy -c "Print :LSMinimumSystemVersion" -c "Print :CFBundleShortVersionString" ./mnt/OrbStack.app/Contents/Info.plist
14.0          # 최소 macOS 14.0
2.2.5         # OrbStack 버전

$ codesign -dv ./mnt/Docker.app 2>&1 | grep TeamIdentifier      # Docker Desktop 4.41.2 서명 확인
TeamIdentifier=9BNSXJN65R
```

<a id="ts2"></a>
## #2 `docker exec` 결과에 컨테이너가 아니라 Mac 의 hostname 이 출력됨

| 단계 | 내용 |
|---|---|
| **문제** | 컨테이너 안의 hostname 을 출력하려 했는데 Mac 의 이름이 출력됨 |
| **원인 가설** | `$(hostname)` 이 컨테이너에 전달되기 **전에** 호스트 셸(zsh)에서 먼저 치환되었다 |
| **확인** | 큰따옴표 안의 `$( )` 는 호스트 셸이 해석함. 출력값이 Mac 이름과 동일 |
| **해결** | 명령 전체를 **작은따옴표** 로 감싸 컨테이너 안의 `sh -c` 가 해석하도록 변경 |
| **증거** | 문제 발생: [07-ubuntu.log](logs/07-ubuntu.log) (`exec works: <Mac 이름>`) → 해결 확인: [07b-ubuntu-hostname.log](logs/07b-ubuntu-hostname.log) |

```bash
# ❌ 호스트에서 치환됨
$ docker exec ubuntu-lab echo "exec works: $(hostname)"
exec works: sin-uilyeong-ui-MacBookPro.local

# ✅ 컨테이너 안에서 치환됨
$ docker exec ubuntu-lab sh -c 'echo "exec works: $(hostname)"'
exec works: 5506f113455a
```

## #3 `docker stop` 이 10초나 걸리고 Exit code 137 로 종료됨

| 단계 | 내용 |
|---|---|
| **문제** | `docker stop ubuntu-lab` 이 약 10초 걸린 뒤 `Exited (137)` 상태가 됨 (nginx 컨테이너는 즉시 `Exited (0)`) |
| **원인 가설** | PID 1 로 실행된 `bash` 가 `SIGTERM` 을 무시 → 10초 유예 후 `SIGKILL` 로 강제 종료 (137 = 128 + 9(SIGKILL)) |
| **확인** | 리눅스에서 PID 1 은 시그널 핸들러가 없으면 기본 동작(종료)이 적용되지 않음. `docker ps -a` 에서 `Exited (137)` 확인 |
| **해결/대안** | 테스트용 컨테이너는 `docker stop -t 1` 로 유예 시간 단축. 실제 서비스는 시그널을 처리하는 프로세스(nginx 등)를 PID 1 로 두거나 `docker run --init` 사용 |
| **증거** | 137 종료: [07-ubuntu.log](logs/07-ubuntu.log) (`docker stop ubuntu-lab`) · `-t 1` 적용: [07b-ubuntu-hostname.log](logs/07b-ubuntu-hostname.log) |

```bash
$ docker stop ubuntu-lab
$ docker ps -a --filter name=ubuntu
5506f113455a   ubuntu:22.04   "bash"   11 seconds ago   Exited (137) Less than a second ago   ubuntu-lab
```

<a id="ts4"></a>
## #4 같은 포트로 컨테이너를 하나 더 띄우자 `port is already allocated`

| 단계 | 내용 |
|---|---|
| **문제** | `docker run -p 8080:80 --name web-dup ...` 실행 시 `Bind for 0.0.0.0:8080 failed: port is already allocated` |
| **원인 가설** | 호스트의 8080 을 다른 프로세스(또는 컨테이너)가 이미 LISTEN 중 |
| **확인** | `lsof -nP -iTCP:8080 -sTCP:LISTEN` → `com.docker.backend` (PID 1722), `netstat -anv` 로 동일 PID 확인, `docker ps --filter publish=8080` → `web-8080` 이 점유 |
| **해결/대안** | 기존 서비스를 유지할 땐 **대체 포트** `-p 8083:80`, 필요 없으면 `docker rm -f web-8080` 후 재실행. Docker 가 아닌 프로세스가 점유한 경우 `ps -p <PID>` 로 확인 후 `kill <PID>` |
| **증거** | [15-port-conflict.log](logs/15-port-conflict.log) · [6.11](VERIFICATION.md#611-포트-충돌-진단-및-해결) |

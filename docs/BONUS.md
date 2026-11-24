# 보너스 과제

> ← [README 로 돌아가기](../README.md)

## 7.1 Compose 기초 (단일 서비스)

`docker run -d -p 8085:80 --name single-web codyssey-web:1.0` 을 파일로 옮긴 것입니다. → [`compose/single/docker-compose.yml`](../compose/single/docker-compose.yml)

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

> **배움 포인트** — 긴 `docker run` 옵션은 사람이 기억해서 매번 다시 입력해야 하지만, Compose 파일은 **저장소에 커밋되는 "실행 설정 문서"** 가 됩니다. 누구나 `docker compose up` 한 줄로 같은 구성을 재현할 수 있습니다. ([로그](logs/11-compose-single.log))

## 7.2 Compose 멀티 컨테이너 + 서비스 간 통신

```text
 Browser ──► localhost:8090 ──► [web: nginx]  ──/api/──►  [api: python]
                                     │    codyssey_backend    │
                                     └──── (bridge network) ──┘
             호스트에는 web 만 공개, api(5000)는 내부 네트워크에서만 접근 가능
```

[`compose/docker-compose.yml`](../compose/docker-compose.yml)

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

> **배움 포인트** — 컨테이너 IP 는 실행할 때마다 바뀔 수 있지만, 같은 Compose 네트워크 안에서는 **서비스 이름(`api`, `web`)이 DNS 이름** 으로 등록되어 IP 를 몰라도 통신할 수 있습니다 (서비스 디스커버리). ([로그](logs/12-compose-multi.log))

## 7.3 Compose 운영 루틴

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

## 7.4 환경 변수로 포트/모드 변경

코드 · 이미지 수정 없이 **환경 변수만** 바꿔 재실행했습니다. ([로그](logs/13-compose-env.log))

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

## 7.5 GitHub SSH 키

([로그](logs/14-github-ssh.log))

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

$ git log --oneline -1                           # push 할 커밋
c9373a5 docs: E1-1 개발 워크스테이션 구축 결과물 및 기술 문서

$ git push -u origin main
To github.com:ll-0l/codyssey-e1-1-dev-workstation.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
```

> 첫 push 커밋 [`c9373a5`](https://github.com/ll-0l/codyssey-e1-1-dev-workstation/commit/c9373a5) 이후의 모든 커밋도 같은 SSH remote 로 push 했습니다. → [커밋 이력](https://github.com/ll-0l/codyssey-e1-1-dev-workstation/commits/main)

| 방식 | 인증 수단 | 특징 |
|---|---|---|
| HTTPS | 사용자 + **토큰(PAT)** / 자격 증명 관리자 | 방화벽 친화적, 토큰 만료·유출 관리 필요 |
| SSH | **공개키(GitHub 등록) + 개인키(로컬 보관)** | 비밀번호/토큰 전송 없음, 개인키만 안전하면 됨 |

> 기존에 등록해 둔 RSA 4096 키를 재사용했습니다. 새로 만든다면 `ssh-keygen -t ed25519 -C "<설명>"` 로 생성 후 `~/.ssh/<키>.pub` 내용을 GitHub → Settings → SSH and GPG keys 에 등록합니다.

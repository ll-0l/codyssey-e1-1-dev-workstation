# 기존 베이스 이미지: 공식 NGINX 이미지(alpine 변형, 경량)
FROM nginx:alpine

# [커스텀 1] 이미지 메타데이터 - 누가/무엇을 위한 이미지인지 기록
LABEL org.opencontainers.image.title="codyssey-web" \
      org.opencontainers.image.description="Codyssey E1-1 custom NGINX static site" \
      org.opencontainers.image.source="https://github.com/ll-0l/codyssey-e1-1-dev-workstation"

# [커스텀 2] 환경 변수 - 실행 환경 구분값(컨테이너 안에서 확인 가능)
ENV APP_ENV=dev

# [커스텀 3] 서버 설정 교체 - /health 엔드포인트, 버전 정보 숨김, 응답 헤더 추가
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# [커스텀 4] 정적 콘텐츠 교체 - 기본 "Welcome to nginx" 페이지 대신 내 페이지
COPY site/ /usr/share/nginx/html/

# [커스텀 5] 헬스체크 - 컨테이너 상태를 docker ps 에서 healthy/unhealthy 로 확인
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1/health || exit 1

EXPOSE 80

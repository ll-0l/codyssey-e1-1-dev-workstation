FROM python:3.12-alpine

# 기본값. 실제 값은 docker-compose.yml / .env 에서 주입한다 (설정과 코드의 분리)
ENV PORT=5000 \
    APP_MODE=dev \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY app.py .

# root 대신 일반 사용자로 실행
RUN adduser -D -H appuser
USER appuser

HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD wget -qO- "http://127.0.0.1:${PORT}/health" || exit 1

CMD ["python", "app.py"]

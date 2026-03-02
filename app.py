import requests
import datetime
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 주소가 동일하게 설정되어 있는데, 나중에 다른 채널을 쓰시려면 URL을 바꿔주세요.
MASKED_CHANNEL_URL = "https://discord.com/api/webhooks/1477910235048968275/otX6RnzhUAWP3WJRe8A_wMAQ9hWyLPSoY3kIAhYC__CIr87A1bXqoRLyWpeHnTsRPA_v"
RAW_CHANNEL_URL = "https://discord.com/api/webhooks/1477910235048968275/otX6RnzhUAWP3WJRe8A_wMAQ9hWyLPSoY3kIAhYC__CIr87A1bXqoRLyWpeHnTsRPA_v"

def get_masked_ip(ip):
    """IP 뒷자리를 가려주는 함수 (안전장치 추가)"""
    try:
        # Render에서 오는 IP 중 첫 번째 것만 추출
        clean_ip = ip.split(',')[0].strip()
        parts = clean_ip.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.xxx.xxx"
        return clean_ip
    except:
        return "Unknown"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def send_to_discord():
    try:
        client_data = request.json or {}
        
        # Render 환경 맞춤형 IP 추출
        raw_ip_header = request.headers.get('X-Forwarded-For', request.remote_addr)
        raw_ip = raw_ip_header.split(',')[0].strip() if raw_ip_header else "Unknown"
        
        masked_ip = get_masked_ip(raw_ip)
        user_agent = request.headers.get('User-Agent', 'Unknown')
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 공통 필드 생성 함수
        def create_embed(ip_value, title_prefix, color):
            return {
                "username": f"{title_prefix} 관제 시스템",
                "embeds": [{
                    "title": f"🌐 {title_prefix}: 방문자 접속 기록",
                    "color": color,
                    "fields": [
                        {"name": "📍 접속 IP", "value": f"`{ip_value}`", "inline": False},
                        {"name": "🌍 브라우저 언어", "value": f"`{client_data.get('language', 'N/A')}`", "inline": False},
                        {"name": "🖥️ 화면 해상도", "value": f"`{client_data.get('screen', 'N/A')}`", "inline": False},
                        {"name": "⚙️ 플랫폼", "value": f"`{client_data.get('platform', 'N/A')}`", "inline": False},
                        {"name": "🔗 유입 경로", "value": f"`{request.referrer or '직접 접속'}`", "inline": False},
                        {"name": "🕵️ 상세 정보", "value": f"```{user_agent}```", "inline": False}
                    ],
                    "footer": {"text": f"기록 시각: {timestamp}"}
                }]
            }

        # 1. IP 가린 버전 전송
        masked_payload = create_embed(masked_ip, "일반 모니터링", 5763719)
        res1 = requests.post(MASKED_CHANNEL_URL, json=masked_payload)
        print(f"Masked Webhook Response: {res1.status_code}")

        # 2. IP 원본 버전 전송
        raw_payload = create_embed(raw_ip, "보안 관리자", 15548997)
        res2 = requests.post(RAW_CHANNEL_URL, json=raw_payload)
        print(f"Raw Webhook Response: {res2.status_code}")

    except Exception as e:
        # 에러 발생 시 로그에 출력하여 원인 파악
        print(f"Webhook Error: {str(e)}")

    return jsonify({"status": "success"})

if __name__ == '__main__':
    # Render 환경 호환 설정
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

import requests
import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 각 채널의 웹훅 URL을 입력하세요
MASKED_CHANNEL_URL = "https://discord.com/api/webhooks/1477910235048968275/otX6RnzhUAWP3WJRe8A_wMAQ9hWyLPSoY3kIAhYC__CIr87A1bXqoRLyWpeHnTsRPA_v"
RAW_CHANNEL_URL = "https://discord.com/api/webhooks/1477910235048968275/otX6RnzhUAWP3WJRe8A_wMAQ9hWyLPSoY3kIAhYC__CIr87A1bXqoRLyWpeHnTsRPA_v"

def get_masked_ip(ip):
    """IP 뒷자리를 가려주는 함수"""
    parts = ip.split('.')
    if len(parts) == 4:
        return f"{parts[0]}.{parts[1]}.xxx.xxx"
    return "Unknown"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def send_to_discord():
    client_data = request.json
    
    # 기본 데이터 추출
    raw_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    masked_ip = get_masked_ip(raw_ip)
    user_agent = request.headers.get('User-Agent')
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 공통 필드 생성 함수 (중복 코드 방지)
    def create_embed(ip_value, title_prefix, color):
        return {
            "username": f"{title_prefix} 관제 시스템",
            "embeds": [{
                "title": f"🌐 {title_prefix}: 방문자 접속 기록",
                "color": color,
                "fields": [
                    {"name": "📍 접속 IP", "value": f"`{ip_value}`", "inline": False},
                    {"name": "🌍 브라우저 언어", "value": f"`{client_data.get('language')}`", "inline": False},
                    {"name": "🖥️ 화면 해상도", "value": f"`{client_data.get('screen')}`", "inline": False},
                    {"name": "⚙️ 플랫폼", "value": f"`{client_data.get('platform')}`", "inline": False},
                    {"name": "🔗 유입 경로", "value": f"`{request.referrer or '직접 접속'}`", "inline": False},
                    {"name": "🕵️ 상세 정보", "value": f"```{user_agent}```", "inline": False}
                ],
                "footer": {"text": f"기록 시각: {timestamp}"}
            }]
        }

    # 1. IP 가린 버전 전송 (MASKED_CHANNEL_URL)
    masked_payload = create_embed(masked_ip, "일반 모니터링", 5763719) # 초록색
    requests.post(MASKED_CHANNEL_URL, json=masked_payload)

    # 2. IP 원본 버전 전송 (RAW_CHANNEL_URL)
    raw_payload = create_embed(raw_ip, "보안 관리자", 15548997) # 빨간색
    requests.post(RAW_CHANNEL_URL, json=raw_payload)

    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
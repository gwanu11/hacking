# 새 URL로 교체 필수!
NEW_URL = "https://discord.com/api/webhooks/1477918744222367805/byxyOVzR83kgiOPbNjHE-54G8Ta94AtfIipDb-6wobO1NvUSreqfJjdzQwcuqiwmKtCU"
PROXY = "http://mkmp3kpf:pka5tdl4@p.tokenu.to:10008" # 포트 변경

try:
    # 1. 프록시가 진짜 작동하는지 확인
    my_real_ip = requests.get("https://api.ipify.org", proxies={"http": PROXY, "https": PROXY}).text
    print(f"현재 나가는 IP: {my_real_ip}") # 이게 렌더 IP가 아니어야 함

    # 2. 새 주소로 전송
    res = requests.post(NEW_URL, json={"content": "프록시 테스트"}, proxies={"http": PROXY, "https": PROXY})
    print(f"결과: {res.status_code}")
except Exception as e:
    print(f"에러: {e}")

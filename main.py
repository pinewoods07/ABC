# main.py
import network
import socket
import time
import uasyncio as asyncio
from machine import Pin
from huskylensPythonLibrary import HuskyLensLibrary

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [와이파이 설정] 당곡고 교실이나 집의 와이파이 정보를 적어주세요!
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SSID = "app"          # 와이파이 이름
PASSWORD = "20242024"  # 와이파이 비밀번호

# 실시간 감지 상태를 저장하는 전역 변수
detected_id = 0
detected_name = "감지 안 됨"
coord_x = 0
coord_y = 0

# 사물 분류 ID 매핑 테이블
object_map = {
    1: "사과",
    2: "자동차",
    3: "별",
    4: "우산",
    5: "연필",
    6: "새",
    7: "고양이",
    8: "집",
    9: "나무",
    10: "바나나"
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [검증 웹사이트 HTML 템플릿]
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>👁️ 당곡고 허스키렌즈 Wi-Fi 검증 센터</title>
    <style>
        body {
            font-family: 'Malgun Gothic', -apple-system, sans-serif;
            background-color: #f0f4f8;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 90vh;
        }
        .container {
            max-width: 480px;
            width: 100%;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.08);
            padding: 30px;
            box-sizing: border-box;
            text-align: center;
        }
        h1 {
            color: #1a73e8;
            font-size: 1.8rem;
            margin-bottom: 5px;
        }
        .subtitle {
            color: #5f6368;
            font-size: 0.9rem;
            margin-bottom: 25px;
        }
        .card {
            background-color: #f8f9fa;
            border: 2px solid #e8eaed;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        .card.active {
            background-color: #e8f0fe;
            border-color: #1a73e8;
        }
        .indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            background-color: #dadce0;
            border-radius: 50%;
            margin-right: 8px;
        }
        .indicator.active {
            background-color: #34a853;
            box-shadow: 0 0 8px #34a853;
        }
        .status-header {
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: #5f6368;
            font-size: 0.95rem;
        }
        .object-name {
            font-size: 2.8rem;
            font-weight: 800;
            color: #202124;
            margin: 20px 0;
        }
        .info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            text-align: left;
        }
        .info-box {
            background-color: #f1f3f4;
            padding: 12px;
            border-radius: 8px;
        }
        .info-label {
            font-size: 0.75rem;
            color: #5f6368;
            margin-bottom: 4px;
        }
        .info-value {
            font-size: 1.1rem;
            font-weight: bold;
            color: #202124;
        }
        .footer {
            margin-top: 25px;
            font-size: 0.8rem;
            color: #9aa0a6;
        }
    </style>
</head>
<body>

<div class="container">
    <h1>👁️ 허스키렌즈 검증 센터</h1>
    <div class="subtitle">실시간 와이파이 센서 감지 모니터링</div>

    <div class="card" id="statusCard">
        <div class="status-header">
            <span class="indicator" id="statusIndicator"></span>
            <span id="statusText">탐색 중...</span>
        </div>
        <div class="object-name" id="objectName">대기 중</div>
    </div>

    <div class="info-grid">
        <div class="info-box">
            <div class="info-label">학습 ID</div>
            <div class="info-value" id="idVal">-</div>
        </div>
        <div class="info-box">
            <div class="info-label">업데이트 주기</div>
            <div class="info-value">300ms</div>
        </div>
        <div class="info-box">
            <div class="info-label">중심 X 좌표</div>
            <div class="info-value" id="xVal">-</div>
        </div>
        <div class="info-box">
            <div class="info-label">중심 Y 좌표</div>
            <div class="info-value" id="yVal">-</div>
        </div>
    </div>

    <div class="footer">
        당곡고등학교 하드웨어-AI 실습 프로젝트
    </div>
</div>

<script>
    // 0.3초마다 피코 2 서버에 비동기(AJAX) 요청을 보내 상태를 갱신합니다.
    async function fetchSensorData() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();

            const statusCard = document.getElementById('statusCard');
            const statusIndicator = document.getElementById('statusIndicator');
            const statusText = document.getElementById('statusText');
            const objectName = document.getElementById('objectName');
            const idVal = document.getElementById('idVal');
            const xVal = document.getElementById('xVal');
            const yVal = document.getElementById('yVal');

            if (data.id > 0) {
                statusCard.classList.add('active');
                statusIndicator.classList.add('active');
                statusText.textContent = "사물 인식 완료!";
                objectName.textContent = data.name;
                idVal.textContent = "ID " + data.id;
                xVal.textContent = data.x + " px";
                yVal.textContent = data.y + " px";
            } else {
                statusCard.classList.remove('active');
                statusIndicator.classList.remove('active');
                statusText.textContent = "새로운 사물 탐색 중...";
                objectName.textContent = "감지 안 됨 🔍";
                idVal.textContent = "없음";
                xVal.textContent = "-";
                yVal.textContent = "-";
            }
        } catch (error) {
            console.error("데이터 갱신 오류:", error);
        }
    }

    // 주기적 호출 시작
    setInterval(fetchSensorData, 300);
</script>

</body>
</html>
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [와이파이 연결 함수]
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    print("📶 Wi-Fi 연결 중...", end="")
    max_wait = 15
    while max_wait > 0:
        # 3은 STAT_GOT_IP(IP 할당 성공)을 의미합니다.
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print(".", end="")
        time.sleep(1)
        
    if wlan.isconnected():
        status = wlan.ifconfig()
        print("\n✅ Wi-Fi 연결 성공!")
        print(f"🔗 접속할 기기 IP 주소: {status[0]}")
        return status[0]
    else:
        print("\n❌ 연결 실패. (시리얼 출력 모드로만 작동합니다.)")
        return None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [허스키렌즈 실시간 측정 비동기 루프]
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def poll_huskylens(husky, led):
    global detected_id, detected_name, coord_x, coord_y
    print("📷 허스키렌즈 감지 센서 작동 시작...")
    
    while True:
        try:
            # I2C 통신으로 블록 데이터 가져오기 (비동기 루프를 방해하지 않는 수준)
            result = husky.command_request_blocks()
            if result:
                for obj in result:
                    x, y, w, h, obj_id = obj
                    if obj_id > 0:
                        detected_id = obj_id
                        detected_name = object_map.get(obj_id, "알 수 없는 사물 ❓")
                        coord_x = x
                        coord_y = y
                        led.on() # 정상 인식 시 초록 LED ON
                    else:
                        detected_id = 0
                        detected_name = "학습되지 않은 사물"
                        coord_x = 0
                        coord_y = 0
                        led.off()
                    break # 첫 번째 물체 기준값만 전송
            else:
                detected_id = 0
                detected_name = "감지 안 됨"
                coord_x = 0
                coord_y = 0
                led.off()
        except Exception as e:
            # 일시적인 센서 통신 노이즈 발생 시 무시하고 진행
            pass
            
        # 다른 비동기 테스크(웹 통신 등)에 CPU를 일시 양보합니다.
        await asyncio.sleep(0.1)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [비동기 웹 서버 클라이언트 처리기]
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def handle_client(reader, writer):
    global detected_id, detected_name, coord_x, coord_y
    
    try:
        # 첫 번째 요청 헤더 라인 파싱
        request_line = await reader.readline()
        # 남은 패킷 헤더 버퍼 비우기
        while True:
            line = await reader.readline()
            if line == b'\r\n' or line == b'\n' or not line:
                break
                
        request = request_line.decode('utf-8')
        
        # 1. API 데이터 요청 처리 (JSON 리턴)
        if "GET /api/status" in request:
            # JSON 포맷으로 실시간 정보 제공
            json_response = '{"id": %d, "name": "%s", "x": %d, "y": %d}' % (
                detected_id, detected_name, coord_x, coord_y
            )
            writer.write(b"HTTP/1.1 200 OK\r\n")
            writer.write(b"Content-Type: application/json; charset=utf-8\r\n")
            writer.write(b"Connection: close\r\n\r\n")
            writer.write(json_response.encode('utf-8'))
            
        # 2. 메인 페이지 요청 처리 (HTML 리턴)
        else:
            writer.write(b"HTTP/1.1 200 OK\r\n")
            writer.write(b"Content-Type: text/html; charset=utf-8\r\n")
            writer.write(b"Connection: close\r\n\r\n")
            writer.write(HTML_TEMPLATE.encode('utf-8'))
            
        await writer.drain()
    except Exception as e:
        print("서버 전송 중 에러 발생:", e)
    finally:
        writer.close()
        await writer.wait_closed()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [메인 실행 제어기]
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def main():
    # 1. 내장 LED 및 허스키렌즈 통신 초기화
    led = Pin("LED", Pin.OUT)
    husky = HuskyLensLibrary("I2C")
    await asyncio.sleep(0.5)
    
    # 사물 분류 모드로 초기화
    husky.command_request_algorthim("ALGORITHM_OBJECT_CLASSIFICATION")
    await asyncio.sleep(0.5)

    # 2. Wi-Fi 연결 시도
    ip_addr = connect_wifi(SSID, PASSWORD)
    
    # 3. 비동기 Task 스케줄에 센서 폴링 태스크 등록
    asyncio.create_task(poll_huskylens(husky, led))
    
    # 4. 와이파이 연결 성공 시에만 웹 서버 구동
    if ip_addr:
        print(f"📢 스마트폰/컴퓨터 주소창에 다음을 입력하세요 ➡️ http://{ip_addr}")
        # 포트 80(기본 HTTP 포트)으로 서버 열기
        server = await asyncio.start_server(handle_client, "0.0.0.0", 80)
        
        while True:
            await asyncio.sleep(3600) # 서버 백그라운드 무한 대기
    else:
        # Wi-Fi가 없으면 시리얼(Thonny) 모니터 전용 모드로 전환
        while True:
            print(f"📡 시리얼 확인용 모드 -> {detected_name} (ID: {detected_id})")
            await asyncio.sleep(1)

# 시스템 진입점 설정
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\n시스템이 수동 종료되었습니다.")

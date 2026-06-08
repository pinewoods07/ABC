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

# 사물 분류 ID 매핑 테이블 (학생의 6가지 사물 그대로 적용)
object_map = {
    1: "사과",
    2: "자동차",
    3: "별",
    4: "우산",
    5: "의자",
    6: "핸드폰",
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [대폭 업그레이드된 게임 및 검증 웹사이트 HTML 템플릿]
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎮 당곡고 AI 드로잉 챌린지</title>
    <style>
        body {
            font-family: 'Malgun Gothic', -apple-system, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 95vh;
            color: #333;
        }
        .container {
            max-width: 500px;
            width: 100%;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 24px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.3);
            padding: 30px;
            box-sizing: border-box;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        h1 {
            color: #1e3c72;
            font-size: 2.2rem;
            margin: 0 0 5px 0;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        .subtitle {
            color: #666;
            font-size: 0.95rem;
            margin-bottom: 25px;
            font-weight: bold;
        }
        
        /* 메인 게임 보드 패널 */
        .game-card {
            background-color: #f8f9fa;
            border: 4px solid #1e3c72;
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 20px;
            position: relative;
            overflow: hidden;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .game-card.playing {
            border-color: #e67e22;
            background-color: #fdfaf6;
        }
        .game-card.solved {
            border-color: #2ecc71;
            background-color: #ebfaf0;
            box-shadow: 0 0 20px rgba(46, 204, 113, 0.5);
        }
        .game-card.gameover {
            border-color: #e74c3c;
            background-color: #fdf5f5;
        }

        .status-badge {
            display: inline-block;
            background: #1e3c72;
            color: white;
            padding: 6px 15px;
            border-radius: 30px;
            font-size: 0.85rem;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .game-card.solved .status-badge { background: #2ecc71; }
        .game-card.playing .status-badge { background: #e67e22; }
        .game-card.gameover .status-badge { background: #e74c3c; }

        /* 룰렛 단어 영역 */
        .quiz-word {
            font-size: 3.5rem;
            font-weight: 900;
            color: #2c3e50;
            margin: 15px 0;
            min-height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.1s ease;
        }
        .quiz-word.rolling {
            animation: shake 0.1s infinite;
            color: #7f8c8d;
        }
        
        /* 정보 그리드 */
        .stats-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 25px;
        }
        .stat-box {
            background: #f1f3f5;
            border-radius: 14px;
            padding: 12px;
            border: 1px solid #dee2e6;
        }
        .stat-label {
            font-size: 0.8rem;
            color: #666;
            margin-bottom: 5px;
            text-transform: uppercase;
        }
        .stat-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: #1e3c72;
        }
        
        /* 타이머 프로그레스 바 */
        .timer-container {
            width: 100%;
            height: 10px;
            background-color: #e9ecef;
            border-radius: 5px;
            margin-bottom: 25px;
            overflow: hidden;
        }
        .timer-bar {
            height: 100%;
            width: 100%;
            background-color: #2ecc71;
            transition: width 1s linear, background-color 0.5s;
            border-radius: 5px;
        }

        /* 컨트롤 버튼들 */
        .btn {
            background-color: #1e3c72;
            color: white;
            border: none;
            padding: 14px 28px;
            font-size: 1.15rem;
            font-weight: bold;
            border-radius: 12px;
            cursor: pointer;
            width: 100%;
            transition: all 0.2s;
            box-shadow: 0 4px 10px rgba(30, 60, 114, 0.3);
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(30, 60, 114, 0.4);
        }
        .btn:active {
            transform: translateY(1px);
        }
        .btn-next {
            background-color: #2ecc71;
            box-shadow: 0 4px 10px rgba(46, 204, 113, 0.3);
        }
        .btn-next:hover {
            background-color: #27ae60;
            box-shadow: 0 6px 15px rgba(46, 204, 113, 0.4);
        }
        
        .realtime-text {
            font-size: 0.85rem;
            color: #7f8c8d;
            margin-top: 15px;
            font-style: italic;
        }

        @keyframes shake {
            0% { transform: translate(1px, 1px) rotate(0deg); }
            10% { transform: translate(-1px, -1px) rotate(-1deg); }
            20% { transform: translate(-2px, 0px) rotate(1deg); }
            30% { transform: translate(0px, 1px) rotate(0deg); }
            40% { transform: translate(1px, -1px) rotate(1deg); }
            50% { transform: translate(-1px, 1px) rotate(-1deg); }
            60% { transform: translate(-2px, -1px) rotate(0deg); }
            70% { transform: translate(1px, 1px) rotate(-1deg); }
            80% { transform: translate(-1px, -1px) rotate(1deg); }
            90% { transform: translate(2px, 1px) rotate(0deg); }
            100% { transform: translate(1px, -2px) rotate(-1deg); }
        }
    </style>
</head>
<body>

<div class="container">
    <h1>🎨 AI 드로잉 챌린지</h1>
    <div class="subtitle">당곡고등학교 하드웨어-AI 융합 부스</div>

    <!-- 타이머 바 -->
    <div class="timer-container">
        <div id="timerBar" class="timer-bar"></div>
    </div>

    <!-- 메인 게임 카드 -->
    <div id="gameCard" class="game-card">
        <div id="statusBadge" class="status-badge">대기 중</div>
        <div id="quizWord" class="quiz-word">START 버튼을 눌러요!</div>
        <div id="realtimeSensor" class="realtime-text">허스키렌즈 연결 상태를 확인해주세요.</div>
    </div>

    <!-- 상태 정보 보드 -->
    <div class="stats-grid">
        <div class="stat-box">
            <div class="stat-label">현재 점수</div>
            <div class="stat-value" id="scoreVal">0</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">남은 시간</div>
            <div class="stat-value" id="timeVal">대기 중</div>
        </div>
    </div>

    <!-- 컨트롤 버튼 -->
    <button id="actionBtn" class="btn">게임 시작 🎮</button>
</div>

<script>
    // 6가지 정답 사물 목록
    const items = [
        { id: 1, name: "사과 🍎" },
        { id: 2, name: "자동차 🚗" },
        { id: 3, name: "별 ⭐" },
        { id: 4, name: "우산 ☂️" },
        { id: 5, name: "의자 🪑" },
        { id: 6, name: "핸드폰 📱" }
    ];

    // 게임 상태 변수
    let currentTarget = null;
    let score = 0;
    let roundCount = 0;        // 현재 진행 중인 라운드(문제 수)
    let timeLeft = 0;          // 이번 라운드에 남은 시간
    let currentRoundLimit = 0; // 이번 라운드에 부여된 총 제한 시간
    let timerInterval = null;
    let gameState = "IDLE";    // IDLE, ROULETTE, PLAYING, SOLVED, GAMEOVER
    let pollInterval = null;

    const gameCard = document.getElementById("gameCard");
    const statusBadge = document.getElementById("statusBadge");
    const quizWord = document.getElementById("quizWord");
    const realtimeSensor = document.getElementById("realtimeSensor");
    const scoreVal = document.getElementById("scoreVal");
    const timeVal = document.getElementById("timeVal");
    const timerBar = document.getElementById("timerBar");
    const actionBtn = document.getElementById("actionBtn");

    // 가상 오디오 재생기 (효과음)
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

    function playSound(freq, type, duration, delay=0) {
        setTimeout(() => {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.type = type;
            osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
            gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.00001, audioCtx.currentTime + duration);
            osc.start();
            osc.stop(audioCtx.currentTime + duration);
        }, delay);
    }

    // 룰렛 회전 효과음 (짧게 째깍째깍)
    function playTickSound() {
        playSound(800, "triangle", 0.05);
    }

    // 정답 팡파르 효과음 ("따단~" 쾌감 업!)
    function playTadaSound() {
        playSound(523.25, "sine", 0.15, 0);      // 도 (C5)
        playSound(659.25, "sine", 0.15, 120);    // 미 (E5)
        playSound(783.99, "sine", 0.3, 240);     // 솔 (G5)
        playSound(1046.50, "sine", 0.5, 360);    // 도 (C6)
    }

    // 타임아웃 삐 소리
    function playGameOverSound() {
        playSound(330, "sawtooth", 0.3, 0);
        playSound(220, "sawtooth", 0.6, 300);
    }

    // 버튼 클릭 이벤트 리스너
    actionBtn.addEventListener("click", () => {
        if (gameState === "IDLE" || gameState === "GAMEOVER") {
            startGame();
        } else if (gameState === "SOLVED") {
            triggerRoulette();
        }
    });

    // 1. 게임 전반 시동 함수
    function startGame() {
        score = 0;
        roundCount = 0;
        scoreVal.textContent = score;
        
        triggerRoulette(); // 첫 문제 선택 룰렛 시동
        
        // 피코 데이터 수신 센서 루프 시작
        if (pollInterval) clearInterval(pollInterval);
        pollInterval = setInterval(fetchSensorData, 300);
    }

    // 2. 랜덤 돌림판 애니메이션 (도로로로 굴러가기)
    function triggerRoulette() {
        gameState = "ROULETTE";
        gameCard.className = "game-card"; // 기본 스타일로 초기화
        statusBadge.textContent = "돌림판 선택 중";
        quizWord.classList.add("rolling");
        actionBtn.disabled = true;
        actionBtn.textContent = "문제를 고르는 중...";
        timerBar.style.width = "100%";
        timerBar.style.backgroundColor = "#3498db"; // 대기 상태 파란색 바

        let spinDuration = 1600; // 1.6초간 돌림판 작동
        let tickInterval = 80;
        let elapsed = 0;
        let lastIdx = -1;

        let spinTimer = setInterval(() => {
            let randIdx;
            do {
                randIdx = Math.floor(Math.random() * items.length);
            } while (randIdx === lastIdx);
            
            lastIdx = randIdx;
            quizWord.textContent = items[randIdx].name;
            playTickSound(); // 째깍 효과음 재생
            elapsed += tickInterval;

            if (elapsed >= spinDuration) {
                clearInterval(spinTimer);
                
                // 새로운 문제 확정 (직전 문제와 겹치지 않게)
                let finalTarget;
                do {
                    finalTarget = items[Math.floor(Math.random() * items.length)];
                } while (currentTarget && finalTarget.id === currentTarget.id);

                currentTarget = finalTarget;
                quizWord.textContent = currentTarget.name;
                quizWord.classList.remove("rolling");
                
                // 라운드 수 증가
                roundCount++;

                // 📌 [중요] 각 문제마다 새로운 제한 시간 동적 계산 공식 적용!
                // 1라운드: 45 - (1*3) = 42초
                // 2라운드: 45 - (2*3) = 39초 ...
                // 아무리 어려워져도 15초(Floor) 미만으로는 떨어지지 않음!
                currentRoundLimit = Math.max(15, 45 - (roundCount * 3));
                timeLeft = currentRoundLimit;
                
                timeVal.textContent = timeLeft + "초";
                timerBar.style.width = "100%";
                timerBar.style.backgroundColor = "#2ecc71"; // 게임 시작 시 안전한 초록색 바

                // 본격 플레이 모드 돌입
                gameState = "PLAYING";
                gameCard.className = "game-card playing";
                statusBadge.textContent = `Q ${roundCount} (제한시간: ${currentRoundLimit}초)`;
                actionBtn.textContent = "그림 그리는 중...";
                actionBtn.className = "btn";
                actionBtn.disabled = true;

                // 타이머 재시동
                startRoundTimer();
            }
        }, tickInterval);
    }

    // 3. 개별 라운드 카운트다운 타이머
    function startRoundTimer() {
        if (timerInterval) clearInterval(timerInterval);
        timerInterval = setInterval(() => {
            if (gameState === "PLAYING") {
                timeLeft--;
                timeVal.textContent = timeLeft + "초";
                
                let percent = (timeLeft / currentRoundLimit) * 100;
                timerBar.style.width = percent + "%";
                
                // 시간에 따라 프로그레스 바 색상을 변경하여 긴장감 연출
                if (timeLeft <= 5) {
                    timerBar.style.backgroundColor = "#e74c3c"; // 5초 이하: 아주 위험한 빨간색
                } else if (timeLeft <= 12) {
                    timerBar.style.backgroundColor = "#e67e22"; // 12초 이하: 경고용 주황색
                }

                if (timeLeft <= 0) {
                    endGame();
                }
            }
        }, 1000);
    }

    // 4. 피코 2 WH 로부터 센서 데이터를 가져오는 비동기 폴링 루프
    async function fetchSensorData() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();

            // 현재 렌즈가 보고 있는 상태 하단에 모니터링 출력
            if (data.id > 0) {
                realtimeSensor.textContent = `👁️ 실시간 인식: [ID ${data.id}] ${data.name} (X: ${data.x}, Y: ${data.y})`;
            } else {
                realtimeSensor.textContent = "🔍 허스키렌즈가 사물을 찾는 중입니다...";
            }

            // [핵심] 게임 플레이 진행 중이고, 수신된 ID가 타겟 퀴즈 ID와 완벽히 맞아떨어졌을 때!
            if (gameState === "PLAYING" && data.id === currentTarget.id) {
                gameState = "SOLVED"; // 즉시 정답 고정 모드로 상태 변환 (센서 감지 멈춤!)
                
                // 📌 정답을 맞췄으므로 즉시 시간 차감 정지!
                if (timerInterval) {
                    clearInterval(timerInterval);
                    timerInterval = null;
                }
                
                score += 10; // 10점 플러스!
                scoreVal.textContent = score;

                // 시각 및 청각 피드백 연출
                gameCard.className = "game-card solved";
                statusBadge.textContent = `Q ${roundCount} 해결 성공! 🎉`;
                playTadaSound(); // 따단~

                // 다음 문제로 넘어갈 수 있는 버튼 활성화
                actionBtn.disabled = false;
                actionBtn.className = "btn btn-next";
                actionBtn.textContent = "다음 문제 도전! ➡️";
            }

        } catch (error) {
            console.error("데이터 통신 중 에러 발생:", error);
        }
    }

    // 5. 제한시간 만료 시 게임 오버 처리
    function endGame() {
        gameState = "GAMEOVER";
        clearInterval(timerInterval);
        timerInterval = null;
        if (pollInterval) clearInterval(pollInterval);
        pollInterval = null;

        gameCard.className = "game-card gameover";
        statusBadge.textContent = "TIME OVER";
        quizWord.textContent = "게임 오버! 😵";
        realtimeSensor.textContent = `최종 점수는 ${score}점입니다! (총 ${roundCount - 1}개 해결)`;
        playGameOverSound();

        actionBtn.disabled = false;
        actionBtn.className = "btn";
        actionBtn.textContent = "다시 도전하기 🔄";
    }
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
            pass
            
        await asyncio.sleep(0.1)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# [비동기 웹 서버 클라이언트 처리기]
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def handle_client(reader, writer):
    global detected_id, detected_name, coord_x, coord_y
    
    try:
        request_line = await reader.readline()
        while True:
            line = await reader.readline()
            if line == b'\r\n' or line == b'\n' or not line:
                break
                
        request = request_line.decode('utf-8')
        
        # 1. API 데이터 요청 처리 (JSON 리턴)
        if "GET /api/status" in request:
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
    led = Pin("LED", Pin.OUT)
    husky = HuskyLensLibrary("I2C")
    await asyncio.sleep(0.5)
    
    # 사물 분류 모드로 초기화
    husky.command_request_algorthim("ALGORITHM_OBJECT_CLASSIFICATION")
    await asyncio.sleep(0.5)

    ip_addr = connect_wifi(SSID, PASSWORD)
    asyncio.create_task(poll_huskylens(husky, led))
    
    if ip_addr:
        print(f"📢 스마트폰/컴퓨터 주소창에 다음을 입력하세요 ➡️ http://{ip_addr}")
        server = await asyncio.start_server(handle_client, "0.0.0.0", 80)
        while True:
            await asyncio.sleep(3600)
    else:
        while True:
            print(f"📡 시리얼 확인용 모드 -> {detected_name} (ID: {detected_id})")
            await asyncio.sleep(1)

# 시스템 진입점 설정
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\n시스템이 수동 종료되었습니다.")

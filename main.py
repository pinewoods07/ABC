# main.py
import network
import time
import uasyncio as asyncio
from machine import Pin
from huskylensPythonLibrary import HuskyLensLibrary

SSID = "app"
PASSWORD = "20242024"

detected_id = 0
detected_name = "감지 안 됨"
coord_x = 0
coord_y = 0

# ★ 피코의 사물 목록 (ID: 이름)
object_map = {
    1: "사과",
    2: "자동차",
    3: "별",
    4: "의자",
    5: "핸드폰",
    6: "치즈",
}

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
            background: rgba(255,255,255,0.95);
            border-radius: 24px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.3);
            padding: 30px;
            box-sizing: border-box;
            text-align: center;
        }
        h1 {
            color: #1e3c72;
            font-size: 2.2rem;
            margin: 0 0 5px 0;
        }
        .subtitle {
            color: #666;
            font-size: 0.95rem;
            margin-bottom: 25px;
            font-weight: bold;
        }
        .game-card {
            background-color: #f8f9fa;
            border: 4px solid #1e3c72;
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 20px;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .game-card.playing  { border-color: #e67e22; background-color: #fdfaf6; }
        .game-card.solved   { border-color: #2ecc71; background-color: #ebfaf0; box-shadow: 0 0 20px rgba(46,204,113,0.5); }
        .game-card.gameover { border-color: #e74c3c; background-color: #fdf5f5; }

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
        .game-card.solved   .status-badge { background: #2ecc71; }
        .game-card.playing  .status-badge { background: #e67e22; }
        .game-card.gameover .status-badge { background: #e74c3c; }

        .quiz-word {
            font-size: 3.5rem;
            font-weight: 900;
            color: #2c3e50;
            margin: 15px 0;
            min-height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .quiz-word.rolling {
            animation: shake 0.1s infinite;
            color: #7f8c8d;
        }

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
            box-shadow: 0 4px 10px rgba(30,60,114,0.3);
            margin-bottom: 10px;
        }
        .btn:hover   { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(30,60,114,0.4); }
        .btn:active  { transform: translateY(1px); }

        .btn-next {
            background-color: #2ecc71;
            box-shadow: 0 4px 10px rgba(46,204,113,0.3);
        }
        .btn-next:hover { background-color: #27ae60; }

        .btn-pass {
            background-color: #9b59b6;
            box-shadow: 0 4px 10px rgba(155,89,182,0.3);
        }
        .btn-pass:hover { background-color: #8e44ad; }

        .realtime-text {
            font-size: 0.85rem;
            color: #7f8c8d;
            margin-top: 15px;
            font-style: italic;
        }

        @keyframes shake {
            0%   { transform: translate(1px, 1px)   rotate(0deg);  }
            10%  { transform: translate(-1px, -1px) rotate(-1deg); }
            20%  { transform: translate(-2px, 0px)  rotate(1deg);  }
            30%  { transform: translate(0px, 1px)   rotate(0deg);  }
            40%  { transform: translate(1px, -1px)  rotate(1deg);  }
            50%  { transform: translate(-1px, 1px)  rotate(-1deg); }
            60%  { transform: translate(-2px, -1px) rotate(0deg);  }
            70%  { transform: translate(1px, 1px)   rotate(-1deg); }
            80%  { transform: translate(-1px, -1px) rotate(1deg);  }
            90%  { transform: translate(2px, 1px)   rotate(0deg);  }
            100% { transform: translate(1px, -2px)  rotate(-1deg); }
        }
    </style>
</head>
<body>
<div class="container">
    <h1>🎨 AI 드로잉 챌린지</h1>
    <div class="subtitle">당곡고등학교 하드웨어-AI 융합 부스</div>

    <div class="timer-container">
        <div id="timerBar" class="timer-bar"></div>
    </div>

    <div id="gameCard" class="game-card">
        <div id="statusBadge" class="status-badge">대기 중</div>
        <div id="quizWord" class="quiz-word">START 버튼을 눌러요!</div>
        <div id="realtimeSensor" class="realtime-text">허스키렌즈 연결 상태를 확인해주세요.</div>
    </div>

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

    <button id="actionBtn" class="btn">게임 시작 🎮</button>
    <button id="passBtn"   class="btn btn-pass" disabled>패스 ⏩ (남은 기회: 2회)</button>
</div>

<script>
    // ★ 핵심 수정 포인트!
    // 피코의 object_map과 완벽히 동기화된 사물 목록
    // 사물을 추가/변경할 때는 여기와 파이썬 object_map을 항상 함께 수정하세요!
    const items = [
        { id: 1, name: "사과 🍎" },
        { id: 2, name: "자동차 🚗" },
        { id: 3, name: "별 ⭐" },
        { id: 4, name: "의자 🪑" },
        { id: 5, name: "핸드폰 📱" },
        { id: 6, name: "치즈 🧀" }
    ];

    let currentTarget  = null;
    let score          = 0;
    let roundCount     = 0;
    let timeLeft       = 0;
    let currentRoundLimit = 0;
    let passLeft       = 2;
    let timerInterval  = null;
    let gameState      = "IDLE";
    let pollInterval   = null;

    const gameCard      = document.getElementById("gameCard");
    const statusBadge   = document.getElementById("statusBadge");
    const quizWord      = document.getElementById("quizWord");
    const realtimeSensor= document.getElementById("realtimeSensor");
    const scoreVal      = document.getElementById("scoreVal");
    const timeVal       = document.getElementById("timeVal");
    const timerBar      = document.getElementById("timerBar");
    const actionBtn     = document.getElementById("actionBtn");
    const passBtn       = document.getElementById("passBtn");

    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

    function playSound(freq, type, duration, delay = 0) {
        setTimeout(() => {
            const osc  = audioCtx.createOscillator();
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

    const playTickSound     = () => playSound(800, "triangle", 0.05);
    const playTadaSound     = () => {
        playSound(523.25, "sine", 0.15, 0);
        playSound(659.25, "sine", 0.15, 120);
        playSound(783.99, "sine", 0.3,  240);
        playSound(1046.5, "sine", 0.5,  360);
    };
    const playPassSound     = () => {
        playSound(600, "sine", 0.1,  0);
        playSound(900, "sine", 0.15, 80);
    };
    const playGameOverSound = () => {
        playSound(330, "sawtooth", 0.3, 0);
        playSound(220, "sawtooth", 0.6, 300);
    };

    // ── 버튼 이벤트 ──────────────────────────────────────────
    actionBtn.addEventListener("click", () => {
        if (gameState === "IDLE" || gameState === "GAMEOVER") startGame();
        else if (gameState === "SOLVED") triggerRoulette();
    });

    passBtn.addEventListener("click", () => {
        if (gameState === "PLAYING" && passLeft > 0) usePass();
    });

    // ── 1. 게임 시작 ─────────────────────────────────────────
    function startGame() {
        score      = 0;
        roundCount = 0;
        passLeft   = 2;
        scoreVal.textContent = score;
        updatePassButton();

        if (pollInterval) clearInterval(pollInterval);
        pollInterval = setInterval(fetchSensorData, 300);

        triggerRoulette();
    }

    // ── 2. 돌림판 ────────────────────────────────────────────
    function triggerRoulette() {
        gameState = "ROULETTE";
        gameCard.className = "game-card";
        statusBadge.textContent = "돌림판 선택 중";
        quizWord.classList.add("rolling");
        actionBtn.disabled = true;
        actionBtn.textContent = "문제를 고르는 중...";
        updatePassButton();
        timerBar.style.width = "100%";
        timerBar.style.backgroundColor = "#3498db";

        let elapsed = 0;
        const spinDuration = 1600;
        const tickInterval = 80;
        let lastIdx = -1;

        const spinTimer = setInterval(() => {
            let randIdx;
            do { randIdx = Math.floor(Math.random() * items.length); }
            while (randIdx === lastIdx);
            lastIdx = randIdx;
            quizWord.textContent = items[randIdx].name;
            playTickSound();
            elapsed += tickInterval;

            if (elapsed >= spinDuration) {
                clearInterval(spinTimer);

                // 직전 문제와 겹치지 않게 최종 문제 확정
                let finalTarget;
                do { finalTarget = items[Math.floor(Math.random() * items.length)]; }
                while (currentTarget && finalTarget.id === currentTarget.id);

                currentTarget = finalTarget;
                quizWord.textContent = currentTarget.name;
                quizWord.classList.remove("rolling");

                roundCount++;
                // 라운드마다 3초씩 감소, 최소 15초 보장
                currentRoundLimit = Math.max(15, 45 - (roundCount * 3));
                timeLeft = currentRoundLimit;

                timeVal.textContent = timeLeft + "초";
                timerBar.style.width = "100%";
                timerBar.style.backgroundColor = "#2ecc71";

                gameState = "PLAYING";
                gameCard.className = "game-card playing";
                statusBadge.textContent = `Q ${roundCount}  (제한시간: ${currentRoundLimit}초)`;
                actionBtn.textContent = "그림 그리는 중...";
                actionBtn.className = "btn";
                actionBtn.disabled = true;

                updatePassButton();
                startRoundTimer();
            }
        }, tickInterval);
    }

    // ── 3. 라운드 타이머 ──────────────────────────────────────
    function startRoundTimer() {
        if (timerInterval) clearInterval(timerInterval);
        timerInterval = setInterval(() => {
            if (gameState !== "PLAYING") return;
            timeLeft--;
            timeVal.textContent = timeLeft + "초";
            timerBar.style.width = (timeLeft / currentRoundLimit * 100) + "%";

            if      (timeLeft <= 5)  timerBar.style.backgroundColor = "#e74c3c";
            else if (timeLeft <= 12) timerBar.style.backgroundColor = "#e67e22";

            if (timeLeft <= 0) endGame();
        }, 1000);
    }

    // ── 4. 패스 ──────────────────────────────────────────────
    function usePass() {
        if (gameState !== "PLAYING" || passLeft <= 0) return;
        passLeft--;
        playPassSound();
        updatePassButton();
        if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }
        triggerRoulette();
    }

    function updatePassButton() {
        passBtn.textContent = `패스 ⏩ (남은 기회: ${passLeft}회)`;
        const canUse = (gameState === "PLAYING" && passLeft > 0);
        passBtn.disabled       = !canUse;
        passBtn.style.opacity  = canUse ? "1"         : "0.5";
        passBtn.style.cursor   = canUse ? "pointer"   : "not-allowed";
    }

    // ── 5. 센서 폴링 ──────────────────────────────────────────
    async function fetchSensorData() {
        try {
            const res  = await fetch('/api/status');
            const data = await res.json();

            realtimeSensor.textContent = data.id > 0
                ? `👁️ 실시간 인식: [ID ${data.id}] ${data.name}  (X: ${data.x}, Y: ${data.y})`
                : "🔍 허스키렌즈가 사물을 찾는 중입니다...";

            if (gameState === "PLAYING" && data.id === currentTarget.id) {
                gameState = "SOLVED";

                if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }
                updatePassButton();

                score += 10;
                scoreVal.textContent = score;
                gameCard.className   = "game-card solved";
                statusBadge.textContent = `Q ${roundCount} 해결 성공! 🎉`;
                playTadaSound();

                actionBtn.disabled   = false;
                actionBtn.className  = "btn btn-next";
                actionBtn.textContent = "다음 문제 도전! ➡️";
            }
        } catch (e) {
            console.error("데이터 통신 오류:", e);
        }
    }

    // ── 6. 게임 오버 ──────────────────────────────────────────
    function endGame() {
        gameState = "GAMEOVER";
        clearInterval(timerInterval); timerInterval = null;
        if (pollInterval) { clearInterval(pollInterval); pollInterval = null; }

        gameCard.className      = "game-card gameover";
        statusBadge.textContent = "TIME OVER";
        quizWord.textContent    = "게임 오버! 😵";
        realtimeSensor.textContent =
            `최종 점수: ${score}점  (총 ${roundCount - 1}개 해결)`;
        playGameOverSound();
        updatePassButton();

        actionBtn.disabled    = false;
        actionBtn.className   = "btn";
        actionBtn.textContent = "다시 도전하기 🔄";
    }
</script>
</body>
</html>
"""

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
                        detected_id   = obj_id
                        detected_name = object_map.get(obj_id, "알 수 없는 사물")
                        coord_x, coord_y = x, y
                        led.on()
                    else:
                        detected_id = 0
                        detected_name = "학습되지 않은 사물"
                        coord_x = coord_y = 0
                        led.off()
                    break
            else:
                detected_id = 0
                detected_name = "감지 안 됨"
                coord_x = coord_y = 0
                led.off()
        except Exception:
            pass
        await asyncio.sleep(0.1)

async def handle_client(reader, writer):
    global detected_id, detected_name, coord_x, coord_y
    try:
        request_line = await reader.readline()
        while True:
            line = await reader.readline()
            if line in (b'\r\n', b'\n') or not line:
                break
        request = request_line.decode('utf-8')

        if "GET /api/status" in request:
            json_response = '{"id":%d,"name":"%s","x":%d,"y":%d}' % (
                detected_id, detected_name, coord_x, coord_y)
            writer.write(b"HTTP/1.1 200 OK\r\n")
            writer.write(b"Content-Type: application/json; charset=utf-8\r\n")
            writer.write(b"Connection: close\r\n\r\n")
            writer.write(json_response.encode('utf-8'))
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

async def main():
    led = Pin("LED", Pin.OUT)
    husky = HuskyLensLibrary("I2C")
    await asyncio.sleep(0.5)
    husky.command_request_algorthim("ALGORITHM_OBJECT_CLASSIFICATION")
    await asyncio.sleep(0.5)

    ip_addr = connect_wifi(SSID, PASSWORD)
    asyncio.create_task(poll_huskylens(husky, led))

    if ip_addr:
        print(f"📢 브라우저 주소창에 입력 ➡️  http://{ip_addr}")
        await asyncio.start_server(handle_client, "0.0.0.0", 80)
        while True:
            await asyncio.sleep(3600)
    else:
        while True:
            print(f"📡 시리얼 모드 → {detected_name} (ID: {detected_id})")
            await asyncio.sleep(1)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\n시스템이 수동 종료되었습니다.")

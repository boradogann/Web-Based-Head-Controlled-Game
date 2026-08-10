import streamlit as st
import streamlit.components.v1 as components

# Streamlit Sayfa Düzeni (Mobilde daha iyi görünüm için wide/centered dengesi)
st.set_page_config(
    page_title="Minion 3D Runner",
    page_icon="🍌",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("🍌 Minion 3D Runner")
st.caption("Kafanızı sağa/sola eğerek Minyonu yönlendirin.")

# Mobil Uyumlu HTML / CSS / JS Oyun Kodu
game_html = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Minion 3D Runner - Mobile Ready</title>

  <!-- TensorFlow.js ve BlazeFace Kütüphaneleri -->
  <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.20.0/dist/tf.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/blazeface@0.0.7/dist/blazeface.min.js"></script>

  <style>
    * {
      box-sizing: border-box;
      touch-action: none; /* Mobilde oynarken sayfanın aşağı/yukarı kaymasını engeller */
    }
    body {
      margin: 0;
      padding: 0;
      background: #0f141d;
      color: #fff;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-start;
      overflow: hidden;
      width: 100vw;
    }
    #status {
      font-size: 14px;
      margin: 8px 0;
      color: #ffcc00;
      font-weight: bold;
      text-shadow: 0 0 10px rgba(255,204,0,0.3);
      width: 90%;
      text-align: center;
    }
    /* Mobil Responsive Container */
    #game-container {
      position: relative;
      width: 95vw;
      max-width: 400px;
      height: 75vh;
      max-height: 600px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.8);
      border-radius: 16px;
      overflow: hidden;
      border: 2px solid #ffcc00;
    }
    canvas {
      width: 100%;
      height: 100%;
      background: linear-gradient(to bottom, #0f172a 0%, #1e293b 30%, #000000 100%);
      display: block;
    }
    #webcam {
      position: absolute;
      top: 10px;
      right: 10px;
      width: 75px;
      height: 56px;
      border: 2px solid #ffcc00;
      border-radius: 6px;
      transform: scaleX(-1);
      z-index: 10;
      object-fit: cover;
    }
    #ui-layer {
      position: absolute;
      top: 12px;
      left: 12px;
      font-size: 18px;
      font-weight: bold;
      color: #ffcc00;
      text-shadow: 2px 2px 4px #000;
      pointer-events: none;
      z-index: 5;
    }
    #restart-btn {
      position: absolute;
      top: 65%;
      left: 50%;
      transform: translate(-50%, -50%);
      padding: 12px 24px;
      font-size: 16px;
      font-weight: bold;
      color: #000;
      background-color: #ffcc00;
      border: none;
      border-radius: 25px;
      cursor: pointer;
      box-shadow: 0 0 20px rgba(255,204,0,0.6);
      display: none;
      z-index: 20;
    }
  </style>
</head>
<body>

  <div id="status">Kamera Başlatılıyor...</div>
  
  <div id="game-container">
    <video id="webcam" autoplay playsinline muted></video>
    <div id="ui-layer">SKOR: <span id="score">0</span></div>
    <button id="restart-btn" onclick="resetGame()">YENİDEN BAŞLAT</button>
    <canvas id="gameCanvas" width="400" height="600"></canvas>
  </div>

  <script>
    const video = document.getElementById('webcam');
    const statusText = document.getElementById('status');
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const scoreElement = document.getElementById('score');
    const restartBtn = document.getElementById('restart-btn');

    let model;
    let score = 0;
    let gameOver = false;
    let animationFrameId;
    
    const baseLanes = [80, 200, 320];   
    const topLanes = [170, 200, 230];   
    
    let playerLane = 1; 
    let playerX = baseLanes[1]; 
    let playerY = 500;

    let moveState = 'neutral'; 

    let obstacles = [];
    const FIXED_OBSTACLE_SPEED = 0.012; 
    let spawnTimer = 0;

    const obstacleTypes = [
      { emoji: '🚆', sizeOffset: 1.2 },
      { emoji: '🚧', sizeOffset: 1.0 },
      { emoji: '🗑️', sizeOffset: 0.9 },
      { emoji: '⚠️', sizeOffset: 0.8 }
    ];

    let sideDecorations = [];
    let decorTimer = 0;

    async function setupCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "user", width: { ideal: 320 }, height: { ideal: 240 } },
          audio: false
        });
        video.srcObject = stream;
        return new Promise((resolve) => {
          video.onloadeddata = () => {
            video.play();
            resolve(video);
          };
        });
      } catch (err) {
        throw new Error("Kamera erişimi başarısız! İzin verdiğinizden emin olun.");
      }
    }

    async function detectFace() {
      if (!gameOver && model) {
        try {
          const predictions = await model.estimateFaces(video, false);

          if (predictions.length > 0) {
            const face = predictions[0];
            const noseX = face.landmarks[2][0]; 

            if (moveState === 'neutral') {
              if (noseX > 180) { 
                if (playerLane > 0) playerLane--;
                moveState = 'moved'; 
              } else if (noseX < 120) { 
                if (playerLane < 2) playerLane++;
                moveState = 'moved'; 
              }
            } else if (moveState === 'moved') {
              if (noseX >= 120 && noseX <= 180) {
                moveState = 'neutral'; 
              }
            }
          }
        } catch (e) {
          console.error("Yüz tespiti hatası:", e);
        }
      }
      requestAnimationFrame(detectFace);
    }

    function lerp(start, end, t) {
      return start + (end - start) * t;
    }

    function drawBackground() {
      const horizonY = 180;
      ctx.fillStyle = '#0f172a';
      ctx.fillRect(0, 0, 400, horizonY);

      ctx.fillStyle = '#1e1b4b';
      ctx.fillRect(20, 100, 50, 80);
      ctx.fillRect(80, 70, 60, 110);
      ctx.fillRect(260, 80, 55, 100);
      ctx.fillRect(330, 110, 45, 70);

      ctx.fillStyle = '#fde047';
      ctx.fillRect(90, 85, 8, 8);
      ctx.fillRect(110, 105, 8, 8);
      ctx.fillRect(280, 95, 8, 8);
    }

    function draw3DRoad() {
      const horizonY = 180;
      const bottomY = 600;

      ctx.fillStyle = '#1e293b';
      ctx.beginPath();
      ctx.moveTo(140, horizonY);
      ctx.lineTo(260, horizonY);
      ctx.lineTo(380, bottomY);
      ctx.lineTo(20, bottomY);
      ctx.closePath();
      ctx.fill();

      ctx.strokeStyle = '#ffcc00';
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.moveTo(140, horizonY); ctx.lineTo(20, bottomY);
      ctx.moveTo(260, horizonY); ctx.lineTo(380, bottomY);
      ctx.stroke();

      ctx.strokeStyle = '#475569';
      ctx.lineWidth = 2;
      ctx.setLineDash([10, 15]);
      ctx.beginPath();
      ctx.moveTo(180, horizonY); ctx.lineTo(140, bottomY);
      ctx.moveTo(220, horizonY); ctx.lineTo(260, bottomY);
      ctx.stroke();
      ctx.setLineDash([]); 
    }

    function updateAndDrawDecorations() {
      decorTimer++;
      if (decorTimer > 35) {
        sideDecorations.push({ side: 'left', z: 0, type: Math.random() > 0.5 ? '🌳' : '💡' });
        sideDecorations.push({ side: 'right', z: 0, type: Math.random() > 0.5 ? '🌳' : '💡' });
        decorTimer = 0;
      }

      for (let i = 0; i < sideDecorations.length; i++) {
        let dec = sideDecorations[i];
        dec.z += FIXED_OBSTACLE_SPEED;

        const horizonY = 180;
        const currentY = lerp(horizonY, 600, dec.z);
        const scale = lerp(0.3, 1.3, dec.z);

        const currentX = dec.side === 'left' 
          ? lerp(120, -20, dec.z) 
          : lerp(280, 420, dec.z);

        ctx.font = `${30 * scale}px serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(dec.type, currentX, currentY);

        if (dec.z > 1.1) {
          sideDecorations.splice(i, 1);
          i--;
        }
      }
    }

    function drawVectorMinion(x, y) {
      ctx.save();
      ctx.translate(x, y);

      ctx.fillStyle = '#ffcc00';
      ctx.beginPath();
      ctx.arc(0, -15, 20, Math.PI, 0, false); 
      ctx.rect(-20, -15, 40, 30);            
      ctx.arc(0, 15, 20, 0, Math.PI, false);  
      ctx.fill();

      ctx.fillStyle = '#2563eb';
      ctx.fillRect(-20, 5, 40, 20);
      ctx.fillRect(-12, -2, 24, 10); 

      ctx.strokeStyle = '#1d4ed8';
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.moveTo(-18, -2); ctx.lineTo(-10, 8);
      ctx.moveTo(18, -2); ctx.lineTo(10, 8);
      ctx.stroke();

      ctx.fillStyle = '#111';
      ctx.fillRect(-20, -18, 40, 6);

      ctx.fillStyle = '#9ca3af';
      ctx.beginPath();
      ctx.arc(0, -15, 10, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#fff';
      ctx.beginPath();
      ctx.arc(0, -15, 7, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#374151'; 
      ctx.beginPath();
      ctx.arc(0, -15, 3, 0, Math.PI * 2);
      ctx.fill();

      ctx.strokeStyle = '#000';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(0, -5, 8, 0.1 * Math.PI, 0.9 * Math.PI, false);
      ctx.stroke();

      ctx.restore();
    }

    function updateGame() {
      if (gameOver) return;

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      drawBackground();
      draw3DRoad();
      updateAndDrawDecorations();

      const targetX = baseLanes[playerLane];
      playerX += (targetX - playerX) * 0.2; 

      ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
      ctx.beginPath();
      ctx.ellipse(playerX, playerY + 30, 22, 7, 0, 0, Math.PI * 2);
      ctx.fill();

      drawVectorMinion(playerX, playerY);

      spawnTimer++;
      if (spawnTimer > 70) { 
        const randomLane = Math.floor(Math.random() * 3);
        const randomType = obstacleTypes[Math.floor(Math.random() * obstacleTypes.length)];
        
        obstacles.push({
          lane: randomLane,
          z: 0,
          type: randomType
        });
        spawnTimer = 0;
      }

      for (let i = 0; i < obstacles.length; i++) {
        let obs = obstacles[i];
        obs.z += FIXED_OBSTACLE_SPEED;

        const horizonY = 180;
        const currentY = lerp(horizonY, 520, obs.z);
        const currentX = lerp(topLanes[obs.lane], baseLanes[obs.lane], obs.z);
        const currentScale = lerp(0.2, 1.0, obs.z); 

        ctx.fillStyle = 'rgba(0, 0, 0, 0.4)';
        ctx.beginPath();
        ctx.ellipse(currentX, currentY + (15 * currentScale), 20 * currentScale, 6 * currentScale, 0, 0, Math.PI * 2);
        ctx.fill();

        const fontSize = 42 * currentScale * obs.type.sizeOffset;
        ctx.font = `${fontSize}px serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(obs.type.emoji, currentX, currentY);

        if (obs.z >= 0.88 && obs.z <= 1.02 && playerLane === obs.lane) {
          endGame();
          return;
        }

        if (obs.z > 1.1) {
          obstacles.splice(i, 1);
          i--;
          score += 10;
          scoreElement.innerText = score;
        }
      }

      animationFrameId = requestAnimationFrame(updateGame);
    }

    function endGame() {
      gameOver = true;
      cancelAnimationFrame(animationFrameId);

      ctx.fillStyle = 'rgba(0, 0, 0, 0.85)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      
      ctx.fillStyle = '#ff0055';
      ctx.font = 'bold 30px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('GAME OVER', 200, 260);
      
      ctx.fillStyle = '#ffcc00';
      ctx.font = '18px sans-serif';
      ctx.fillText('Toplanan Skor: ' + score, 200, 310);

      restartBtn.style.display = 'block';
    }

    function resetGame() {
      score = 0;
      scoreElement.innerText = score;
      playerLane = 1;
      playerX = baseLanes[1];
      obstacles = [];
      sideDecorations = [];
      spawnTimer = 0;
      decorTimer = 0;
      gameOver = false;
      moveState = 'neutral';

      restartBtn.style.display = 'none';
      updateGame();
    }

    async function main() {
      try {
        statusText.innerText = "Kamera İzni İsteniyor...";
        await setupCamera();
        
        statusText.innerText = "AI Modeli Yükleniyor...";
        
        if (typeof blazeface === 'undefined') {
          throw new Error("BlazeFace kütüphanesi yüklenemedi!");
        }

        model = await blazeface.load();
        
        statusText.innerText = "Oyun Hazır! Kafanı Eğerek Yönlendir.";
        
        detectFace();
        updateGame();
      } catch (e) {
        statusText.style.color = "#ff0055";
        statusText.innerText = "Hata: " + e.message;
        console.error("Detaylı Hata:", e);
      }
    }

    main();
  </script>
</body>
</html>
"""

components.html(game_html, height=680)

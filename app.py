import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Minion 3D Runner - Ultra Fast",
    page_icon="🍌",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("🍌 Minion 3D Runner: Ultra Seri Kontrol")
st.caption("Kafa hareket algılama hızı ve hassasiyeti maksimuma çıkarıldı!")

game_html = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Minion Runner - Fast Detection</title>

  <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.20.0/dist/tf.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/blazeface@0.0.7/dist/blazeface.min.js"></script>

  <style>
    * { box-sizing: border-box; touch-action: none; }
    body {
      margin: 0; padding: 0; background: #0f141d; color: #fff;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      display: flex; flex-direction: column; align-items: center; justify-content: flex-start;
      overflow: hidden; width: 100vw;
    }
    #status {
      font-size: 14px; margin: 6px 0; color: #ffcc00; font-weight: bold;
      text-shadow: 0 0 10px rgba(255,204,0,0.3); width: 90%; text-align: center;
    }
    #game-container {
      position: relative; width: 95vw; max-width: 400px; height: 75vh; max-height: 600px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.8); border-radius: 16px; overflow: hidden; border: 2px solid #ffcc00;
    }
    canvas { width: 100%; height: 100%; background: linear-gradient(to bottom, #0f172a 0%, #1e293b 30%, #000000 100%); display: block; }
    #webcam {
      position: absolute; top: 10px; left: 10px; width: 70px; height: 52px;
      border: 2px solid #ffcc00; border-radius: 6px; transform: scaleX(-1); z-index: 10; object-fit: cover;
    }
    #distance-ui {
      position: absolute; top: 10px; left: 90px; background: rgba(15, 23, 42, 0.85);
      border: 2px solid #38bdf8; padding: 6px 12px; border-radius: 20px; font-size: 14px; font-weight: bold; color: #38bdf8; z-index: 10;
    }
    #wallet-ui {
      position: absolute; top: 10px; right: 10px; background: rgba(30, 58, 138, 0.85);
      border: 2px solid #ffcc00; padding: 6px 14px; border-radius: 20px; font-size: 15px; font-weight: bold; color: #ffcc00; z-index: 10;
    }
    #word-ui {
      position: absolute; top: 48px; left: 50%; transform: translateX(-50%);
      display: flex; gap: 4px; z-index: 10; max-width: 380px; flex-wrap: wrap; justify-content: center;
    }
    .char-box {
      width: 28px; height: 34px; background: rgba(15, 23, 42, 0.9); border: 2px solid #475569;
      border-radius: 6px; display: flex; align-items: center; justify-content: center;
      font-size: 16px; font-weight: bold; color: #94a3b8; box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: all 0.3s ease;
    }
    .char-box.collected {
      background: #ffcc00; border-color: #ffffff; color: #000000; box-shadow: 0 0 10px #ffcc00; transform: scale(1.1);
    }
    .game-btn {
      position: absolute; left: 50%; transform: translateX(-50%); padding: 12px 28px;
      font-size: 16px; font-weight: bold; border: none; border-radius: 25px; cursor: pointer; display: none; z-index: 20;
    }
    #restart-btn { top: 58%; color: #000; background-color: #ffcc00; }
    #shop-btn { top: 70%; color: #fff; background-color: #2563eb; border: 2px solid #3b82f6; }

    #shop-modal {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(15, 20, 29, 0.95); z-index: 30; display: none; flex-direction: column; align-items: center; padding: 15px; overflow-y: auto;
    }
    #shop-header { width: 100%; display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; border-bottom: 2px solid #334155; padding-bottom: 10px; }
    #back-btn { background: #334155; color: #fff; border: none; padding: 8px 16px; border-radius: 15px; font-weight: bold; cursor: pointer; }
    #shop-title { font-size: 18px; font-weight: bold; color: #ffcc00; }
    .shop-items-container { width: 100%; display: flex; flex-direction: column; gap: 12px; }
    .shop-item { display: flex; align-items: center; justify-content: space-between; background: #1e293b; border: 2px solid #334155; padding: 10px 15px; border-radius: 12px; }
    .shop-item-info { display: flex; align-items: center; gap: 12px; }
    .shop-item-icon { font-size: 30px; }
    .shop-item-details { display: flex; flex-direction: column; }
    .shop-item-name { font-weight: bold; font-size: 14px; color: #fff; }
    .shop-item-price { font-size: 12px; color: #ffcc00; }
    .buy-btn { padding: 8px 14px; border-radius: 15px; border: none; font-weight: bold; cursor: pointer; background: #10b981; color: #fff; font-size: 13px; }
    .buy-btn.selected { background: #64748b; cursor: default; }
    .buy-btn.disabled { background: #475569; opacity: 0.6; cursor: not-allowed; }
  </style>
</head>
<body>

  <div id="status">Kamera Başlatılıyor...</div>
  
  <div id="game-container">
    <video id="webcam" autoplay playsinline muted></video>
    
    <div id="distance-ui">🏃 <span id="distance">0</span> m</div>
    <div id="wallet-ui">🍌 <span id="coins">0</span></div>
    
    <div id="word-ui"></div>

    <button id="restart-btn" class="game-btn" onclick="resetGame()">YENİDEN BAŞLAT</button>
    <button id="shop-btn" class="game-btn" onclick="openShop()">🛒 MARKET</button>

    <div id="shop-modal">
      <div id="shop-header">
        <button id="back-btn" onclick="closeShop()">← GERİ</button>
        <div id="shop-title">MINYON MARKETİ</div>
        <div style="font-size:14px; color:#ffcc00;">🍌 <span id="shop-coins">0</span></div>
      </div>
      <div class="shop-items-container" id="shop-items"></div>
    </div>

    <canvas id="gameCanvas" width="400" height="600"></canvas>
  </div>

  <script>
    const video = document.getElementById('webcam');
    const statusText = document.getElementById('status');
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const coinsElement = document.getElementById('coins');
    const distanceElement = document.getElementById('distance');
    const shopCoinsElement = document.getElementById('shop-coins');
    const wordUi = document.getElementById('word-ui');
    const restartBtn = document.getElementById('restart-btn');
    const shopBtn = document.getElementById('shop-btn');
    const shopModal = document.getElementById('shop-modal');
    const shopItemsContainer = document.getElementById('shop-items');

    let model;
    let coins = 0;
    let distance = 0;
    let nextDistanceMilestone = 500;
    let gameOver = false;
    let animationFrameId;
    let isDetecting = false; // Asenkron kilit engelleme
    
    const baseLanes = [80, 200, 320];   
    const topLanes = [170, 200, 230];   
    
    let playerLane = 1; 
    let playerX = baseLanes[1]; 
    let playerY = 500;

    let moveState = 'neutral'; 
    const FIXED_SPEED = 0.012; 
    
    let obstacles = [];
    let letters = [];
    let sparkles = []; 
    let spawnTimer = 0;

    const wordList = [
      "BANANA", "BELLO", "GELATO", "PAPOY", "POOPA", 
      "KANPAI", "BEEDO", "TANKYU", "TULALILOO", "UNDERWEAR"
    ];
    let wordIndex = 0;
    let currentWord = wordList[wordIndex];
    let collectedCount = 0;
    let floatingMessage = null;

    let activeSkin = 'classic';
    const skins = [
      { id: 'classic', name: 'Klasik Minyon', price: 0, icon: '🍌', purchased: true },
      { id: 'agent', name: 'Ajan Minyon', price: 50, icon: '🕶️', purchased: false },
      { id: 'king', name: 'Kral Minyon', price: 100, icon: '👑', purchased: false },
      { id: 'firefighter', name: 'İtfaiyeci Minyon', price: 150, icon: '👨‍🚒', purchased: false }
    ];

    const obstacleTypes = [
      { emoji: '🚆', sizeOffset: 1.2 },
      { emoji: '🚧', sizeOffset: 1.0 },
      { emoji: '🗑️', sizeOffset: 0.9 },
      { emoji: '⚠️', sizeOffset: 0.8 }
    ];

    let sideDecorations = [];
    let decorTimer = 0;

    function renderWordUI() {
      wordUi.innerHTML = '';
      for (let i = 0; i < currentWord.length; i++) {
        const box = document.createElement('div');
        box.className = 'char-box' + (i < collectedCount ? ' collected' : '');
        box.innerText = currentWord[i];
        wordUi.appendChild(box);
      }
    }

    function renderShopUI() {
      shopCoinsElement.innerText = coins;
      shopItemsContainer.innerHTML = '';

      skins.forEach(skin => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'shop-item';

        let btnText = '';
        let btnClass = 'buy-btn';
        let onClickAction = '';

        if (activeSkin === skin.id) {
          btnText = 'SEÇİLDİ';
          btnClass += ' selected';
        } else if (skin.purchased) {
          btnText = 'SEÇ';
          onClickAction = `selectSkin('${skin.id}')`;
        } else if (coins >= skin.price) {
          btnText = `${skin.price} 🍌 SATIN AL`;
          onClickAction = `buySkin('${skin.id}')`;
        } else {
          btnText = `${skin.price} 🍌 Yetersiz`;
          btnClass += ' disabled';
        }

        itemDiv.innerHTML = `
          <div class="shop-item-info">
            <div class="shop-item-icon">${skin.icon}</div>
            <div class="shop-item-details">
              <div class="shop-item-name">${skin.name}</div>
              <div class="shop-item-price">${skin.price === 0 ? 'Ücretsiz' : skin.price + ' Banana'}</div>
            </div>
          </div>
          <button class="${btnClass}" ${onClickAction ? `onclick="${onClickAction}"` : ''}>${btnText}</button>
        `;
        shopItemsContainer.appendChild(itemDiv);
      });
    }

    function openShop() { renderShopUI(); shopModal.style.display = 'flex'; }
    function closeShop() { shopModal.style.display = 'none'; }

    function buySkin(skinId) {
      const skin = skins.find(s => s.id === skinId);
      if (skin && !skin.purchased && coins >= skin.price) {
        coins -= skin.price;
        skin.purchased = true;
        activeSkin = skinId;
        coinsElement.innerText = coins;
        renderShopUI();
      }
    }

    function selectSkin(skinId) {
      activeSkin = skinId;
      renderShopUI();
    }

    // 1. KAMERA DÜŞÜK ÇÖZÜNÜRLÜKLE BAŞLATILIR (Hızlı İşleme İçin 160x120)
    async function setupCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "user", width: { ideal: 160 }, height: { ideal: 120 } },
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
        throw new Error("Kamera erişimi başarısız!");
      }
    }

    // 2. ULTRA HIZLI VE KİLİTSİZ YÜZ ALGILAMA DÖNGÜSÜ
    async function runDetectionLoop() {
      if (!gameOver && model && !isDetecting) {
        isDetecting = true;
        try {
          const predictions = await model.estimateFaces(video, false);

          if (predictions.length > 0) {
            const face = predictions[0];
            const noseX = face.landmarks[2][0]; // Burun X koordinatı

            // Hassel Eşikleri Daraltıldı (Daha hassas ve tepkisel)
            // Kamera 160px genişliğinde olduğu için merkez: 80px civarıdır
            if (moveState === 'neutral') {
              if (noseX > 90) { 
                if (playerLane > 0) playerLane--;
                moveState = 'moved'; 
              } else if (noseX < 65) { 
                if (playerLane < 2) playerLane++;
                moveState = 'moved'; 
              }
            } else if (moveState === 'moved') {
              if (noseX >= 65 && noseX <= 90) {
                moveState = 'neutral'; 
              }
            }
          }
        } catch (e) {
          console.error("Hızlı Yüz Tespiti Hatası:", e);
        }
        isDetecting = false;
      }
      
      // Saniyede ~60 kez yerine hemen sonraki mikro kareye geç
      if (!gameOver) {
        setTimeout(runDetectionLoop, 15); // ~60 FPS AI Çıkarım Döngüsü
      }
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
      if (decorTimer > 25) {
        sideDecorations.push({ side: 'left', z: 0, type: Math.random() > 0.5 ? '🌳' : '💡' });
        sideDecorations.push({ side: 'right', z: 0, type: Math.random() > 0.5 ? '🌳' : '💡' });
        decorTimer = 0;
      }

      for (let i = 0; i < sideDecorations.length; i++) {
        let dec = sideDecorations[i];
        dec.z += FIXED_SPEED;

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

      if (activeSkin === 'agent') {
        ctx.fillStyle = '#111827';
        ctx.fillRect(-20, 5, 40, 20);
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(-6, 5, 12, 10); 
        ctx.fillStyle = '#dc2626';
        ctx.fillRect(-2, 7, 4, 12);  
      } else if (activeSkin === 'king') {
        ctx.fillStyle = '#dc2626'; 
        ctx.fillRect(-24, 0, 48, 25);
        ctx.fillStyle = '#2563eb'; 
        ctx.fillRect(-20, 5, 40, 20);
      } else if (activeSkin === 'firefighter') {
        ctx.fillStyle = '#1e293b';
        ctx.fillRect(-20, 5, 40, 20);
        ctx.fillStyle = '#f59e0b';
        ctx.fillRect(-20, 12, 40, 4); 
      } else {
        ctx.fillStyle = '#2563eb';
        ctx.fillRect(-20, 5, 40, 20);
        ctx.fillRect(-12, -2, 24, 10); 

        ctx.strokeStyle = '#1d4ed8';
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(-18, -2); ctx.lineTo(-10, 8);
        ctx.moveTo(18, -2); ctx.lineTo(10, 8);
        ctx.stroke();
      }

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

      ctx.fillStyle = activeSkin === 'agent' ? '#000' : '#374151'; 
      ctx.beginPath();
      ctx.arc(0, -15, activeSkin === 'agent' ? 6 : 3, 0, Math.PI * 2);
      ctx.fill();

      if (activeSkin === 'king') {
        ctx.fillStyle = '#f59e0b';
        ctx.beginPath();
        ctx.moveTo(-12, -35); ctx.lineTo(-15, -45); ctx.lineTo(-6, -38);
        ctx.lineTo(0, -48); ctx.lineTo(6, -38); ctx.lineTo(15, -45); ctx.lineTo(12, -35);
        ctx.closePath();
        ctx.fill();
      } else if (activeSkin === 'firefighter') {
        ctx.fillStyle = '#dc2626';
        ctx.beginPath();
        ctx.arc(0, -32, 22, Math.PI, 0, false);
        ctx.fill();
        ctx.fillRect(-24, -34, 48, 5); 
      }

      ctx.strokeStyle = '#000';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(0, -5, 8, 0.1 * Math.PI, 0.9 * Math.PI, false);
      ctx.stroke();

      ctx.restore();
    }

    function createSparkles() {
      for (let i = 0; i < 10; i++) {
        sparkles.push({
          x: playerX,
          y: playerY - 30,
          vx: (Math.random() - 0.5) * 6,
          vy: (Math.random() - 0.5) * 6 - 2,
          size: Math.random() * 5 + 2,
          color: Math.random() > 0.5 ? '#ffcc00' : '#ffffff',
          alpha: 1.0
        });
      }
    }

    function triggerWordCompletedEffect() {
      coins += 10;
      coinsElement.innerText = coins;

      floatingMessage = {
        text: '🍌 +10 BANANA!',
        x: playerX,
        y: playerY - 30,
        alpha: 1.0,
        scale: 1.0
      };

      createSparkles();

      wordIndex = (wordIndex + 1) % wordList.length;
      currentWord = wordList[wordIndex];
      collectedCount = 0;
      renderWordUI();
    }

    function triggerDistanceBonusEffect() {
      coins += 10;
      coinsElement.innerText = coins;

      floatingMessage = {
        text: `🏃 ${nextDistanceMilestone}m BONUS! +10 BANANA`,
        x: playerX,
        y: playerY - 30,
        alpha: 1.0,
        scale: 0.9
      };

      createSparkles();
      nextDistanceMilestone += 500;
    }

    function updateGame() {
      if (gameOver) return;

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      distance += 0.4;
      distanceElement.innerText = Math.floor(distance);

      if (Math.floor(distance) >= nextDistanceMilestone) {
        triggerDistanceBonusEffect();
      }

      drawBackground();
      draw3DRoad();
      updateAndDrawDecorations();

      // 3. ŞERİT KAYMA HIZI HIZLANDIRILDI (0.25 -> 0.45)
      const targetX = baseLanes[playerLane];
      playerX += (targetX - playerX) * 0.45; 

      ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
      ctx.beginPath();
      ctx.ellipse(playerX, playerY + 30, 22, 7, 0, 0, Math.PI * 2);
      ctx.fill();

      drawVectorMinion(playerX, playerY);

      spawnTimer++;
      if (spawnTimer > 45) { 
        const randomLane = Math.floor(Math.random() * 3);
        
        if (Math.random() < 0.5 && collectedCount < currentWord.length) {
          const isCorrect = Math.random() < 0.7;
          const charToSpawn = isCorrect 
            ? currentWord[collectedCount] 
            : String.fromCharCode(65 + Math.floor(Math.random() * 26));

          letters.push({
            char: charToSpawn,
            lane: randomLane,
            z: 0
          });
        } else {
          const randomType = obstacleTypes[Math.floor(Math.random() * obstacleTypes.length)];
          obstacles.push({
            lane: randomLane,
            z: 0,
            type: randomType
          });
        }
        spawnTimer = 0;
      }

      for (let i = 0; i < letters.length; i++) {
        let letObj = letters[i];
        letObj.z += FIXED_SPEED;

        const horizonY = 180;
        const currentY = lerp(horizonY, 520, letObj.z);
        const currentX = lerp(topLanes[letObj.lane], baseLanes[letObj.lane], letObj.z);
        const currentScale = lerp(0.2, 1.0, letObj.z);

        ctx.fillStyle = 'rgba(255, 204, 0, 0.9)';
        ctx.beginPath();
        ctx.arc(currentX, currentY, 20 * currentScale, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = '#000000';
        ctx.font = `bold ${22 * currentScale}px sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(letObj.char, currentX, currentY);

        if (letObj.z >= 0.88 && letObj.z <= 1.02 && playerLane === letObj.lane) {
          if (letObj.char === currentWord[collectedCount]) {
            collectedCount++;
            renderWordUI();

            if (collectedCount === currentWord.length) {
              triggerWordCompletedEffect();
            }
          }
          letters.splice(i, 1);
          i--;
          continue;
        }

        if (letObj.z > 1.1) {
          letters.splice(i, 1);
          i--;
        }
      }

      for (let i = 0; i < obstacles.length; i++) {
        let obs = obstacles[i];
        obs.z += FIXED_SPEED;

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
        }
      }

      if (floatingMessage) {
        ctx.save();
        ctx.globalAlpha = floatingMessage.alpha;
        ctx.font = `bold ${28 * floatingMessage.scale}px sans-serif`;
        ctx.textAlign = 'center';
        ctx.fillStyle = '#ffcc00';
        ctx.lineWidth = 3;
        ctx.strokeStyle = '#000000';
        ctx.strokeText(floatingMessage.text, floatingMessage.x, floatingMessage.y);
        ctx.fillText(floatingMessage.text, floatingMessage.x, floatingMessage.y);
        ctx.restore();

        floatingMessage.y -= 3.5; 
        floatingMessage.alpha -= 0.025; 
        floatingMessage.scale += 0.005; 

        if (floatingMessage.alpha <= 0) {
          floatingMessage = null;
        }
      }

      for (let i = 0; i < sparkles.length; i++) {
        let sp = sparkles[i];
        sp.x += sp.vx;
        sp.y += sp.vy;
        sp.alpha -= 0.03;

        ctx.fillStyle = sp.color;
        ctx.globalAlpha = Math.max(0, sp.alpha);
        ctx.beginPath();
        ctx.arc(sp.x, sp.y, sp.size, 0, Math.PI * 2);
        ctx.fill();

        if (sp.alpha <= 0) {
          sparkles.splice(i, 1);
          i--;
        }
      }
      ctx.globalAlpha = 1.0;

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
      ctx.fillText('GAME OVER', 200, 220);
      
      ctx.fillStyle = '#38bdf8';
      ctx.font = '18px sans-serif';
      ctx.fillText('Mesafe: ' + Math.floor(distance) + ' m', 200, 270);

      ctx.fillStyle = '#ffcc00';
      ctx.font = '18px sans-serif';
      ctx.fillText('Muz Bakiyesi: ' + coins + ' 🍌', 200, 310);

      restartBtn.style.display = 'block';
      shopBtn.style.display = 'block';
    }

    function resetGame() {
      playerLane = 1;
      playerX = baseLanes[1];
      obstacles = [];
      letters = [];
      sideDecorations = [];
      sparkles = [];
      spawnTimer = 0;
      decorTimer = 0;
      collectedCount = 0;
      distance = 0;
      nextDistanceMilestone = 500;
      distanceElement.innerText = '0';
      floatingMessage = null;
      gameOver = false;
      moveState = 'neutral';

      renderWordUI();
      restartBtn.style.display = 'none';
      shopBtn.style.display = 'none';
      closeShop();
      
      runDetectionLoop();
      updateGame();
    }

    window.addEventListener('keydown', (e) => {
      if (e.code === 'Space' && gameOver && shopModal.style.display !== 'flex') {
        resetGame();
      }
    });

    async function main() {
      try {
        renderWordUI();
        statusText.innerText = "Kamera İzni İsteniyor...";
        await setupCamera();
        
        statusText.innerText = "AI Modeli Yükleniyor...";
        
        if (typeof blazeface === 'undefined') {
          throw new Error("BlazeFace kütüphanesi yüklenemedi!");
        }

        model = await blazeface.load();
        
        statusText.innerText = "Bello! Doğru Harfleri Topla.";
        
        runDetectionLoop(); // Bağımsız hızlı döngü başlatılır
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

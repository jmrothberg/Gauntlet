
// REAL LYNX GAMEPLAY LOGIC

// Original Lynx resolution was 102x160 (vertical). We scale up.
const SCALE = 4;
const CANVAS_WIDTH = 102 * SCALE;  // 408
const CANVAS_HEIGHT = 160 * SCALE; // 640
const TILE_SIZE = 16 * SCALE;      // 64

// Stats based on original manual/gameplay
const CLASSES = {
    android:    { name: "ANDROID",    hp: 1000, spd: 2.0, str: 3, mag: 1, shot: 'laser' },
    gunfighter: { name: "GUNFIGHTER", hp: 800,  spd: 2.5, str: 4, mag: 2, shot: 'bullet' },
    nerd:       { name: "NERD",       hp: 600,  spd: 1.8, str: 1, mag: 5, shot: 'magic' },
    pirate:     { name: "PIRATE",     hp: 1200, spd: 1.5, str: 5, mag: 1, shot: 'cannon' },
    punkrocker: { name: "PUNK",       hp: 900,  spd: 2.2, str: 4, mag: 2, shot: 'note' },
    samurai:    { name: "SAMURAI",    hp: 1100, spd: 2.3, str: 5, mag: 1, shot: 'star' },
    valkyrie:   { name: "VALKYRIE",   hp: 1000, spd: 2.0, str: 4, mag: 3, shot: 'axe' },
    wizard:     { name: "WIZARD",     hp: 700,  spd: 1.8, str: 2, mag: 6, shot: 'fireball' }
};

let canvas, ctx;
let gameState = "MENU";
let keys = {};
let player = null;
let projectiles = [];
let enemies = [];
let map = [];
let camera = { x: 0, y: 0 };
let score = 0;
let level = 1;
let frame = 0;

// Audio Context
const AudioContext = window.AudioContext || window.webkitAudioContext;
const audioCtx = new AudioContext();

function playSound(type) {
    if (audioCtx.state === 'suspended') audioCtx.resume();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);

    const now = audioCtx.currentTime;
    
    if (type === 'shoot') {
        osc.frequency.setValueAtTime(600, now);
        osc.frequency.exponentialRampToValueAtTime(100, now + 0.15);
        gain.gain.setValueAtTime(0.1, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.15);
        osc.start(now);
        osc.stop(now + 0.15);
    } else if (type === 'hit') {
        osc.type = 'square';
        osc.frequency.setValueAtTime(150, now);
        osc.frequency.linearRampToValueAtTime(100, now + 0.1);
        gain.gain.setValueAtTime(0.1, now);
        gain.gain.linearRampToValueAtTime(0.01, now + 0.1);
        osc.start(now);
        osc.stop(now + 0.1);
    }
}

function init() {
    canvas = document.getElementById('gameCanvas');
    ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = false; // Keep pixels sharp

    window.addEventListener('keydown', e => keys[e.key] = true);
    window.addEventListener('keyup', e => keys[e.key] = false);

    requestAnimationFrame(loop);
}

function startGame(className) {
    let cls = CLASSES[className];
    player = {
        x: CANVAS_WIDTH / 2,
        y: CANVAS_HEIGHT / 2,
        class: cls,
        hp: cls.hp,
        maxHp: cls.hp,
        dir: { x: 0, y: 1 },
        cooldown: 0,
        invincible: 0
    };
    
    score = 0;
    level = 1;
    loadLevel(level);
    gameState = "PLAY";
}

function loadLevel(lvl) {
    map = [];
    enemies = [];
    projectiles = [];
    
    // Infinite vertical scroller style
    // We generate a buffer of walls
    const MAP_W = Math.floor(CANVAS_WIDTH / TILE_SIZE);
    const MAP_H = 100; 
    
    for(let y = 0; y < MAP_H; y++) {
        for(let x = 0; x < MAP_W; x++) {
            let isWall = false;
            if(x === 0 || x === MAP_W - 1) isWall = true; // Borders
            else if(Math.random() < 0.15) isWall = true;  // Random pillars
            
            if(isWall) {
                map.push({ x: x * TILE_SIZE, y: y * TILE_SIZE, w: TILE_SIZE, h: TILE_SIZE });
            }
        }
    }
    
    // Spawn enemies
    for(let i=0; i<20 + lvl * 5; i++) {
        enemies.push({
            x: Math.random() * (CANVAS_WIDTH - 64) + 32,
            y: Math.random() * (MAP_H * TILE_SIZE - 500) + 500,
            w: 48, h: 48,
            hp: 10 + lvl * 2,
            type: 'ghost'
        });
    }
    
    player.y = 100;
    camera.y = 0;
}

function update() {
    if(gameState !== "PLAY") return;
    
    // Player Move
    let dx = 0;
    let dy = 0;
    if(keys['ArrowLeft'] || keys['a']) dx = -1;
    if(keys['ArrowRight'] || keys['d']) dx = 1;
    if(keys['ArrowUp'] || keys['w']) dy = -1;
    if(keys['ArrowDown'] || keys['s']) dy = 1;
    
    if(dx || dy) {
        // Update Direction
        player.dir = { x: dx, y: dy };
        
        let spd = player.class.spd * 3; // Base speed scaling
        let nx = player.x + dx * spd;
        let ny = player.y + dy * spd;
        
        // Wall Collision
        if(!checkWall(nx, player.y)) player.x = nx;
        if(!checkWall(player.x, ny)) player.y = ny;
        
        // Camera Follow (Vertical)
        let targetCamY = player.y - CANVAS_HEIGHT / 3;
        camera.y += (targetCamY - camera.y) * 0.1;
        if(camera.y < 0) camera.y = 0;
    }
    
    // Shoot
    if(keys[' '] && player.cooldown <= 0) {
        playSound('shoot');
        let shotDir = { ...player.dir };
        if(shotDir.x === 0 && shotDir.y === 0) shotDir.y = 1;
        
        projectiles.push({
            x: player.x, y: player.y,
            vx: shotDir.x * 10, vy: shotDir.y * 10,
            life: 60
        });
        player.cooldown = 15;
    }
    if(player.cooldown > 0) player.cooldown--;
    
    // Projectiles
    for(let i = projectiles.length - 1; i >= 0; i--) {
        let p = projectiles[i];
        p.x += p.vx;
        p.y += p.vy;
        p.life--;
        
        if(p.life <= 0 || checkWall(p.x, p.y)) {
            projectiles.splice(i, 1);
            continue;
        }
        
        // Hit Enemy
        for(let j = enemies.length - 1; j >= 0; j--) {
            let e = enemies[j];
            if(Math.abs(p.x - e.x) < 30 && Math.abs(p.y - e.y) < 30) {
                e.hp -= player.class.str * 2;
                playSound('hit');
                projectiles.splice(i, 1);
                if(e.hp <= 0) {
                    enemies.splice(j, 1);
                    score += 100;
                }
                break;
            }
        }
    }
    
    // Enemies
    for(let e of enemies) {
        let dist = Math.hypot(player.x - e.x, player.y - e.y);
        if(dist < 400) {
            e.x += (player.x - e.x) * 0.01;
            e.y += (player.y - e.y) * 0.01;
            
            // Hit Player
            if(dist < 32 && player.invincible <= 0) {
                player.hp -= 50;
                player.invincible = 60;
                if(player.hp <= 0) gameState = "GAMEOVER";
            }
        }
    }
    if(player.invincible > 0) player.invincible--;
    
    // Hunger
    if(frame % 60 === 0) {
        player.hp -= 1;
        if(player.hp <= 0) gameState = "GAMEOVER";
    }
    
    frame++;
}

function checkWall(x, y) {
    for(let w of map) {
        // Simple rect collision
        if(x > w.x && x < w.x + w.w && y > w.y && y < w.y + w.h) return true;
    }
    return false;
}

function draw() {
    // Clear
    ctx.fillStyle = "#111";
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    if(gameState === "MENU") {
        drawMenu();
        return;
    }
    
    ctx.save();
    ctx.translate(0, -camera.y);
    
    // Draw Floor (Tiled)
    let bg = new Image(); bg.src = EXTRACTED_ASSETS.floor_extracted;
    if(bg.width > 0) {
        // Simple tiling pattern
        let pat = ctx.createPattern(bg, 'repeat');
        ctx.fillStyle = pat;
        ctx.fillRect(0, camera.y, CANVAS_WIDTH, CANVAS_HEIGHT);
    } else {
        ctx.fillStyle = "#222";
        ctx.fillRect(0, camera.y, CANVAS_WIDTH, CANVAS_HEIGHT);
    }
    
    // Draw Walls
    let wallImg = new Image(); wallImg.src = EXTRACTED_ASSETS.sample_1; // Use extracted wall
    for(let w of map) {
        if(w.y < camera.y - TILE_SIZE || w.y > camera.y + CANVAS_HEIGHT) continue;
        if(wallImg.width > 0) ctx.drawImage(wallImg, w.x, w.y, w.w, w.h);
        else {
            ctx.fillStyle = "#666";
            ctx.fillRect(w.x, w.y, w.w, w.h);
        }
    }
    
    // Draw Enemies
    for(let e of enemies) {
        if(e.y < camera.y - 50 || e.y > camera.y + CANVAS_HEIGHT) continue;
        ctx.fillStyle = "red";
        ctx.fillRect(e.x - 24, e.y - 24, 48, 48);
        // Eyes
        ctx.fillStyle = "yellow";
        ctx.fillRect(e.x - 10, e.y - 10, 8, 8);
        ctx.fillRect(e.x + 2, e.y - 10, 8, 8);
    }
    
    // Draw Player
    if(player.invincible % 10 < 5) {
        let pImg = new Image(); pImg.src = EXTRACTED_ASSETS.player_extracted;
        if(pImg.width > 0) {
            ctx.drawImage(pImg, player.x - 32, player.y - 32, 64, 64);
        } else {
            ctx.fillStyle = "cyan";
            ctx.fillRect(player.x - 20, player.y - 20, 40, 40);
        }
    }
    
    // Projectiles
    ctx.fillStyle = "yellow";
    for(let p of projectiles) {
        ctx.beginPath();
        ctx.arc(p.x, p.y, 6, 0, Math.PI*2);
        ctx.fill();
    }
    
    ctx.restore();
    
    // UI
    ctx.fillStyle = "#000";
    ctx.fillRect(0, CANVAS_HEIGHT - 80, CANVAS_WIDTH, 80);
    ctx.fillStyle = "#FFF";
    ctx.font = "20px Courier New";
    ctx.fillText("HP: " + player.hp, 20, CANVAS_HEIGHT - 30);
    ctx.fillText("SCORE: " + score, 200, CANVAS_HEIGHT - 30);
    
    if(gameState === "GAMEOVER") {
        ctx.fillStyle = "rgba(0,0,0,0.8)";
        ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
        ctx.fillStyle = "red";
        ctx.font = "40px Courier New";
        ctx.textAlign = "center";
        ctx.fillText("GAME OVER", CANVAS_WIDTH/2, CANVAS_HEIGHT/2);
        ctx.fillStyle = "white";
        ctx.font = "20px Courier New";
        ctx.fillText("Press R to Restart", CANVAS_WIDTH/2, CANVAS_HEIGHT/2 + 60);
        if(keys['r'] || keys['R']) gameState = "MENU";
    }
}

function drawMenu() {
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
    
    let logo = new Image(); logo.src = EXTRACTED_ASSETS.logo;
    if(logo.width > 0) {
        ctx.drawImage(logo, CANVAS_WIDTH/2 - 150, 50, 300, 200);
    } else {
        ctx.fillStyle = "orange";
        ctx.textAlign = "center";
        ctx.font = "50px Courier New";
        ctx.fillText("GAUNTLET", CANVAS_WIDTH/2, 150);
    }
    
    ctx.fillStyle = "white";
    ctx.textAlign = "center";
    ctx.font = "24px Courier New";
    ctx.fillText("SELECT CLASS", CANVAS_WIDTH/2, 300);
    
    let y = 350;
    let idx = 1;
    for(let k in CLASSES) {
        ctx.fillStyle = (keys[idx.toString()]) ? "yellow" : "gray";
        ctx.fillText(idx + ". " + CLASSES[k].name, CANVAS_WIDTH/2, y);
        y += 35;
        
        if(keys[idx.toString()]) startGame(k);
        idx++;
    }
}

function loop() {
    update();
    draw();
    requestAnimationFrame(loop);
}

window.onload = init;


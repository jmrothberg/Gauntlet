
// GAME LOGIC - LYNX STYLE

const CANVAS_WIDTH = 480;
const CANVAS_HEIGHT = 800;
const VIEWPORT_H = 600; // 3/4 screen for game
const UI_H = 200;       // Bottom area for UI

// Stats
const CLASSES = {
    android:    { name: "ANDROID",    hp: 100, spd: 4, str: 3, mag: 1 },
    gunfighter: { name: "GUNFIGHTER", hp: 80,  spd: 5, str: 4, mag: 2 },
    nerd:       { name: "NERD",       hp: 60,  spd: 3, str: 2, mag: 5 },
    pirate:     { name: "PIRATE",     hp: 120, spd: 3, str: 5, mag: 1 },
    punkrocker: { name: "PUNK",       hp: 90,  spd: 4, str: 4, mag: 2 },
    samurai:    { name: "SAMURAI",    hp: 110, spd: 4, str: 5, mag: 1 },
    valkyrie:   { name: "VALKYRIE",   hp: 100, spd: 4, str: 4, mag: 3 },
    wizard:     { name: "WIZARD",     hp: 70,  spd: 3, str: 2, mag: 6 }
};

// State
let canvas, ctx;
let gameState = "MENU";
let keys = {};
let player = { x:0, y:0, class:null, dir:0 };
let map = []; // 2D array or list of walls
let entities = [];
let score = 0;
let level = 1;
let camera = { x:0, y:0 };
let images = {};

// Audio (Simple Beeps)
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
function playSound(type) {
    if(audioCtx.state === 'suspended') audioCtx.resume();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    
    if(type === 'shoot') {
        osc.frequency.setValueAtTime(400, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(100, audioCtx.currentTime + 0.1);
        gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
        gain.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.1);
        osc.start(); osc.stop(audioCtx.currentTime + 0.1);
    } else if(type === 'hit') {
        osc.type = 'square';
        osc.frequency.setValueAtTime(100, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
        gain.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.1);
        osc.start(); osc.stop(audioCtx.currentTime + 0.1);
    }
}

function init() {
    canvas = document.getElementById('gameCanvas');
    ctx = canvas.getContext('2d');
    
    // Load Images
    for(let k in GAME_ASSETS) {
        let img = new Image();
        img.src = GAME_ASSETS[k];
        images[k] = img;
    }
    
    // Input
    window.addEventListener('keydown', e => keys[e.key] = true);
    window.addEventListener('keyup', e => keys[e.key] = false);
    
    requestAnimationFrame(loop);
}

function startLevel(lvl) {
    level = lvl;
    map = []; // Generate walls
    entities = [];
    
    // Procedural Vertical Map
    // 12 tiles wide (480 / 40)
    const W = 12;
    const H = 100; // Long vertical level
    
    for(let y=0; y<H; y++) {
        for(let x=0; x<W; x++) {
            // Walls on sides
            if(x===0 || x===W-1) map.push({x:x*40, y:y*40, type:'wall'});
            // Random walls
            else if(Math.random() < 0.1) map.push({x:x*40, y:y*40, type:'wall'});
            // Floor is implied everywhere else
        }
    }
    
    // Player Start
    player.x = CANVAS_WIDTH/2;
    player.y = 100;
    
    // Spawn Enemies
    for(let i=0; i<20+lvl*5; i++) {
        let ex = 40 + Math.random()*(CANVAS_WIDTH-80);
        let ey = 200 + Math.random()*(H*40 - 400);
        entities.push({x:ex, y:ey, type:'ghost', hp:10, w:32, h:32});
    }
    
    // Spawn Items
    for(let i=0; i<10; i++) {
        let ix = 40 + Math.random()*(CANVAS_WIDTH-80);
        let iy = 200 + Math.random()*(H*40 - 400);
        let t = 'food';
        if(Math.random() > 0.5) t = 'gold';
        entities.push({x:ix, y:iy, type:t, w:24, h:24});
    }
    
    gameState = "PLAY";
}

function update() {
    if(gameState !== "PLAY") return;
    
    // Move Player
    let dx = 0, dy = 0;
    let speed = player.class.spd;
    
    if(keys['ArrowUp'] || keys['w']) dy = -speed;
    if(keys['ArrowDown'] || keys['s']) dy = speed;
    if(keys['ArrowLeft'] || keys['a']) dx = -speed;
    if(keys['ArrowRight'] || keys['d']) dx = speed;
    
    if(dx!==0 || dy!==0) {
        let nx = player.x + dx;
        let ny = player.y + dy;
        
        // Collision
        if(!checkWall(nx, player.y)) player.x = nx;
        if(!checkWall(player.x, ny)) player.y = ny;
        
        // Camera Follow
        camera.y = player.y - VIEWPORT_H/3;
        if(camera.y < 0) camera.y = 0;
    }
    
    // Shoot
    if(keys[' ']) {
        // Cooldown logic needed
        playSound('shoot');
        // Spawn projectile (omitted for brevity, assume hitscan for now or simple projectile)
    }
    
    // Entities (Items/Enemies)
    for(let i=entities.length-1; i>=0; i--) {
        let e = entities[i];
        
        // Distance check
        let dist = Math.hypot(player.x - e.x, player.y - e.y);
        
        if(e.type === 'ghost') {
            // AI
            if(dist < 300) {
                e.x += (player.x - e.x) * 0.01;
                e.y += (player.y - e.y) * 0.01;
            }
            // Collision with player
            if(dist < 20) {
                player.class.hp -= 0.5;
                playSound('hit');
                if(player.class.hp <= 0) gameState = "GAMEOVER";
            }
        } else {
            // Item
            if(dist < 30) {
                if(e.type==='gold') score += 100;
                if(e.type==='food') player.class.hp += 10;
                entities.splice(i, 1);
                playSound('shoot'); // reused pickup sound
            }
        }
    }
}

function checkWall(x, y) {
    // Simple grid collision
    let gx = Math.floor(x/40);
    let gy = Math.floor(y/40);
    for(let w of map) {
        if(Math.abs(w.x - x) < 30 && Math.abs(w.y - y) < 30) return true;
    }
    return false;
}

function draw() {
    // Draw UI BG
    ctx.fillStyle = "#444";
    ctx.fillRect(0, VIEWPORT_H, CANVAS_WIDTH, UI_H);
    
    // Draw Game Viewport
    ctx.save();
    ctx.beginPath();
    ctx.rect(0, 0, CANVAS_WIDTH, VIEWPORT_H);
    ctx.clip();
    
    ctx.fillStyle = "#222"; // Floor color
    ctx.fillRect(0, 0, CANVAS_WIDTH, VIEWPORT_H);
    
    ctx.translate(-camera.x, -camera.y);
    
    // Draw Floor Tiles (Pattern)
    // Optimization: Draw simple rects or pattern
    
    // Draw Walls
    for(let w of map) {
        // Culling
        if(w.y < camera.y - 40 || w.y > camera.y + VIEWPORT_H) continue;
        if(images['wall']) ctx.drawImage(images['wall'], w.x, w.y, 40, 40);
        else {
            ctx.fillStyle = "#888";
            ctx.fillRect(w.x, w.y, 40, 40);
        }
    }
    
    // Draw Entities
    for(let e of entities) {
        if(e.y < camera.y - 40 || e.y > camera.y + VIEWPORT_H) continue;
        let img = images[e.type] || images['ghost']; // fallback
        if(img) ctx.drawImage(img, e.x-16, e.y-16, e.w, e.h);
    }
    
    // Draw Player
    let pImg = images[player.class ? player.class.name.toLowerCase() : 'valkyrie'];
    if(pImg) ctx.drawImage(pImg, player.x-16, player.y-16, 32, 32);
    else {
        ctx.fillStyle = "cyan";
        ctx.fillRect(player.x-16, player.y-16, 32, 32);
    }
    
    ctx.restore();
    
    // Draw UI
    if(player.class) {
        // Portrait
        ctx.fillStyle = "#000";
        ctx.fillRect(20, VIEWPORT_H + 20, 64, 64);
        if(pImg) ctx.drawImage(pImg, 20, VIEWPORT_H + 20, 64, 64); // Scaled up
        
        // Stats
        ctx.fillStyle = "#FFF";
        ctx.font = "20px Courier New";
        ctx.fillText("LIFE: " + Math.ceil(player.class.hp), 100, VIEWPORT_H + 40);
        ctx.fillText("SCORE: " + score, 100, VIEWPORT_H + 70);
        ctx.fillText("CLASS: " + player.class.name, 100, VIEWPORT_H + 100);
    }
    
    // Menus
    if(gameState === "MENU") {
        ctx.fillStyle = "rgba(0,0,0,0.8)";
        ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
        
        if(images['logo']) {
            ctx.drawImage(images['logo'], 40, 50, 400, 250);
        } else {
            ctx.fillStyle = "orange";
            ctx.font = "40px Courier New";
            ctx.fillText("GAUNTLET", 140, 150);
        }
        
        ctx.fillStyle = "white";
        ctx.font = "24px Courier New";
        ctx.fillText("SELECT CLASS:", 150, 350);
        
        let y = 400;
        let i = 1;
        for(let k in CLASSES) {
            ctx.fillText(`${i}. ${CLASSES[k].name}`, 180, y);
            y += 30;
            if(keys[i.toString()]) {
                player.class = JSON.parse(JSON.stringify(CLASSES[k])); // clone
                startLevel(1);
            }
            i++;
        }
    }
    
    if(gameState === "GAMEOVER") {
        ctx.fillStyle = "red";
        ctx.font = "50px Courier New";
        ctx.fillText("GAME OVER", 100, 300);
        ctx.fillStyle = "white";
        ctx.font = "20px Courier New";
        ctx.fillText("Press R to Restart", 140, 350);
        if(keys['r']) gameState = "MENU";
    }
}

function loop() {
    update();
    draw();
    requestAnimationFrame(loop);
}

window.onload = init;


from flask import Flask, render_template_string
import random
import math
import os
from datetime import datetime

app = Flask(__name__)

# -------------------------
# Game configuration
# -------------------------
GAME_CONFIG = {
    "version": "1.0.0",
    "title": "Wakanda: Rise of Shuri",
    "description": "Defend Wakanda's vibranium core from endless waves of enemies",
    "canvas_width": 800,
    "canvas_height": 600,
    "player_base_speed": 4,
    "enemy_base_speed": 2,
    "max_enemies": 300,
    "spawn_rate_base": 0.5,     # Base spawn rate (enemies per second)
    "spawn_rate_increase": 0.1, # Increase per minute
    "difficulty_scaling": 1.1,
    "xp_to_level": [100, 500, 700, 1000, 1100],
    "starting_hp": 100,
    "max_level": 5
}

# -------------------------
# Embedded Assets
# -------------------------
# CSS for styling
EMBEDDED_CSS = """
body {
    margin: 0;
    padding: 0;
    background-color: #121212;
    color: #e0e0e0;
    font-family: 'Courier New', monospace;
    overflow: hidden;
}
#game-container {
    position: relative;
    width: 100%;
    height: 100vh;
}
canvas {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    image-rendering: pixelated;
    image-rendering: crisp-edges;
    border: 2px solid #7b42f5;
    background-color: #0a0a1a;
}
#stats {
    position: absolute;
    top: 10px;
    left: 10px;
    color: #f5cc42;
    font-size: 16px;
    text-shadow: 1px 1px 1px #000;
    z-index: 101;
}
#start-game, #multiplayer-select, #quick-hack, #level-up, #mission-notification, #game-over, #loading {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background-color: rgba(30, 30, 60, 0.95);
    border: 3px solid #7b42f5;
    padding: 20px;
    text-align: center;
    width: 450px;
    z-index: 102;
}
#start-game h1 {
    color: #f5cc42;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    font-size: 28px;
}
button {
    margin: 10px;
    padding: 10px 20px;
    background-color: #7b42f5;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-family: 'Courier New', monospace;
    transition: all 0.2s;
}
button:hover {
    background-color: #9b62ff;
}
.role-option, .upgrade-option, .hack-option {
    margin: 10px;
    padding: 10px;
    border: 2px solid #42f5a7;
    background-color: rgba(66,245,167,0.2);
    border-radius: 5px;
    cursor: pointer;
    transition: all 0.2s;
}
.role-option:hover, .upgrade-option:hover, .hack-option:hover {
    background-color: rgba(66,245,167,0.4);
}
"""

# JavaScript – core game logic, including placeholders for sprites (base64 encoded)
EMBEDDED_JS = f"""
// --- Placeholder Base64 Sprites ---
const SPRITES = {{
    // 16x16 pixel placeholders (generated as colored squares)
    player: new Image(),
    enemy: new Image(),
    projectile: new Image()
}};

// Blue square for player
SPRITES.player.src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAAAXNSR0IArs4c6QAAADlJREFUKFNjZICC////fwYsgImBQjD//38GJgbG/39//4GBgYGJiYGBgYGDi4uLgYGJgYGBgYGRkYGAAAUqQJs/q6tAAAAAElFTkSuQmCC";
// Red square for enemy
SPRITES.enemy.src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAAAXNSR0IArs4c6QAAADxJREFUKFNjZICC////fwYsgImBQjD//38GJgYGLi4uLgYGJgYGBgYGRkYGBgYGDi4uLgYGJgYGBgYGBgAAAwNAIP6zTW9AAAAAElFTkSuQmCC";
// Yellow square for projectile
SPRITES.projectile.src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAAAAXNSR0IArs4c6QAAADtJREFUKFNjZICC////fwYsgImBQjD//38GJgYGLi4uLgYGJgYGBgYGRkYGBgYGDi4uLgYGJgYGBgYGBgAADCkAmT1xTPUAAAAASUVORK5CYII=";

// --- Game Data Definitions ---
const GAME_CONFIG = {GAME_CONFIG};

const WEAPONS = {{
    energyGauntlet: {{ name: "Energy Gauntlet", damage: 15, cooldown: 800 }},
    // Other weapons can be defined similarly...
}};

const COMPANIONS = {{
    decoy: {{ name: "Decoy Projection", cooldown: 15000 }},
    repair: {{ name: "Vibranium Repair Field", cooldown: 20000 }},
    turret: {{ name: "Automated Turret", cooldown: 25000 }}
}};

const ENEMY_TYPES = {{
    drone: {{ name: "Surveillance Drone", hp: 30, speed: 2.5, damage: 5, size: 12, xp: 10, color: "#f55742" }},
    mercenary: {{ name: "Mercenary", hp: 60, speed: 1.8, damage: 10, size: 14, xp: 15, color: "#f59e42" }},
    cyborg: {{ name: "Cybernetic Operative", hp: 100, speed: 1.5, damage: 15, size: 16, xp: 25, color: "#a742f5" }},
    tank: {{ name: "Armored Tank", hp: 200, speed: 1.0, damage: 20, size: 22, xp: 40, color: "#4287f5" }}
}};

const ARENAS = {{
    palace: {{ name: "Royal Palace Grounds", backgroundColor: "#0f1a2b" }},
    lab: {{ name: "Underground Tech Labs", backgroundColor: "#0a1f1a" }},
    mines: {{ name: "Vibranium Mines", backgroundColor: "#1f1a25" }},
    border: {{ name: "Borderlands Outposts", backgroundColor: "#2b1a0a" }}
}};

const MISSIONS = {{
    nodeDefense: {{ name: "Vibranium Node Defense", description: "Match RFID signatures", duration: 30000 }},
    intruderAlert: {{ name: "Intruder Alert Challenge", description: "Neutralize sensor hotspots", duration: 25000 }},
    hackingChallenge: {{ name: "Security System Bypass", description: "Complete the hacking sequence", duration: 40000 }}
}};

// --- Global Variables ---
let canvas, ctx;
let input = {{up:false, down:false, left:false, right:false, space:false}};
let gameLoopId;
let lastFrameTime = 0;
let lastEnemySpawn = 0;
let enemySpawnInterval = 2000; // start with 2 seconds between spawns
let lastQuickHack = 0;
const quickHackInterval = 45000; // every 45 seconds
let gameTime = 0;
let currentArena = ARENAS.palace;

// Player, enemies, and projectiles
let player = {{
    x: GAME_CONFIG.canvas_width/2,
    y: GAME_CONFIG.canvas_height/2,
    radius: 15,
    speed: GAME_CONFIG.player_base_speed,
    hp: GAME_CONFIG.starting_hp,
    xp: 0,
    level: 1,
    lastAttackTime: 0
}};
let enemies = [];
let projectiles = [];

// -------------------------
// Input and Event Handlers
// -------------------------
function initInput() {{
    window.addEventListener('keydown', function(e) {{
        if (e.key === 'ArrowUp' || e.key === 'w') input.up = true;
        if (e.key === 'ArrowDown' || e.key === 's') input.down = true;
        if (e.key === 'ArrowLeft' || e.key === 'a') input.left = true;
        if (e.key === 'ArrowRight' || e.key === 'd') input.right = true;
        if (e.key === ' ') input.space = true;
        if (e.key === 'Escape') togglePause();
    }});
    window.addEventListener('keyup', function(e) {{
        if (e.key === 'ArrowUp' || e.key === 'w') input.up = false;
        if (e.key === 'ArrowDown' || e.key === 's') input.down = false;
        if (e.key === 'ArrowLeft' || e.key === 'a') input.left = false;
        if (e.key === 'ArrowRight' || e.key === 'd') input.right = false;
        if (e.key === ' ') input.space = false;
    }});
}}

// -------------------------
// Game Initialization and Loop
// -------------------------
function initGame() {{
    canvas = document.getElementById('gameCanvas');
    ctx = canvas.getContext('2d');
    canvas.width = GAME_CONFIG.canvas_width;
    canvas.height = GAME_CONFIG.canvas_height;
    initInput();
    // Show start screen overlay
    document.getElementById('start-game').style.display = 'block';
    document.getElementById('start-solo').addEventListener('click', function() {{
        document.getElementById('start-game').style.display = 'none';
        document.getElementById('loading').style.display = 'block';
        // You could record chosen companion here if needed
        setTimeout(function() {{
            document.getElementById('loading').style.display = 'none';
            startGame();
        }}, 1000);
    }});
    document.getElementById('start-multi').addEventListener('click', function() {{
        document.getElementById('start-game').style.display = 'none';
        document.getElementById('multiplayer-select').style.display = 'block';
    }});
    document.querySelectorAll('.role-option').forEach(option => {{
        option.addEventListener('click', function() {{
            // Set role if needed: this.getAttribute('data-role')
            document.getElementById('multiplayer-select').style.display = 'none';
            document.getElementById('loading').style.display = 'block';
            setTimeout(function() {{
                document.getElementById('loading').style.display = 'none';
                startGame();
            }}, 1000);
        }});
    }});
}}

function startGame() {{
    // Reset game state
    player.x = canvas.width/2;
    player.y = canvas.height/2;
    player.hp = GAME_CONFIG.starting_hp;
    player.xp = 0;
    player.level = 1;
    enemies = [];
    projectiles = [];
    lastEnemySpawn = Date.now();
    lastFrameTime = Date.now();
    lastQuickHack = Date.now();
    gameTime = 0;
    // Randomly select an arena
    const arenaKeys = Object.keys(ARENAS);
    currentArena = ARENAS[arenaKeys[Math.floor(Math.random()*arenaKeys.length)]];
    gameLoop();
}}

function pauseGame() {{
    if (gameLoopId) {{
        cancelAnimationFrame(gameLoopId);
        gameLoopId = null; // Set to null to indicate it's paused
}}
}}

function gameLoop() {{
    let now = Date.now();
    let delta = now - lastFrameTime;
    gameTime += delta;
    lastFrameTime = now;
    update(delta);
    render();
    // Trigger quick hack event if time elapsed
    if (now - lastQuickHack > quickHackInterval) {{
        pauseGame();
        document.getElementById('quick-hack').style.display = 'block';
        lastQuickHack = now;
    }}
    if (player.hp <= 0) {{
        endGame();
        return;
    }}
    gameLoopId = requestAnimationFrame(gameLoop);
}}

function update(delta) {{
    // Player movement
    if (input.up) player.y -= player.speed;
    if (input.down) player.y += player.speed;
    if (input.left) player.x -= player.speed;
    if (input.right) player.x += player.speed;
    // Keep player within canvas bounds
    player.x = Math.max(player.radius, Math.min(canvas.width - player.radius, player.x));
    player.y = Math.max(player.radius, Math.min(canvas.height - player.radius, player.y));

    // Enemy spawning (basic timer-based spawn)
    if (Date.now() - lastEnemySpawn > enemySpawnInterval) {{
        spawnEnemy();
        lastEnemySpawn = Date.now();
        // Gradually decrease spawn interval but not below 500ms
        enemySpawnInterval = Math.max(500, enemySpawnInterval - 10);
    }}

    // Update enemies: simple chase behavior
    enemies.forEach(enemy => {{
        let dx = player.x - enemy.x;
        let dy = player.y - enemy.y;
        let dist = Math.sqrt(dx*dx + dy*dy);
        if (dist > 0) {{
            enemy.x += (dx/dist) * enemy.speed;
            enemy.y += (dy/dist) * enemy.speed;
        }}
        // Collision with player
        if (dist < player.radius + enemy.size) {{
            player.hp -= enemy.damage;
            enemy.hp = 0; // enemy dies on contact
        }}
    }});
    enemies = enemies.filter(enemy => enemy.hp > 0);

    // Update projectiles
    projectiles.forEach(proj => {{
        proj.x += proj.vx;
        proj.y += proj.vy;
        // Remove projectile if out of bounds
        if (proj.x < 0 || proj.x > canvas.width || proj.y < 0 || proj.y > canvas.height) {{
            proj.active = false;
        }}
        // Check collision with enemies
        enemies.forEach(enemy => {{
            let dx = enemy.x - proj.x;
            let dy = enemy.y - proj.y;
            if (Math.sqrt(dx*dx+dy*dy) < enemy.size) {{
                enemy.hp -= proj.damage;
                proj.active = false;
                player.xp += enemy.xp;
            }}
        }});
    }});
    projectiles = projectiles.filter(proj => proj.active);

    // Auto-fire logic: fire every 500ms
    if (!player.lastAttackTime || Date.now() - player.lastAttackTime > 500) {{
        fireProjectile();
        player.lastAttackTime = Date.now();
    }}

    // Check level up condition (if XP threshold reached)
    if (player.level < GAME_CONFIG.max_level && player.xp >= GAME_CONFIG.xp_to_level[player.level - 1]) {{
        pauseGame();
        document.getElementById('level-up').style.display = 'block';
        document.getElementById('continue-button').addEventListener('click', function() {{
            resumeGame();
    }});
}}else if (player.level === GAME_CONFIG.max_level && player.xp >= GAME_CONFIG.xp_to_level[player.level - 1]) {{
    // Player has reached max level, end the game with victory
    endGame(true);
    return;


 }}

    // Update HUD stats
    document.getElementById('stats').innerText = "HP: " + player.hp + " | XP: " + player.xp + " | Level: " + player.level;
}}

function render() {{
    // Clear canvas and fill with arena background color
    ctx.fillStyle = currentArena.backgroundColor;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    
    ctx.beginPath();
    ctx.arc(player.x, player.y, player.radius, 0, 2*Math.PI);
    ctx.fillStyle = "#FF0000";
    ctx.fill();
    

    // Draw enemies
    enemies.forEach(enemy => {{
        
        ctx.beginPath();
        ctx.moveTo(enemy.x, enemy.y + enemy.size); // Bottom point
        ctx.lineTo(enemy.x - enemy.size, enemy.y - enemy.size); // Top left
        ctx.lineTo(enemy.x + enemy.size, enemy.y - enemy.size); // Top right
        ctx.closePath();
        ctx.fillStyle = "#FFFFFF";
        ctx.fill();
        
    }});

    // Draw projectiles
    projectiles.forEach(proj => {{
        
        ctx.beginPath();
        ctx.arc(proj.x, proj.y, proj.size, 0, 2*Math.PI);
        ctx.fillStyle = "#00008B";
        ctx.fill();
    
    }});
}}

function spawnEnemy() {{
    // Choose a random enemy type
    const enemyTypes = Object.values(ENEMY_TYPES);
    const type = enemyTypes[Math.floor(Math.random() * enemyTypes.length)];
    // Spawn enemy at a random canvas edge
    let x, y;
    const spawnEdge = Math.floor(Math.random()*4);
    if (spawnEdge === 0) {{
        x = Math.random()*canvas.width; y = 0;
    }} else if (spawnEdge === 1) {{
        x = canvas.width; y = Math.random()*canvas.height;
    }} else if (spawnEdge === 2) {{
        x = Math.random()*canvas.width; y = canvas.height;
    }} else {{
        x = 0; y = Math.random()*canvas.height;
    }}
    enemies.push({{
        x: x,
        y: y,
        size: type.size,
        color: type.color,
        speed: type.speed,
        hp: type.hp,
        damage: type.damage,
        xp: type.xp
    }});
}}

function fireProjectile() {{
    // Aim at the nearest enemy
    let target = null, minDist = Infinity;
    enemies.forEach(enemy => {{
        const dx = enemy.x - player.x;
        const dy = enemy.y - player.y;
        const dist = Math.sqrt(dx*dx+dy*dy);
        if (dist < minDist) {{
            minDist = dist;
            target = enemy;
        }}
    }});
    let angle = target ? Math.atan2(target.y - player.y, target.x - player.x) : 0;
    projectiles.push({{
        x: player.x,
        y: player.y,
        vx: Math.cos(angle)*8,
        vy: Math.sin(angle)*8,
        damage: 15,
        size: 5,
        active: true
    }});
}}

function togglePause() {{
    if (gameLoopId) {{
        pauseGame;

    }} else {{
        resumeGame;
    }}
}}



function resumeGame() {{
    // Hide overlays related to pause or level-up
    document.getElementById('level-up').style.display = 'none';
    document.getElementById('quick-hack').style.display = 'none';
    document.getElementById('mission-notification').style.display = 'none';
    
    // Reset last frame time to avoid a big delta on resume
    lastFrameTime = Date.now();
    
    // Restart game loop if it was paused
    if (!gameLoopId) {{
        gameLoop();
    }}
}}


function performQuickHack(option) {{
    console.log("Quick hack chosen: " + option);
    // For demo, simply resume game after quick hack
    document.getElementById('quick-hack').style.display = 'none';
    resumeGame();
}}

function applyUpgrade(option) {{
    // For demo, apply a simple upgrade effect
    if (option === 'damage') {{
        // Reset last attack time so next shot goes immediately
        player.lastAttackTime = 0;
    }} else if (option === 'cooldown') {{
        // In a full version, you could reduce firing cooldown multiplier
    }} else if (option === 'range') {{
        // In a full version, you could increase projectile speed or range
    }}
    player.level += 1;
    document.getElementById('level-up').style.display = 'none';
    resumeGame();
}}

function endGame(isVictory = false) {{
  cancelAnimationFrame(gameLoopId);
  gameLoop = null;
  const gameOverElement = document.getElementById('game-over');
  gameOverElement.style.display = 'block';
  
  // Get the h2 element
  const headingElement = gameOverElement.querySelector('h2');
  
  if (isVictory) {{
    
    headingElement.innerText = "Victory!";
    
    // Check if victory message already exists to avoid duplicates
    const victoryMsgExists = gameOverElement.querySelector('.victory-message');
    if (!victoryMsgExists) {{
      // Create a new paragraph element instead of using innerHTML +=
      const victoryMessage = document.createElement('p');
      victoryMessage.className = 'victory-message';
      victoryMessage.textContent = "You've reached maximum level and mastered Wakanda's defenses!";
      
      // Insert it after the heading
      headingElement.insertAdjacentElement('afterend', victoryMessage);
    }}
  }} else {{
    headingElement.innerText = "Game Over";
    
    // Remove victory message if it exists
    const victoryMsg = gameOverElement.querySelector('.victory-message');
    if (victoryMsg) {{
      victoryMsg.remove();
    }}
  }}
  
  document.getElementById('final-score').innerText = player.xp;
  const restartButton = gameOverElement.querySelector('button');
  restartButton.style.display = 'block';

  restartButton.onclick = function() {{
    document.getElementById('game-over').style.display = 'none';
    startGame();
  }};
  
}}


function restartGame() {{
    document.getElementById('game-over').style.display = 'none';
    startGame();
}}

function closeMission() {{
    document.getElementById('mission-notification').style.display = 'none';
    resumeGame();
}}



// Initialize game on page load
window.onload = initGame;
"""

# -------------------------
# HTML Template (embedded CSS & JS)
# -------------------------
HTML_TEMPLATE = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>{GAME_CONFIG["title"]}</title>
  <style>
    {EMBEDDED_CSS}
  </style>
</head>
<body>
  <div id="game-container">
    <canvas id="gameCanvas"></canvas>
    <div id="stats"></div>
    <!-- Start Screen -->
    <div id="start-game" style="display:none;">
      <h1>{GAME_CONFIG["title"]}</h1>
      <p>{GAME_CONFIG["description"]}</p>
      <div id="companion-select">
        <p>Select your AI Companion:</p>
        <label><input type="radio" name="companion" value="decoy" checked> Decoy Projection</label>
        <label><input type="radio" name="companion" value="repair"> Vibranium Repair Field</label>
        <label><input type="radio" name="companion" value="turret"> Automated Turret</label>
      </div>
      <button id="start-solo">Start Solo</button>
      <button id="start-multi">Start Multiplayer</button>
    </div>
    <!-- Multiplayer Role Selection -->
    <div id="multiplayer-select" style="display:none;">
      <p>Select your role:</p>
      <div class="role-option" data-role="warrior">Warrior</div>
      <div class="role-option" data-role="scientist">Scientist</div>
      <div class="role-option" data-role="hacker">Hacker</div>
    </div>
    <!-- Quick Hack Event -->
    <div id="quick-hack" style="display:none;">
      <p>Quick Hack! Choose an option:</p>
      <div class="hack-option" onclick="performQuickHack('drone')">Drone Overload</div>
      <div class="hack-option" onclick="performQuickHack('confuse')">Guard Confusion</div>
      <div class="hack-option" onclick="performQuickHack('blackout')">Surveillance Blackout</div>
    </div>
    <!-- Level Up Upgrade -->
    <div id="level-up" style="display:none;">
      <p>Level Up! Choose an upgrade:</p>
      <div class="upgrade-option" onclick="applyUpgrade('damage')">Increase Damage</div>
      <div class="upgrade-option" onclick="applyUpgrade('cooldown')">Reduce Cooldown</div>
      <div class="upgrade-option" onclick="applyUpgrade('range')">Increase Range</div>
      <p>You have reached Level <span id="new-level"></span></p>
      <button onclick="resumeGame()">Continue</button>
    </div>
    <!-- Mission Notification (Placeholder) -->
    <div id="mission-notification" style="display:none;">
      <p>Mission Event: <span id="mission-text"></span></p>
      <button onclick="closeMission()">Close Mission</button>
    </div>
    <!-- Game Over Screen -->
    <div id="game-over" style="display:none;">
      <h2>Game Over</h2>
      <p>Your final score: <span id="final-score"></span></p>
      <button onclick="restartGame()">Restart</button>
    </div>
    <!-- Loading Screen -->
    <div id="loading" style="display:none;">Loading...</div>
  </div>
  <script>
    {EMBEDDED_JS}
  </script>
</body>
</html>
"""

# -------------------------
# Flask Route
# -------------------------
@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

# -------------------------
# Run the Flask App
# -------------------------
if __name__ == "__main__":
    # Debug mode on for development; remove debug=True when deploying
    app.run(debug=True)


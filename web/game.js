const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');

const W = canvas.width;
const H = canvas.height;
const FLOOR_Y = 600;

const keys = new Set();
window.addEventListener('keydown', (e) => keys.add(e.code));
window.addEventListener('keyup', (e) => keys.delete(e.code));

class AssetBank {
  constructor() {
    this.images = new Map();
  }

  load(name, src) {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => {
        this.images.set(name, img);
        resolve(true);
      };
      img.onerror = () => resolve(false);
      img.src = src;
    });
  }

  get(name) {
    return this.images.get(name) ?? null;
  }
}

const assets = new AssetBank();

const game = {
  scene: 'menu',
  message: 'Presioná Enter para empezar',
  timerMs: 90_000,
  player: null,
  boss: null,
  furniture: [],
  petals: [],
  effects: [],
  bossThrows: 0,
  maxBossThrows: 10,
  roundsWon: 0,
  roundsLost: 0,
};

function makePlayer() {
  return {
    x: 280,
    y: FLOOR_Y,
    vy: 0,
    width: 150,
    height: 210,
    hp: 100,
    combo: 0,
    comboTimer: 0,
    state: 'idle',
    facing: 1,
    invuln: 0,
    attackCd: 0,
    hitFlash: 0,
    frameTime: 0,
    currentPose: 0,
  };
}

function makeBoss() {
  return {
    x: 980,
    y: 380,
    hp: 100,
    phase: 1,
    throwCd: 1200,
    drift: 0,
    hitFlash: 0,
  };
}

function resetRound() {
  game.scene = 'fight';
  game.message = '';
  game.timerMs = 90_000;
  game.player = makePlayer();
  game.boss = makeBoss();
  game.furniture = [];
  game.effects = [];
  game.bossThrows = 0;
  if (game.petals.length === 0) {
    for (let i = 0; i < 32; i += 1) {
      game.petals.push({
        x: Math.random() * W,
        y: Math.random() * H,
        vx: 0.25 + Math.random() * 0.6,
        vy: 0.15 + Math.random() * 0.45,
        size: 2 + Math.random() * 3,
      });
    }
  }
}

function aabb(a, b) {
  return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
}

function handleInput(dt) {
  const p = game.player;
  if (!p) return;

  p.attackCd = Math.max(0, p.attackCd - dt);
  p.invuln = Math.max(0, p.invuln - dt);
  p.hitFlash = Math.max(0, p.hitFlash - dt);
  p.comboTimer += dt;
  if (p.comboTimer > 1300) p.combo = 0;

  let dx = 0;
  if (keys.has('KeyA')) dx -= 5.1;
  if (keys.has('KeyD')) dx += 5.1;

  if (dx !== 0) {
    p.facing = dx > 0 ? 1 : -1;
    p.state = 'walk';
    p.x = Math.max(120, Math.min(620, p.x + dx));
  } else if (p.state === 'walk') {
    p.state = 'idle';
  }

  if (keys.has('KeyW') && p.y >= FLOOR_Y) {
    p.vy = -18;
    p.state = 'jump';
  }

  if (keys.has('KeyJ') && p.attackCd === 0) {
    p.attackCd = 280;
    p.state = 'slash';
    p.currentPose = 4;
    p.frameTime = 0;
    const sword = {
      x: p.x + (p.facing > 0 ? 40 : -120),
      y: p.y - 180,
      w: 120,
      h: 110,
    };
    const bossBody = { x: game.boss.x - 70, y: game.boss.y - 120, w: 140, h: 210 };
    if (aabb(sword, bossBody)) {
      game.boss.hp = Math.max(0, game.boss.hp - 8);
      game.boss.hitFlash = 140;
      p.combo += 1;
      p.comboTimer = 0;
      game.effects.push({ x: game.boss.x, y: game.boss.y - 70, ttl: 180 });
    }
  }

  if (keys.has('KeyK') && p.attackCd === 0) {
    p.attackCd = 560;
    p.state = 'heavy';
    p.currentPose = 5;
    p.frameTime = 0;
    const sword = {
      x: p.x + (p.facing > 0 ? 20 : -130),
      y: p.y - 210,
      w: 150,
      h: 160,
    };
    const bossBody = { x: game.boss.x - 70, y: game.boss.y - 120, w: 140, h: 210 };
    if (aabb(sword, bossBody)) {
      game.boss.hp = Math.max(0, game.boss.hp - 14);
      game.boss.hitFlash = 220;
      p.combo += 1;
      p.comboTimer = 0;
      game.effects.push({ x: game.boss.x + 25, y: game.boss.y - 120, ttl: 220 });
    }
  }
}

function updatePlayer(dt) {
  const p = game.player;
  p.vy += 0.88;
  p.y += p.vy;

  if (p.y >= FLOOR_Y) {
    p.y = FLOOR_Y;
    p.vy = 0;
    if (p.state === 'jump') p.state = 'idle';
  }

  p.frameTime += dt;
  if (p.frameTime > 180) {
    p.frameTime = 0;
    if (p.state === 'walk') p.currentPose = (p.currentPose + 1) % 2 === 0 ? 1 : 2;
    else if (p.state === 'jump') p.currentPose = 3;
    else if (p.state === 'idle') p.currentPose = 0;
  }
}

function spawnFurniture() {
  const p = game.player;
  const b = game.boss;
  const targetY = p.y - 120 + (Math.random() * 60 - 30);
  const vx = -5.6 - Math.random() * 3.4;
  const vy = (targetY - b.y) / 65;
  game.furniture.push({
    x: b.x - 30,
    y: b.y - 70,
    w: 72,
    h: 52,
    vx,
    vy,
    rot: 0,
    kind: Math.floor(Math.random() * 3),
  });
  game.bossThrows += 1;
}

function updateBoss(dt) {
  const p = game.player;
  const b = game.boss;

  b.hitFlash = Math.max(0, b.hitFlash - dt);
  b.throwCd -= dt;
  b.drift += dt * 0.0024;
  b.y = 365 + Math.sin(b.drift) * 28;

  if (b.hp < 56) b.phase = 2;
  if (b.hp < 26) b.phase = 3;

  if (b.throwCd <= 0) {
    spawnFurniture();
    const base = b.phase === 1 ? 1100 : b.phase === 2 ? 820 : 590;
    b.throwCd = base + Math.random() * 280;
  }

  for (const item of game.furniture) {
    item.x += item.vx;
    item.y += item.vy;
    item.rot += 0.07;

    const hb = { x: item.x - item.w / 2, y: item.y - item.h / 2, w: item.w, h: item.h };
    const playerHb = { x: p.x - 52, y: p.y - 188, w: 104, h: 188 };

    if (aabb(hb, playerHb) && p.invuln === 0) {
      p.hp = Math.max(0, p.hp - 10);
      p.invuln = 520;
      p.hitFlash = 240;
      p.combo = 0;
      game.effects.push({ x: p.x, y: p.y - 120, ttl: 240 });
      item.x = -200;
    }
  }
  game.furniture = game.furniture.filter((f) => f.x > -180 && f.y < H + 80);
}

function updatePetals() {
  for (const petal of game.petals) {
    petal.x += petal.vx;
    petal.y += petal.vy;
    if (petal.x > W + 10) petal.x = -10;
    if (petal.y > H + 10) petal.y = -10;
  }
}

function updateEffects(dt) {
  for (const fx of game.effects) fx.ttl -= dt;
  game.effects = game.effects.filter((fx) => fx.ttl > 0);
}

function update(dt) {
  if (game.scene === 'menu') {
    if (keys.has('Enter')) resetRound();
    return;
  }

  if (game.scene === 'result') {
    if (keys.has('Enter')) resetRound();
    return;
  }

  game.timerMs = Math.max(0, game.timerMs - dt);
  handleInput(dt);
  updatePlayer(dt);
  updateBoss(dt);
  updatePetals();
  updateEffects(dt);

  if (game.boss.hp <= 0) {
    game.roundsWon += 1;
    game.scene = 'result';
    game.message = '¡GANASTE! Kike venció a La Baronesa';
  } else if (game.player.hp <= 0 || game.timerMs <= 0) {
    game.roundsLost += 1;
    game.scene = 'result';
    game.message = 'DERROTA: La Baronesa dominó el dojo';
  }
}

function drawHud() {
  const p = game.player;
  const b = game.boss;

  ctx.fillStyle = '#00000088';
  ctx.fillRect(18, 14, W - 36, 102);

  ctx.font = 'bold 38px "Press Start 2P", monospace';
  ctx.fillStyle = '#f8f5d8';
  ctx.fillText('P1: KIKE (UA NINJA)', 28, 48);
  ctx.fillText('BOSS: LA BARONESA', 690, 48);

  ctx.fillStyle = '#1f2940';
  ctx.fillRect(28, 60, 500, 28);
  ctx.fillRect(752, 60, 500, 28);

  ctx.fillStyle = '#f6b329';
  ctx.fillRect(32, 64, 492 * (p.hp / 100), 20);

  ctx.fillStyle = '#eb594f';
  const bw = 492 * (b.hp / 100);
  ctx.fillRect(756 + (492 - bw), 64, bw, 20);

  ctx.fillStyle = '#69d5ff';
  ctx.fillRect(32, 96, 220 * Math.min(1, p.combo / 8), 12);
  ctx.fillStyle = '#f8f5d8';
  ctx.fillText(`COMBOS: ${p.combo}`, 28, 138);

  ctx.textAlign = 'right';
  ctx.fillText(`MUEBLES LANZADOS: ${game.bossThrows}/${game.maxBossThrows}`, W - 22, 138);
  ctx.textAlign = 'left';

  const timer = Math.ceil(game.timerMs / 1000);
  ctx.fillText(`TIEMPO: ${String(timer).padStart(2, '0')}`, W / 2 - 120, 94);
}

function drawFallbackBackground() {
  const grad = ctx.createLinearGradient(0, 0, 0, H);
  grad.addColorStop(0, '#4d1f2d');
  grad.addColorStop(1, '#1f0a11');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, W, H);

  ctx.fillStyle = '#7a4c2f';
  ctx.fillRect(0, 420, W, 300);

  ctx.fillStyle = '#ae6a4a';
  for (let i = 0; i < 26; i += 1) {
    ctx.fillRect(i * 58, 430 + (i % 2) * 10, 54, 260);
  }

  ctx.fillStyle = '#f49dc9';
  for (const petal of game.petals) {
    ctx.fillRect(petal.x, petal.y, petal.size, petal.size);
  }
}

function drawKike() {
  const p = game.player;
  const poses = assets.get('kikePoses');

  if (poses) {
    const frameW = poses.width / 4;
    const frameH = poses.height / 3;
    const idx = p.currentPose;
    const col = idx % 4;
    const row = Math.floor(idx / 4);
    const drawW = 210;
    const drawH = 250;

    ctx.save();
    ctx.translate(p.x, p.y - drawH + 12);
    if (p.facing < 0) {
      ctx.translate(drawW, 0);
      ctx.scale(-1, 1);
    }
    ctx.drawImage(poses, col * frameW, row * frameH, frameW, frameH, 0, 0, drawW, drawH);
    ctx.restore();
  } else {
    ctx.fillStyle = p.hitFlash > 0 ? '#b7ffb7' : '#34b258';
    ctx.fillRect(p.x - 44, p.y - 140, 88, 140);
    ctx.fillStyle = '#1c2f2e';
    ctx.fillRect(p.x - 18, p.y - 173, 36, 36);
    ctx.strokeStyle = '#dfe8ef';
    ctx.lineWidth = 4;
    const bladeOffset = p.facing > 0 ? 56 : -56;
    ctx.beginPath();
    ctx.moveTo(p.x, p.y - 124);
    ctx.lineTo(p.x + bladeOffset, p.y - 150);
    ctx.stroke();
  }
}

function drawBoss() {
  const b = game.boss;
  const bossImg = assets.get('baronesa');

  if (bossImg) {
    const glow = 20 + Math.sin(performance.now() * 0.008) * 8;
    ctx.save();
    ctx.shadowColor = '#fff7ff';
    ctx.shadowBlur = glow;
    ctx.globalAlpha = b.hitFlash > 0 ? 0.7 : 1;
    ctx.drawImage(bossImg, b.x - 95, b.y - 190, 190, 290);
    ctx.restore();
  } else {
    ctx.save();
    ctx.globalAlpha = b.hitFlash > 0 ? 0.55 : 1;
    ctx.fillStyle = '#8f3a53';
    ctx.fillRect(b.x - 62, b.y - 140, 124, 190);
    ctx.fillStyle = '#ffe9de';
    ctx.fillRect(b.x - 22, b.y - 170, 44, 44);
    ctx.restore();
  }
}

function drawFurniture() {
  for (const item of game.furniture) {
    ctx.save();
    ctx.translate(item.x, item.y);
    ctx.rotate(item.rot);

    if (item.kind === 0) {
      ctx.fillStyle = '#7e4f30';
      ctx.fillRect(-36, -22, 72, 44);
      ctx.fillStyle = '#593821';
      ctx.fillRect(-31, -17, 15, 15);
      ctx.fillRect(16, -17, 15, 15);
    } else if (item.kind === 1) {
      ctx.fillStyle = '#9e6039';
      ctx.fillRect(-35, -10, 70, 20);
      ctx.fillRect(-28, -24, 8, 14);
      ctx.fillRect(20, -24, 8, 14);
    } else {
      ctx.fillStyle = '#6d4027';
      ctx.fillRect(-20, -30, 40, 48);
      ctx.fillRect(-12, 18, 8, 18);
      ctx.fillRect(4, 18, 8, 18);
    }

    ctx.restore();
  }
}

function drawEffects() {
  for (const fx of game.effects) {
    ctx.save();
    ctx.globalAlpha = Math.min(1, fx.ttl / 220);
    ctx.strokeStyle = '#ffffff';
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.arc(fx.x, fx.y, 24, 0, Math.PI * 2);
    ctx.stroke();
    ctx.restore();
  }
}

function draw() {
  const bg = assets.get('scene');
  if (bg) ctx.drawImage(bg, 0, 0, W, H);
  else drawFallbackBackground();

  drawFurniture();
  drawBoss();
  drawKike();
  drawEffects();

  if (game.scene !== 'menu') drawHud();

  if (game.scene === 'menu') {
    ctx.fillStyle = '#00000099';
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = '#fff6ce';
    ctx.font = 'bold 56px "Press Start 2P", monospace';
    ctx.fillText('KIKEFIGHT: BARONESA DEL MUEBLE', 120, 260);
    ctx.font = 'bold 26px "Press Start 2P", monospace';
    ctx.fillText('A/D mover · W saltar · J ataque · K ataque pesado', 180, 330);
    ctx.fillText('ENTER para iniciar', 450, 390);
    if (!assets.get('scene') || !assets.get('kikePoses') || !assets.get('baronesa')) {
      ctx.fillStyle = '#ffdf8f';
      ctx.fillText('Tip: coloca tus imágenes en web/assets para ver la estética exacta.', 120, 450);
    }
  }

  if (game.scene === 'result') {
    ctx.fillStyle = '#000000bb';
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 44px "Press Start 2P", monospace';
    ctx.fillText(game.message, 170, 320);
    ctx.font = 'bold 24px "Press Start 2P", monospace';
    ctx.fillText(`Victorias: ${game.roundsWon} | Derrotas: ${game.roundsLost}`, 360, 370);
    ctx.fillText('ENTER para reintentar', 450, 420);
  }
}

let last = performance.now();
function loop(now) {
  const dt = Math.min(34, now - last);
  last = now;
  update(dt);
  draw();
  requestAnimationFrame(loop);
}

async function boot() {
  await Promise.all([
    assets.load('scene', 'assets/scene_ref.png'),
    assets.load('kikePoses', 'assets/kike_poses.png'),
    assets.load('baronesa', 'assets/baronesa.png'),
  ]);
  requestAnimationFrame(loop);
}

boot();

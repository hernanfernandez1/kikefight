const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');

const CFG = {
  w: 1280,
  h: 720,
  floorY: 530,
  gravity: 0.9,
  speed: 6,
  jump: -22,
  maxHp: 100,
  roundTimeMs: 99_000,
  comboWindow: 1800,
};

const CHAR = {
  HERO: { name: 'Kike', canFly: false, furnitureEnemy: false },
  ENEMY: { name: 'Enemiga Mueble', canFly: true, furnitureEnemy: true },
};

const ST = {
  IDLE: 'idle', WALK: 'walk', JUMP: 'jump',
  LIGHT: 'light', HEAVY: 'heavy', SPECIAL: 'special',
  BLOCK: 'block', HIT: 'hit', DEAD: 'dead',
};

const ATTACK = {
  [ST.LIGHT]: { dmg: 7, duration: 220, box: { w: 110, h: 80 }, activeFrom: 60, activeTo: 150 },
  [ST.HEAVY]: { dmg: 14, duration: 320, box: { w: 150, h: 110 }, activeFrom: 90, activeTo: 240 },
  [ST.SPECIAL]: { dmg: 20, duration: 380, box: { w: 170, h: 120 }, activeFrom: 130, activeTo: 260 },
};

const keys = new Set();
window.addEventListener('keydown', (e) => keys.add(e.code));
window.addEventListener('keyup', (e) => keys.delete(e.code));

class Fighter {
  constructor(id, x, flip, color, profile) {
    this.id = id;
    this.x = x;
    this.y = CFG.floorY;
    this.vy = 0;
    this.flip = flip;
    this.color = color;
    this.profile = profile;
    this.hp = CFG.maxHp;
    this.state = ST.IDLE;
    this.stateTime = 0;
    this.onGround = true;
    this.didHit = false;
    this.spawnProjectile = false;
    this.combo = 0;
    this.comboTimer = 0;
    this.stun = 0;
  }

  get rect() {
    return { x: this.x - 40, y: this.y - 180, w: 80, h: 180 };
  }

  get attackRect() {
    const a = ATTACK[this.state];
    if (!a) return null;
    if (this.stateTime < a.activeFrom || this.stateTime > a.activeTo) return null;
    const dir = this.flip ? -1 : 1;
    const baseX = this.x + dir * 20;
    return dir === 1
      ? { x: baseX, y: this.y - 140, w: a.box.w, h: a.box.h }
      : { x: baseX - a.box.w, y: this.y - 140, w: a.box.w, h: a.box.h };
  }

  setState(s) {
    if (this.state === ST.DEAD) return;
    this.state = s;
    this.stateTime = 0;
    this.didHit = false;
  }

  update(dt, input) {
    if (this.state === ST.DEAD) return;
    this.comboTimer += dt;
    if (this.comboTimer > CFG.comboWindow) this.combo = 0;

    if (this.stun > 0) {
      this.stun -= dt;
      this.state = ST.HIT;
    } else if (this.state === ST.HIT) {
      this.setState(ST.IDLE);
    }

    this.stateTime += dt;

    const fighterGravity = this.profile.canFly ? CFG.gravity * 0.65 : CFG.gravity;
    if (!this.onGround) this.vy += fighterGravity;
    this.y += this.vy;
    if (this.y >= CFG.floorY) {
      this.y = CFG.floorY;
      this.vy = 0;
      this.onGround = true;
    }

    const inAttack = [ST.LIGHT, ST.HEAVY, ST.SPECIAL].includes(this.state);
    if (inAttack) {
      const done = this.stateTime >= ATTACK[this.state].duration;
      if (this.state === ST.SPECIAL && this.profile.canFly && this.stateTime < 220) {
        this.vy = Math.min(this.vy, -1.6);
      }
      if (this.state === ST.SPECIAL && this.profile.furnitureEnemy && !this.spawnProjectile && this.stateTime > 140) {
        this.spawnProjectile = true;
      }
      if (done) this.setState(ST.IDLE);
    } else if (this.stun <= 0) {
      if (input.block) this.setState(ST.BLOCK);
      else if (input.special && this.onGround) this.setState(ST.SPECIAL);
      else if (input.heavy && this.onGround) this.setState(ST.HEAVY);
      else if (input.light) this.setState(ST.LIGHT);
      else if (input.up && this.onGround) {
        this.vy = CFG.jump;
        this.onGround = false;
        this.setState(ST.JUMP);
      } else {
        let dx = 0;
        if (input.left) dx -= CFG.speed;
        if (input.right) dx += CFG.speed;
        this.x = Math.max(80, Math.min(CFG.w - 80, this.x + dx));
        this.setState(!this.onGround ? ST.JUMP : dx ? ST.WALK : ST.IDLE);
      }
    }
  }

  takeHit(dmg) {
    const final = this.state === ST.BLOCK ? 2 : dmg;
    this.hp -= final;
    if (this.hp <= 0) {
      this.hp = 0;
      this.state = ST.DEAD;
      return;
    }
    this.stun = 200;
    this.setState(ST.HIT);
  }

  draw() {
    const r = this.rect;
    ctx.fillStyle = this.color.body;
    ctx.fillRect(r.x, r.y + 40, r.w, 140);
    ctx.fillStyle = this.color.head;
    ctx.fillRect(r.x + 18, r.y + 8, 44, 44);

    if (this.state === ST.BLOCK) {
      ctx.strokeStyle = '#ffd34a';
      ctx.lineWidth = 5;
      ctx.strokeRect(r.x - 4, r.y - 4, r.w + 8, r.h + 8);
    }

    const atk = this.attackRect;
    if (atk) {
      ctx.globalAlpha = 0.25;
      ctx.fillStyle = '#fff5aa';
      ctx.fillRect(atk.x, atk.y, atk.w, atk.h);
      ctx.globalAlpha = 1;
    }
  }
}

class Projectile {
  constructor(x, y, dir) {
    this.x = x;
    this.y = y;
    this.vx = dir * 9;
    this.vy = -10;
    this.active = true;
    this.hit = false;
  }
  get rect() { return { x: this.x - 18, y: this.y - 14, w: 36, h: 28 }; }
  update() {
    this.x += this.vx;
    this.y += this.vy;
    this.vy += 0.45;
    if (this.y >= CFG.floorY - 8 || this.x < -40 || this.x > CFG.w + 40) this.active = false;
  }
  draw() {
    const r = this.rect;
    ctx.fillStyle = '#a77a4f';
    ctx.fillRect(r.x, r.y, r.w, r.h);
    ctx.fillStyle = '#6b4f36';
    ctx.fillRect(r.x + 4, r.y + 4, 8, 20);
    ctx.fillRect(r.x + r.w - 12, r.y + 4, 8, 20);
  }
}

const game = {
  state: 'menu',
  p1: null,
  p2: null,
  projectiles: [],
  timer: CFG.roundTimeMs,
  wins1: 0,
  wins2: 0,
  message: '',
  endAt: 0,
};

function hit(a, b) {
  return a && b && a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
}

function startRound() {
  game.p1 = new Fighter(1, 300, false, { body: '#36ab53', head: '#dfb17f' }, CHAR.HERO);
  game.p2 = new Fighter(2, 980, true, { body: '#7f46c9', head: '#d8a280' }, CHAR.ENEMY);
  game.projectiles = [];
  game.timer = CFG.roundTimeMs;
  game.state = 'fight';
}

function readInput() {
  return {
    p1: {
      left: keys.has('KeyA'), right: keys.has('KeyD'), up: keys.has('KeyW'),
      light: keys.has('KeyU'), heavy: keys.has('KeyI'), special: keys.has('KeyO'), block: keys.has('KeyP'),
    },
    p2: null,
  };
}

function enemyAi(enemy, hero, now) {
  const distance = hero.x - enemy.x;
  const absDistance = Math.abs(distance);
  const moveToward = absDistance > 170;
  const moveAway = absDistance < 90;
  const shouldSpecial = absDistance > 170 && absDistance < 430 && now % 1600 < 34;
  const shouldHeavy = absDistance <= 170 && now % 900 < 34;
  const shouldLight = absDistance <= 120 && now % 500 < 34;
  const shouldJump = enemy.onGround && hero.y < enemy.y - 30 && now % 1400 < 34;

  return {
    left: moveToward ? distance < 0 : moveAway ? distance > 0 : false,
    right: moveToward ? distance > 0 : moveAway ? distance < 0 : false,
    up: shouldJump,
    light: shouldLight,
    heavy: shouldHeavy,
    special: shouldSpecial,
    block: absDistance < 130 && now % 700 < 200,
  };
}

function update(dt, now) {
  if (game.state === 'menu') {
    if (keys.has('Enter')) startRound();
    return;
  }

  if (game.state === 'round_end' || game.state === 'game_over') {
    if (now > game.endAt && keys.has('Enter')) {
      if (game.state === 'game_over') {
        game.wins1 = 0; game.wins2 = 0; game.state = 'menu';
      } else startRound();
    }
    return;
  }

  const { p1, p2 } = game;
  const input = readInput();
  p1.flip = p1.x > p2.x;
  p2.flip = p2.x < p1.x;

  p1.update(dt, input.p1);
  p2.update(dt, enemyAi(p2, p1, now));

  const p1Atk = p1.attackRect;
  if (p1Atk && !p1.didHit && hit(p1Atk, p2.rect)) {
    p2.takeHit(ATTACK[p1.state]?.dmg ?? 7);
    p1.didHit = true;
    p1.combo += 1; p1.comboTimer = 0;
  }

  const p2Atk = p2.attackRect;
  if (p2Atk && !p2.didHit && hit(p2Atk, p1.rect)) {
    p1.takeHit(ATTACK[p2.state]?.dmg ?? 7);
    p2.didHit = true;
    p2.combo += 1; p2.comboTimer = 0;
  }

  for (const f of [p1, p2]) {
    if (f.spawnProjectile) {
      f.spawnProjectile = false;
      game.projectiles.push(new Projectile(f.x + (f.flip ? -60 : 60), f.y - 110, f.flip ? -1 : 1));
    }
  }

  for (const proj of game.projectiles) {
    proj.update();
    if (!proj.hit && hit(proj.rect, p1.rect)) { p1.takeHit(20); proj.hit = true; proj.active = false; }
    if (!proj.hit && hit(proj.rect, p2.rect)) { p2.takeHit(20); proj.hit = true; proj.active = false; }
  }
  game.projectiles = game.projectiles.filter((p) => p.active);

  game.timer -= dt;
  const timeout = game.timer <= 0;
  const ko = p1.state === ST.DEAD || p2.state === ST.DEAD;

  if (timeout || ko) {
    if (p1.hp === p2.hp) game.message = '¡Empate!';
    else if (p1.hp > p2.hp) { game.message = '¡Kike gana!'; game.wins1 += 1; }
    else { game.message = '¡La enemiga gana!'; game.wins2 += 1; }

    game.state = game.wins1 >= 2 || game.wins2 >= 2 ? 'game_over' : 'round_end';
    game.endAt = now + 1200;
  }
}

function drawHud() {
  const hpW = 420;
  ctx.fillStyle = '#1f0d0d'; ctx.fillRect(30, 16, hpW, 24);
  ctx.fillStyle = '#43d14f'; ctx.fillRect(30, 16, hpW * (game.p1.hp / CFG.maxHp), 24);

  ctx.fillStyle = '#1f0d0d'; ctx.fillRect(CFG.w - 30 - hpW, 16, hpW, 24);
  const p2W = hpW * (game.p2.hp / CFG.maxHp);
  ctx.fillStyle = '#d84343'; ctx.fillRect(CFG.w - 30 - p2W, 16, p2W, 24);

  ctx.fillStyle = '#f6e7ca';
  ctx.font = 'bold 44px system-ui';
  ctx.textAlign = 'center';
  ctx.fillText(String(Math.max(0, Math.ceil(game.timer / 1000))).padStart(2, '0'), CFG.w / 2, 54);

  ctx.font = '20px system-ui';
  ctx.textAlign = 'left';
  ctx.fillText(`${game.p1.profile.name} · Rondas: ${game.wins1}`, 30, 78);
  ctx.textAlign = 'right';
  ctx.fillText(`${game.p2.profile.name} · Rondas: ${game.wins2}`, CFG.w - 30, 78);
}

function drawBackground() {
  const g = ctx.createLinearGradient(0, 0, 0, CFG.h);
  g.addColorStop(0, '#d5b993'); g.addColorStop(1, '#8b5a35');
  ctx.fillStyle = g; ctx.fillRect(0, 0, CFG.w, CFG.h);
  ctx.fillStyle = '#c0905f'; ctx.fillRect(0, CFG.floorY, CFG.w, CFG.h - CFG.floorY);
}

function drawOverlay(text, sub = 'Pulsa Enter para continuar') {
  ctx.fillStyle = 'rgba(0,0,0,0.55)';
  ctx.fillRect(0, 0, CFG.w, CFG.h);
  ctx.fillStyle = '#ffe9bc';
  ctx.font = 'bold 66px system-ui';
  ctx.textAlign = 'center';
  ctx.fillText(text, CFG.w / 2, CFG.h / 2 - 20);
  ctx.font = '28px system-ui';
  ctx.fillText(sub, CFG.w / 2, CFG.h / 2 + 34);
}

function render() {
  drawBackground();
  if (game.state === 'menu') {
    drawOverlay('KIKEFIGHT WEB', 'Pulsa Enter para empezar (la enemiga vuela y lanza muebles)');
    return;
  }

  for (const p of game.projectiles) p.draw();
  game.p1.draw();
  game.p2.draw();
  drawHud();

  if (game.state === 'round_end') drawOverlay(game.message);
  if (game.state === 'game_over') drawOverlay(game.wins1 > game.wins2 ? '¡Kike campeón!' : '¡La enemiga campeona!');
}

let last = performance.now();
function loop(now) {
  const dt = Math.min(34, now - last);
  last = now;
  update(dt, now);
  render();
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);

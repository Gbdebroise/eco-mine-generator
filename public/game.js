// =============================================================
//  Eco-Mine Runner — game.js  v3  (MOTEUR FIXE + décor piloté par l'agent)
//
//  L'agent choisit un "biome" dans level_config.json. Le moteur
//  charge le décor correspondant. Le biome change aussi la palette
//  des placeholders -> décor différent par site, même sans image.
//
//  Décor réel (optionnel) par biome, dans assets/ :
//    <biome>_far.png   <biome>_near.png
//  Objets (optionnels) : truck.png ore.png bird.png blast.png grove.png spark.png
//  Écran-titre / audio (optionnels) : start_screen.png sfx_collect.mp3 sfx_crash.mp3
//
//  Sans ces fichiers : tout est dessiné par code. 404 console = normal.
// =============================================================

const W = 480;
const H = 640;

const DEFAULT_CONFIG = {
  site_name: "Clerac",
  mineral_name: "Chamotte Clay",
  eco_target: "Migratory Birds (MNHN)",
  danger_obstacle: "Blasting Zone",
  biome: "clay_quarry",
  scrolling_speed: 300,
  spawn_rates: { mineral: 0.6, eco_bonus: 0.4, obstacle: 0.5 },
  ui_strings: {
    title: "MISSION CLERAC",
    instructions: "Collect Chamotte & Band Birds! Avoid Blasting Zones!"
  }
};

const BIOMES = {
  clay_quarry:         { far: 0xb6a484, rock: 0xa3906f, near: 0x6e5a3c, accent: 0xd4a017 },
  granite_underground: { far: 0x3a3d42, rock: 0x2b2e33, near: 0x565d66, accent: 0x7f8c8d },
  wetland:             { far: 0x6b8e4e, rock: 0x557a3a, near: 0x3e5c2a, accent: 0x2e86c1 },
  diatomite:           { far: 0xd8d8d2, rock: 0xc2c2ba, near: 0xb0b0a8, accent: 0x95a5a6 }
};

const OBJECT_ASSETS = {
  truck:   'assets/truck.png',
  mineral: 'assets/ore.png',
  bird:    'assets/bird.png',
  blast:   'assets/blast.png',
  grove:   'assets/grove.png',
  spark:   'assets/spark.png'
};

function drawBgPlaceholder(scene, layer, pal) {
  const g = scene.add.graphics();
  if (layer === 'far') {
    g.fillStyle(pal.far, 1); g.fillRect(0, 0, W, 256);
    g.fillStyle(pal.rock, 1);
    g.fillRect(40, 30, 40, 26); g.fillRect(300, 90, 50, 30);
    g.fillRect(150, 180, 44, 28); g.fillRect(380, 200, 36, 22);
    g.generateTexture('bg_far', W, 256);
  } else {
    g.fillStyle(pal.near, 1);
    g.fillRect(30, 40, 22, 14); g.fillRect(420, 120, 26, 16);
    g.fillRect(120, 250, 20, 12); g.fillRect(330, 300, 24, 14);
    g.fillStyle(pal.accent, 1);
    g.fillCircle(70, 200, 9); g.fillCircle(400, 60, 11);
    g.generateTexture('bg_near', W, 384);
  }
  g.destroy();
}

function drawObjectPlaceholder(scene, key) {
  const g = scene.add.graphics();
  switch (key) {
    case 'truck':
      g.fillStyle(0x2b2b2b, 1);
      g.fillRoundedRect(2, 12, 8, 18, 3); g.fillRoundedRect(2, 40, 8, 18, 3);
      g.fillRoundedRect(34, 12, 8, 18, 3); g.fillRoundedRect(34, 40, 8, 18, 3);
      g.fillStyle(0xf1c40f, 1); g.fillRoundedRect(8, 4, 28, 60, 6);
      g.fillStyle(0xd4a017, 1); g.fillRect(11, 30, 22, 30);
      g.fillStyle(0x34495e, 1); g.fillRoundedRect(12, 8, 20, 15, 3);
      g.generateTexture(key, 44, 68); break;
    case 'mineral':
      g.fillStyle(0xdfe2e6, 1); g.fillRoundedRect(2, 2, 30, 30, 4);
      g.fillStyle(0xb8bdc4, 1); g.fillTriangle(2, 32, 16, 12, 32, 32);
      g.fillStyle(0xf2f4f7, 1); g.fillRect(8, 7, 8, 8);
      g.generateTexture(key, 34, 34); break;
    case 'bird':
      g.fillStyle(0x5da9e9, 1); g.fillEllipse(17, 14, 22, 16);
      g.fillStyle(0x4a90d9, 1); g.fillTriangle(6, 6, 17, 14, 6, 18);
      g.fillStyle(0xf39c12, 1); g.fillTriangle(28, 12, 34, 14, 28, 16);
      g.lineStyle(2, 0xe67e22, 1); g.strokeCircle(17, 22, 4);
      g.generateTexture(key, 34, 28); break;
    case 'blast':
      g.fillStyle(0xe24b4a, 1); g.fillCircle(23, 23, 21);
      g.fillStyle(0xef8b2c, 1); g.fillCircle(23, 23, 13);
      g.fillStyle(0xf9d423, 1); g.fillCircle(23, 23, 6);
      g.fillStyle(0xe24b4a, 1);
      for (let i = 0; i < 8; i++) {
        const a = (i / 8) * Math.PI * 2;
        g.fillTriangle(23 + Math.cos(a) * 21, 23 + Math.sin(a) * 21,
          23 + Math.cos(a + 0.25) * 14, 23 + Math.sin(a + 0.25) * 14,
          23 + Math.cos(a - 0.25) * 14, 23 + Math.sin(a - 0.25) * 14);
      }
      g.generateTexture(key, 46, 46); break;
    case 'grove':
      g.fillStyle(0x7a5230, 1); g.fillRect(20, 30, 6, 14);
      g.fillStyle(0x639922, 1); g.fillCircle(23, 20, 16);
      g.fillStyle(0x4f7d18, 1); g.fillCircle(14, 24, 9); g.fillCircle(32, 24, 9);
      g.fillStyle(0x9ac44d, 1); g.fillCircle(20, 15, 5);
      g.generateTexture(key, 46, 46); break;
    case 'spark':
      g.fillStyle(0xffffff, 1); g.fillCircle(6, 6, 6);
      g.generateTexture(key, 12, 12); break;
  }
  g.destroy();
}

class BootScene extends Phaser.Scene {
  constructor() { super('Boot'); }
  preload() {
    this.load.on('loaderror', () => {});
    this.load.json('levelConfig', 'level_config.json');
  }
  create() {
    const loaded = this.cache.json.get('levelConfig');
    const cfg = Object.assign({}, DEFAULT_CONFIG, loaded || {});
    cfg.spawn_rates = Object.assign({}, DEFAULT_CONFIG.spawn_rates, (loaded && loaded.spawn_rates) || {});
    cfg.ui_strings = Object.assign({}, DEFAULT_CONFIG.ui_strings, (loaded && loaded.ui_strings) || {});
    if (!BIOMES[cfg.biome]) cfg.biome = 'clay_quarry';
    this.registry.set('cfg', cfg);
    this.scene.start('Preload');
  }
}

class PreloadScene extends Phaser.Scene {
  constructor() { super('Preload'); }
  preload() {
    this.load.on('loaderror', () => {});
    const biome = this.registry.get('cfg').biome;
    this.load.image('bg_far', `assets/${biome}_far.png`);
    this.load.image('bg_near', `assets/${biome}_near.png`);
    for (const [key, path] of Object.entries(OBJECT_ASSETS)) this.load.image(key, path);
    this.load.image('startScreen', 'assets/start_screen.png');
    this.load.audio('sfx_collect', 'assets/sfx_collect.mp3');
    this.load.audio('sfx_crash', 'assets/sfx_crash.mp3');
  }
  create() {
    const pal = BIOMES[this.registry.get('cfg').biome];
    if (!this.textures.exists('bg_far')) drawBgPlaceholder(this, 'far', pal);
    if (!this.textures.exists('bg_near')) drawBgPlaceholder(this, 'near', pal);
    for (const key of Object.keys(OBJECT_ASSETS)) {
      if (!this.textures.exists(key)) drawObjectPlaceholder(this, key);
    }
    this.scene.start('Menu');
  }
}

class MenuScene extends Phaser.Scene {
  constructor() { super('Menu'); }
  create() {
    const cfg = this.registry.get('cfg');
    if (this.textures.exists('startScreen')) {
      this.add.image(W / 2, H / 2, 'startScreen').setDisplaySize(W, H);
      this.add.rectangle(W / 2, H / 2, W, H, 0x000000, 0.25);
    } else {
      this.far = this.add.tileSprite(W / 2, H / 2, W, H, 'bg_far');
      this.add.rectangle(W / 2, H / 2, W, H, 0x000000, 0.4);
    }
    this.add.text(W / 2, 110, cfg.ui_strings.title,
      { fontFamily: 'Arial Black, sans-serif', fontSize: '34px', color: '#f1c40f' }).setOrigin(0.5);
    this.add.text(W / 2, 152, 'ECO-MINE RUNNER',
      { fontFamily: 'Arial', fontSize: '16px', color: '#ffffff' }).setOrigin(0.5);
    this.add.text(W / 2, 240, cfg.ui_strings.instructions,
      { fontFamily: 'Arial', fontSize: '15px', color: '#ecf0f1', align: 'center', wordWrap: { width: 380 } }).setOrigin(0.5);
    this.add.image(150, 350, 'mineral'); this.add.text(178, 342, '+10 production', { fontSize: '13px', color: '#ecf0f1' });
    this.add.image(150, 392, 'bird');    this.add.text(178, 384, '+15 eco', { fontSize: '13px', color: '#ecf0f1' });
    this.add.image(150, 434, 'blast');   this.add.text(178, 426, 'crash — avoid!', { fontSize: '13px', color: '#e74c3c' });
    this.add.image(150, 476, 'grove');   this.add.text(178, 468, 'protected — eco penalty', { fontSize: '13px', color: '#2ecc71' });
    const play = this.add.text(W / 2, 560, '▶  CLICK or SPACE to play',
      { fontFamily: 'Arial', fontSize: '20px', color: '#ffffff', backgroundColor: '#27ae60', padding: { x: 18, y: 10 } })
      .setOrigin(0.5).setInteractive({ useHandCursor: true });
    this.tweens.add({ targets: play, alpha: 0.6, duration: 700, yoyo: true, repeat: -1 });
    const start = () => this.scene.start('Game');
    play.on('pointerdown', start);
    this.input.keyboard.once('keydown-SPACE', start);
  }
  update() { if (this.far) this.far.tilePositionY -= 0.4; }
}

class GameScene extends Phaser.Scene {
  constructor() { super('Game'); }

  create() {
    this.cfg = this.registry.get('cfg');
    this.speed = this.cfg.scrolling_speed;
    this.prodScore = 0; this.ecoScore = 0; this.over = false;
    this.bgFar = this.add.tileSprite(W / 2, H / 2, W, H, 'bg_far');
    this.bgNear = this.add.tileSprite(W / 2, H / 2, W, H, 'bg_near');
    this.player = this.physics.add.sprite(W / 2, H - 70, 'truck').setCollideWorldBounds(true);
    this.player.body.setSize(28, 52).setOffset(8, 10);
    this.minerals = this.physics.add.group();
    this.birds = this.physics.add.group();
    this.blasts = this.physics.add.group();
    this.groves = this.physics.add.group();
    this.physics.add.overlap(this.player, this.minerals, (p, o) => this.collect(o, 'prod', 10), null, this);
    this.physics.add.overlap(this.player, this.birds, (p, o) => this.collect(o, 'eco', 15), null, this);
    this.physics.add.overlap(this.player, this.groves, (p, o) => this.collect(o, 'eco', -20, true), null, this);
    this.physics.add.overlap(this.player, this.blasts, () => this.gameOver(), null, this);
    this.prodText = this.add.text(12, 12, '', { fontFamily: 'Arial', fontSize: '18px', color: '#f1c40f' }).setDepth(5);
    this.ecoText = this.add.text(W - 12, 12, '', { fontFamily: 'Arial', fontSize: '18px', color: '#2ecc71' }).setOrigin(1, 0).setDepth(5);
    this.refreshHUD();
    this.cursors = this.input.keyboard.createCursorKeys();
    this.keys = this.input.keyboard.addKeys('A,D');
    this.spawnTimer = this.time.addEvent({ delay: 750, loop: true, callback: () => this.spawnWave() });
    this.time.addEvent({ delay: 10000, loop: true, callback: () => { this.speed = Math.min(this.speed + 25, 620); } });
  }

  spawnWave() {
    if (this.over) return;
    const r = this.cfg.spawn_rates;
    const roll = (rate, group, key, spin = false, flap = false) => {
      if (Math.random() < rate) {
        const x = Phaser.Math.Between(30, W - 30);
        const item = group.create(x, -30, key);
        item.setVelocityY(this.speed);
        if (spin) this.tweens.add({ targets: item, angle: 360, duration: 2200, repeat: -1 });
        if (flap) this.tweens.add({ targets: item, scaleY: 0.6, duration: 200, yoyo: true, repeat: -1 });
      }
    };
    roll(r.mineral, this.minerals, 'mineral', true);
    roll(r.eco_bonus, this.birds, 'bird', false, true);
    roll(r.obstacle, this.blasts, 'blast');
    roll(r.obstacle * 0.6, this.groves, 'grove');
  }

  collect(obj, kind, points, penalty = false) {
    if (!obj.active) return;
    obj.body.enable = false;
    const color = penalty ? 0xe24b4a : (kind === 'eco' ? 0x2ecc71 : 0xf1c40f);
    const hex = penalty ? '#e74c3c' : (kind === 'eco' ? '#2ecc71' : '#f1c40f');
    this.burst(obj.x, obj.y, color);
    this.popup(obj.x, obj.y, (points >= 0 ? '+' : '') + points, hex);
    if (kind === 'prod') this.prodScore += points; else this.ecoScore += points;
    if (penalty) this.cameras.main.flash(120, 200, 60, 60);
    if (!penalty && this.cache.audio.exists('sfx_collect')) this.sound.play('sfx_collect', { volume: 0.5 });
    this.tweens.add({ targets: obj, scale: 1.6, alpha: 0, duration: 160, onComplete: () => obj.destroy() });
    this.refreshHUD();
  }

  burst(x, y, tint) {
    const e = this.add.particles(x, y, 'spark', {
      speed: { min: 60, max: 170 }, lifespan: 420, scale: { start: 0.9, end: 0 },
      tint, quantity: 10, emitting: false
    }).setDepth(6);
    e.explode(10, x, y);
    this.time.delayedCall(500, () => e.destroy());
  }

  popup(x, y, text, color) {
    const t = this.add.text(x, y, text, { fontFamily: 'Arial Black', fontSize: '18px', color }).setOrigin(0.5).setDepth(7);
    this.tweens.add({ targets: t, y: y - 42, alpha: 0, duration: 650, onComplete: () => t.destroy() });
  }

  refreshHUD() {
    this.prodText.setText('PRODUCTION: ' + this.prodScore);
    this.ecoText.setText('ECO: ' + this.ecoScore);
  }

  update() {
    if (this.over) return;
    this.bgFar.tilePositionY -= this.speed / 120;
    this.bgNear.tilePositionY -= this.speed / 55;
    const left = this.cursors.left.isDown || this.keys.A.isDown;
    const right = this.cursors.right.isDown || this.keys.D.isDown;
    if (left) { this.player.setVelocityX(-260); this.player.setAngle(-8); }
    else if (right) { this.player.setVelocityX(260); this.player.setAngle(8); }
    else { this.player.setVelocityX(0); this.player.setAngle(0); }
    [this.minerals, this.birds, this.blasts, this.groves].forEach(grp => {
      grp.getChildren().forEach(c => {
        if (c.body && c.body.enable) c.setVelocityY(this.speed);
        if (c.y > H + 40) c.destroy();
      });
    });
  }

  gameOver() {
    if (this.over) return;
    this.over = true;
    this.spawnTimer.remove();
    this.player.setVelocity(0, 0);
    this.physics.pause();
    this.cameras.main.shake(250, 0.012);
    this.burst(this.player.x, this.player.y, 0xe24b4a);
    if (this.cache.audio.exists('sfx_crash')) this.sound.play('sfx_crash', { volume: 0.6 });
    this.add.rectangle(W / 2, H / 2, W, H, 0x000000, 0.7).setDepth(8);
    this.add.text(W / 2, 200, 'GAME OVER', { fontFamily: 'Arial Black', fontSize: '40px', color: '#e74c3c' }).setOrigin(0.5).setDepth(9);
    this.add.text(W / 2, 270, 'Production: ' + this.prodScore + '\nEco: ' + this.ecoScore,
      { fontFamily: 'Arial', fontSize: '20px', color: '#ffffff', align: 'center' }).setOrigin(0.5).setDepth(9);
    const verdict = this.ecoScore >= 0
      ? `Like Imerys at ${this.cfg.site_name}, you supported\n${this.cfg.eco_target}!`
      : `Eco score in the red — protect ${this.cfg.eco_target}\nbetter next time.`;
    this.add.text(W / 2, 350, verdict, { fontFamily: 'Arial', fontSize: '15px', color: '#2ecc71', align: 'center' }).setOrigin(0.5).setDepth(9);
    const retry = this.add.text(W / 2, 450, 'Press SPACE to retry',
      { fontFamily: 'Arial', fontSize: '18px', color: '#ffffff', backgroundColor: '#27ae60', padding: { x: 16, y: 8 } })
      .setOrigin(0.5).setDepth(9);
    this.tweens.add({ targets: retry, alpha: 0.6, duration: 600, yoyo: true, repeat: -1 });
    this.input.keyboard.once('keydown-SPACE', () => this.scene.start('Game'));
  }
}

new Phaser.Game({
  type: Phaser.AUTO,
  width: W,
  height: H,
  backgroundColor: '#1a1a1a',
  physics: { default: 'arcade', arcade: { debug: false } },
  scene: [BootScene, PreloadScene, MenuScene, GameScene]
});

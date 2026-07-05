// =============================================================
//  Eco-Mine Runner — game.js  v4  (Sprint 3 : gameplay & méta)
//
//  MOTEUR FIXE, hand-coded. L'agent ne touche jamais ce fichier : il
//  remplit un level_config.json que le moteur vient lire (config-driven).
//
//  Nouveautés Sprint 3 :
//    - dynamite (malus, non fatal)      -> obstacles.dynamite
//    - zones d'eau (ralentissement)     -> zones.water
//    - camions ennemis (game over)      -> entities.enemy_trucks
//    - difficulté progressive           -> src/difficulty.js + difficulty.*
//    - pseudo + leaderboard localStorage -> src/leaderboard.js
//    - badge Imerys Green               -> thresholds.green_badge
//
//  ?config=<chemin> dans l'URL charge un config alternatif (test manuel
//  sans agent). Sans lui : level_config.json à la racine servie.
//
//  Décor réel (optionnel) par biome, dans assets/ :
//    <biome>_far.png   <biome>_near.png
//  Objets (optionnels) : truck.png ore.png bird.png blast.png grove.png
//                        spark.png dynamite.png enemy_truck.png
//  Badge (optionnel) : ui/badge_green.png
//  Sans ces fichiers : tout est dessiné par code. 404 console = normal.
// =============================================================

import { getDifficulty, normalizeDifficulty } from './src/difficulty.js';
import * as Leaderboard from './src/leaderboard.js';

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
  biodiversity_species: ["Migratory Birds", "Cave Bats", "Chestnut Groves"],
  // --- Sprint 3 (défauts = rétro-compat ; voir docs/level_config_schema.md) ---
  obstacles: {
    dynamite: { spawn_weight: 0.15, explosion_radius_px: 80, green_malus: 10, score_malus: 200 }
  },
  zones: {
    water: { spawn_weight: 0.10, min_length_px: 120, max_length_px: 300, effect: "slowdown", slowdown_factor: 0.4 }
  },
  entities: {
    enemy_trucks: { spawn_weight: 0.08, speed_px_per_s: 180, behavior: "straight_line", collision_effect: "game_over" }
  },
  difficulty: {
    curve: "linear", speed_start_px_per_s: 220, speed_max_px_per_s: 480,
    distance_to_max_px: 15000, spawn_rate_multiplier_at_max: 2.2
  },
  thresholds: {
    green_badge: { min_score: 5000, min_green_points: 30 }
  },
  ui_strings: {
    title: "MISSION CLERAC",
    instructions: "Collect Chamotte & Band Birds! Avoid Blasting Zones!",
    intro_story: "Imerys needs you at the Clerac clay quarry. Haul Chamotte to keep the plant running — but the pit is alive with migratory birds tracked by the MNHN. Collect ore, shield the wildlife, and steer clear of the blasting zones.",
    eco_facts: [
      "Migratory birds here are ringed with the MNHN each year.",
      "Chestnut groves are left unmined to shelter bats.",
      "The ACRO-bag program compares quarries with restored sites."
    ],
    end_recap: "Like Imerys at Clerac, you supported bird monitoring with the MNHN through the ACRO-bag program."
  }
};

const BIOMES = {
  clay_quarry:         { far: 0xb6a484, rock: 0xa3906f, near: 0x6e5a3c, accent: 0xd4a017 },
  granite_underground: { far: 0x3a3d42, rock: 0x2b2e33, near: 0x565d66, accent: 0x7f8c8d },
  wetland:             { far: 0x6b8e4e, rock: 0x557a3a, near: 0x3e5c2a, accent: 0x2e86c1 },
  diatomite:           { far: 0xd8d8d2, rock: 0xc2c2ba, near: 0xb0b0a8, accent: 0x95a5a6 }
};

const OBJECT_ASSETS = {
  truck:       'assets/truck.png',
  mineral:     'assets/ore.png',
  bird:        'assets/bird.png',
  blast:       'assets/blast.png',
  grove:       'assets/grove.png',
  spark:       'assets/spark.png',
  dynamite:    'assets/dynamite.png',
  enemy_truck: 'assets/enemy_truck.png'
};

// Fusionne récursivement (1 niveau de profondeur par section) un config chargé
// sur les défauts. Chaque sous-objet manquant est complété. Garantit qu'un
// config Sprint 2 (sans sections Sprint 3) boote à l'identique.
function mergeConfig(loaded) {
  const cfg = Object.assign({}, DEFAULT_CONFIG, loaded || {});
  const sub = (key) => Object.assign({}, DEFAULT_CONFIG[key], (loaded && loaded[key]) || {});
  cfg.spawn_rates = sub('spawn_rates');
  cfg.ui_strings = sub('ui_strings');
  cfg.thresholds = sub('thresholds');
  cfg.thresholds.green_badge = Object.assign({}, DEFAULT_CONFIG.thresholds.green_badge,
    (loaded && loaded.thresholds && loaded.thresholds.green_badge) || {});
  cfg.obstacles = sub('obstacles');
  cfg.obstacles.dynamite = Object.assign({}, DEFAULT_CONFIG.obstacles.dynamite,
    (loaded && loaded.obstacles && loaded.obstacles.dynamite) || {});
  cfg.zones = sub('zones');
  cfg.zones.water = Object.assign({}, DEFAULT_CONFIG.zones.water,
    (loaded && loaded.zones && loaded.zones.water) || {});
  cfg.entities = sub('entities');
  cfg.entities.enemy_trucks = Object.assign({}, DEFAULT_CONFIG.entities.enemy_trucks,
    (loaded && loaded.entities && loaded.entities.enemy_trucks) || {});
  // Difficulté : normalisée par le module dédié (fallback sur scrolling_speed legacy).
  cfg.difficulty = normalizeDifficulty(loaded && loaded.difficulty, cfg.scrolling_speed);
  if (!BIOMES[cfg.biome]) cfg.biome = 'clay_quarry';
  return cfg;
}

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
    case 'enemy_truck':
      // Camion adverse : silhouette rouge/orange, distincte du joueur (jaune).
      g.fillStyle(0x1a1a1a, 1);
      g.fillRoundedRect(2, 12, 8, 18, 3); g.fillRoundedRect(2, 40, 8, 18, 3);
      g.fillRoundedRect(34, 12, 8, 18, 3); g.fillRoundedRect(34, 40, 8, 18, 3);
      g.fillStyle(0xe24b4a, 1); g.fillRoundedRect(8, 4, 28, 60, 6);
      g.fillStyle(0xb03a3a, 1); g.fillRect(11, 30, 22, 30);
      g.fillStyle(0x2c3e50, 1); g.fillRoundedRect(12, 44, 20, 15, 3); // cabine vers le bas
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
    case 'dynamite':
      // Fagot de bâtons rouges + mèche : lisible et distinct du "blast".
      g.fillStyle(0xc0392b, 1);
      g.fillRoundedRect(6, 6, 9, 30, 2); g.fillRoundedRect(17, 6, 9, 30, 2); g.fillRoundedRect(28, 6, 9, 30, 2);
      g.fillStyle(0xf5d76e, 1); g.fillRect(6, 15, 31, 5); // bande
      g.fillStyle(0x7a4a2b, 1); g.fillRect(20, 0, 3, 8);  // mèche
      g.fillStyle(0xf39c12, 1); g.fillCircle(22, 0, 3);   // étincelle
      g.generateTexture(key, 44, 40); break;
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
    // ?config=<chemin> permet de charger un config alternatif (test sans agent).
    let configPath = 'level_config.json';
    try {
      const p = new URLSearchParams(window.location.search).get('config');
      if (p) configPath = p;
    } catch (e) { /* pas d'URL (contexte non-navigateur) : on garde le défaut */ }
    this.load.json('levelConfig', configPath);
  }
  create() {
    const loaded = this.cache.json.get('levelConfig');
    this.registry.set('cfg', mergeConfig(loaded));
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
    this.load.image('badgeGreen', 'assets/ui/badge_green.png');
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
    this.scene.start('Story');
  }
}

// Intro narrative généré par l'agent (ui_strings.intro_story).
class StoryScene extends Phaser.Scene {
  constructor() { super('Story'); }
  create() {
    const cfg = this.registry.get('cfg');
    this.far = this.add.tileSprite(W / 2, H / 2, W, H, 'bg_far');
    this.add.rectangle(W / 2, H / 2, W, H, 0x000000, 0.6);
    this.add.text(W / 2, 90, cfg.ui_strings.title,
      { fontFamily: 'Arial Black, sans-serif', fontSize: '30px', color: '#f1c40f', align: 'center', wordWrap: { width: 420 } }).setOrigin(0.5);
    this.add.text(W / 2, 300, cfg.ui_strings.intro_story || '',
      { fontFamily: 'Arial', fontSize: '17px', color: '#ecf0f1', align: 'center', wordWrap: { width: 400 }, lineSpacing: 7 }).setOrigin(0.5);
    const cont = this.add.text(W / 2, 560, '▶  CLICK or SPACE to continue',
      { fontFamily: 'Arial', fontSize: '18px', color: '#ffffff', backgroundColor: '#27ae60', padding: { x: 16, y: 9 } })
      .setOrigin(0.5).setInteractive({ useHandCursor: true });
    this.tweens.add({ targets: cont, alpha: 0.6, duration: 700, yoyo: true, repeat: -1 });
    const go = () => this.scene.start('Menu');
    cont.on('pointerdown', go);
    this.input.keyboard.once('keydown-SPACE', go);
  }
  update() { if (this.far) this.far.tilePositionY -= 0.4; }
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
    this.add.text(W / 2, 96, cfg.ui_strings.title,
      { fontFamily: 'Arial Black, sans-serif', fontSize: '34px', color: '#f1c40f' }).setOrigin(0.5);
    this.add.text(W / 2, 136, 'ECO-MINE RUNNER',
      { fontFamily: 'Arial', fontSize: '16px', color: '#ffffff' }).setOrigin(0.5);
    this.add.text(W / 2, 210, cfg.ui_strings.instructions,
      { fontFamily: 'Arial', fontSize: '15px', color: '#ecf0f1', align: 'center', wordWrap: { width: 380 } }).setOrigin(0.5);
    this.add.image(150, 300, 'mineral');    this.add.text(178, 292, '+10 production', { fontSize: '13px', color: '#ecf0f1' });
    this.add.image(150, 338, 'bird');       this.add.text(178, 330, '+15 eco  (+1 green)', { fontSize: '13px', color: '#ecf0f1' });
    this.add.image(150, 376, 'dynamite');   this.add.text(178, 368, 'dynamite — malus, keep going', { fontSize: '13px', color: '#e67e22' });
    this.add.image(150, 414, 'enemy_truck');this.add.text(178, 406, 'rival truck — crash!', { fontSize: '13px', color: '#e74c3c' });
    this.add.image(150, 452, 'blast');      this.add.text(178, 444, 'blasting zone — crash!', { fontSize: '13px', color: '#e74c3c' });
    this.add.image(150, 490, 'grove');      this.add.text(178, 482, 'protected — eco penalty', { fontSize: '13px', color: '#2ecc71' });
    const play = this.add.text(W / 2, 552, '▶  SPACE to play',
      { fontFamily: 'Arial', fontSize: '20px', color: '#ffffff', backgroundColor: '#27ae60', padding: { x: 18, y: 10 } })
      .setOrigin(0.5).setInteractive({ useHandCursor: true });
    this.tweens.add({ targets: play, alpha: 0.6, duration: 700, yoyo: true, repeat: -1 });
    const lb = this.add.text(W / 2, 604, '🏆  L — Leaderboard',
      { fontFamily: 'Arial', fontSize: '15px', color: '#ffffff', backgroundColor: '#2c3e50', padding: { x: 12, y: 6 } })
      .setOrigin(0.5).setInteractive({ useHandCursor: true });
    const start = () => this.scene.start('Game');
    const openLb = () => this.scene.start('Leaderboard', { from: 'Menu' });
    play.on('pointerdown', start);
    lb.on('pointerdown', openLb);
    this.input.keyboard.once('keydown-SPACE', start);
    this.input.keyboard.on('keydown-L', openLb);
  }
  update() { if (this.far) this.far.tilePositionY -= 0.4; }
}

class GameScene extends Phaser.Scene {
  constructor() { super('Game'); }

  create() {
    this.cfg = this.registry.get('cfg');
    this.diffCfg = this.cfg.difficulty;
    this.distance = 0;                       // px parcourus (pilote la difficulté)
    this.speed = this.diffCfg.speed_start_px_per_s;
    this.prodScore = 0; this.ecoScore = 0; this.greenPoints = 0; this.over = false;
    this.facts = (this.cfg.ui_strings && this.cfg.ui_strings.eco_facts) || [];
    this.factIdx = 0; this.factBanner = null; this.ecoCollected = 0;
    this.waterZones = [];                    // bandes d'eau actives (ralentissement)
    this.lastSplash = 0;

    this.bgFar = this.add.tileSprite(W / 2, H / 2, W, H, 'bg_far');
    this.bgNear = this.add.tileSprite(W / 2, H / 2, W, H, 'bg_near');
    this.waterLayer = this.add.container(0, 0).setDepth(1);

    this.player = this.physics.add.sprite(W / 2, H - 70, 'truck').setCollideWorldBounds(true).setDepth(4);
    this.player.body.setSize(28, 52).setOffset(8, 10);

    this.minerals = this.physics.add.group();
    this.birds = this.physics.add.group();
    this.blasts = this.physics.add.group();
    this.groves = this.physics.add.group();
    this.dynamites = this.physics.add.group();
    this.enemyTrucks = this.physics.add.group();

    this.physics.add.overlap(this.player, this.minerals, (p, o) => this.collect(o, 'prod', 10), null, this);
    this.physics.add.overlap(this.player, this.birds, (p, o) => this.collect(o, 'eco', 15), null, this);
    this.physics.add.overlap(this.player, this.groves, (p, o) => this.collect(o, 'eco', -20, true), null, this);
    this.physics.add.overlap(this.player, this.blasts, () => this.gameOver('blast'), null, this);
    this.physics.add.overlap(this.player, this.dynamites, (p, o) => this.hitDynamite(o), null, this);
    this.physics.add.overlap(this.player, this.enemyTrucks, () => this.gameOver('enemy_truck'), null, this);

    this.prodText = this.add.text(12, 12, '', { fontFamily: 'Arial', fontSize: '18px', color: '#f1c40f' }).setDepth(5);
    this.ecoText = this.add.text(W - 12, 12, '', { fontFamily: 'Arial', fontSize: '18px', color: '#2ecc71' }).setOrigin(1, 0).setDepth(5);
    this.greenText = this.add.text(W - 12, 36, '', { fontFamily: 'Arial', fontSize: '14px', color: '#7ef7b0' }).setOrigin(1, 0).setDepth(5);
    this.refreshHUD();

    this.cursors = this.input.keyboard.createCursorKeys();
    this.keys = this.input.keyboard.addKeys('A,D');
    this.spawnTimer = this.time.addEvent({ delay: 750, loop: true, callback: () => this.spawnWave() });
  }

  spawnWave() {
    if (this.over) return;
    const r = this.cfg.spawn_rates;
    const m = getDifficulty(this.distance, this.diffCfg).spawnRateMultiplier;
    const roll = (rate, group, key, spin = false, flap = false, velBonus = 0) => {
      if (Math.random() < rate * m) {
        const x = Phaser.Math.Between(30, W - 30);
        const item = group.create(x, -30, key);
        item.setVelocityY(this.speed + velBonus);
        item.setData('velBonus', velBonus);
        if (spin) this.tweens.add({ targets: item, angle: 360, duration: 2200, repeat: -1 });
        if (flap) this.tweens.add({ targets: item, scaleY: 0.6, duration: 200, yoyo: true, repeat: -1 });
      }
    };
    roll(r.mineral, this.minerals, 'mineral', true);
    roll(r.eco_bonus, this.birds, 'bird', false, true);
    roll(r.obstacle, this.blasts, 'blast');
    roll(r.obstacle * 0.6, this.groves, 'grove');
    roll(this.cfg.obstacles.dynamite.spawn_weight, this.dynamites, 'dynamite', false, false);
    // Camions ennemis : vitesse propre ajoutée au défilement (straight_line).
    roll(this.cfg.entities.enemy_trucks.spawn_weight, this.enemyTrucks, 'enemy_truck',
      false, false, this.cfg.entities.enemy_trucks.speed_px_per_s);
    // Zones d'eau : bande de ralentissement (pas un sprite physique).
    if (Math.random() < this.cfg.zones.water.spawn_weight * m) this.spawnWaterZone();
  }

  spawnWaterZone() {
    const z = this.cfg.zones.water;
    const len = Phaser.Math.Between(z.min_length_px, z.max_length_px);
    const band = this.add.rectangle(W / 2, -len / 2, W, len, 0x2e86c1, 0.32);
    band.setStrokeStyle(2, 0x5dade2, 0.6);
    this.waterLayer.add(band);
    this.waterZones.push({ band, top: () => band.y - len / 2, bottom: () => band.y + len / 2 });
  }

  hitDynamite(o) {
    if (!o.active || this.over) return;
    o.body.enable = false;
    const d = this.cfg.obstacles.dynamite;
    this.prodScore -= d.score_malus;
    this.greenPoints -= d.green_malus;
    this.cameras.main.shake(200, 0.02);
    this.cameras.main.flash(180, 230, 120, 40);
    this.explode(o.x, o.y, d.explosion_radius_px);
    this.popup(o.x, o.y, '-' + d.score_malus, '#e67e22');
    if (this.cache.audio.exists('sfx_crash')) this.sound.play('sfx_crash', { volume: 0.4 });
    this.tweens.add({ targets: o, scale: 1.8, alpha: 0, duration: 180, onComplete: () => o.destroy() });
    this.refreshHUD();
  }

  explode(x, y, radiusPx) {
    const qty = Phaser.Math.Clamp(Math.round(radiusPx / 6), 8, 26);
    const e = this.add.particles(x, y, 'spark', {
      speed: { min: radiusPx * 0.6, max: radiusPx * 2.2 }, lifespan: 480,
      scale: { start: 1.1, end: 0 }, tint: [0xf9d423, 0xef8b2c, 0xe24b4a],
      quantity: qty, emitting: false
    }).setDepth(7);
    e.explode(qty, x, y);
    this.time.delayedCall(600, () => e.destroy());
  }

  collect(obj, kind, points, penalty = false) {
    if (!obj.active) return;
    obj.body.enable = false;
    const color = penalty ? 0xe24b4a : (kind === 'eco' ? 0x2ecc71 : 0xf1c40f);
    const hex = penalty ? '#e74c3c' : (kind === 'eco' ? '#2ecc71' : '#f1c40f');
    this.burst(obj.x, obj.y, color);
    this.popup(obj.x, obj.y, (points >= 0 ? '+' : '') + points, hex);
    if (kind === 'prod') this.prodScore += points; else this.ecoScore += points;
    if (penalty) { this.greenPoints -= 3; this.cameras.main.flash(120, 200, 60, 60); }
    if (kind === 'eco' && !penalty) { this.ecoCollected++; this.greenPoints += 1; this.showFact(); }
    if (!penalty && this.cache.audio.exists('sfx_collect')) this.sound.play('sfx_collect', { volume: 0.5 });
    this.tweens.add({ targets: obj, scale: 1.6, alpha: 0, duration: 160, onComplete: () => obj.destroy() });
    this.refreshHUD();
  }

  showFact() {
    if (!this.facts.length) return;
    const msg = this.facts[this.factIdx % this.facts.length];
    this.factIdx++;
    if (this.factBanner) { this.factBanner.destroy(); this.factBanner = null; }
    const t = this.add.text(W / 2, 66, msg,
      { fontFamily: 'Arial', fontSize: '13px', color: '#eafaf1', backgroundColor: '#1e8449',
        padding: { x: 10, y: 6 }, align: 'center', wordWrap: { width: W - 48 } })
      .setOrigin(0.5).setDepth(9);
    this.factBanner = t;
    this.tweens.add({ targets: t, alpha: 0, delay: 1600, duration: 400,
      onComplete: () => { if (this.factBanner === t) this.factBanner = null; t.destroy(); } });
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

  totalScore() {
    return Math.round(this.prodScore + this.ecoScore + this.distance / 10);
  }

  refreshHUD() {
    this.prodText.setText('PRODUCTION: ' + this.prodScore);
    this.ecoText.setText('ECO: ' + this.ecoScore);
    this.greenText.setText('♦ GREEN: ' + this.greenPoints);
  }

  playerInWater() {
    const py = this.player.y;
    for (const z of this.waterZones) {
      if (py >= z.top() && py <= z.bottom()) return true;
    }
    return false;
  }

  update(time, delta) {
    if (this.over) return;
    const dt = delta / 1000;

    // Difficulté pilotée par la distance (aucun magic number ici).
    const diff = getDifficulty(this.distance, this.diffCfg);
    const inWater = this.playerInWater();
    this.speed = inWater ? diff.speed * this.cfg.zones.water.slowdown_factor : diff.speed;
    this.distance += this.speed * dt;

    // Éclaboussures + teinte quand on traverse une zone d'eau.
    if (inWater && time - this.lastSplash > 120) {
      this.lastSplash = time;
      this.burst(this.player.x + Phaser.Math.Between(-14, 14), this.player.y + 20, 0x5dade2);
    }
    this.player.setTint(inWater ? 0x9fd3f0 : 0xffffff);

    this.bgFar.tilePositionY -= this.speed / 120;
    this.bgNear.tilePositionY -= this.speed / 55;

    const left = this.cursors.left.isDown || this.keys.A.isDown;
    const right = this.cursors.right.isDown || this.keys.D.isDown;
    if (left) { this.player.setVelocityX(-260); this.player.setAngle(-8); }
    else if (right) { this.player.setVelocityX(260); this.player.setAngle(8); }
    else { this.player.setVelocityX(0); this.player.setAngle(0); }

    // Vitesse des items = défilement (+ bonus propre pour les camions ennemis).
    [this.minerals, this.birds, this.blasts, this.groves, this.dynamites, this.enemyTrucks].forEach(grp => {
      grp.getChildren().forEach(c => {
        if (c.body && c.body.enable) c.setVelocityY(this.speed + (c.getData('velBonus') || 0));
        if (c.y > H + 40) c.destroy();
      });
    });

    // Défilement + recyclage des bandes d'eau.
    for (let i = this.waterZones.length - 1; i >= 0; i--) {
      const z = this.waterZones[i];
      z.band.y += this.speed * dt;
      if (z.top() > H + 20) { z.band.destroy(); this.waterZones.splice(i, 1); }
    }
  }

  gameOver(cause) {
    if (this.over) return;
    this.over = true;
    this.spawnTimer.remove();
    this.player.setVelocity(0, 0);
    this.player.clearTint();
    this.physics.pause();
    this.cameras.main.shake(250, 0.012);
    this.burst(this.player.x, this.player.y, 0xe24b4a);
    if (this.cache.audio.exists('sfx_crash')) this.sound.play('sfx_crash', { volume: 0.6 });

    const th = this.cfg.thresholds.green_badge;
    const score = this.totalScore();
    const badge = score >= th.min_score && this.greenPoints >= th.min_green_points;

    // Pseudo (max 12, sanitize dans le module) + persistance leaderboard.
    let pseudo = 'ANON';
    try {
      const raw = window.prompt('Game over! Enter your pseudo (max 12 chars):', '');
      pseudo = Leaderboard.sanitizePseudo(raw);
    } catch (e) { pseudo = 'ANON'; }
    const entry = {
      pseudo, score, green_points: this.greenPoints, badge,
      date_iso: new Date().toISOString()
    };
    try { Leaderboard.add(entry); } catch (e) { /* localStorage indispo : on continue */ }
    this.registry.set('lastResult', {
      entry, cause,
      prodScore: this.prodScore, ecoScore: this.ecoScore,
      species: (this.cfg.biodiversity_species || []).slice(0, 4)
    });

    // Badge -> écran de célébration dédié, sinon écran de fin standard.
    if (badge) this.scene.start('Badge');
    else this.scene.start('GameOver');
  }
}

// Écran de célébration dédié au badge Imerys Green.
class BadgeScene extends Phaser.Scene {
  constructor() { super('Badge'); }
  create() {
    const cfg = this.registry.get('cfg');
    const res = this.registry.get('lastResult') || { entry: {} };
    this.add.rectangle(W / 2, H / 2, W, H, 0x0b3d1e, 1);
    for (let i = 0; i < 40; i++) {
      const c = this.add.circle(Phaser.Math.Between(0, W), Phaser.Math.Between(0, H),
        Phaser.Math.Between(2, 5), 0xf1c40f, 0.5);
      this.tweens.add({ targets: c, y: c.y + Phaser.Math.Between(20, 60), alpha: 0.1,
        duration: Phaser.Math.Between(1200, 2600), yoyo: true, repeat: -1 });
    }
    this.add.text(W / 2, 70, '★ IMERYS GREEN BADGE ★',
      { fontFamily: 'Arial Black', fontSize: '24px', color: '#f1c40f', align: 'center', wordWrap: { width: 440 } }).setOrigin(0.5);

    if (this.textures.exists('badgeGreen')) {
      this.add.image(W / 2, 250, 'badgeGreen').setDisplaySize(160, 160);
    } else {
      // Placeholder : médaille arbre doré dessinée par code (badge_green.png absent).
      const g = this.add.graphics();
      g.fillStyle(0xf1c40f, 1); g.fillCircle(W / 2, 250, 74);
      g.fillStyle(0xd4a017, 1); g.fillCircle(W / 2, 250, 62);
      g.fillStyle(0x1e8449, 1); g.fillCircle(W / 2, 238, 34);
      g.fillStyle(0x7a5230, 1); g.fillRect(W / 2 - 5, 250, 10, 34);
      g.fillStyle(0x27ae60, 1); g.fillCircle(W / 2 - 22, 250, 18); g.fillCircle(W / 2 + 22, 250, 18);
    }

    this.add.text(W / 2, 360, `${res.entry.pseudo || 'ANON'} earned it!`,
      { fontFamily: 'Arial', fontSize: '20px', color: '#ffffff' }).setOrigin(0.5);
    this.add.text(W / 2, 402, `Score ${res.entry.score}  ·  ♦ Green ${res.entry.green_points}`,
      { fontFamily: 'Arial', fontSize: '16px', color: '#2ecc71' }).setOrigin(0.5);
    this.add.text(W / 2, 452, `You protected ${cfg.eco_target} at ${cfg.site_name}.`,
      { fontFamily: 'Arial', fontSize: '14px', color: '#ecf0f1', align: 'center', wordWrap: { width: 400 } }).setOrigin(0.5);

    const cont = this.add.text(W / 2, 552, '▶  SPACE to continue',
      { fontFamily: 'Arial', fontSize: '18px', color: '#ffffff', backgroundColor: '#27ae60', padding: { x: 16, y: 9 } })
      .setOrigin(0.5).setInteractive({ useHandCursor: true });
    this.tweens.add({ targets: cont, alpha: 0.6, duration: 600, yoyo: true, repeat: -1 });
    const go = () => this.scene.start('GameOver');
    cont.on('pointerdown', go);
    this.input.keyboard.once('keydown-SPACE', go);
  }
}

class GameOverScene extends Phaser.Scene {
  constructor() { super('GameOver'); }
  create() {
    const cfg = this.registry.get('cfg');
    const res = this.registry.get('lastResult') || { entry: {}, species: [] };
    this.far = this.add.tileSprite(W / 2, H / 2, W, H, 'bg_far');
    this.add.rectangle(W / 2, H / 2, W, H, 0x000000, 0.72);
    this.add.text(W / 2, 90, 'GAME OVER',
      { fontFamily: 'Arial Black', fontSize: '40px', color: '#e74c3c' }).setOrigin(0.5);
    this.add.text(W / 2, 158,
      'Score: ' + res.entry.score + '\nProduction: ' + res.prodScore +
      '   Eco: ' + res.ecoScore + '   ♦ Green: ' + res.entry.green_points,
      { fontFamily: 'Arial', fontSize: '17px', color: '#ffffff', align: 'center', lineSpacing: 4 }).setOrigin(0.5);
    if (res.entry.badge) {
      this.add.text(W / 2, 214, '★ Imerys Green Badge earned ★',
        { fontFamily: 'Arial', fontSize: '15px', color: '#f1c40f' }).setOrigin(0.5);
    }

    const recap = (cfg.ui_strings && cfg.ui_strings.end_recap)
      || `Like Imerys at ${cfg.site_name}, you supported ${cfg.eco_target}!`;
    const recapColor = res.ecoScore >= 0 ? '#2ecc71' : '#e67e22';
    this.add.text(W / 2, 280, recap,
      { fontFamily: 'Arial', fontSize: '15px', color: recapColor, align: 'center', wordWrap: { width: 400 }, lineSpacing: 4 }).setOrigin(0.5);
    const species = (res.species || []).join('  ·  ');
    if (species) {
      this.add.text(W / 2, 366, 'Biodiversity you defended:\n' + species,
        { fontFamily: 'Arial', fontSize: '13px', color: '#ffffff', align: 'center', wordWrap: { width: 400 }, lineSpacing: 4 }).setOrigin(0.5);
    }

    const retry = this.add.text(W / 2, 470, '▶  SPACE to retry',
      { fontFamily: 'Arial', fontSize: '18px', color: '#ffffff', backgroundColor: '#27ae60', padding: { x: 16, y: 8 } })
      .setOrigin(0.5).setInteractive({ useHandCursor: true });
    this.tweens.add({ targets: retry, alpha: 0.6, duration: 600, yoyo: true, repeat: -1 });
    const lb = this.add.text(W / 2, 528, '🏆  L — Leaderboard',
      { fontFamily: 'Arial', fontSize: '15px', color: '#ffffff', backgroundColor: '#2c3e50', padding: { x: 12, y: 6 } })
      .setOrigin(0.5).setInteractive({ useHandCursor: true });
    const menu = this.add.text(W / 2, 578, 'M — Menu',
      { fontFamily: 'Arial', fontSize: '14px', color: '#bdc3c7' }).setOrigin(0.5).setInteractive({ useHandCursor: true });

    const doRetry = () => this.scene.start('Game');
    const openLb = () => this.scene.start('Leaderboard', { from: 'GameOver' });
    const openMenu = () => this.scene.start('Menu');
    retry.on('pointerdown', doRetry);
    lb.on('pointerdown', openLb);
    menu.on('pointerdown', openMenu);
    this.input.keyboard.once('keydown-SPACE', doRetry);
    this.input.keyboard.on('keydown-L', openLb);
    this.input.keyboard.on('keydown-M', openMenu);
  }
  update() { if (this.far) this.far.tilePositionY -= 0.4; }
}

class LeaderboardScene extends Phaser.Scene {
  constructor() { super('Leaderboard'); }
  create(data) {
    const from = (data && data.from) || 'Menu';
    this.add.rectangle(W / 2, H / 2, W, H, 0x14171c, 1);
    this.add.text(W / 2, 60, '🏆  LEADERBOARD',
      { fontFamily: 'Arial Black', fontSize: '28px', color: '#f1c40f' }).setOrigin(0.5);
    this.add.text(W / 2, 96, 'Top 10 — by score',
      { fontFamily: 'Arial', fontSize: '14px', color: '#95a5a6' }).setOrigin(0.5);

    let rows = [];
    try { rows = Leaderboard.getTop(10); } catch (e) { rows = []; }
    if (!rows.length) {
      this.add.text(W / 2, 300, 'No scores yet.\nPlay a run to appear here!',
        { fontFamily: 'Arial', fontSize: '18px', color: '#ecf0f1', align: 'center', lineSpacing: 6 }).setOrigin(0.5);
    } else {
      rows.forEach((e, i) => {
        const y = 140 + i * 40;
        const c = i === 0 ? '#f1c40f' : '#ecf0f1';
        this.add.text(28, y, String(i + 1).padStart(2, ' '),
          { fontFamily: 'Arial', fontSize: '16px', color: '#7f8c8d' }).setOrigin(0, 0.5);
        this.add.text(64, y, (e.badge ? '★ ' : '') + e.pseudo,
          { fontFamily: 'Arial', fontSize: '16px', color: c }).setOrigin(0, 0.5);
        this.add.text(300, y, String(e.score),
          { fontFamily: 'Arial Black', fontSize: '16px', color: c }).setOrigin(0, 0.5);
        this.add.text(392, y, '♦' + e.green_points,
          { fontFamily: 'Arial', fontSize: '14px', color: '#2ecc71' }).setOrigin(0, 0.5);
      });
    }

    const back = this.add.text(W / 2, 578, '◀  BACK',
      { fontFamily: 'Arial', fontSize: '18px', color: '#ffffff', backgroundColor: '#2c3e50', padding: { x: 16, y: 8 } })
      .setOrigin(0.5).setInteractive({ useHandCursor: true });
    const clear = this.add.text(W / 2, 618, 'C — clear scores',
      { fontFamily: 'Arial', fontSize: '13px', color: '#7f8c8d' }).setOrigin(0.5).setInteractive({ useHandCursor: true });
    const goBack = () => this.scene.start(from === 'GameOver' ? 'GameOver' : 'Menu');
    const doClear = () => { try { Leaderboard.clear(); } catch (e) {} this.scene.restart({ from }); };
    back.on('pointerdown', goBack);
    clear.on('pointerdown', doClear);
    this.input.keyboard.once('keydown-SPACE', goBack);
    this.input.keyboard.once('keydown-ESC', goBack);
    this.input.keyboard.once('keydown-C', doClear);
  }
}

new Phaser.Game({
  type: Phaser.AUTO,
  width: W,
  height: H,
  backgroundColor: '#1a1a1a',
  physics: { default: 'arcade', arcade: { debug: false } },
  scene: [BootScene, PreloadScene, StoryScene, MenuScene, GameScene, BadgeScene, GameOverScene, LeaderboardScene]
});

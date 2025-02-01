#!/usr/bin/env python
# title: Enhanced VJ with GA, Reaction-Diffusion, Boids, Game of Life
# author: karaage
# desc: Pyxelを用いたVJアプリ。音は派手に連続再生し、パターンに合わせて変化。パラメータはGenetic Algorithmにより進化し、さらに反応拡散シミュレーション、Boids、ライフゲームの各シミュレーションを実装。
# site: https://github.com/karaage0703/pyxel-examples
# license: MIT
# version: 1.1

import pyxel
import math
import random
from collections import deque


class EnhancedVJ:
    def __init__(self):
        self.SCREEN_WIDTH = 256
        self.SCREEN_HEIGHT = 256
        pyxel.init(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

        # パターンとサブパターンの設定
        # pattern_typeは0～7の8種類（0:フラクタル, 1:パーティクル, 2:波形, 3:幾何学, 4:グリッチ, 5:反応拡散, 6:Boids, 7:ライフゲーム）
        self.pattern_type = 0
        self.sub_pattern = 0
        self.rotation = 0
        self.scale = 1.0
        self.color_phase = 0
        self.wave_phase = 0
        self.particles = []
        self.trails = deque(maxlen=32)
        self.beat = False
        self.auto_beat = 0

        # パラメータ（GAによる進化対象：speed, intensity, complexity）
        self.speed = 1.0
        self.intensity = 1.0
        self.complexity = 1.0

        # グリッチ効果
        self.glitch = False

        # 派手な音の再生用タイマー
        self.sound_timer = 0
        self.init_sound()

        # GAの初期化：各個体は speed, intensity, complexity の3要素
        self.ga_population = []
        for _ in range(10):
            ind = {
                "speed": random.uniform(0.5, 2.0),
                "intensity": random.uniform(0.1, 2.0),
                "complexity": random.uniform(0.1, 2.0),
            }
            self.ga_population.append(ind)
        self.ga_timer = 0  # GA更新用タイマー

        # 反応拡散シミュレーションの初期化（グリッドサイズ32x32）
        self.rd_grid_size_x = 32
        self.rd_grid_size_y = 32
        self.rd_U = [[1.0 for _ in range(self.rd_grid_size_x)] for _ in range(self.rd_grid_size_y)]
        self.rd_V = [[0.0 for _ in range(self.rd_grid_size_x)] for _ in range(self.rd_grid_size_y)]
        # 中央に摂動を加える
        cx, cy = self.rd_grid_size_x // 2, self.rd_grid_size_y // 2
        self.rd_U[cy][cx] = 0.50
        self.rd_V[cy][cx] = 0.25

        # Boidsの初期化：20体の個体
        self.boids = []
        for _ in range(20):
            boid = {
                "x": random.uniform(0, self.SCREEN_WIDTH),
                "y": random.uniform(0, self.SCREEN_HEIGHT),
                "vx": random.uniform(-1, 1),
                "vy": random.uniform(-1, 1),
            }
            self.boids.append(boid)

        # ライフゲームの初期化（グリッドサイズ32x32、各セルは0または1）
        self.life_width = 32
        self.life_height = 32
        self.life_grid = [[random.randint(0, 1) for _ in range(self.life_width)] for _ in range(self.life_height)]

        # アナログ入力とキーボード対応
        self.analog_inputs = [
            ("GAMEPAD1_AXIS_LEFTX", [pyxel.KEY_D, pyxel.KEY_A]),  # 回転制御
            ("GAMEPAD1_AXIS_LEFTY", [pyxel.KEY_S, pyxel.KEY_W]),  # スケール制御
            ("GAMEPAD1_AXIS_RIGHTX", [pyxel.KEY_RIGHT, pyxel.KEY_LEFT]),  # 速度
            ("GAMEPAD1_AXIS_RIGHTY", [pyxel.KEY_DOWN, pyxel.KEY_UP]),  # 強度
            ("GAMEPAD1_AXIS_TRIGGERLEFT", [pyxel.KEY_Q]),  # 複雑さ-
            ("GAMEPAD1_AXIS_TRIGGERRIGHT", [pyxel.KEY_E]),  # 複雑さ+
        ]

        # デジタル入力とキーボード対応
        self.digital_inputs = [
            ("GAMEPAD1_BUTTON_A", [pyxel.KEY_J]),  # ビート
            ("GAMEPAD1_BUTTON_B", [pyxel.KEY_K]),  # パターン変更
            ("GAMEPAD1_BUTTON_X", [pyxel.KEY_U]),  # サブパターン-
            ("GAMEPAD1_BUTTON_Y", [pyxel.KEY_I]),  # サブパターン+
            ("GAMEPAD1_BUTTON_LEFTSHOULDER", [pyxel.KEY_1]),  # 自動ビート-
            ("GAMEPAD1_BUTTON_RIGHTSHOULDER", [pyxel.KEY_2]),  # 自動ビート+
        ]

        pyxel.run(self.update, self.draw)

    def init_sound(self):
        """サウンドの初期化"""
        # ベース音
        pyxel.sounds[0].set("a2c3e3a3c4e4", "t", "7", "n", 30)
        # ビート音
        pyxel.sounds[1].set("c3", "p", "7", "n", 10)
        # アンビエント
        pyxel.sounds[2].set("f3a3c4f4", "s", "7", "f", 40)
        # ノイズ
        pyxel.sounds[3].set("c3", "n", "7", "f", 10)
        # BGMパターン（シンプルなループ）
        pyxel.musics[0].set([0], [], [], [])
        pyxel.musics[1].set([0, 1], [], [], [])
        pyxel.musics[2].set([0, 2], [], [], [])
        pyxel.musics[3].set([0, 3], [], [], [])

    def update(self):
        # 終了処理：STARTボタンまたはESCで終了
        if pyxel.btn(pyxel.GAMEPAD1_BUTTON_START) or pyxel.btn(pyxel.KEY_ESCAPE):
            pyxel.quit()

        # グリッチ効果のトグル（キーCで切替）
        if pyxel.btnp(pyxel.KEY_C):
            self.glitch = not self.glitch
            pyxel.play(1, 1)

        # 自動ビート更新
        self.auto_beat = (self.auto_beat + 1) % 30
        if self.auto_beat == 0:
            self.beat = True
            pyxel.play(1, 1)
        else:
            self.beat = False

        # パラメータ更新
        self.update_parameters()
        # パーティクル更新
        self.update_particles()
        # 軌跡更新
        self.update_trails()
        # 波動位相更新
        self.wave_phase += self.speed * 0.1
        # 色相更新
        self.color_phase = (self.color_phase + self.speed * 0.02) % 16
        # 回転更新（ゲームパッドまたはキーボード）
        self.rotation += self.get_analog_value("GAMEPAD1_AXIS_LEFTX", [pyxel.KEY_D, pyxel.KEY_A]) / 10000.0
        # スケール更新
        self.scale = max(
            0.1,
            min(
                2.0,
                self.scale + self.get_analog_value("GAMEPAD1_AXIS_LEFTY", [pyxel.KEY_S, pyxel.KEY_W]) / 50000.0,
            ),
        )

        # パターン変更（ボタンBまたはKキー）：パターンは0～7に拡張
        if self.is_button_pressed("GAMEPAD1_BUTTON_B", [pyxel.KEY_K]):
            self.pattern_type = (self.pattern_type + 1) % 8
            pyxel.play(2, 2)
            # BGMパターンも切替（musicsは4種類）
            pyxel.playm(self.pattern_type % 4)

        # サブパターン変更（キーUで-、キーIで+）
        if self.is_button_pressed("GAMEPAD1_BUTTON_X", [pyxel.KEY_U]):
            self.sub_pattern = (self.sub_pattern - 1) % 4
            pyxel.play(3, 3)
        if self.is_button_pressed("GAMEPAD1_BUTTON_Y", [pyxel.KEY_I]):
            self.sub_pattern = (self.sub_pattern + 1) % 4
            pyxel.play(3, 3)

        # ビート効果（ボタンAまたはJキー）
        if self.is_button_pressed("GAMEPAD1_BUTTON_A", [pyxel.KEY_J]):
            self.beat = True
            pyxel.play(1, 1)

        # 自動ビート速度変更
        if self.is_button_pressed("GAMEPAD1_BUTTON_LEFTSHOULDER", [pyxel.KEY_1]):
            self.speed = max(0.5, self.speed - 0.1)
        if self.is_button_pressed("GAMEPAD1_BUTTON_RIGHTSHOULDER", [pyxel.KEY_2]):
            self.speed = min(2.0, self.speed + 0.1)

        # 新規アルゴリズムの更新処理
        self.update_genetic_algorithm()
        self.update_reaction_diffusion()
        self.update_boids()
        self.update_game_of_life()
        self.update_sound()

    def update_parameters(self):
        """パラメータの更新"""
        self.speed = max(
            0.5,
            min(
                2.0,
                self.speed + self.get_analog_value("GAMEPAD1_AXIS_RIGHTX", [pyxel.KEY_RIGHT, pyxel.KEY_LEFT]) / 50000.0,
            ),
        )
        self.intensity = max(
            0.1,
            min(
                2.0,
                self.intensity + self.get_analog_value("GAMEPAD1_AXIS_RIGHTY", [pyxel.KEY_DOWN, pyxel.KEY_UP]) / 50000.0,
            ),
        )
        trigger_left = self.get_analog_value("GAMEPAD1_AXIS_TRIGGERLEFT", [pyxel.KEY_Q])
        trigger_right = self.get_analog_value("GAMEPAD1_AXIS_TRIGGERRIGHT", [pyxel.KEY_E])
        self.complexity = max(
            0.1,
            min(
                2.0,
                self.complexity + (trigger_right - trigger_left) / 50000.0,
            ),
        )

    def update_particles(self):
        """パーティクルの更新"""
        if random.random() < self.intensity * 0.1:
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 3) * self.speed
            self.particles.append(
                {
                    "x": self.SCREEN_WIDTH // 2,
                    "y": self.SCREEN_HEIGHT // 2,
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": 60,
                    "color": int(self.color_phase),
                }
            )
        new_particles = []
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
            if p["life"] > 0:
                new_particles.append(p)
        self.particles = new_particles

    def update_trails(self):
        """軌跡の更新"""
        t = pyxel.frame_count * self.speed
        x = self.SCREEN_WIDTH // 2 + math.cos(t * 0.1) * 50
        y = self.SCREEN_HEIGHT // 2 + math.sin(t * 0.1) * 50
        self.trails.append((x, y))

    def update_genetic_algorithm(self):
        """GAによるパラメータ進化の更新（300フレーム毎に評価・交叉）"""
        self.ga_timer += 1
        if self.ga_timer >= 300:
            for ind in self.ga_population:
                ind["fitness"] = ind["speed"] + ind["intensity"] + ind["complexity"]
            best = max(self.ga_population, key=lambda ind: ind["fitness"])
            self.speed = best["speed"]
            self.intensity = best["intensity"]
            self.complexity = best["complexity"]
            parent1 = random.choice(self.ga_population)
            parent2 = random.choice(self.ga_population)
            child = {
                "speed": (parent1["speed"] + parent2["speed"]) / 2 * random.uniform(0.95, 1.05),
                "intensity": (parent1["intensity"] + parent2["intensity"]) / 2 * random.uniform(0.95, 1.05),
                "complexity": (parent1["complexity"] + parent2["complexity"]) / 2 * random.uniform(0.95, 1.05),
            }
            self.ga_population.append(child)
            if len(self.ga_population) > 10:
                self.ga_population.pop(0)
            self.ga_timer = 0

    def update_reaction_diffusion(self):
        """反応拡散シミュレーション（Gray-Scottモデル）"""
        Du = 0.16
        Dv = 0.08
        F = 0.035
        k = 0.065
        newU = [[self.rd_U[i][j] for j in range(self.rd_grid_size_x)] for i in range(self.rd_grid_size_y)]
        newV = [[self.rd_V[i][j] for j in range(self.rd_grid_size_x)] for i in range(self.rd_grid_size_y)]
        for i in range(1, self.rd_grid_size_y - 1):
            for j in range(1, self.rd_grid_size_x - 1):
                lapU = (
                    self.rd_U[i + 1][j] + self.rd_U[i - 1][j] + self.rd_U[i][j + 1] + self.rd_U[i][j - 1] - 4 * self.rd_U[i][j]
                )
                lapV = (
                    self.rd_V[i + 1][j] + self.rd_V[i - 1][j] + self.rd_V[i][j + 1] + self.rd_V[i][j - 1] - 4 * self.rd_V[i][j]
                )
                newU[i][j] = (
                    self.rd_U[i][j]
                    + (Du * lapU - self.rd_U[i][j] * self.rd_V[i][j] * self.rd_V[i][j] + F * (1 - self.rd_U[i][j])) * 0.2
                )
                newV[i][j] = (
                    self.rd_V[i][j]
                    + (Dv * lapV + self.rd_U[i][j] * self.rd_V[i][j] * self.rd_V[i][j] - (F + k) * self.rd_V[i][j]) * 0.2
                )
        self.rd_U = newU
        self.rd_V = newV

    def update_boids(self):
        """Boidsシミュレーションの更新"""
        alignment_weight = 0.05
        cohesion_weight = 0.01
        separation_weight = 0.1
        perception_radius = 30
        max_speed = 2
        for boid in self.boids:
            vx_align = 0
            vy_align = 0
            x_cohesion = 0
            y_cohesion = 0
            x_separation = 0
            y_separation = 0
            count = 0
            for other in self.boids:
                if other is boid:
                    continue
                dx = other["x"] - boid["x"]
                dy = other["y"] - boid["y"]
                distance = math.sqrt(dx * dx + dy * dy)
                if distance < perception_radius:
                    vx_align += other["vx"]
                    vy_align += other["vy"]
                    x_cohesion += other["x"]
                    y_cohesion += other["y"]
                    if distance < 10:
                        x_separation -= dx
                        y_separation -= dy
                    count += 1
            if count > 0:
                vx_align /= count
                vy_align /= count
                x_cohesion /= count
                y_cohesion /= count
                boid["vx"] += (vx_align - boid["vx"]) * alignment_weight
                boid["vy"] += (vy_align - boid["vy"]) * alignment_weight
                boid["vx"] += (x_cohesion - boid["x"]) * cohesion_weight
                boid["vy"] += (y_cohesion - boid["y"]) * cohesion_weight
                boid["vx"] += x_separation * separation_weight
                boid["vy"] += y_separation * separation_weight
            speed = math.sqrt(boid["vx"] ** 2 + boid["vy"] ** 2)
            if speed > max_speed:
                boid["vx"] = (boid["vx"] / speed) * max_speed
                boid["vy"] = (boid["vy"] / speed) * max_speed
            boid["x"] = (boid["x"] + boid["vx"]) % self.SCREEN_WIDTH
            boid["y"] = (boid["y"] + boid["vy"]) % self.SCREEN_HEIGHT

    def update_game_of_life(self):
        """ライフゲームの更新（Conway's Game of Life）"""
        new_grid = [[0 for _ in range(self.life_width)] for _ in range(self.life_height)]
        for i in range(self.life_height):
            for j in range(self.life_width):
                count = 0
                for di in (-1, 0, 1):
                    for dj in (-1, 0, 1):
                        if di == 0 and dj == 0:
                            continue
                        ni = (i + di) % self.life_height
                        nj = (j + dj) % self.life_width
                        count += self.life_grid[ni][nj]
                if self.life_grid[i][j] == 1:
                    if count == 2 or count == 3:
                        new_grid[i][j] = 1
                    else:
                        new_grid[i][j] = 0
                else:
                    if count == 3:
                        new_grid[i][j] = 1
                    else:
                        new_grid[i][j] = 0
        self.life_grid = new_grid

    def update_sound(self):
        """派手なサウンドをパターンに合わせて連続再生"""
        self.sound_timer += 1
        if self.sound_timer >= 20:
            pyxel.playm(self.pattern_type % 4)
            self.sound_timer = 0

    def get_analog_value(self, input_name, keyboard_keys):
        """アナログ入力値の取得"""
        value = pyxel.btnv(getattr(pyxel, input_name))
        if len(keyboard_keys) == 2:
            if pyxel.btn(keyboard_keys[0]):
                value = 32767
            elif pyxel.btn(keyboard_keys[1]):
                value = -32768
        elif len(keyboard_keys) == 1:
            if pyxel.btn(keyboard_keys[0]):
                value = 32767
        return value

    def is_button_pressed(self, input_name, keyboard_keys):
        """ボタンの押下状態を取得"""
        return pyxel.btn(getattr(pyxel, input_name)) or any(pyxel.btn(key) for key in keyboard_keys)

    def draw(self):
        pyxel.cls(0)
        center_x = self.SCREEN_WIDTH // 2
        center_y = self.SCREEN_HEIGHT // 2
        beat_scale = 1.2 if self.beat else 1.0
        if self.pattern_type == 0:
            self.draw_fractal(center_x, center_y, beat_scale)
        elif self.pattern_type == 1:
            self.draw_particles(center_x, center_y, beat_scale)
        elif self.pattern_type == 2:
            self.draw_wave(center_x, center_y, beat_scale)
        elif self.pattern_type == 3:
            self.draw_geometric(center_x, center_y, beat_scale)
        elif self.pattern_type == 4:
            self.draw_glitch_pattern(center_x, center_y, beat_scale)
        elif self.pattern_type == 5:
            self.draw_reaction_diffusion()
        elif self.pattern_type == 6:
            self.draw_boids()
        elif self.pattern_type == 7:
            self.draw_game_of_life()
        else:
            self.draw_glitch_pattern(center_x, center_y, beat_scale)
        if self.glitch:
            self.draw_glitch()

    def draw_fractal(self, x, y, beat_scale):
        """フラクタルパターンの描画"""

        def draw_recursive(x, y, size, depth):
            if depth <= 0 or size < 2:
                return
            color = (int(self.color_phase) + depth) % 16
            if self.sub_pattern == 0:
                pyxel.circb(x, y, size, color)
                for i in range(6):
                    angle = self.rotation + i * math.pi / 3
                    nx = x + math.cos(angle) * size
                    ny = y + math.sin(angle) * size
                    draw_recursive(nx, ny, size * 0.5, depth - 1)
            elif self.sub_pattern == 1:
                size_half = size * 0.5
                points = []
                for i in range(3):
                    angle = self.rotation + i * math.pi * 2 / 3
                    px = x + math.cos(angle) * size
                    py = y + math.sin(angle) * size
                    points.append((px, py))
                for i in range(3):
                    p1 = points[i]
                    p2 = points[(i + 1) % 3]
                    pyxel.line(p1[0], p1[1], p2[0], p2[1], color)
                for px, py in points:
                    draw_recursive(px, py, size_half, depth - 1)
            elif self.sub_pattern == 2:
                size_half = size * 0.5
                pyxel.rectb(x - size_half, y - size_half, size, size, color)
                for i in range(4):
                    angle = self.rotation + i * math.pi / 2
                    nx = x + math.cos(angle) * size_half
                    ny = y + math.sin(angle) * size_half
                    draw_recursive(nx, ny, size * 0.5, depth - 1)
            else:
                points = []
                for i in range(5):
                    angle = self.rotation + i * math.pi * 2 / 5
                    px = x + math.cos(angle) * size
                    py = y + math.sin(angle) * size
                    points.append((px, py))
                for i in range(5):
                    p1 = points[i]
                    p2 = points[(i + 2) % 5]
                    pyxel.line(p1[0], p1[1], p2[0], p2[1], color)
                for px, py in points:
                    draw_recursive(px, py, size * 0.4, depth - 1)

        depth = int(self.complexity * 4)
        size = 80 * self.scale * beat_scale
        draw_recursive(x, y, size, depth)

    def draw_particles(self, x, y, beat_scale):
        """パーティクルパターンの描画"""
        t = pyxel.frame_count * self.speed
        if self.sub_pattern == 0:
            for p in self.particles:
                pyxel.pset(p["x"], p["y"], p["color"])
        elif self.sub_pattern == 1:
            points = list(self.trails)
            if len(points) > 1:
                for i in range(len(points) - 1):
                    p1 = points[i]
                    p2 = points[i + 1]
                    color = (int(self.color_phase) + i // 4) % 16
                    pyxel.line(p1[0], p1[1], p2[0], p2[1], color)
        elif self.sub_pattern == 2:
            for i in range(int(32 * self.complexity)):
                angle = self.rotation + i * 0.2 + t * 0.05
                r = i * 2 * self.scale * beat_scale
                px = x + math.cos(angle) * r
                py = y + math.sin(angle) * r
                color = (int(self.color_phase) + i // 4) % 16
                pyxel.pset(px, py, color)
        else:
            for i in range(int(50 * self.complexity)):
                angle = self.rotation + i * math.pi * 2 / (50 * self.complexity)
                r = 40 * self.scale * beat_scale * (1 + math.sin(t * 0.1))
                px = x + math.cos(angle) * r
                py = y + math.sin(angle) * r
                color = (int(self.color_phase) + i // 8) % 16
                pyxel.pset(px, py, color)

    def draw_wave(self, x, y, beat_scale):
        """波形パターンの描画"""
        if self.sub_pattern == 0:
            points = []
            for i in range(256):
                angle = i * math.pi / 32 + self.wave_phase
                r = 80 * self.scale * beat_scale
                px = i
                py = y + math.sin(angle) * r * self.intensity
                points.append((px, py))
            for i in range(len(points) - 1):
                p1 = points[i]
                p2 = points[i + 1]
                color = (int(self.color_phase) + i // 16) % 16
                pyxel.line(p1[0], p1[1], p2[0], p2[1], color)
        elif self.sub_pattern == 1:
            for r in range(0, int(100 * self.scale * beat_scale), 10):
                points = []
                num_points = int(16 * self.complexity)
                for i in range(num_points):
                    angle = i * math.pi * 2 / num_points + self.wave_phase
                    wave = math.sin(angle * 8) * 10 * self.intensity
                    px = x + math.cos(angle) * (r + wave)
                    py = y + math.sin(angle) * (r + wave)
                    points.append((px, py))
                for i in range(len(points)):
                    p1 = points[i]
                    p2 = points[(i + 1) % len(points)]
                    color = (int(self.color_phase) + r // 10) % 16
                    pyxel.line(p1[0], p1[1], p2[0], p2[1], color)
        elif self.sub_pattern == 2:
            points = []
            for i in range(int(100 * self.complexity)):
                t_val = i * 0.1 + self.wave_phase
                px = x + math.sin(t_val * 2) * 80 * self.scale * beat_scale
                py = y + math.sin(t_val * 3) * 80 * self.scale * beat_scale
                points.append((px, py))
            for i in range(len(points) - 1):
                p1 = points[i]
                p2 = points[i + 1]
                color = (int(self.color_phase) + i // 8) % 16
                pyxel.line(p1[0], p1[1], p2[0], p2[1], color)
        else:
            points = []
            for i in range(256):
                px = i
                py = y + (pyxel.noise(i * 0.05 + self.wave_phase, 0) * 2 - 1) * 80 * self.scale * beat_scale * self.intensity
                points.append((px, py))
            for i in range(len(points) - 1):
                p1 = points[i]
                p2 = points[i + 1]
                color = (int(self.color_phase) + i // 16) % 16
                pyxel.line(p1[0], p1[1], p2[0], p2[1], color)

    def draw_geometric(self, x, y, beat_scale):
        """幾何学パターンの描画"""
        t = pyxel.frame_count * self.speed
        if self.sub_pattern == 0:
            num_lines = int(16 * self.complexity)
            for i in range(num_lines):
                angle = self.rotation + i * math.pi / num_lines
                r = 100 * self.scale * beat_scale
                x1 = x + math.cos(angle) * r
                y1 = y + math.sin(angle) * r
                x2 = x + math.cos(angle + math.pi) * r
                y2 = y + math.sin(angle + math.pi) * r
                color = (int(self.color_phase) + i) % 16
                pyxel.line(x1, y1, x2, y2, color)
        elif self.sub_pattern == 1:
            points = []
            num_points = int(100 * self.complexity)
            for i in range(num_points):
                angle = self.rotation + i * 0.2
                r = i * 0.5 * self.scale * beat_scale
                px = x + math.cos(angle) * r
                py = y + math.sin(angle) * r
                points.append((px, py))
            for i in range(len(points) - 1):
                p1 = points[i]
                p2 = points[i + 1]
                color = (int(self.color_phase) + i // 8) % 16
                pyxel.line(p1[0], p1[1], p2[0], p2[1], color)
        elif self.sub_pattern == 2:
            num_vertices = int(3 + self.complexity * 5)
            points = []
            for i in range(num_vertices):
                angle = self.rotation + i * math.pi * 2 / num_vertices
                r = 80 * self.scale * beat_scale
                px = x + math.cos(angle) * r
                py = y + math.sin(angle) * r
                points.append((px, py))
            for i in range(num_vertices):
                for j in range(i + 1, num_vertices):
                    color = (int(self.color_phase) + (i + j)) % 16
                    pyxel.line(points[i][0], points[i][1], points[j][0], points[j][1], color)
        else:
            size = 100 * self.scale * beat_scale
            for i in range(int(8 * self.complexity)):
                angle = self.rotation + i * math.pi / 8
                dx = math.cos(angle) * i * 5
                dy = math.sin(angle) * i * 5
                color = (int(self.color_phase) + i) % 16
                pyxel.circb(x + dx, y + dy, size - i * 5, color)

    def draw_glitch_pattern(self, x, y, beat_scale):
        """グリッチパターンの描画"""
        for _ in range(10):
            x0 = random.randint(0, self.SCREEN_WIDTH)
            y0 = random.randint(0, self.SCREEN_HEIGHT)
            x1 = random.randint(0, self.SCREEN_WIDTH)
            y1 = random.randint(0, self.SCREEN_HEIGHT)
            color = random.randint(8, 15)
            pyxel.line(x0, y0, x1, y1, color)

    def draw_glitch(self):
        """グリッチ効果の描画"""
        for i in range(5):
            x0 = random.randint(0, self.SCREEN_WIDTH)
            y0 = random.randint(0, self.SCREEN_HEIGHT)
            x1 = random.randint(0, self.SCREEN_WIDTH)
            y1 = random.randint(0, self.SCREEN_HEIGHT)
            color = random.randint(8, 15)
            pyxel.line(x0, y0, x1, y1, color)

    def draw_reaction_diffusion(self):
        """反応拡散シミュレーションの描画"""
        cell_w = self.SCREEN_WIDTH / self.rd_grid_size_x
        cell_h = self.SCREEN_HEIGHT / self.rd_grid_size_y
        for i in range(self.rd_grid_size_y):
            for j in range(self.rd_grid_size_x):
                val = self.rd_U[i][j] - self.rd_V[i][j]
                col = int((val + 1) * 7.5) % 16
                x0 = int(j * cell_w)
                y0 = int(i * cell_h)
                x1 = int((j + 1) * cell_w)
                y1 = int((i + 1) * cell_h)
                pyxel.rect(x0, y0, x1 - x0, y1 - y0, col)

    def draw_boids(self):
        """Boidsの描画"""
        for boid in self.boids:
            angle = math.atan2(boid["vy"], boid["vx"])
            size = 4
            x = boid["x"]
            y = boid["y"]
            p1 = (x + math.cos(angle) * size, y + math.sin(angle) * size)
            p2 = (x + math.cos(angle + 2.5) * size, y + math.sin(angle + 2.5) * size)
            p3 = (x + math.cos(angle - 2.5) * size, y + math.sin(angle - 2.5) * size)
            pyxel.tri(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1], (int(self.color_phase)) % 16)

    def draw_game_of_life(self):
        """ライフゲームの描画"""
        cell_w = self.SCREEN_WIDTH / self.life_width
        cell_h = self.SCREEN_HEIGHT / self.life_height
        for i in range(self.life_height):
            for j in range(self.life_width):
                if self.life_grid[i][j] == 1:
                    x0 = int(j * cell_w)
                    y0 = int(i * cell_h)
                    pyxel.rect(x0, y0, int(cell_w), int(cell_h), (int(self.color_phase) + i + j) % 16)


if __name__ == "__main__":
    EnhancedVJ()

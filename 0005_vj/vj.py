# title: Enhanced VJ
# author: karaage
# desc: Enhanced Pyxel VJ app with glitch effect
# site: https://github.com/karaage0703/pyxel-examples
# license: MIT
# version: 1.0

import pyxel
import math
import random
from collections import deque


class EnhancedVJ:
    def __init__(self):
        self.SCREEN_WIDTH = 256
        self.SCREEN_HEIGHT = 256
        pyxel.init(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

        # パターンの状態
        self.pattern_type = 0  # パターンの種類
        self.sub_pattern = 0  # サブパターン
        self.rotation = 0  # 回転角度
        self.scale = 1.0  # スケール
        self.color_phase = 0  # 色相
        self.wave_phase = 0  # 波動位相
        self.particles = []  # パーティクル
        self.trails = deque(maxlen=32)  # 軌跡
        self.beat = False  # ビート状態
        self.auto_beat = 0  # 自動ビート

        # パラメータ
        self.speed = 1.0  # 速度
        self.intensity = 1.0  # 強度
        self.complexity = 1.0  # 複雑さ

        # グリッチ効果の初期状態
        self.glitch = False

        # サウンドの初期化
        self.init_sound()

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

        # BGMパターン
        pyxel.musics[0].set([0], [], [], [])
        pyxel.musics[1].set([0, 1], [], [], [])
        pyxel.musics[2].set([0, 2], [], [], [])
        pyxel.musics[3].set([0, 3], [], [], [])

    def update(self):
        # STARTボタンまたはESCキーで終了
        if pyxel.btn(pyxel.GAMEPAD1_BUTTON_START) or pyxel.btn(pyxel.KEY_ESCAPE):
            pyxel.quit()

        # グリッチ効果のトグル切り替え（キーCを押す）
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

        # 回転更新
        self.rotation += self.get_analog_value("GAMEPAD1_AXIS_LEFTX", [pyxel.KEY_D, pyxel.KEY_A]) / 10000.0

        # スケール更新
        self.scale = max(
            0.1,
            min(
                2.0,
                self.scale + self.get_analog_value("GAMEPAD1_AXIS_LEFTY", [pyxel.KEY_S, pyxel.KEY_W]) / 50000.0,
            ),
        )

        # パターン変更
        if self.is_button_pressed("GAMEPAD1_BUTTON_B", [pyxel.KEY_K]):
            self.pattern_type = (self.pattern_type + 1) % 5  # 4種類から5種類へ（新パターン追加）
            pyxel.play(2, 2)
            pyxel.playm(self.pattern_type)

        # サブパターン変更
        if self.is_button_pressed("GAMEPAD1_BUTTON_X", [pyxel.KEY_U]):
            self.sub_pattern = (self.sub_pattern - 1) % 4
            pyxel.play(3, 3)
        if self.is_button_pressed("GAMEPAD1_BUTTON_Y", [pyxel.KEY_I]):
            self.sub_pattern = (self.sub_pattern + 1) % 4
            pyxel.play(3, 3)

        # ビート効果
        if self.is_button_pressed("GAMEPAD1_BUTTON_A", [pyxel.KEY_J]):
            self.beat = True
            pyxel.play(1, 1)

        # 自動ビート速度変更
        if self.is_button_pressed("GAMEPAD1_BUTTON_LEFTSHOULDER", [pyxel.KEY_1]):
            self.speed = max(0.5, self.speed - 0.1)
        if self.is_button_pressed("GAMEPAD1_BUTTON_RIGHTSHOULDER", [pyxel.KEY_2]):
            self.speed = min(2.0, self.speed + 0.1)

    def update_parameters(self):
        """パラメータの更新"""
        # 速度
        self.speed = max(
            0.5,
            min(
                2.0,
                self.speed + self.get_analog_value("GAMEPAD1_AXIS_RIGHTX", [pyxel.KEY_RIGHT, pyxel.KEY_LEFT]) / 50000.0,
            ),
        )
        # 強度
        self.intensity = max(
            0.1,
            min(
                2.0,
                self.intensity + self.get_analog_value("GAMEPAD1_AXIS_RIGHTY", [pyxel.KEY_DOWN, pyxel.KEY_UP]) / 50000.0,
            ),
        )
        # 複雑さ
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
        # 新しいパーティクルの生成
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
        # パーティクルの移動と寿命管理
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
        # 画面中心座標
        center_x = self.SCREEN_WIDTH // 2
        center_y = self.SCREEN_HEIGHT // 2

        # ビート効果
        beat_scale = 1.2 if self.beat else 1.0

        # パターンの描画
        if self.pattern_type == 0:
            # フラクタルパターン
            self.draw_fractal(center_x, center_y, beat_scale)
        elif self.pattern_type == 1:
            # パーティクルパターン
            self.draw_particles(center_x, center_y, beat_scale)
        elif self.pattern_type == 2:
            # 波形パターン
            self.draw_wave(center_x, center_y, beat_scale)
        elif self.pattern_type == 3:
            # 幾何学パターン
            self.draw_geometric(center_x, center_y, beat_scale)
        else:
            # 新規パターン：グリッチパターン
            self.draw_glitch_pattern(center_x, center_y, beat_scale)

        # グリッチ効果の描画（切り替えにより表示）
        if self.glitch:
            self.draw_glitch()

    def draw_fractal(self, x, y, beat_scale):
        """フラクタルパターンの描画"""

        def draw_recursive(x, y, size, depth):
            if depth <= 0 or size < 2:
                return
            color = (int(self.color_phase) + depth) % 16
            if self.sub_pattern == 0:
                # 円フラクタル
                pyxel.circb(x, y, size, color)
                for i in range(6):
                    angle = self.rotation + i * math.pi / 3
                    nx = x + math.cos(angle) * size
                    ny = y + math.sin(angle) * size
                    draw_recursive(nx, ny, size * 0.5, depth - 1)
            elif self.sub_pattern == 1:
                # 三角フラクタル
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
                # 四角フラクタル
                size_half = size * 0.5
                pyxel.rectb(x - size_half, y - size_half, size, size, color)
                for i in range(4):
                    angle = self.rotation + i * math.pi / 2
                    nx = x + math.cos(angle) * size_half
                    ny = y + math.sin(angle) * size_half
                    draw_recursive(nx, ny, size * 0.5, depth - 1)
            else:
                # 星フラクタル
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
            # 通常パーティクル
            for p in self.particles:
                pyxel.pset(p["x"], p["y"], p["color"])
        elif self.sub_pattern == 1:
            # 軌跡パーティクル
            points = list(self.trails)
            if len(points) > 1:
                for i in range(len(points) - 1):
                    p1 = points[i]
                    p2 = points[i + 1]
                    color = (int(self.color_phase) + i // 4) % 16
                    pyxel.line(p1[0], p1[1], p2[0], p2[1], color)
        elif self.sub_pattern == 2:
            # 渦巻きパーティクル
            for i in range(int(32 * self.complexity)):
                angle = self.rotation + i * 0.2 + t * 0.05
                r = i * 2 * self.scale * beat_scale
                px = x + math.cos(angle) * r
                py = y + math.sin(angle) * r
                color = (int(self.color_phase) + i // 4) % 16
                pyxel.pset(px, py, color)
        else:
            # 爆発パーティクル
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
            # サイン波
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
            # 円形波
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
            # リサージュ波形
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
            # ノイズ波形
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
            # 万華鏡
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
            # 螺旋
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
            # 多角形
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
            # モアレ
            size = 100 * self.scale * beat_scale
            for i in range(int(8 * self.complexity)):
                angle = self.rotation + i * math.pi / 8
                dx = math.cos(angle) * i * 5
                dy = math.sin(angle) * i * 5
                color = (int(self.color_phase) + i) % 16
                pyxel.circb(x + dx, y + dy, size - i * 5, color)

    def draw_glitch_pattern(self, x, y, beat_scale):
        """新規パターン：グリッチパターンの描画"""
        # ランダムな線を画面に多数描画してグリッチ風の効果を出す
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


if __name__ == "__main__":
    EnhancedVJ()

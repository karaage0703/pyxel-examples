# title: vj
# author: karaage
# desc: A Pyxel simple vj app
# site: https://github.com/karaage0703/pyxel-examples
# license: MIT
# version: 1.0

import pyxel
import math


class VJSimple:
    def __init__(self):
        self.SCREEN_WIDTH = 512
        self.SCREEN_HEIGHT = 512
        pyxel.init(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)

        # サウンドの初期化
        self.init_sound()

        # パターンの状態
        self.pattern_type = 0  # パターンの種類
        self.rotation = 0  # 回転角度
        self.scale = 1.0  # スケール
        self.color = 7  # 色
        self.beat = False  # ビート状態

        # アナログ入力とキーボード対応
        self.analog_inputs = [
            ("GAMEPAD1_AXIS_LEFTX", [pyxel.KEY_D, pyxel.KEY_A]),  # 回転制御
            ("GAMEPAD1_AXIS_LEFTY", [pyxel.KEY_S, pyxel.KEY_W]),  # スケール制御
            ("GAMEPAD1_AXIS_RIGHTX", [pyxel.KEY_RIGHT, pyxel.KEY_LEFT]),  # 色変更
            ("GAMEPAD1_AXIS_RIGHTY", [pyxel.KEY_DOWN, pyxel.KEY_UP]),  # パターン変更
        ]

        # デジタル入力とキーボード対応
        self.digital_inputs = [
            ("GAMEPAD1_BUTTON_A", [pyxel.KEY_J]),  # ビート効果
            ("GAMEPAD1_BUTTON_B", [pyxel.KEY_K]),  # サウンド1
            ("GAMEPAD1_BUTTON_X", [pyxel.KEY_U]),  # サウンド2
            ("GAMEPAD1_BUTTON_Y", [pyxel.KEY_I]),  # サウンド3
        ]

        pyxel.run(self.update, self.draw)

    def init_sound(self):
        """サウンドの初期化"""
        # ビート音
        pyxel.sound(0).set("c3", "p", "7", "n", 10)
        # メロディ1
        pyxel.sound(1).set("c3e3g3c4", "p", "7", "n", 20)
        # メロディ2
        pyxel.sound(2).set("f3a3c4f4", "p", "7", "n", 20)
        # メロディ3
        pyxel.sound(3).set("g3b3d4g4", "p", "7", "n", 20)

    def update(self):
        # STARTボタンまたはESCキーで終了
        if pyxel.btn(pyxel.GAMEPAD1_BUTTON_START) or pyxel.btn(pyxel.KEY_ESCAPE):
            pyxel.quit()

        # 左スティックX: 回転
        self.rotation += (
            self.get_analog_value("GAMEPAD1_AXIS_LEFTX", [pyxel.KEY_D, pyxel.KEY_A])
            / 10000.0
        )

        # 左スティックY: スケール
        self.scale = max(
            0.1,
            min(
                2.0,
                self.scale
                + self.get_analog_value(
                    "GAMEPAD1_AXIS_LEFTY", [pyxel.KEY_S, pyxel.KEY_W]
                )
                / 50000.0,
            ),
        )

        # 右スティックX: 色
        self.color = (
            self.color
            + int(
                self.get_analog_value(
                    "GAMEPAD1_AXIS_RIGHTX", [pyxel.KEY_RIGHT, pyxel.KEY_LEFT]
                )
                / 10000.0
            )
        ) % 16

        # 右スティックY: パターン
        self.pattern_type = (
            self.pattern_type
            + int(
                self.get_analog_value(
                    "GAMEPAD1_AXIS_RIGHTY", [pyxel.KEY_DOWN, pyxel.KEY_UP]
                )
                / 10000.0
            )
        ) % 4

        # ボタン入力の処理
        if self.is_button_pressed("GAMEPAD1_BUTTON_A", [pyxel.KEY_J]):
            self.beat = True
            pyxel.play(0, 0)
        else:
            self.beat = False

        if self.is_button_pressed("GAMEPAD1_BUTTON_B", [pyxel.KEY_K]):
            pyxel.play(1, 1)
        if self.is_button_pressed("GAMEPAD1_BUTTON_X", [pyxel.KEY_U]):
            pyxel.play(2, 2)
        if self.is_button_pressed("GAMEPAD1_BUTTON_Y", [pyxel.KEY_I]):
            pyxel.play(3, 3)

    def get_analog_value(self, input_name, keyboard_keys):
        """アナログ入力値の取得"""
        value = pyxel.btnv(getattr(pyxel, input_name))

        if len(keyboard_keys) == 2:
            if pyxel.btn(keyboard_keys[0]):
                value = 32767
            elif pyxel.btn(keyboard_keys[1]):
                value = -32768

        return value

    def is_button_pressed(self, input_name, keyboard_keys):
        """ボタンの押下状態を取得"""
        return pyxel.btn(getattr(pyxel, input_name)) or any(
            pyxel.btn(key) for key in keyboard_keys
        )

    def draw(self):
        pyxel.cls(0)

        # 画面中心座標
        center_x = self.SCREEN_WIDTH // 2
        center_y = self.SCREEN_HEIGHT // 2

        # ビート効果
        beat_scale = 1.2 if self.beat else 1.0

        # パターンの描画
        if self.pattern_type == 0:
            # 回転する星
            self.draw_star(
                center_x, center_y, self.rotation, self.scale * beat_scale, self.color
            )
        elif self.pattern_type == 1:
            # 同心円
            self.draw_circles(
                center_x, center_y, self.rotation, self.scale * beat_scale, self.color
            )
        elif self.pattern_type == 2:
            # スパイラル
            self.draw_spiral(
                center_x, center_y, self.rotation, self.scale * beat_scale, self.color
            )
        else:
            # 波紋
            self.draw_ripple(
                center_x, center_y, self.rotation, self.scale * beat_scale, self.color
            )

    def draw_star(self, x, y, rotation, scale, color):
        """星型のパターンを描画"""
        points = []
        num_points = 5
        for i in range(num_points * 2):
            angle = rotation + i * math.pi / num_points
            r = 100 * scale * (0.5 if i % 2 else 1.0)
            px = x + math.cos(angle) * r
            py = y + math.sin(angle) * r
            points.append((px, py))

        for i in range(num_points * 2):
            p1 = points[i]
            p2 = points[(i + 1) % (num_points * 2)]
            pyxel.line(p1[0], p1[1], p2[0], p2[1], color)

    def draw_circles(self, x, y, rotation, scale, color):
        """同心円のパターンを描画"""
        num_circles = 8
        for i in range(num_circles):
            r = (i + 1) * 20 * scale
            steps = 32
            points = []
            for j in range(steps):
                angle = rotation + j * math.pi * 2 / steps
                px = x + math.cos(angle) * r
                py = y + math.sin(angle) * r
                points.append((px, py))

            for j in range(steps):
                p1 = points[j]
                p2 = points[(j + 1) % steps]
                pyxel.line(p1[0], p1[1], p2[0], p2[1], (color + i) % 16)

    def draw_spiral(self, x, y, rotation, scale, color):
        """スパイラルパターンを描画"""
        points = []
        steps = 100
        for i in range(steps):
            angle = rotation + i * math.pi / 8
            r = i * 2 * scale
            px = x + math.cos(angle) * r
            py = y + math.sin(angle) * r
            points.append((px, py))

        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]
            pyxel.line(p1[0], p1[1], p2[0], p2[1], (color + i // 10) % 16)

    def draw_ripple(self, x, y, rotation, scale, color):
        """波紋パターンを描画"""
        num_rings = 5
        for i in range(num_rings):
            r = (i + 1) * 30 * scale
            steps = 32
            points = []
            wave_height = math.sin(rotation + i * 0.5) * 10 * scale

            for j in range(steps):
                angle = j * math.pi * 2 / steps
                wave = math.sin(angle * 8 + rotation) * wave_height
                px = x + math.cos(angle) * (r + wave)
                py = y + math.sin(angle) * (r + wave)
                points.append((px, py))

            for j in range(steps):
                p1 = points[j]
                p2 = points[(j + 1) % steps]
                pyxel.line(p1[0], p1[1], p2[0], p2[1], (color + i) % 16)


if __name__ == "__main__":
    VJSimple()

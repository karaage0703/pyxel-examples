import pyxel
import math


class App:
    def __init__(self):
        self.width = 320
        self.height = 320
        pyxel.init(self.width, self.height)

        # シミュレーション用の時間変数
        self.time = 0
        # 地球の自転角度
        self.earth_rot = 0.0

        # 太陽のパラメータ
        self.sun = {
            "size": 8,
            "color": 10,  # 黄色
        }

        # 各惑星のパラメータ: 「name」, 軌道半径「orbit」, 公転速度「speed」, 惑星サイズ「size」, 色「color」
        self.planets = [
            {"name": "Mercury", "orbit": 20, "speed": 0.06, "size": 2, "color": 5},
            {"name": "Venus", "orbit": 30, "speed": 0.045, "size": 3, "color": 9},
            {"name": "Earth", "orbit": 40, "speed": 0.03, "size": 3, "color": 14},
            {"name": "Mars", "orbit": 50, "speed": 0.024, "size": 2, "color": 8},
            {"name": "Jupiter", "orbit": 70, "speed": 0.018, "size": 6, "color": 7},
            {"name": "Saturn", "orbit": 90, "speed": 0.015, "size": 5, "color": 11},
            {"name": "Uranus", "orbit": 110, "speed": 0.012, "size": 4, "color": 13},
            {"name": "Neptune", "orbit": 130, "speed": 0.009, "size": 4, "color": 2},
        ]

        pyxel.run(self.update, self.draw)

    def update(self):
        # GAMEPAD1_BUTTON_START または ESCキーで終了
        if pyxel.btn(pyxel.GAMEPAD1_BUTTON_START) or pyxel.btn(pyxel.KEY_ESCAPE):
            pyxel.quit()
        # 右アナログスティックX軸でシミュレーション速度を制御(初期値は1)
        analog_speed = pyxel.btnv(pyxel.GAMEPAD1_AXIS_RIGHTX)
        norm_speed = analog_speed / 32768
        self.time += 1 + norm_speed
        # 左アナログスティックX軸で地球の自転角度を制御（基本0.2ラジアンに調整分＋0.2)
        analog_rot = pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX)
        norm_rot = analog_rot / 32768
        self.earth_rot = (self.earth_rot + (0.2 + norm_rot * 0.2)) % (2 * math.pi)

    def draw(self):
        pyxel.cls(0)

        cx = self.width // 2
        cy = self.height // 2

        # 各惑星の軌道を描画（白色の円）
        for planet in self.planets:
            pyxel.circb(cx, cy, planet["orbit"], 7)

        # 太陽を描画
        pyxel.circ(cx, cy, self.sun["size"], self.sun["color"])

        # 各惑星を描画
        for planet in self.planets:
            angle = self.time * planet["speed"]
            px = cx + planet["orbit"] * math.cos(angle)
            py = cy + planet["orbit"] * math.sin(angle)
            pyxel.circ(int(px), int(py), planet["size"], planet["color"])

            # 地球の場合は自転を示すインジケータを追加
            if planet["name"] == "Earth":
                indicator_length = planet["size"] + 2
                ix = px + indicator_length * math.cos(self.earth_rot)
                iy = py + indicator_length * math.sin(self.earth_rot)
                pyxel.line(int(px), int(py), int(ix), int(iy), 7)


App()

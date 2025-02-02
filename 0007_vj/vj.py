#!/usr/bin/env python
import pyxel
import math


class VJ:
    def __init__(self):
        self.WIDTH = 256
        self.HEIGHT = 256
        pyxel.init(self.WIDTH, self.HEIGHT, title="VJ Media Art")
        # 現在のパターン（0～2）
        self.pattern = 0
        # 最後に設定されたパターン（パターン変更時の音楽再生用）
        self.last_pattern = -1
        # アニメーション用のカウンタ
        self.ticker = 0
        pyxel.run(self.update, self.draw)

    def update(self):
        self.ticker = (self.ticker + 1) % 1000

        # ゲームパッドとキーボードの両方の入力に対応
        # パターン0: ゲームパッドのLEFTSHOULDER または キーボードの1キー
        if pyxel.btnp(pyxel.GAMEPAD1_BUTTON_LEFTSHOULDER) or pyxel.btnp(pyxel.KEY_1):
            self.pattern = 0
        # パターン1: ゲームパッドのRIGHTSHOULDER または キーボードの2キー
        if pyxel.btnp(pyxel.GAMEPAD1_BUTTON_RIGHTSHOULDER) or pyxel.btnp(pyxel.KEY_2):
            self.pattern = 1
        # パターン2: ゲームパッドのAボタン または キーボードの3キー
        if pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A) or pyxel.btnp(pyxel.KEY_3):
            self.pattern = 2

        # パターンが変わったらヤバい音楽を再生（各パターンに対応した音番号を使用）
        if self.pattern != self.last_pattern:
            # 前の音を停止してから新たな音楽を再生する
            pyxel.stop(0)
            if self.pattern == 0:
                # パターン0の音楽 (例: サウンド番号3)
                pyxel.play(0, 3, loop=True)
            elif self.pattern == 1:
                # パターン1の音楽 (例: サウンド番号4)
                pyxel.play(0, 4, loop=True)
            elif self.pattern == 2:
                # パターン2の音楽 (例: サウンド番号5)
                pyxel.play(0, 5, loop=True)
            self.last_pattern = self.pattern

        # ゲームパッドのSTARTボタンまたはESCキーで終了
        if pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START) or pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

    def draw(self):
        pyxel.cls(0)
        # 現在のパターン番号（表示は1～3）を画面上部に表示
        pyxel.text(10, 10, f"Pattern: {self.pattern + 1}", 7)

        # パターンに応じた映像表現
        if self.pattern == 0:
            # パターン0: 赤い円が脈打つように表示
            for i in range(0, self.WIDTH, 20):
                x = i
                y = self.HEIGHT // 2 + int(10 * math.sin(self.ticker / 10 + i))
                r = 5 + int(5 * math.sin(self.ticker / 5 + i))
                pyxel.circ(x, y, r, 8)

        elif self.pattern == 1:
            # パターン1: 緑色の水平ラインを動かす
            offset = self.ticker % 20
            for y in range(0, self.HEIGHT, 20):
                pyxel.line(0, y + offset, self.WIDTH, y + offset, 11)

        elif self.pattern == 2:
            # パターン2: 黄色い矩形が振動する
            for i in range(0, self.WIDTH, 30):
                x = i
                y = self.HEIGHT // 2 + int(20 * math.sin(self.ticker / 15 + i))
                w = 20
                h = 20 + int(10 * math.sin(self.ticker / 7 + i))
                pyxel.rect(x, y, w, h, 9)


if __name__ == "__main__":
    VJ()

import pyxel
import math

# 拡張オーディオ設定用定数
EXTENDED_CHANNELS = [
    (0.1 / 2.0, 0),  # Lead Melody
    (0.1 / 2.0, 20),  # Detuned Lead Melody
    (0.1, 0),  # Sub Melody
    (0.1 / 3.0, 0),  # Chord Backing 1
    (0.1 / 3.0, 0),  # Chord Backing 2
    (0.1 / 3.0, 0),  # Chord Backing 3
    (0.1, 0),  # Bass Line
    (0.1, 0),  # Drums
]

EXTENDED_TONES = [
    (  # Sine Wave
        0.8,
        0,
        [15, 15, 15, 15, 15, 15, 15, 15, 15, 14, 13, 12, 11, 10, 9, 8] + [7, 6, 5, 4, 3, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ),
    (  # Sine Wave
        0.4,
        0,
        [8, 9, 10, 12, 13, 14, 14, 15, 15, 15, 14, 14, 13, 12, 10, 9] + [8, 6, 5, 3, 2, 1, 1, 0, 0, 0, 1, 1, 2, 3, 5, 6],
    ),
    (  # Narrow (1:7) Pulse Wave
        0.7,
        0,
        [15] * 4 + [0] * 28,
    ),
    (  # Saw Wave
        1.0,
        0,
        [15, 15, 14, 14, 13, 13, 12, 12, 11, 11, 10, 10, 9, 9, 8, 8] + [7, 7, 6, 6, 5, 5, 4, 4, 3, 3, 2, 2, 1, 1, 0, 0],
    ),
    (  # Short Period Noise
        0.8,
        1,
        [0] * 32,
    ),
]


def extend_audio():
    channels = []
    for gain, detune in EXTENDED_CHANNELS:
        channel = pyxel.Channel()
        channel.gain = gain
        channel.detune = detune
        channels.append(channel)
    pyxel.channels.from_list(channels)

    tones = []
    for gain, noise, waveform in EXTENDED_TONES:
        tone = pyxel.Tone()
        tone.gain = gain
        tone.noise = noise
        tone.waveform.from_list(waveform)
        tones.append(tone)
    pyxel.tones.from_list(tones)


def setup_music():
    pyxel.sounds[0].set(
        "b-2b-2b-2b-2a-2a-2a-2a-2 g2g2e-2e-2c2c2f2f2 f2f2g2g2f2f2e2e2 e2e2c2c2c2c2rr"
        "rrb-1b-1c2c2e-2e-2 f3f3f3g3g3g3g3g3 rrb-3b-3a-3a-3f3f3 a-3a-3a-3g3g3g3g3g3",
        "0",
        "5",
        "vvvfnnnf nfnfnfvv vfnfnfvv vfvvvfvv vfnfnfvf vfnfnfnf nfnfnfvv vfnnnfnf",
        16,
    )
    pyxel.sounds[1].set(
        "rrc3c3e-3e-3g3g3 f3f3f3g3g3g3g3g3 rrb-3b-3a-3a-3f3f3 a-3a-3a-3g3g3g3g3g3"
        "rrc3c3e-3e-3g3g3 f3f3f3g3g3g3g3g3 rrb-3b-3a-3a-3f3f3 a-3a-3a-3g3g3g3g3g3",
        "1",
        "3",
        "vvvvvvvv vvvvvvvf",
        32,
    )
    pyxel.sounds[2].set("a-2a-2ra-2 a-2a-2ra-2 g2g2rg2 g2g2rg2", "2", "5", "f", 32)
    pyxel.sounds[3].set("c3c3rc3 b-2b-2rb-2 b-2b-2rb-2 c3c3rc3", "2", "5", "f", 32)
    pyxel.sounds[4].set(
        "e-3e-3re-3 d3d3rd3 d3d3rd3 e3e3re3 e-3e-3re-3 d3d3rd3 d3d3rd3 e-3e-3re-3",
        "2",
        "5",
        "f",
        32,
    )
    pyxel.sounds[5].set("a-0rra-0 b-0rrb-0 g0rrg0 c1rrc1", "3", "5", "f", 32)
    pyxel.sounds[6].set("g1rrrd2rrr" * 3 + "g1rd2rd2rrr", "4", "50006000" * 3 + "50506000", "f", 16)
    # 背景音楽は再生せず、パターン切替時に個別に音を再生します。


class VJArt:
    def __init__(self):
        self.WIDTH = 256
        self.HEIGHT = 256
        pyxel.init(self.WIDTH, self.HEIGHT, title="0008_vj - Gamepad VJ")

        # 拡張オーディオの初期化
        extend_audio()
        setup_music()

        # パターン数（異なる視覚表現）
        self.num_patterns = 3
        self.current_pattern = 0

        # フレームカウント
        self.t = 0

        # ゲームパッドの位置（初期配置は画面中央）
        self.pos_x = self.WIDTH // 2
        self.pos_y = self.HEIGHT // 2

        pyxel.run(self.update, self.draw)

    def get_axis(self, axis_name, keyboard_keys):
        # アナログ入力値の取得（キーボード入力の場合は最大値を返す）
        value = pyxel.btnv(getattr(pyxel, axis_name))
        if len(keyboard_keys) == 2:
            if pyxel.btn(keyboard_keys[0]):
                value = 32767
            elif pyxel.btn(keyboard_keys[1]):
                value = -32768
        elif len(keyboard_keys) == 1:
            if pyxel.btn(keyboard_keys[0]):
                value = 32767
        return value

    def update(self):
        self.t += 1
        # 終了処理：STARTボタンまたはESCキーで終了
        if pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START) or pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

        # パターン切替：ボタンAまたはJキーで切替
        if pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A) or pyxel.btnp(pyxel.KEY_J):
            self.current_pattern = (self.current_pattern + 1) % self.num_patterns
            # パターン切替時に対応するサウンドを再生（チャンネル7を使用）
            pyxel.play(7, self.current_pattern)

        # アナログ入力（左スティックまたはキーボード D/A, S/W）で位置更新
        axis_x = self.get_axis("GAMEPAD1_AXIS_LEFTX", [pyxel.KEY_D, pyxel.KEY_A])
        axis_y = self.get_axis("GAMEPAD1_AXIS_LEFTY", [pyxel.KEY_S, pyxel.KEY_W])
        self.pos_x = int((axis_x + 32768) / 65535 * self.WIDTH)
        self.pos_y = int((axis_y + 32768) / 65535 * self.HEIGHT)

    def draw(self):
        pyxel.cls(0)
        # 現在のパターンに応じた描画処理
        if self.current_pattern == 0:
            # パターン0: 移動する円（sin波で半径変化）
            radius = 20 + int(10 * math.sin(self.t / 10))
            pyxel.circ(self.pos_x, self.pos_y, radius, pyxel.COLOR_RED)
            pyxel.text(10, 10, "Pattern 0: Circle", pyxel.COLOR_YELLOW)
        elif self.current_pattern == 1:
            # パターン1: 中央に向かって引かれる線
            for i in range(0, self.WIDTH, 10):
                pyxel.line(i, 0, self.pos_x, self.pos_y, pyxel.COLOR_GREEN)
                pyxel.line(0, i, self.pos_x, self.pos_y, pyxel.COLOR_GREEN)
            pyxel.text(10, 10, "Pattern 1: Lines", pyxel.COLOR_YELLOW)
        elif self.current_pattern == 2:
            # パターン2: 格子状の四角形のアニメーション
            grid_size = 20
            offset = self.t % grid_size
            for x in range(0, self.WIDTH, grid_size):
                for y in range(0, self.HEIGHT, grid_size):
                    color = (pyxel.frame_count + x + y) % 16
                    pyxel.rect(x + offset, y + offset, grid_size // 2, grid_size // 2, color)
            pyxel.text(10, 10, "Pattern 2: Grid", pyxel.COLOR_YELLOW)

        # 現在のパターン番号を表示
        pyxel.text(10, self.HEIGHT - 10, f"Current pattern: {self.current_pattern}", pyxel.COLOR_WHITE)


if __name__ == "__main__":
    VJArt()

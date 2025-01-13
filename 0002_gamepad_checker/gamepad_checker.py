import pyxel

class GamepadChecker:
    def __init__(self):
        self.SCREEN_WIDTH = 256
        self.SCREEN_HEIGHT = 256
        pyxel.init(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        
        # 表示位置の初期設定
        self.title_y = 10
        self.start_y = 30
        self.line_height = 10
        
        # 色の定義
        self.COLOR_INACTIVE = 7  # 白
        self.COLOR_ACTIVE = 10   # 緑
        
        # アナログ入力とキーボード対応
        self.analog_inputs = [
            ("GAMEPAD1_AXIS_LEFTX", [pyxel.KEY_D, pyxel.KEY_A]),  # D/Aキーで左右
            ("GAMEPAD1_AXIS_LEFTY", [pyxel.KEY_S, pyxel.KEY_W]),  # S/Wキーで上下
            ("GAMEPAD1_AXIS_RIGHTX", [pyxel.KEY_RIGHT, pyxel.KEY_LEFT]),  # 右左キー
            ("GAMEPAD1_AXIS_RIGHTY", [pyxel.KEY_DOWN, pyxel.KEY_UP]),  # 下上キー
            ("GAMEPAD1_AXIS_TRIGGERLEFT", [pyxel.KEY_Q]),  # Qキー
            ("GAMEPAD1_AXIS_TRIGGERRIGHT", [pyxel.KEY_E])  # Eキー
        ]
        
        # デジタル入力とキーボード対応
        self.digital_inputs = [
            ("GAMEPAD1_BUTTON_LEFTSTICK", [pyxel.KEY_Z]),  # Zキー
            ("GAMEPAD1_BUTTON_RIGHTSTICK", [pyxel.KEY_X]), # Xキー
            ("GAMEPAD1_BUTTON_A", [pyxel.KEY_J]),  # Jキー
            ("GAMEPAD1_BUTTON_B", [pyxel.KEY_K]),  # Kキー
            ("GAMEPAD1_BUTTON_X", [pyxel.KEY_U]),  # Uキー
            ("GAMEPAD1_BUTTON_Y", [pyxel.KEY_I]),  # Iキー
            ("GAMEPAD1_BUTTON_BACK", [pyxel.KEY_B]),  # Bキー
            ("GAMEPAD1_BUTTON_GUIDE", [pyxel.KEY_G]),  # Gキー
            ("GAMEPAD1_BUTTON_START", [pyxel.KEY_RETURN]),  # Enterキー
            ("GAMEPAD1_BUTTON_LEFTSHOULDER", [pyxel.KEY_1]),  # 1キー
            ("GAMEPAD1_BUTTON_RIGHTSHOULDER", [pyxel.KEY_2]),  # 2キー
            ("GAMEPAD1_BUTTON_DPAD_UP", [pyxel.KEY_UP]),  # ↑キー
            ("GAMEPAD1_BUTTON_DPAD_DOWN", [pyxel.KEY_DOWN]),  # ↓キー
            ("GAMEPAD1_BUTTON_DPAD_LEFT", [pyxel.KEY_LEFT]),  # ←キー
            ("GAMEPAD1_BUTTON_DPAD_RIGHT", [pyxel.KEY_RIGHT])  # →キー
        ]
        
        pyxel.run(self.update, self.draw)

    def update(self):
        # STARTボタンまたはESCキーで終了
        if (pyxel.btn(pyxel.GAMEPAD1_BUTTON_START) or 
            pyxel.btn(pyxel.KEY_ESCAPE)):
            pyxel.quit()

    def get_analog_value(self, input_name, keyboard_keys):
        """アナログ入力値の取得（キーボードの場合は最大値を返す）"""
        value = pyxel.btnv(getattr(pyxel, input_name))
        
        # キーボード入力のチェック
        if len(keyboard_keys) == 2:  # 左右/上下の場合
            if pyxel.btn(keyboard_keys[0]):  # 正の値
                value = 32767
            elif pyxel.btn(keyboard_keys[1]):  # 負の値
                value = -32768
        elif len(keyboard_keys) == 1:  # トリガーの場合
            if pyxel.btn(keyboard_keys[0]):
                value = 32767
                
        return value

    def is_button_pressed(self, input_name, keyboard_keys):
        """ボタンの押下状態を取得"""
        return (pyxel.btn(getattr(pyxel, input_name)) or 
                any(pyxel.btn(key) for key in keyboard_keys))

    def draw(self):
        pyxel.cls(0)
        
        # タイトルの表示
        title = "GAMEPAD1 INPUT TEST (Press START or ESC to exit)"
        self.draw_centered_text(title, self.title_y, self.COLOR_INACTIVE)
        
        current_y = self.start_y
        
        # アナログ入力の表示
        for input_name, keyboard_keys in self.analog_inputs:
            value = self.get_analog_value(input_name, keyboard_keys)
            color = self.COLOR_ACTIVE if value != 0 else self.COLOR_INACTIVE
            self.draw_centered_text(f"{input_name} {value}", current_y, color)
            current_y += self.line_height
        
        # デジタル入力の表示
        for input_name, keyboard_keys in self.digital_inputs:
            is_pressed = self.is_button_pressed(input_name, keyboard_keys)
            color = self.COLOR_ACTIVE if is_pressed else self.COLOR_INACTIVE
            key_info = f" ({'+'.join([str(k) for k in keyboard_keys])})"
            self.draw_centered_text(input_name + key_info, current_y, color)
            current_y += self.line_height

    def draw_centered_text(self, text, y, color):
        """画面中央にテキストを表示する"""
        x = (self.SCREEN_WIDTH - len(text) * 8) // 2  # 8はフォントの幅
        pyxel.text(x, y, text, color)

if __name__ == "__main__":
    GamepadChecker()
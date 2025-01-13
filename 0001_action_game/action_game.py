# title: action game
# author: karaage
# desc: A Pyxel simple action game
# site: https://github.com/karaage0703/pyxel-examples
# license: MIT
# version: 1.0

import pyxel
import math
import random


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 2
        self.dash_speed = 4
        self.size = 8
        self.color = 12  # 水色
        self.shield_active = False
        self.dash_active = False
        self.power_mode = False
        self.power_timer = 0
        self.bullets = []
        self.energy_balls = []
        self.dash_cooldown = 0
        self.health = 100
        self.score = 0


class Enemy:
    def __init__(self, x, y, type="normal"):
        self.x = x
        self.y = y
        self.type = type
        self.speed = 1 if type == "normal" else 2
        self.size = 8
        self.health = 2 if type == "normal" else 4
        self.color = 8 if type == "normal" else 10  # 赤または黄色


class Game:
    def __init__(self):
        pyxel.init(160, 120)
        self.reset_game()
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        self.player = Player(80, 60)
        self.enemies = []
        self.effects = []
        self.game_over = False
        self.spawn_timer = 0

    def update(self):
        # スタートボタンで終了
        if pyxel.btn(pyxel.GAMEPAD1_BUTTON_START) or pyxel.btn(pyxel.KEY_ESCAPE):
            pyxel.quit()

        if self.game_over:
            if pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A) or pyxel.btnp(pyxel.KEY_SPACE):
                self.reset_game()
            return

        self.update_player()
        self.update_enemies()
        self.update_projectiles()
        self.update_effects()
        self.check_collisions()

    def update_player(self):
        # アナログスティックによる移動
        lx = pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX)
        ly = pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTY)

        # キーボード入力のサポート
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A):
            lx = -32767
        elif pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D):
            lx = 32767
        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W):
            ly = -32767
        elif pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_S):
            ly = 32767

        # 移動速度の計算
        speed = self.player.dash_speed if self.player.dash_active else self.player.speed
        if abs(lx) > 10000 or abs(ly) > 10000:  # デッドゾーンの設定
            angle = math.atan2(ly, lx)
            self.player.x += math.cos(angle) * speed
            self.player.y += math.sin(angle) * speed

        # 画面端の制限
        self.player.x = max(0, min(self.player.x, pyxel.width - self.player.size))
        self.player.y = max(0, min(self.player.y, pyxel.height - self.player.size))

        # ダッシュクールダウンの更新
        if self.player.dash_cooldown > 0:
            self.player.dash_cooldown -= 1

        # パワーモードの更新
        if self.player.power_mode:
            self.player.power_timer -= 1
            if self.player.power_timer <= 0:
                self.player.power_mode = False

        # Aボタン: 通常攻撃（弾を発射）
        if pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A) or pyxel.btnp(pyxel.KEY_J):
            rx = pyxel.btnv(pyxel.GAMEPAD1_AXIS_RIGHTX)
            ry = pyxel.btnv(pyxel.GAMEPAD1_AXIS_RIGHTY)
            if abs(rx) > 10000 or abs(ry) > 10000:
                angle = math.atan2(ry, rx)
            else:
                angle = 0  # デフォルトは右向き
            self.player.bullets.append(
                {
                    "x": self.player.x + self.player.size / 2,
                    "y": self.player.y + self.player.size / 2,
                    "angle": angle,
                    "speed": 4,
                }
            )

        # Bボタン: ダッシュ
        if (
            pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B) or pyxel.btnp(pyxel.KEY_K)
        ) and self.player.dash_cooldown <= 0:
            self.player.dash_active = True
            self.player.dash_cooldown = 30

        if not (pyxel.btn(pyxel.GAMEPAD1_BUTTON_B) or pyxel.btn(pyxel.KEY_K)):
            self.player.dash_active = False

        # Xボタン: シールド
        self.player.shield_active = pyxel.btn(pyxel.GAMEPAD1_BUTTON_X) or pyxel.btn(
            pyxel.KEY_U
        )

        # Yボタン: パワーモード
        if pyxel.btnp(pyxel.GAMEPAD1_BUTTON_Y) or pyxel.btnp(pyxel.KEY_I):
            self.player.power_mode = True
            self.player.power_timer = 60

        # トリガー: エネルギーボール
        if pyxel.btnv(pyxel.GAMEPAD1_AXIS_TRIGGERRIGHT) > 10000 or pyxel.btn(
            pyxel.KEY_E
        ):
            self.player.energy_balls.append(
                {
                    "x": self.player.x + self.player.size / 2,
                    "y": self.player.y + self.player.size / 2,
                    "size": 4,
                    "growing": True,
                }
            )

    def update_enemies(self):
        # 敵の生成
        self.spawn_timer += 1
        if self.spawn_timer >= 30:
            self.spawn_timer = 0
            if random.random() < 0.3:
                enemy_type = "elite" if random.random() < 0.2 else "normal"
                x = random.choice([0, pyxel.width])
                y = random.randint(0, pyxel.height - 8)
                self.enemies.append(Enemy(x, y, enemy_type))

        # 敵の移動
        for enemy in self.enemies:
            dx = self.player.x - enemy.x
            dy = self.player.y - enemy.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                enemy.x += (dx / dist) * enemy.speed
                enemy.y += (dy / dist) * enemy.speed

    def update_projectiles(self):
        # 弾の更新
        for bullet in self.player.bullets[:]:
            bullet["x"] += math.cos(bullet["angle"]) * bullet["speed"]
            bullet["y"] += math.sin(bullet["angle"]) * bullet["speed"]
            if (
                bullet["x"] < 0
                or bullet["x"] > pyxel.width
                or bullet["y"] < 0
                or bullet["y"] > pyxel.height
            ):
                self.player.bullets.remove(bullet)

        # エネルギーボールの更新
        for ball in self.player.energy_balls[:]:
            if ball["growing"]:
                ball["size"] += 0.5
                if ball["size"] >= 20:
                    ball["growing"] = False
            else:
                ball["size"] -= 0.5
                if ball["size"] <= 0:
                    self.player.energy_balls.remove(ball)

    def update_effects(self):
        # エフェクトの更新
        for effect in self.effects[:]:
            effect["timer"] -= 1
            if effect["timer"] <= 0:
                self.effects.remove(effect)

    def check_collisions(self):
        # 弾と敵の衝突判定
        for bullet in self.player.bullets[:]:
            for enemy in self.enemies[:]:
                if (
                    abs(bullet["x"] - enemy.x) < enemy.size
                    and abs(bullet["y"] - enemy.y) < enemy.size
                ):
                    enemy.health -= 1
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    if enemy.health <= 0:
                        self.enemies.remove(enemy)
                        self.player.score += 2 if enemy.type == "elite" else 1
                    self.effects.append(
                        {"x": enemy.x, "y": enemy.y, "type": "hit", "timer": 5}
                    )
                    break

        # エネルギーボールと敵の衝突判定
        for ball in self.player.energy_balls:
            for enemy in self.enemies[:]:
                if (
                    abs(ball["x"] - enemy.x) < ball["size"] + enemy.size
                    and abs(ball["y"] - enemy.y) < ball["size"] + enemy.size
                ):
                    enemy.health -= 0.1
                    if enemy.health <= 0:
                        self.enemies.remove(enemy)
                        self.player.score += 2 if enemy.type == "elite" else 1

        # プレイヤーと敵の衝突判定
        if not self.player.shield_active and not self.player.power_mode:
            for enemy in self.enemies:
                if (
                    abs(self.player.x - enemy.x) < (self.player.size + enemy.size) / 2
                    and abs(self.player.y - enemy.y)
                    < (self.player.size + enemy.size) / 2
                ):
                    self.player.health -= 10
                    if self.player.health <= 0:
                        self.game_over = True
                    self.effects.append(
                        {
                            "x": self.player.x,
                            "y": self.player.y,
                            "type": "damage",
                            "timer": 10,
                        }
                    )

    def draw(self):
        pyxel.cls(0)

        if self.game_over:
            pyxel.text(60, 50, "GAME OVER", 8)  # 赤色
            pyxel.text(45, 60, f"SCORE: {self.player.score}", 10)  # 黄色
            pyxel.text(35, 70, "PRESS A TO RESTART", 7)  # 白色
            return

        # プレイヤーの描画
        player_color = self.player.color
        if self.player.power_mode and pyxel.frame_count % 4 < 2:
            player_color = 10  # 黄色
        pyxel.tri(
            self.player.x,
            self.player.y + self.player.size,
            self.player.x + self.player.size,
            self.player.y + self.player.size / 2,
            self.player.x,
            self.player.y,
            player_color,
        )

        # シールドの描画
        if self.player.shield_active:
            pyxel.circb(
                self.player.x + self.player.size / 2,
                self.player.y + self.player.size / 2,
                10,
                12,  # 水色
            )

        # 弾の描画
        for bullet in self.player.bullets:
            pyxel.rect(bullet["x"] - 1, bullet["y"] - 1, 2, 2, 10)  # 黄色

        # エネルギーボールの描画
        for ball in self.player.energy_balls:
            pyxel.circb(
                ball["x"],
                ball["y"],
                int(ball["size"]),
                8 if ball["growing"] else 9,  # 赤または橙色
            )

        # 敵の描画
        for enemy in self.enemies:
            pyxel.rect(enemy.x, enemy.y, enemy.size, enemy.size, enemy.color)

        # エフェクトの描画
        for effect in self.effects:
            if effect["type"] == "hit":
                pyxel.circb(effect["x"], effect["y"], 10 - effect["timer"], 10)  # 黄色
            elif effect["type"] == "damage":
                pyxel.circb(effect["x"], effect["y"], effect["timer"], 8)  # 赤色

        # UI表示
        pyxel.text(5, 5, f"SCORE: {self.player.score}", 10)  # 黄色
        health_color = 11 if self.player.health >= 30 else 8  # 緑または赤
        pyxel.text(5, 15, f"HEALTH: {self.player.health}", health_color)

        if self.player.dash_cooldown > 0:
            pyxel.text(5, 25, "DASH COOLING...", 12)  # 水色

        if self.player.power_mode:
            pyxel.text(5, 35, "POWER MODE!", 10)  # 黄色


if __name__ == "__main__":
    Game()

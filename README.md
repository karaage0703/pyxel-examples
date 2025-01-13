# pyxel-examples
Pyxel examples

[GitHub Pages WebSite](https://karaage0703.github.io/pyxel-examples)

[GitHub Repository](https://github.com/karaage0703/pyxel-examples)

## Setup
Execute following command for setup [pyxel](https://github.com/kitao/pyxel).

```sh
$ pip install pyxel
```

## Web App

- [0001_action_game](./0001_action_game)
- [0002_gamepad_checker](./0002_gamepad_checker)
- [0003_vj_simple](./0003_vj_simple)

### Run at local
Run http server

```sh
$ python -m http.server 8000
```

Set URL at browser

```
http://localhost:8000/<directory>/

# e.g.
# http://localhost:8000/0001_action_game/
```

## How to make pyxapp 
Execute following command

```sh
$ pyxel package <package name> <python file path>
# e.g.
# pyxel package 0001_action_game 0001_action_game/action_game.py
```

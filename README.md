# KikeFight 🥷🌸

Juego de lucha 2D en el navegador — sin instalar nada.

## 🎮 Jugar online
**https://hernanfernandez1.github.io/kikefight**

*(Activar GitHub Pages: Settings → Pages → Source: main / root)*

---

## 📁 Setup de assets

El juego carga los sprite sheets desde `assets/`.

1. Guardá el sprite sheet de Kike como → `assets/kike_sheet.png`
2. Guardá el sprite sheet de Kurenai como → `assets/kurenai_sheet.png`

El motor detecta los frames automáticamente. Si los archivos no están, arranca igual con placeholders.

---

## 🕹️ Controles

| Acción | Player 1 (KIKE) | Player 2 (KURENAI) |
|---|---|---|
| Mover | A / D | ← / → |
| Saltar | W | ↑ |
| Ataque leve | U | KP1 |
| Ataque fuerte | I | KP3 |
| **🪑 Lanzar mueble** | **O** | — |
| **🌸 Shuriken flurry** | — | **KP2** |
| Bloquear | P | KP0 |
| Modo noche | G | G |
| Debug sprites | D | D |

---

## 🛠️ Local

```bash
python -m http.server 8000
# → http://localhost:8000
```

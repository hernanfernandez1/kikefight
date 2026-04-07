# KikeFight 🥷

Ahora tienes una versión para jugar **directamente en la web** (sin Python).

## Jugar en web

1. Entra en la carpeta del proyecto.
2. Levanta un servidor estático:

```bash
python -m http.server 8000
```

3. Abre en tu navegador: <http://localhost:8000/web/>

## Controles

| Acción | Jugador 1 | Jugador 2 |
|---|---|---|
| Mover | A / D | ← / → |
| Saltar | W | ↑ |
| Ataque ligero | U | Numpad 1 |
| Ataque pesado | I | Numpad 3 |
| Especial | O | Numpad 2 |
| Bloquear | P | Numpad 0 |

## Qué incluye la versión web

- Lucha 1vs1 con barra de vida y temporizador.
- Ataques ligero/pesado/especial.
- Proyectil en el ataque especial.
- Rondas al mejor de 3.
- Pantallas de menú, fin de ronda y campeón.

## Nota

El código original en Python/Pygame se mantiene en la raíz (`main.py`, `fighter.py`, etc.) como referencia.

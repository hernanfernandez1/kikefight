# KikeFight 🥷

Ahora tienes una versión para jugar **directamente en la web** (sin Python).

## Jugar en web

1. Entra en la carpeta del proyecto.
2. Levanta un servidor estático:

```bash
python -m http.server 8000
```

3. Abre en tu navegador: <http://localhost:8000/web/>

## Controles (Jugador)

| Acción | Tecla |
|---|---|
| Mover | A / D |
| Saltar | W |
| Ataque ligero | U |
| Ataque pesado | I |
| Especial | O |
| Bloquear | P |

## Qué incluye la versión web

- Lucha 1vs1 con barra de vida y temporizador.
- Ataques ligero/pesado/especial.
- La enemiga es quien vuela y lanza muebles como especial.
- IA enemiga para jugar en modo un jugador.
- Rondas al mejor de 3.
- Pantallas de menú, fin de ronda y campeón.

## Nota

El código original en Python/Pygame se mantiene en la raíz (`main.py`, `fighter.py`, etc.) como referencia.

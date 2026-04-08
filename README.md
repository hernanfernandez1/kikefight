# KikeFight 🥷

Versión web rehecha desde cero con estética pixel retro tipo boss-fight: **Kike vs La Baronesa del Mueble**.

## Jugar en web

1. Entra en la carpeta del proyecto.
2. Levanta un servidor estático:

```bash
python -m http.server 8000
```

3. Abre en tu navegador: <http://localhost:8000/web/>

## Controles

| Acción | Tecla |
|---|---|
| Mover | A / D |
| Saltar | W |
| Ataque rápido | J |
| Ataque pesado | K |
| Iniciar/Reintentar | Enter |

## Estética y assets (tus imágenes)

El juego ya está preparado para usar recortes y fondos en estilo pixel-art. Para aplicar exactamente la estética que compartiste, coloca estos archivos:

- `web/assets/scene_ref.png` → fondo/escena (dojo)
- `web/assets/kike_poses.png` → sheet con poses de Kike
- `web/assets/baronesa.png` → recorte de la jefa flotante

Si no existen esos archivos, el juego usa fallback dibujado por canvas para que igual se pueda jugar.

## Qué incluye esta versión

- Combate 1 jugador vs boss.
- Boss enemiga flotante que tira muebles.
- HUD retro: vida P1, vida boss, combo y contador de muebles.
- Ronda con timer y pantalla de resultado.

## Nota

El código original en Python/Pygame se mantiene en la raíz (`main.py`, `fighter.py`, etc.) como referencia.

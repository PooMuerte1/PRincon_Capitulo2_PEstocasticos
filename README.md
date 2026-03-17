## ProyectRincon — Quant Path (Caminatas Aleatorias → Finanzas)

Este repositorio contiene:

- **`docs/`**: notas rigurosas en Markdown (teoría + conexión a finanzas + bibliografía/papers).
- **`projects/random-walks-finance/`**: proyecto Python reproducible (simulación, hitting times, ruina del jugador, verificación numérica).
- **`PEstocasticos/`** y PDFs: material fuente (libro/apuntes).

### Empezar rápido (Python)

Desde `projects/random-walks-finance/`:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m src.cli --help
```

### Ruta sugerida

1. Leer `docs/00_roadmap.md`.
2. Leer `docs/07_guia_maestra_por_que_y_como.md` (por qué el método funciona).
2. Estudiar `docs/01_random_walks_rigor_finance.md` (Cap. 2 del PDF).
   - Para ver bien las fórmulas matemáticas en el editor, se recomienda usar una extensión de vista previa de Markdown con soporte de LaTeX (por ejemplo, **“Markdown Preview Enhanced”** en VSCode/Cursor) y abrir el archivo en la vista previa.
   - Si no tienes esa extensión, puedes usar `docs/08_formulas_cap2_en_cristiano.md`, donde las fórmulas clave están explicadas en texto plano y con ejemplos numéricos.
3. Resolver y validar por simulación los ejercicios del capítulo:
   - ver `docs/02_ejercicios_industria_random_walks.md`.
4. Ejecutar experimentos y scripts en `projects/random-walks-finance/`.


# Lonogram

Lonogram és un projecte Python per explorar grafs de carrers i calcular rutes entre dos punts.

## Estat actual

La primera versió carrega la xarxa de carrers d'una població des d'OpenStreetMap, la mostra en una finestra Pygame i permet comparar BFS, DFS i Dijkstra.

- **BFS**: troba un camí amb el mínim nombre d'arestes.
- **DFS**: troba el primer camí que explora.
- **Dijkstra**: troba el camí amb el cost total més baix (en aquesta versió, metres de carrer).

Les arestes del graf provenen de la xarxa de carrers d'OpenStreetMap; no es genera una quadrícula artificial.

## Instal·lació

Recomanat: Python 3.11 o posterior.

```bash
python -m venv .venv
```

Activa l'entorn virtual i instal·la les dependències:

Windows:
```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS / Linux:
```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Executar

```bash
python main.py
```

Escriu el nom d'una població que OpenStreetMap pugui trobar, per exemple `Vic, Catalunya, Espanya`.

A la finestra:
1. Prem **1**, **2** o **3** per seleccionar BFS, DFS o Dijkstra.
2. Fes clic en un punt del mapa per seleccionar l'origen.
3. Fes clic en un altre punt per seleccionar la destinació.
4. Prem **Enter** per calcular i animar la ruta.
5. Prem **R** per reiniciar la selecció o **Esc** per sortir.
6. Utilitza la roda del ratolí per fer zoom i arrossega amb el botó dret per moure el mapa.

## Notes

- Cal connexió a Internet per descarregar les dades d'OpenStreetMap.
- Respecta les condicions d'ús d'OpenStreetMap i atribueix les dades quan comparteixis captures o resultats.
- Aquesta és una eina educativa, no un navegador de conducció. Encara no calcula restriccions de gir, accessibilitat, obres ni trànsit en temps real.

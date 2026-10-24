from graphs import load_graph
from visualization.visualize import run_viewer


def main():
    place = input(
        "Quina població vols carregar? "
        "(ex.: Vic, Catalunya, Espanya): "
    ).strip()

    if not place:
        print("Has d'escriure el nom d'una població.")
        return

    print(f"Descarregant la xarxa de carrers de: {place}")
    print("Això pot trigar una mica la primera vegada...")

    try:
        graph = load_graph(place)
    except Exception as exc:
        print(f"No s'ha pogut carregar el mapa: {exc}")
        print(
            "Comprova la connexió a Internet i prova un nom "
            "de població més específic."
        )
        return

    print(
        f"Mapa carregat: {len(graph['nodes'])} nodes, "
        f"{sum(len(v) for v in graph['adj'].values()) // 2} connexions."
    )
    run_viewer(graph, place)


if __name__ == "__main__":
    main()

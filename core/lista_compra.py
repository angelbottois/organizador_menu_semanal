def generar_lista_compra(plan):
    compra = {}
    for dia in plan:
        for momento in plan[dia]:
            for ing, cant in plan[dia][momento]["ingredientes"].items():
                compra[ing] = compra.get(ing, 0) + cant
    
    compra_ordenada = dict(sorted(compra.items(), key=lambda x: x[0].lower()))
    return compra_ordenada
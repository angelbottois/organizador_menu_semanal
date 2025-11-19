import random

def cocinero_disponible(dia, momento, cocinero, restricciones):
    """
    Comprueba si un cocinero puede cocinar en un turno,
    respetando las restricciones.
    """
    dia = dia.upper()
    momento = momento.upper()
    cocinero = cocinero.upper()

    if cocinero not in restricciones:
        return True

    # Restricciones normalizadas
    restr = [(d.upper(), m.upper()) for (d, m) in restricciones[cocinero]]
    return (dia, momento) not in restr


def generar_plan_semanal(semana, momentos, recetas, cocineros, restricciones, personas_menus):
    """
    Genera un plan semanal equilibrado usando backtracking,
    respetando:
    - restricciones por cocinero
    - equidad 3–4 turnos por semana
    - no repetir recetas
    - no cocinar dos veces el mismo día
    """
    # Normalizar claves de cocineros en restricciones
    restricciones = {c.upper(): [(d.upper(), m.upper()) for d, m in turnos] 
                     for c, turnos in restricciones.items()}

    # Todos los turnos en orden
    turnos = [(dia.upper(), momento.upper()) for dia in semana for momento in momentos]

    MIN_VECES = 3
    MAX_VECES = 4
    TURNOS_TOTALES = len(turnos)

    # Contador de turnos por cocinero
    contador = {c.upper(): 0 for c in cocineros}

    # Para evitar que un cocinero cocine dos veces el mismo día
    ya_cocino_hoy = {dia.upper(): set() for dia in semana}

    solucion = {}

    # -------------------------------
    # Backtracking con aleatoriedad filtrada
    # -------------------------------
    def backtrack(indice):
        if indice == TURNOS_TOTALES:
            # Comprobar mínimo y máximo turnos
            return all(MIN_VECES <= contador[c.upper()] <= MAX_VECES for c in cocineros)

        dia, momento = turnos[indice]

        # candidatos válidos
        candidatos = [
            c for c in cocineros
            if cocinero_disponible(dia, momento, c, restricciones)
            and c.upper() not in ya_cocino_hoy[dia]
            and contador[c.upper()] < MAX_VECES
        ]

        if not candidatos:
            return False  # No hay candidatos válidos, backtrack

        # Aleatoriedad ligera + priorizar cocineros con menos turnos
        candidatos.sort(key=lambda c: contador[c.upper()] + random.random()*0.1)

        for c in candidatos:
            contador[c.upper()] += 1
            ya_cocino_hoy[dia].add(c.upper())
            solucion[(dia, momento)] = c

            # Validación anticipada: comprobar si los cocineros pueden alcanzar MIN_VECES
            turnos_restantes = TURNOS_TOTALES - (indice + 1)
            valido = True
            for coc in cocineros:
                coc_upper = coc.upper()
                if contador[coc_upper] < MIN_VECES:
                    min_necesarios = MIN_VECES - contador[coc_upper]
                    if min_necesarios > turnos_restantes:
                        valido = False
                        break

            if valido and backtrack(indice + 1):
                return True

            # Deshacer asignación
            contador[c.upper()] -= 1
            ya_cocino_hoy[dia].remove(c.upper())
            del solucion[(dia, momento)]

        return False

    exito = backtrack(0)
    if not exito:
        raise RuntimeError("No se pudo generar un plan válido.")

    # -------------------------------
    # Asignar recetas únicas por cocinero
    # -------------------------------
    plan = {}
    recetas_usadas = set()

    for dia, momento in turnos:
        cocinero = solucion[(dia, momento)]
        # recetas que puede cocinar ese cocinero
        recetas_permitidas = [r for r in recetas if r["nombre"] in cocineros[cocinero]]
        recetas_disponibles = [r for r in recetas_permitidas if r["nombre"] not in recetas_usadas]

        if not recetas_disponibles:
            raise RuntimeError(f"No hay recetas únicas disponibles para {cocinero} en {dia} {momento}")

        receta = random.choice(recetas_disponibles)
        recetas_usadas.add(receta["nombre"])

        if dia not in plan:
            plan[dia] = {}
        plan[dia][momento] = {
            "receta": receta["nombre"],
            "cocinero": cocinero,
            "ingredientes": receta.get("ingredientes", []),
            "personas": personas_menus[(dia, momento)]
        }

    return plan

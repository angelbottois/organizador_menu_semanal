import random

def cocinero_disponible(dia, momento, cocinero, restricciones):
    if cocinero not in restricciones:
        return True
    return (dia, momento) not in restricciones[cocinero]


def generar_plan_semanal(semana, momentos, recetas, cocineros, restricciones, personas_menus):

    # Todos los turnos en orden lineal
    turnos = [(dia, momento) for dia in semana for momento in momentos]

    # Requisitos de equilibrio
    MIN_VECES = 3
    MAX_VECES = 4
    TURNOS_TOTALES = len(turnos)

    # Contadores iniciales
    contador = {c: 0 for c in cocineros}

    # Para evitar cocinar dos veces en el mismo día
    ya_cocino_hoy = {dia: set() for dia in semana}

    # Solución parcial
    solucion = {}

    # ------------------------------
    # BACKTRACKING
    # ------------------------------
    def backtrack(indice):
        # Caso base: todos los turnos asignados
        if indice == TURNOS_TOTALES:
            # Comprobamos el mínimo requerido
            return all(MIN_VECES <= contador[c] <= MAX_VECES for c in cocineros)

        dia, momento = turnos[indice]

        # Candidatos válidos
        candidatos = [
            c for c in cocineros
            if cocinero_disponible(dia, momento, c, restricciones)
            and c not in ya_cocino_hoy[dia]
            and contador[c] < MAX_VECES
        ]

        # Heurística: ordenar candidatos por menor carga
        candidatos.sort(key=lambda c: contador[c])

        for c in candidatos:
            # Intenta asignar
            contador[c] += 1
            ya_cocino_hoy[dia].add(c)

            solucion[(dia, momento)] = c

            # Validación anticipada:
            # Verificar que los cocineros restantes pueden cumplir el mínimo
            turnos_restantes = TURNOS_TOTALES - (indice + 1)
            for coc in cocineros:
                if contador[coc] < MIN_VECES:
                    min_necesarios = MIN_VECES - contador[coc]
                    if min_necesarios > turnos_restantes:
                        break
            else:
                # Si la validación no rompe, seguimos
                if backtrack(indice + 1):
                    return True

            # Deshacer asignación
            contador[c] -= 1
            ya_cocino_hoy[dia].remove(c)
            del solucion[(dia, momento)]

        return False

    # Ejecutar el backtracking
    exito = backtrack(0)
    if not exito:
        raise RuntimeError("No se pudo generar un plan válido (muy raro).")

    # Construir el plan completo con recetas
    plan = {}
    recetas_usadas = set()  # NUEVO: para impedir repetir recetas

    for dia in semana:
        plan[dia] = {}
        for momento in momentos:
            cocinero = solucion[(dia, momento)]

            # Recetas permitidas por cocinero
            recetas_permitidas = [
                r for r in recetas
                if r["nombre"] in cocineros[cocinero]
            ]

            # Filtrar recetas no usadas aún
            recetas_disponibles = [
                r for r in recetas_permitidas
                if r["nombre"] not in recetas_usadas
            ]

            # Si no quedan recetas disponibles → no hay solución, backtracking
            if not recetas_disponibles:
                raise RuntimeError(
                    f"No hay recetas únicas disponibles para {cocinero} en {dia} {momento}"
                )

            # Elegimos una receta disponible
            receta = random.choice(recetas_disponibles)

            # Marcar como usada
            recetas_usadas.add(receta["nombre"])

            # Guardar en el plan semanal
            plan[dia][momento] = {
                "receta": receta["nombre"],
                "cocinero": cocinero,
                "ingredientes": receta["ingredientes"],
                "personas": personas_menus[(dia, momento)]
            }

    return plan
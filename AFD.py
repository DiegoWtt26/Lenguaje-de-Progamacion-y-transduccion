import sys

 
def parse_conf(path):
    """
    Lee y valida el archivo de configuracion del AFD (conf.txt) y
    construye la representacion interna del automata.
 
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            lineas = [l.rstrip("\n") for l in f]
    except FileNotFoundError:
        error(f"no se encontro el archivo de configuracion '{path}'")
 
    # Componentes de la 5-tupla del AFD, inicializadas vacias/None.
    estados = []
    alfabeto = []
    inicial = None
    aceptacion = []
    transiciones = {}
 
    modo_transiciones = False
 
    for numero, linea in enumerate(lineas, start=1):
        contenido = linea.strip()
 
        if not contenido or contenido.startswith("#"):
            continue
 
        if modo_transiciones:
            partes = [p.strip() for p in contenido.split(",")]
            if len(partes) != 3:
                error(f"linea {numero} invalida en TRANSICIONES: '{linea}'")
            origen, simbolo, destino = partes
            transiciones[(origen, simbolo)] = destino
            continue
 
        if contenido.upper().startswith("ESTADOS:"):
            estados = [s.strip() for s in contenido.split(":", 1)[1].split(",") if s.strip()]
        elif contenido.upper().startswith("ALFABETO:"):
            alfabeto = [s.strip() for s in contenido.split(":", 1)[1].split(",") if s.strip()]
        elif contenido.upper().startswith("INICIAL:"):
            inicial = contenido.split(":", 1)[1].strip()
        elif contenido.upper().startswith("ACEPTACION:"):
            aceptacion = [s.strip() for s in contenido.split(":", 1)[1].split(",") if s.strip()]
        elif contenido.upper().startswith("TRANSICIONES:"):
            modo_transiciones = True
        else:
            error(f"linea {numero} no reconocida en configuracion: '{linea}'")
 
    if not estados:
        error("la seccion ESTADOS esta vacia o ausente")
    if not alfabeto:
        error("la seccion ALFABETO esta vacia o ausente")
    if inicial is None:
        error("la seccion INICIAL esta ausente")
    if inicial not in estados:
        error(f"el estado inicial '{inicial}' no esta declarado en ESTADOS")
    for a in aceptacion:
        if a not in estados:
            error(f"el estado de aceptacion '{a}' no esta declarado en ESTADOS")
 
    return {
        "estados": estados,
        "alfabeto": alfabeto,
        "inicial": inicial,
        "aceptacion": set(aceptacion), 
        "transiciones": transiciones,
    }
 
 
def leer_cadenas(path):

    try:
        with open(path, "r", encoding="utf-8") as f:
            lineas = [l.rstrip("\n") for l in f]
    except FileNotFoundError:
        error(f"no se encontro el archivo de cadenas '{path}'")
 
    cadenas = []
    for linea in lineas:
        contenido = linea.strip()
        if not contenido or contenido.startswith("#"):
            continue
        if contenido.upper() in ("EPSILON", "LAMBDA", "EMPTY"):
            cadenas.append("")
        else:
            cadenas.append(contenido)
    return cadenas
 
 
def simular(afd, cadena):
   
    estado_actual = afd["inicial"]
    secuencia_estados = [estado_actual]
    secuencia_simbolos = []
    motivo_rechazo = None
 
    for simbolo in cadena:
        if simbolo not in afd["alfabeto"]:
            motivo_rechazo = f"simbolo '{simbolo}' no pertenece al alfabeto"
            return secuencia_estados, secuencia_simbolos, False, motivo_rechazo
 
        clave = (estado_actual, simbolo)
        if clave not in afd["transiciones"]:
            motivo_rechazo = (
                f"no existe transicion desde '{estado_actual}' con '{simbolo}' "
                "(estado trampa implicito)"
            )
            return secuencia_estados, secuencia_simbolos, False, motivo_rechazo
 
        estado_actual = afd["transiciones"][clave]
        secuencia_estados.append(estado_actual)
        secuencia_simbolos.append(simbolo)
 
    aceptada = estado_actual in afd["aceptacion"]
    return secuencia_estados, secuencia_simbolos, aceptada, motivo_rechazo
 
 
def imprimir_secuencia(secuencia_estados, secuencia_simbolos):
    partes = [secuencia_estados[0]]
    for simbolo, estado in zip(secuencia_simbolos, secuencia_estados[1:]):
        partes.append(f"--{simbolo}-->")
        partes.append(estado)
    print("  " + " ".join(partes))
 
 
def main():
   
    if len(sys.argv) != 3:
        print("Uso: python3 AFD.py conf.txt cadenas.txt", file=sys.stderr)
        sys.exit(1)
 
    conf_path, cadenas_path = sys.argv[1], sys.argv[2]
 
    afd = parse_conf(conf_path)
    cadenas = leer_cadenas(cadenas_path)
 
    print(f"Configuracion cargada desde: {conf_path}")
    print(f"  Estados      : {', '.join(afd['estados'])}")
    print(f"  Alfabeto     : {', '.join(afd['alfabeto'])}")
    print(f"  Inicial      : {afd['inicial']}")
    print(f"  Aceptacion   : {', '.join(sorted(afd['aceptacion']))}")
 
    if not cadenas:
        print("No hay cadenas para procesar en", cadenas_path)
        return
 
    for cadena in cadenas:
        etiqueta = cadena if cadena != "" else "ε (cadena vacia)"
        print(f"\nCadena de entrada: {etiqueta}")
 
        secuencia_estados, secuencia_simbolos, aceptada, motivo = simular(afd, cadena)
        imprimir_secuencia(secuencia_estados, secuencia_simbolos)
 
        if aceptada:
            print(f"  Estado final: {secuencia_estados[-1]}  ->  ACEPTADA")
        else:
            extra = f" ({motivo})" if motivo else ""
            print(f"  Estado final: {secuencia_estados[-1]}  ->  RECHAZADA{extra}")

if __name__ == "__main__":
    main()
 

# AFD.py — Simulador de Autómatas Finitos Deterministas


## 1. Contexto del ejercicio

| EJercicio| Expresión regular          |
|---------|-----------------------------|
| a)     | `(a\|b)*`                    |
| b)     | `(a*\|b*)*`                  |
| c)     | `((ε\|a)b*)*`                |
| d)     | `(b\|b)*abb(a\|b)*`          |

A partir de esto, se implementó AFD.py un simulador genérico
de **Autómatas Finitos Deterministas (AFD)** que, en vez de estar
"programado a mano" para un ejercicio puntual, lee la definición completa
del autómata desde un archivo de configuración de texto y evalúa
cualquier conjunto de cadenas de entrada contra él.

### 1.1 Análisis de las expresiones regulares

Antes de construir los autómatas, se simplificó el lenguaje que reconoce
cada expresión:

- **a) `(a|b)*`** **cualquier** cadena sobre `{a,b}`,
  incluida la cadena vacía.

- **b) `(a*|b*)*`** — Este lenguaje **también equivale a `(a|b)*`**. 

- **c) `((ε|a)b*)*`** — También equivale a `(a|b)*`. Cada bloque
  `(ε|a)b*` aporta como máximo una `a` seguida de cualquier cantidad de
  `b`; encadenando bloques dentro del `*` externo se puede reconstruir
  cualquier cadena sobre `{a,b}` (una `a` sola es un bloque con `b*`
  vacío; una `b` sola es un bloque con la opción `ε` seguida de una `b`).

- **d) `(b|b)*abb(a|b)*`** — `(b|b)` es simplemente `b` (unión de un
  símbolo consigo mismo), así que el lenguaje real es:
  b* a b b (a|b)*
 

## 3. ¿Qué hace `AFD.py`?

`AFD.py` implementa un **simulador de Autómata Finito Determinista**
(en inglés, *DFA — Deterministic Finite Automaton*), es decir, la
5-tupla formal:

```
M = (Q, Σ, δ, q0, F)
```

| Símbolo | Significado                                   | Sección en `conf.txt` |
|---------|------------------------------------------------|------------------------|
| `Q`     | Conjunto finito de estados                      | `ESTADOS`               |
| `Σ`     | Alfabeto de entrada                             | `ALFABETO`               |
| `δ`     | Función de transición `Q × Σ → Q`                | `TRANSICIONES`            |
| `q0`    | Estado inicial (`q0 ∈ Q`)                        | `INICIAL`                  |
| `F`     | Conjunto de estados de aceptación (`F ⊆ Q`)       | `ACEPTACION`                |

El programa **no asume nada** sobre el autómata: todo (estados,
alfabeto, transiciones, estado inicial, estados de aceptación) se
declara en el archivo de configuración. Esto permite reutilizar el mismo
script para cualquier AFD, no solo para los del ejercicio 3.16.

### 3.1 Uso desde la terminal

```bash
python3 AFD.py ConfiguracionX.txt CadenaX.txt
```

### 3.2 Formato del archivo de configuración (`conf.txt`)

```
ESTADOS: q0,q1,q2
ALFABETO: a,b
INICIAL: q0
ACEPTACION: q2
TRANSICIONES:
q0,a,q1
q0,b,q0
q1,a,q1
q1,b,q2
q2,a,q2
q2,b,q2
```


### 3.3 Formato del archivo de cadenas (`cadenas.txt`)

```
# Comentario de ejemplo
EPSILON
a
ab
abb
```

### 3.4 Salida del programa

Para cada cadena procesada, el programa imprime:

1. La cadena que se está evaluando.
2. La secuencia completa de movimientos del autómata, en el formato:

   ```
   q0 --a--> q1 --b--> q2
   ```

3. El estado final alcanzado y si la cadena fue **ACEPTADA** o
   **RECHAZADA** (y, en caso de rechazo, el motivo: símbolo fuera del
   alfabeto, transición no definida, o estado final que no pertenece a
   `F`).

---

## 4. Explicación del código (`AFD.py`)

### `error(msg)`
Función auxiliar centralizada para reportar errores imprime el mensaje
por `stderr` con el prefijo `"Error: "` y termina el programa
(`sys.exit(1)`). 

### `parse_conf(path)`
Lee el archivo de configuración y construye la representación interna
del AFD. Recorre el archivo línea por línea, ignorando comentarios y
líneas vacías, y usa una bandera (`modo_transiciones`) para saber cuándo
dejar de buscar encabezados de sección y empezar a interpretar cada
línea como una transición.

Valida que:
- `ESTADOS` y `ALFABETO` no estén vacíos.
- `INICIAL` esté presente y pertenezca a `ESTADOS`.
- Cada estado en `ACEPTACION` pertenezca a `ESTADOS`.
- Cada línea de `TRANSICIONES` tenga exactamente 3 campos.

Devuelve un diccionario con las 5 componentes del autómata, incluyendo
`transiciones` como un diccionario Python que mapea la pareja
`(estado_origen, símbolo)` al `estado_destino` — esto modela
directamente la función `δ(estado, símbolo) = destino`.

### `leer_cadenas(path)`
Lee el archivo de cadenas de prueba y devuelve una lista de cadenas a
evaluar. Traduce las palabras clave `EPSILON` / `LAMBDA` / `EMPTY` a la
cadena vacía real (`""`), y descarta comentarios y líneas vacías.

### `simular(afd, cadena)`
El corazón del programa: ejecuta el AFD sobre una cadena, símbolo por
símbolo, empezando en el estado inicial. En cada paso:

1. Verifica que el símbolo pertenezca al alfabeto declarado (si no,
   rechaza de inmediato).
2. Busca la transición `δ(estado_actual, símbolo)` en el diccionario de
   transiciones (si no existe, rechaza — estado trampa implícito).
3. Avanza al estado destino y registra el movimiento.

Al terminar de consumir la cadena completa, determina si fue aceptada
comprobando si el estado final pertenece al conjunto `F`
(`aceptación`). Devuelve la secuencia de estados visitados, la secuencia
de símbolos consumidos, un booleano de aceptación, y el motivo del
rechazo (si aplica).

### `imprimir_secuencia(secuencia_estados, secuencia_simbolos)`
Función de presentación: intercala estados y símbolos para construir la
traza legible `q0 --a--> q1 --b--> q2 ...` que pide el enunciado
("muéstrese la secuencia de movimiento").

---

| Estado | Significado                                                        |
|--------|----------------------------------------------------------------------|
| `q0`   | Leyendo el prefijo `b*` (aún no ha aparecido la `a` clave).            |
| `q1`   | Se leyó la `a`; se espera la primera `b` de `"abb"`.                   |
| `q2`   | Se leyó la primera `b`; se espera la segunda `b`.                      |
| `q3`   | Se completó `"abb"`; a partir de aquí acepta cualquier cosa `(a\|b)*`. |
| `qt`   | Estado trampa: el patrón ya no se puede cumplir (no es de aceptación).|

```
ESTADOS: q0,q1,q2,q3,qt
ALFABETO: a,b
INICIAL: q0
ACEPTACION: q3
TRANSICIONES:
q0,b,q0
q0,a,q1
q1,b,q2
q1,a,qt
q2,b,q3
q2,a,qt
q3,a,q3
q3,b,q3
qt,a,qt
qt,b,qt
```



## 7. Cómo ejecutar el proyecto

Ejecuta cualquiera de los 4 ejercicios:

   ```bash
   python3 AFD.py ConfiguracionAtxt CadenaA.txt
   python3 AFD.py ConfiguracionB.txt CadenaB.txt
   python3 AFD.py ConfiguracionC.txt CadenaC.txt
   python3 AFD.py ConfiguracionD.txt CadenaD.txt
 

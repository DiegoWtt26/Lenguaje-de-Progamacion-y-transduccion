# AFD.py — Simulador de Autómatas Finitos Deterministas

Proyecto para el **ejercicio 3.16**: construcción de autómatas para las
expresiones regulares dadas y prueba de su funcionamiento sobre distintas
cadenas de entrada, usando un simulador de Autómata Finito Determinista
(AFD) implementado en Python.

---

## 1. Contexto del ejercicio

El ejercicio original pide construir autómatas finitos no deterministas
(AFN) mediante el **algoritmo 3.3 (construcción de Thompson)** para las
siguientes expresiones regulares, y mostrar la secuencia de movimientos
al procesar la cadena `ababbab`:

| Inciso | Expresión regular          |
|--------|-----------------------------|
| a)     | `(a\|b)*`                    |
| b)     | `(a*\|b*)*`                  |
| c)     | `((ε\|a)b*)*`                |
| d)     | `(b\|b)*abb(a\|b)*`          |

A partir de ese análisis, se implementó `AFD.py`: un simulador genérico
de **Autómatas Finitos Deterministas (AFD)** que, en vez de estar
"programado a mano" para un ejercicio puntual, lee la definición completa
del autómata desde un archivo de configuración de texto y evalúa
cualquier conjunto de cadenas de entrada contra él.

### 1.1 Análisis de las expresiones regulares

Antes de construir los autómatas, se simplificó el lenguaje que reconoce
cada expresión:

- **a) `(a|b)*`** — Lenguaje trivial: **cualquier** cadena sobre `{a,b}`,
  incluida la cadena vacía.

- **b) `(a*|b*)*`** — Aunque no es evidente a simple vista, este lenguaje
  **también equivale a `(a|b)*`**. Razón: `a*` y `b*` contienen cadenas
  de una sola letra (`"a"` y `"b"`), así que al concatenar piezas de una
  letra dentro del `*` externo se puede formar cualquier cadena sobre
  `{a,b}` (por ejemplo, `"ab"` se logra concatenando la pieza `"a"` de
  `a*` con la pieza `"b"` de `b*`).

- **c) `((ε|a)b*)*`** — También equivale a `(a|b)*`. Cada bloque
  `(ε|a)b*` aporta como máximo una `a` seguida de cualquier cantidad de
  `b`; encadenando bloques dentro del `*` externo se puede reconstruir
  cualquier cadena sobre `{a,b}` (una `a` sola es un bloque con `b*`
  vacío; una `b` sola es un bloque con la opción `ε` seguida de una `b`).

- **d) `(b|b)*abb(a|b)*`** — `(b|b)` es simplemente `b` (unión de un
  símbolo consigo mismo), así que el lenguaje real es:

  ```
  b* a b b (a|b)*
  ```

  Es decir: **cero o más `b` iniciales, luego literalmente `"abb"`, y
  después cualquier cosa** sobre `{a,b}`. A diferencia de a), b) y c),
  este autómata **sí rechaza** muchas cadenas.

  **Dato importante:** la cadena `ababbab` del ejercicio original **es
  rechazada** por este autómata. La primera `a` aparece en la posición 0,
  por lo que inmediatamente después se espera `"bb"` — pero lo que sigue
  es `"ba"`, no `"bb"`. Al no existir mecanismo de "reintento" en esta
  expresión regular (no hay `.*` al inicio), el autómata cae en un
  estado trampa y la cadena queda rechazada.

Como a), b) y c) terminan siendo el mismo lenguaje (`Σ*`, cualquier
cadena sobre `{a,b}`), sus AFD resultantes son equivalentes: un único
estado de aceptación con auto-transiciones para `a` y `b`.

---

## 2. Estructura del repositorio

```
.
├── AFD.py            # Simulador genérico de AFD (el programa principal)
├── conf_a.txt         # Configuración del AFD para el inciso a)
├── conf_b.txt         # Configuración del AFD para el inciso b)
├── conf_c.txt         # Configuración del AFD para el inciso c)
├── conf_d.txt         # Configuración del AFD para el inciso d)
├── cadenas_a.txt       # Cadenas de prueba para el inciso a)
├── cadenas_b.txt       # Cadenas de prueba para el inciso b)
├── cadenas_c.txt       # Cadenas de prueba para el inciso c)
├── cadenas_d.txt       # Cadenas de prueba para el inciso d)
└── README.md           # Este archivo
```

`AFD.py` es completamente genérico: no tiene ningún autómata ni ninguna
cadena "quemada" en el código. Todo lo que hace es leer dos archivos que
se le pasan como argumentos y ejecutar la simulación con base en ellos.
Por eso hay un par de archivos `conf_X.txt` / `cadenas_X.txt` por cada
inciso, en vez de tener 4 copias del script.

---

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
python3 AFD.py <archivo_configuracion> <archivo_cadenas>
```

Ejemplo:

```bash
python3 AFD.py conf_d.txt cadenas_d.txt
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

Reglas:

- El archivo tiene 5 secciones, identificadas por una palabra clave
  seguida de `:`. Las primeras 4 (`ESTADOS`, `ALFABETO`, `INICIAL`,
  `ACEPTACION`) pueden ir en cualquier orden, pero `TRANSICIONES` debe
  ser la última, porque **todo** lo que aparece después de esa línea se
  interpreta como una transición (`origen,simbolo,destino`).
- Las líneas vacías y las que empiezan con `#` se ignoran (sirven como
  comentarios).
- Si una cadena de entrada usa un símbolo fuera de `ALFABETO`, se
  rechaza automáticamente.
- Si no existe una transición definida para `(estado_actual, símbolo)`,
  el programa asume un **estado trampa implícito**: la cadena se
  rechaza en ese punto, sin que sea obligatorio declarar explícitamente
  un estado trampa con auto-bucles (aunque también se puede declarar
  uno de forma explícita, como se hizo en el inciso d) con el estado
  `qt`).

### 3.3 Formato del archivo de cadenas (`cadenas.txt`)

```
# Comentario de ejemplo
EPSILON
a
ab
abb
```

Reglas:

- Una cadena de entrada por línea, sin espacios.
- Líneas vacías y líneas que empiezan con `#` se ignoran (sirven para
  documentar el archivo de pruebas).
- Para probar la **cadena vacía** (ε) hay que escribir literalmente
  `EPSILON` (o sus sinónimos `LAMBDA` / `EMPTY`, sin distinguir
  mayúsculas de minúsculas), ya que una línea realmente vacía se ignora.

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

El script está dividido en 5 funciones, cada una con una responsabilidad
única:

### `error(msg)`
Función auxiliar centralizada para reportar errores: imprime el mensaje
por `stderr` con el prefijo `"Error: "` y termina el programa
(`sys.exit(1)`). Se usa en todos los puntos de validación de
`parse_conf()` y `leer_cadenas()` para no repetir la lógica de
"imprimir y salir".

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

### `main()`
Punto de entrada del programa:

1. Valida que se hayan pasado exactamente 2 argumentos por línea de
   comandos.
2. Llama a `parse_conf()` y `leer_cadenas()`.
3. Imprime un resumen de la configuración cargada (a modo de
   verificación visual).
4. Para cada cadena de prueba, llama a `simular()`, imprime la
   secuencia de movimientos con `imprimir_secuencia()`, y muestra si fue
   ACEPTADA o RECHAZADA.

---

## 5. Diseño de los autómatas (`conf_a.txt` … `conf_d.txt`)

### a), b) y c) — equivalentes a `(a|b)*`

Como se explicó en la sección 1.1, los tres lenguajes son `Σ*`
(cualquier cadena sobre `{a,b}`). El AFD resultante es el más simple
posible: **un solo estado**, que es a la vez inicial y de aceptación,
con auto-transiciones para ambos símbolos:

```
ESTADOS: q0
ALFABETO: a,b
INICIAL: q0
ACEPTACION: q0
TRANSICIONES:
q0,a,q0
q0,b,q0
```

### d) — `b* a b b (a|b)*`

Este autómata sí necesita varios estados porque el lenguaje es
restrictivo:

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

---

## 6. Casos de prueba (`cadenas_a.txt` … `cadenas_d.txt`)

Se creó un archivo de cadenas independiente para cada inciso, con casos
pensados específicamente para el lenguaje de ese autómata:

- **`cadenas_a.txt`, `cadenas_b.txt`, `cadenas_c.txt`** — incluyen la
  cadena vacía y varias combinaciones de `a`/`b` de distinta longitud
  (incluida `ababbab`, la del enunciado original). Todas deben dar
  **ACEPTADA**, ya que el lenguaje es `Σ*`. Se incluye además la cadena
  `abc`, que contiene un símbolo fuera del alfabeto, para comprobar el
  manejo de errores del simulador (debe dar **RECHAZADA**).

- **`cadenas_d.txt`** — incluye dos bloques de casos:
  - Cadenas que **deben aceptarse**: `abb`, `babb`, `bbabb`, `abba`,
    `bbabbaa`, etc. (todas de la forma `b* a b b (a|b)*`).
  - Cadenas que **deben rechazarse**: la cadena vacía, cadenas sin `a`,
    cadenas donde la `a` no va seguida de `"bb"` (como `ababbab`, la del
    enunciado original, y `aabb`), y `abc` (símbolo inválido).

Puedes agregar o quitar líneas libremente en cualquiera de estos
archivos para probar más casos, siempre respetando el formato descrito
en la sección 3.3.

---

## 7. Cómo ejecutar el proyecto (Ubuntu / Linux)

1. Verifica que tengas Python 3 instalado:

   ```bash
   python3 --version
   ```

2. Clona o descarga este repositorio y entra a la carpeta:

   ```bash
   cd AFD
   ```

3. Ejecuta cualquiera de los 4 incisos:

   ```bash
   python3 AFD.py conf_a.txt cadenas_a.txt
   python3 AFD.py conf_b.txt cadenas_b.txt
   python3 AFD.py conf_c.txt cadenas_c.txt
   python3 AFD.py conf_d.txt cadenas_d.txt
   ```

También puedes combinar libremente cualquier `conf_X.txt` con cualquier
`cadenas_X.txt` (o con un archivo propio que sigas creando con el mismo
formato), sin necesidad de modificar `AFD.py`:

```bash
python3 AFD.py conf_d.txt cadenas_propias.txt
```

---

## 8. Resultados esperados (resumen)

| Inciso | Lenguaje real          | ¿Acepta `ababbab`? |
|--------|--------------------------|----------------------|
| a)     | `Σ*` (cualquier cadena)   | ✅ Sí                  |
| b)     | `Σ*` (cualquier cadena)   | ✅ Sí                  |
| c)     | `Σ*` (cualquier cadena)   | ✅ Sí                  |
| d)     | `b* a b b (a\|b)*`        | ❌ No                  |

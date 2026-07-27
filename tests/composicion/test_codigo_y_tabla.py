"""Los dos tipos de bloque que agrega el frente del libro impreso.

Se agregan sin tocar el esquema: `tipo` es cadena libre, y la regla 1 del
contrato ya preveia que llegaran `tabla` y otros.
"""

from ctex.composicion.bloques import componer_codigo, componer_tabla


# ---------------------------------------------------------------- codigo


def test_un_listado_conserva_sus_lineas():
    fragmento = componer_codigo({"lineas": ["int main()", "return 0;"]})
    assert "int main()" in fragmento
    assert "return 0;" in fragmento
    assert fragmento.count("\\\\") == 1  # un salto entre las dos lineas


def test_la_sangria_se_conserva():
    fragmento = componer_codigo({"lineas": ["if (x) {", "    return 1;", "}"]})
    assert "~~~~return 1;" in fragmento


def test_el_listado_va_en_su_entorno_y_no_en_verbatim():
    fragmento = componer_codigo({"lineas": ["x = 1"]})
    assert fragmento.startswith("\\begin{ctexcodigo}")
    assert fragmento.endswith("\\end{ctexcodigo}")
    assert "verbatim" not in fragmento


def test_un_listado_vacio_no_revienta():
    fragmento = componer_codigo({"lineas": []})
    assert "ctexcodigo" in fragmento


# ---- seguridad: el codigo es texto de un tercero y no puede ejecutar nada


def test_una_barra_invertida_en_el_codigo_queda_inerte():
    fragmento = componer_codigo({"lineas": ["printf(\"hola\\n\");"]})
    assert "\\textbackslash{}" in fragmento


def test_write18_en_el_codigo_no_llega_como_comando():
    fragmento = componer_codigo({"lineas": ["\\write18{rm -rf /}"]})
    assert "\\write18" not in fragmento
    assert "\\textbackslash{}write18" in fragmento


def test_no_se_puede_cerrar_el_entorno_desde_el_contenido():
    # El ataque que hace peligroso a verbatim: si el contenido puede escribir
    # la cadena de cierre, se sale del entorno y lo que siga es LaTeX.
    fragmento = componer_codigo({
        "lineas": ["\\end{ctexcodigo}", "\\input{/etc/passwd}"],
    })
    assert fragmento.count("\\end{ctexcodigo}") == 1  # solo el de verdad, al final
    assert "\\input{" not in fragmento


def test_la_notacion_caret_en_el_codigo_queda_inerte():
    fragmento = componer_codigo({"lineas": ["\\^^77rite18{x}"]})
    assert "^^" not in fragmento


# ---------------------------------------------------------------- tabla


def test_una_tabla_lleva_sus_celdas():
    fragmento = componer_tabla({
        "encabezado": ["Operacion", "Tiempo"],
        "filas": [["Buscar", "O(log n)"]],
    })
    assert "Operacion & Tiempo" in fragmento
    assert "Buscar & O(log n)" in fragmento


def test_el_numero_de_columnas_sale_del_encabezado():
    fragmento = componer_tabla({
        "encabezado": ["a", "b", "c"],
        "filas": [["1", "2", "3"]],
    })
    assert "\\begin{tabular}{lll}" in fragmento


def test_sin_encabezado_las_columnas_salen_de_la_primera_fila():
    fragmento = componer_tabla({"filas": [["1", "2"]]})
    assert "\\begin{tabular}{ll}" in fragmento


def test_una_fila_corta_se_rellena_en_vez_de_romper_la_tabla():
    fragmento = componer_tabla({
        "encabezado": ["a", "b", "c"],
        "filas": [["1"]],
    })
    assert "1 &  &  \\\\" in fragmento


def test_una_fila_larga_se_recorta():
    fragmento = componer_tabla({"encabezado": ["a", "b"], "filas": [["1", "2", "3"]]})
    assert "1 & 2 \\\\" in fragmento
    assert "3" not in fragmento.split("\\hline")[-2]


def test_una_tabla_sin_columnas_se_degrada_en_vez_de_reventar():
    fragmento = componer_tabla({"filas": []})
    assert "ctexdegradado" in fragmento


def test_un_ampersand_en_una_celda_no_agrega_una_columna():
    # Sin escapar, "A & B" partiria la celda en dos y la tabla no compilaria.
    fragmento = componer_tabla({"encabezado": ["x"], "filas": [["A & B"]]})
    assert "A \\& B" in fragmento
    assert fragmento.count("\\begin{tabular}{l}") == 1


def test_un_comando_en_una_celda_queda_inerte():
    fragmento = componer_tabla({"encabezado": ["x"], "filas": [["\\input{/etc/passwd}"]]})
    assert "\\input{" not in fragmento
    assert "\\textbackslash{}input" in fragmento

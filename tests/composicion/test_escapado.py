from ctex.composicion.escapado import (
    comandos_no_permitidos,
    escapar,
    motivos_de_rechazo,
    notacion_peligrosa,
)


def test_escapa_los_caracteres_especiales_de_latex():
    assert escapar("100% & 50$") == r"100\% \& 50\$"
    assert escapar("a_b^c") == r"a\_b\textasciicircum{}c"
    assert escapar("#1 {x}") == r"\#1 \{x\}"


def test_la_barra_invertida_no_cascadea():
    # \textbackslash{} introduce llaves. Si el escapado hiciera varias pasadas,
    # esas llaves se volverian a escapar y el resultado seria basura.
    assert escapar("\\") == r"\textbackslash{}"


def test_un_intento_de_inyeccion_queda_inerte():
    peligro = r"\write18{rm -rf /}"
    resultado = escapar(peligro)
    assert r"\write18" not in resultado
    assert resultado.startswith(r"\textbackslash{}write18")


def test_el_texto_sin_caracteres_especiales_no_cambia():
    assert escapar("Series de Fourier") == "Series de Fourier"


def test_una_ecuacion_normal_no_tiene_comandos_prohibidos():
    assert comandos_no_permitidos(r"f(x)=\sum_{n=1}^{6} a_n \cos(nx)") == set()


def test_write18_es_un_comando_prohibido():
    assert comandos_no_permitidos(r"\write18{ls}") == {"write"}


def test_input_es_un_comando_prohibido():
    assert comandos_no_permitidos(r"\input{/etc/passwd}") == {"input"}


def test_def_es_un_comando_prohibido():
    # Bomba de expansion: \def\x{\x\x}\x
    assert "def" in comandos_no_permitidos(r"\def\x{\x\x}\x")


def test_devuelve_todos_los_prohibidos_no_solo_el_primero():
    assert comandos_no_permitidos(r"\input{a} \write18{b}") == {"input", "write"}


# La notacion ^^ de TeX codifica un caracter por su valor hexadecimal, ANTES de
# que exista el nombre del comando. `\^^77rite18` es `\write18` para el motor,
# pero para una busqueda de \[a-zA-Z]+ no hay ningun comando que filtrar.
# Verificado compilando: `\^^73ection{X}` produce una seccion de verdad.


def test_la_notacion_caret_no_la_ve_la_lista_blanca():
    # Documenta el limite real de comandos_no_permitidos: no es su trabajo.
    assert comandos_no_permitidos(r"\^^77rite18{ls}") == set()


def test_la_notacion_caret_se_detecta():
    assert notacion_peligrosa(r"\^^77rite18{ls}") == {"^^"}


def test_la_notacion_caret_de_cuatro_digitos_tambien():
    # XeTeX y LuaTeX admiten ^^^^0077. Tambien empieza con dos acentos.
    assert notacion_peligrosa(r"\^^^^0077rite18{ls}") == {"^^"}


def test_un_superindice_normal_no_es_notacion_peligrosa():
    # `x^2` y `x^{n+1}` son matematicas legitimas y deben pasar. Lo que nunca
    # aparece en matematicas escritas a mano son dos acentos seguidos.
    assert notacion_peligrosa(r"x^2 + y^{n+1}") == set()


def test_los_motivos_de_rechazo_juntan_las_dos_defensas():
    assert motivos_de_rechazo(r"f(x)=\sum_{n=1}^{6} a_n \cos(nx)") == set()
    assert motivos_de_rechazo(r"\write18{ls}") == {"write"}
    assert motivos_de_rechazo(r"\^^77rite18{ls}") == {"^^"}
    assert motivos_de_rechazo(r"\input{a} \^^77rite18{b}") == {"input", "^^"}

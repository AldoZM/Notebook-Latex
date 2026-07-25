from ctex.composicion.escapado import comandos_no_permitidos, escapar


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

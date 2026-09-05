import json
from pathlib import Path

from espresso3d.config import PipelineConfig
from espresso3d.library import store
from espresso3d.pipeline import Resultado


def criar_modelo(raiz: Path, nome: str, faces: int = 4000) -> Path:
    pasta = raiz / f"2026-09-05_120000_{nome}"
    pasta.mkdir(parents=True)
    (pasta / f"{nome}.glb").write_bytes(b"x" * 2048)
    (pasta / "source.png").write_bytes(b"y" * 512)

    resultado = Resultado(
        pasta=pasta,
        arquivos=[pasta / f"{nome}.glb"],
        partes=1,
        estatisticas={"faces": faces},
        duracao_s=12.3,
    )
    store.registrar(resultado, PipelineConfig(), nome)
    return pasta


def test_registrar_escreve_meta(tmp_path):
    pasta = criar_modelo(tmp_path, "xicara")
    meta = json.loads((pasta / "meta.json").read_text(encoding="utf-8"))

    assert meta["nome"] == "xicara"
    assert meta["faces"] == 4000
    assert meta["formatos"] == ["glb"]
    assert meta["config"]["engine"] == "stable_fast_3d"


def test_listar_le_o_que_foi_registrado(tmp_path):
    criar_modelo(tmp_path, "xicara")
    criar_modelo(tmp_path, "vaso", faces=8000)

    itens = store.listar(tmp_path)
    assert {i.nome for i in itens} == {"xicara", "vaso"}
    assert all(i.bytes > 0 for i in itens)
    assert all(i.preview is not None for i in itens)


def test_listar_ignora_pasta_sem_meta(tmp_path):
    criar_modelo(tmp_path, "bom")
    (tmp_path / "pasta_solta").mkdir()

    assert len(store.listar(tmp_path)) == 1


def test_listar_ignora_meta_corrompido(tmp_path):
    pasta = criar_modelo(tmp_path, "quebrado")
    (pasta / "meta.json").write_text("{ isso não é json", encoding="utf-8")

    assert store.listar(tmp_path) == []


def test_listar_raiz_inexistente(tmp_path):
    assert store.listar(tmp_path / "nao_existe") == []


def test_espaco_total(tmp_path):
    criar_modelo(tmp_path, "a")
    criar_modelo(tmp_path, "b")

    quantidade, bytes_totais = store.espaco_total(tmp_path)
    assert quantidade == 2
    assert bytes_totais > 4000


def test_apagar_definitivo_remove_a_pasta(tmp_path):
    pasta = criar_modelo(tmp_path, "descartavel")

    assert store.apagar(pasta, para_lixeira=False) is True
    assert not pasta.exists()


def test_apagar_pasta_inexistente(tmp_path):
    assert store.apagar(tmp_path / "fantasma") is False


def test_apagar_varios(tmp_path):
    pastas = [criar_modelo(tmp_path, n) for n in ("a", "b", "c")]

    assert store.apagar_varios(pastas[:2], para_lixeira=False) == 2
    assert len(store.listar(tmp_path)) == 1


def test_apagar_cai_para_definitivo_sem_send2trash(tmp_path, monkeypatch):
    """Sem a lixeira disponível, apaga mesmo assim em vez de falhar."""
    pasta = criar_modelo(tmp_path, "sem_lixeira")

    import builtins

    original = builtins.__import__

    def sem_send2trash(nome, *args, **kwargs):
        if nome == "send2trash":
            raise ImportError("simulando ausência")
        return original(nome, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", sem_send2trash)
    assert store.apagar(pasta, para_lixeira=True) is True
    assert not pasta.exists()

"""Configuração de uma geração.

Uma única instância de :class:`PipelineConfig` é compartilhada pelas abas
"Imagem → 3D" e "Lote": o lote não tem painel próprio, ele herda o que
estiver configurado na aba de imagem única.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum


class Topologia(str, Enum):
    """Como a malha é reduzida até a contagem de polígonos alvo."""

    ALTO_DETALHE = "alto_detalhe"
    SMART = "smart_topology"


class Pose(str, Enum):
    NENHUM = "nenhum"
    T_POSE = "t_pose"
    A_POSE = "a_pose"
    CUSTOM = "customizada"


class Licenca(str, Enum):
    PRIVADA = "privada"
    COMERCIAL = "comercial"


class ResolucaoTextura(str, Enum):
    PADRAO = "padrao"
    ULTRA_2K = "ultra_2k"

    @property
    def pixels(self) -> int:
        return 1024 if self is ResolucaoTextura.PADRAO else 2048


@dataclass(frozen=True)
class Formato:
    """Um formato de exportação e o que ele consegue carregar."""

    ext: str
    grupo: str
    backend: str  # "trimesh" (puro Python) ou "blender" (script headless)
    carrega_rig: bool
    carrega_textura: bool
    nota: str = ""


#: Catálogo de formatos, agrupado pelo destino do modelo — não por extensão.
FORMATOS: dict[str, Formato] = {
    "glb": Formato("glb", "Web e AR no Android", "trimesh", True, True, "AR Web"),
    "gltf": Formato("gltf", "Web e AR no Android", "trimesh", True, True),
    "usdz": Formato("usdz", "AR no iPhone / Vision Pro", "blender", True, True, "AR iOS"),
    "usdc": Formato("usdc", "Pipelines USD / Omniverse", "blender", True, True),
    "usda": Formato("usda", "Pipelines USD / Omniverse", "blender", True, True),
    "fbx": Formato("fbx", "Unity / Unreal / VR", "blender", True, True),
    "vrm": Formato("vrm", "Unity / Unreal / VR", "blender", True, True, "avatar · beta"),
    "obj": Formato("obj", "Edição e uso geral", "trimesh", False, True, "vai zipado com .mtl"),
    "ply": Formato("ply", "Edição e uso geral", "trimesh", False, False),
    "dae": Formato("dae", "Edição e uso geral", "blender", True, True),
    "blend": Formato("blend", "Edição e uso geral", "blender", True, True),
    "stl": Formato("stl", "Impressão 3D", "trimesh", False, False),
    "3mf": Formato("3mf", "Impressão 3D", "trimesh", False, True),
}

POLY_MIN, POLY_MAX = 500, 20_000
MAX_IMAGENS_LOTE = 10


@dataclass
class PipelineConfig:
    """Tudo que o usuário escolhe antes de gerar."""

    engine: str = "stable_fast_3d"
    topologia: Topologia = Topologia.ALTO_DETALHE
    poly_count_alvo: int = 4000
    gerar_textura: bool = True
    resolucao_textura: ResolucaoTextura = ResolucaoTextura.PADRAO
    pose: Pose = Pose.NENHUM
    pose_prompt: str = ""
    pose_ref_imagem: str | None = None
    dividir_partes: bool = False
    melhorar_imagem: bool = True
    licenca: Licenca = Licenca.PRIVADA
    formatos: list[str] = field(default_factory=lambda: ["glb"])

    # ------------------------------------------------------------------ #

    def validar(self) -> None:
        """Levanta ``ValueError`` com uma mensagem que o usuário entenda."""
        if not self.formatos:
            raise ValueError("Escolha pelo menos um formato de exportação.")

        desconhecidos = [f for f in self.formatos if f not in FORMATOS]
        if desconhecidos:
            raise ValueError(f"Formato desconhecido: {', '.join(desconhecidos)}")

        if not POLY_MIN <= self.poly_count_alvo <= POLY_MAX:
            raise ValueError(
                f"Contagem de polígonos deve ficar entre {POLY_MIN} e {POLY_MAX:,}."
                .replace(",", ".")
            )

        if self.pose is Pose.CUSTOM and not (self.pose_prompt.strip() or self.pose_ref_imagem):
            raise ValueError(
                "Pose personalizada precisa de uma descrição em texto "
                "ou de uma foto de referência."
            )

    def avisos(self) -> list[str]:
        """Perdas que o usuário precisa saber ANTES de gerar.

        Melhor avisar na hora de configurar do que entregar um arquivo
        sem textura e deixar a pessoa descobrir sozinha no Blender.
        """
        avisos: list[str] = []
        escolhidos = [FORMATOS[f] for f in self.formatos if f in FORMATOS]

        if self.gerar_textura:
            sem_textura = [f.ext for f in escolhidos if not f.carrega_textura]
            if sem_textura:
                avisos.append(
                    f".{', .'.join(sem_textura)} não guarda textura nem cor."
                )

        if self.pose is not Pose.NENHUM:
            sem_rig = [f.ext for f in escolhidos if not f.carrega_rig]
            if sem_rig:
                avisos.append(
                    f".{', .'.join(sem_rig)} não carrega esqueleto — "
                    "o rig será descartado nesses arquivos."
                )

        if "obj" in self.formatos:
            avisos.append(".obj sai zipado junto com o .mtl e as texturas.")

        return avisos

    @property
    def precisa_blender(self) -> list[str]:
        """Formatos escolhidos que só saem com o Blender instalado."""
        return [f for f in self.formatos if FORMATOS[f].backend == "blender"]

    @property
    def precisa_rig(self) -> bool:
        return self.pose is not Pose.NENHUM

    def como_dict(self) -> dict:
        d = asdict(self)
        for chave in ("topologia", "pose", "licenca", "resolucao_textura"):
            d[chave] = getattr(self, chave).value
        return d

    @classmethod
    def de_dict(cls, d: dict) -> "PipelineConfig":
        d = dict(d)
        conversoes = {
            "topologia": Topologia,
            "pose": Pose,
            "licenca": Licenca,
            "resolucao_textura": ResolucaoTextura,
        }
        for chave, tipo in conversoes.items():
            if chave in d and not isinstance(d[chave], tipo):
                d[chave] = tipo(d[chave])
        conhecidos = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in d.items() if k in conhecidos})


def formatos_por_grupo() -> dict[str, list[Formato]]:
    """Formatos agrupados por destino, na ordem em que aparecem na interface."""
    grupos: dict[str, list[Formato]] = {}
    for fmt in FORMATOS.values():
        grupos.setdefault(fmt.grupo, []).append(fmt)
    return grupos

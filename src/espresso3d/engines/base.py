"""Interface comum dos motores de geração 3D."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..config import Licenca, PipelineConfig


class DependenciaFaltando(RuntimeError):
    """Erro com instrução de instalação, em vez de um ImportError seco."""

    def __init__(self, pacote: str, como_instalar: str):
        super().__init__(
            f"'{pacote}' não está instalado.\n\nPara instalar:\n  {como_instalar}"
        )
        self.pacote = pacote
        self.como_instalar = como_instalar


@dataclass(frozen=True)
class InfoMotor:
    """Metadados que a interface mostra antes de o motor ser carregado."""

    id: str
    nome: str
    descricao: str
    vram_min_gb: float
    licenca_pesos: str
    uso_comercial: bool
    pbr: bool
    repo: str


class Motor(ABC):
    """Um gerador de malha 3D a partir de uma imagem.

    Os pesos são pesados (GB) e as dependências são específicas de cada
    projeto, então tudo é importado só na hora de gerar — assim o app abre
    normalmente numa máquina sem nada instalado e explica o que falta.
    """

    info: InfoMotor

    @abstractmethod
    def _gerar(self, imagem, cfg: PipelineConfig):
        """Devolve uma ``trimesh.Trimesh``. Implementado por cada motor."""

    def gerar(self, imagem, cfg: PipelineConfig):
        vram_livre = _vram()
        if vram_livre is not None and vram_livre + 0.5 < self.info.vram_min_gb:
            raise RuntimeError(
                f"{self.info.nome} precisa de ~{self.info.vram_min_gb:g} GB de VRAM "
                f"e a sua GPU tem {vram_livre:g} GB. "
                "Escolha um motor mais leve na lista."
            )
        return self._gerar(imagem, cfg)

    def compativel_com(self, licenca: Licenca) -> bool:
        if licenca is Licenca.COMERCIAL:
            return self.info.uso_comercial
        return True

    def __repr__(self) -> str:  # pragma: no cover - conveniência de debug
        return f"<Motor {self.info.id}>"


def _vram() -> float | None:
    from ..hardware import vram_gb

    return vram_gb()

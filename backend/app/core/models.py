"""Data models for contraídos"""

from dataclasses import dataclass


@dataclass
class Operation:
    """Representa una operación individual de contraído"""

    num_operacion: int
    año: int
    aplicacion: int
    num_contraido: str
    importe: float
    cpgc: int
    fase: str
    fecha: str
    tercero: str
    descripcion: str
    estado: str

    @property
    def is_arqueo(self) -> bool:
        """Operación de arqueo (positiva)"""
        return self.fase == "AINP"

    @property
    def is_cargo(self) -> bool:
        """Operación de cargo (negativa)"""
        return self.fase == "M;P"

    @property
    def is_valid_cargo(self) -> bool:
        """Cargo válido solo si estado == 4"""
        return self.is_cargo and (self.estado == 4 or self.estado == "4")

    @property
    def is_invalid_cargo(self) -> bool:
        """Cargo inválido o incompleto"""
        return self.is_cargo and self.estado != 4 and self.estado != "4"

    @property
    def effective_amount(self) -> float:
        """Importe efectivo considerando la fase y validez"""
        if self.is_arqueo:
            return self.importe
        elif self.is_valid_cargo:
            return -self.importe
        else:
            return 0  # Operaciones inválidas no cuentan

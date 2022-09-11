from abc import ABC, abstractmethod

class PatchConstructor(ABC):
    @classmethod
    @abstractmethod
    def get_type() -> str:
        pass

    @classmethod
    @abstractmethod
    def is_same_type(cls, obj) -> bool:
        pass

    @classmethod
    @abstractmethod
    def get_neighbor_verts(cls, obj) -> list:
        pass

    @classmethod
    @abstractmethod
    def get_patch(cls, obj, isBspline=True) -> list:  # List of bezier coef list (multiple patches)
        pass

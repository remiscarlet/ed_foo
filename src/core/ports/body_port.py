from abc import ABC, abstractmethod

from src.core.models.body_model import Body


class BodyPort(ABC):
    @abstractmethod
    def upsert_body(self, body: Body) -> Body:
        pass

    @abstractmethod
    def get_body(self, body_name: str) -> Body:
        pass

    @abstractmethod
    def delete_body(self, body_name: str) -> None:
        pass

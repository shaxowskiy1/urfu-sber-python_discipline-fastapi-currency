from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic, Optional

T = TypeVar('T')
ID = TypeVar('ID')


class CrudRepository(ABC, Generic[T, ID]):

    @abstractmethod
    def find_by_id(self, id: ID) -> Optional[T]:
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[T]:
        pass

    @abstractmethod
    def find_all(self) -> List[T]:
        pass

    @abstractmethod
    def create(self, entity: T) -> None:
        pass

    @abstractmethod
    def update(self, entity: T, id: ID) -> None:
        pass

    @abstractmethod
    def delete(self, id: ID) -> None:
        pass


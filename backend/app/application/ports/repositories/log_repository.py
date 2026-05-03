from abc import ABC, abstractmethod
from typing import List, Optional

from backend.app.domain.entities import log


class LogRepository(ABC):
    @abstractmethod
    def create_log(self, log: log.Log) -> log.Log:
        pass

    @abstractmethod
    def get_log_by_id(self, log_id: int) -> Optional[log.Log]:
        pass

    @abstractmethod
    def list_logs(self) -> List[log.Log]:
        pass

    @abstractmethod
    def list_logs_by_level(self, log_level: log.LogLevel) -> List[log.Log]:
        pass

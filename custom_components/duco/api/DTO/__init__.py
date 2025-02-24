from dataclasses import dataclass, asdict


@dataclass
class DTO:
    def asdict(self):
        return asdict(self)

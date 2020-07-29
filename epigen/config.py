import dataclasses

from typing import List


@dataclasses.dataclass
class EpiGenConfig:

    dir_input: str
    dir_output: str
    dir_output_build: str

    debug: bool = False
    backup: bool = False
    caching: bool = True

    ignore_list: List[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class EpiGenManifest:

    modules: List[str]

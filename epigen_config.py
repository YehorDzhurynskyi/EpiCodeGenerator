from typing import List

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json


@dataclass
@dataclass_json
class EpiGenConfig:

    dir_input: str
    dir_output: str
    dir_output_build: str

    debug: bool = False
    backup: bool = False

    ignore_list: List[str] = field(default_factory=list)


@dataclass
@dataclass_json
class EpiGenManifest:

    modules: List[str]

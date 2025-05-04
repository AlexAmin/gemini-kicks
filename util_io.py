import os
import tempfile
from datetime import datetime

from typing import Optional
from pydantic_core.core_schema import TimeSchema

TIMESTAMP = datetime.now().isoformat().replace(":", "_")


def get_temp_path(subfolder: str | None = None) -> str:
    path_components = [tempfile.gettempdir(), "llama-hoops", TIMESTAMP]
    if subfolder is not None:
        path_components.append(subfolder)
    output_dir = os.path.join(*path_components)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

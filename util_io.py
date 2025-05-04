import os
import tempfile


def get_temp_path(subfolder: str) -> str:
    output_dir = os.path.join(tempfile.gettempdir(), "llama-hoops", subfolder)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

from importlib import metadata

from langchain_compass.toolkits import LangchainCompassToolkit
from langchain_compass.tools import LangchainCompassTool

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = ""
del metadata  # optional, avoids polluting the results of dir(__package__)

__all__ = [
    "LangchainCompassToolkit",
    "LangchainCompassTool",
    "__version__",
]

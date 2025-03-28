from importlib import metadata

from langchain_compass.chat_models import ChatLangchainCompass
from langchain_compass.document_loaders import LangchainCompassLoader
from langchain_compass.embeddings import LangchainCompassEmbeddings
from langchain_compass.retrievers import LangchainCompassRetriever
from langchain_compass.toolkits import LangchainCompassToolkit
from langchain_compass.tools import LangchainCompassTool
from langchain_compass.vectorstores import LangchainCompassVectorStore

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = ""
del metadata  # optional, avoids polluting the results of dir(__package__)

__all__ = [
    "ChatLangchainCompass",
    "LangchainCompassVectorStore",
    "LangchainCompassEmbeddings",
    "LangchainCompassLoader",
    "LangchainCompassRetriever",
    "LangchainCompassToolkit",
    "LangchainCompassTool",
    "__version__",
]

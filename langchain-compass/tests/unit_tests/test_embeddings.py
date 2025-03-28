"""Test embedding model integration."""

from typing import Type

from langchain_compass.embeddings import LangchainCompassEmbeddings
from langchain_tests.unit_tests import EmbeddingsUnitTests


class TestParrotLinkEmbeddingsUnit(EmbeddingsUnitTests):
    @property
    def embeddings_class(self) -> Type[LangchainCompassEmbeddings]:
        return LangchainCompassEmbeddings

    @property
    def embedding_model_params(self) -> dict:
        return {"model": "nest-embed-001"}

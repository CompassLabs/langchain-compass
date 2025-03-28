"""Test LangchainCompass embeddings."""

from typing import Type

from langchain_compass.embeddings import LangchainCompassEmbeddings
from langchain_tests.integration_tests import EmbeddingsIntegrationTests


class TestParrotLinkEmbeddingsIntegration(EmbeddingsIntegrationTests):
    @property
    def embeddings_class(self) -> Type[LangchainCompassEmbeddings]:
        return LangchainCompassEmbeddings

    @property
    def embedding_model_params(self) -> dict:
        return {"model": "nest-embed-001"}

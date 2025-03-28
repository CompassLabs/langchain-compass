from typing import Generator

import pytest
from langchain_compass.vectorstores import LangchainCompassVectorStore
from langchain_core.vectorstores import VectorStore
from langchain_tests.integration_tests import VectorStoreIntegrationTests


class TestLangchainCompassVectorStore(VectorStoreIntegrationTests):
    @pytest.fixture()
    def vectorstore(self) -> Generator[VectorStore, None, None]:  # type: ignore
        """Get an empty vectorstore for unit tests."""
        store = LangchainCompassVectorStore(self.get_embeddings())
        # note: store should be EMPTY at this point
        # if you need to delete data, you may do so here
        try:
            yield store
        finally:
            # cleanup operations, or deleting data
            pass

# langchain-compass

This package contains the LangChain integration with LangchainCompass

## Installation

```bash
pip install -U langchain-compass
```

And you should configure credentials by setting the following environment variables:

* TODO: fill this out

## Chat Models

`ChatLangchainCompass` class exposes chat models from LangchainCompass.

```python
from langchain_compass import ChatLangchainCompass

llm = ChatLangchainCompass()
llm.invoke("Sing a ballad of LangChain.")
```

## Embeddings

`LangchainCompassEmbeddings` class exposes embeddings from LangchainCompass.

```python
from langchain_compass import LangchainCompassEmbeddings

embeddings = LangchainCompassEmbeddings()
embeddings.embed_query("What is the meaning of life?")
```

## LLMs
`LangchainCompassLLM` class exposes LLMs from LangchainCompass.

```python
from langchain_compass import LangchainCompassLLM

llm = LangchainCompassLLM()
llm.invoke("The meaning of life is")
```

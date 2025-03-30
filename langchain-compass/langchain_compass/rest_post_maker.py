from typing import Any, Optional, Type

import requests
from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel


def make_post_tool(
    name1: str,
    description1: str,
    args_schema1: Type[BaseModel],
    return_direct1: bool,
    url1: str,
    response_type1: type,
    api_key: Optional[str] = None,
    example_args1: Optional[dict] = None,
) -> type[BaseTool]:
    class PostRequestTool(BaseTool):
        name: str = name1
        description: str = description1
        url: str = url1
        args_schema: Type[BaseModel] = args_schema1
        return_direct: bool = return_direct1
        verbose: bool = True
        response_type: Any = response_type1
        example_args: Optional[dict] = example_args1

        def _run(
            self,
            run_manager: CallbackManagerForToolRun | None = None,
            **kwargs: Any,
        ) -> response_type1:  # type: ignore
            """Use the tool."""

            headers = {"accept": "application/json", "Content-Type": "application/json"}
            if api_key is not None:
                headers["x-api-key"] = api_key

            response = requests.post(
                self.url,
                json=self.args_schema(**kwargs).model_dump(mode="json"),
                headers=headers,
            )
            if response.status_code != 200:
                raise Exception(response.text)
            if self.return_direct:  # TODO
                if "image" in response.json():
                    return {"type": "image", "content": response.json()["image"]}
                return {"type": "unsigned_transaction", "content": response.json()}
            return self.response_type(**response.json())

    PostRequestTool.__name__ = name1
    return PostRequestTool

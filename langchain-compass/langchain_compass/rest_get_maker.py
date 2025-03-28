from typing import Any, Optional

import requests
from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool


def make_get_tool(
    name1: str,
    description1: str,
    return_direct1: bool,
    args_schema1: Any,
    url1: str,
    response_type1: type,
    api_key: Optional[str] = None,
) -> type[BaseTool]:
    class GetRequestTool(BaseTool):
        name: str = name1
        description: str = description1
        url: str = url1
        return_direct: bool = return_direct1
        args_schema: Any = args_schema1
        verbose: bool = True
        response_type: Any = response_type1

        def _run(
            self, run_manager: CallbackManagerForToolRun | None = None, **kwargs: Any
        ) -> response_type1:  # type: ignore
            headers = {"accept": "application/json", "Content-Type": "application/json"}
            if api_key is not None:
                headers["x-api-key"] = api_key
            params = {
                key: value
                for key, value in kwargs.items()
                if "{" + key + "}" not in self.url
            }

            response = requests.get(
                self.url.format(**kwargs), params=params, headers=headers
            )
            if response.status_code != 200:
                raise Exception(response.text)
            data = response.json()
            if isinstance(data, list):
                try:
                    result = self.response_type(response.json())
                except:  # noqa: E722
                    result = [self.response_type(**i) for i in data][0]  # strange hack
            else:
                result = self.response_type(**response.json())

            return result

    GetRequestTool.__name__ = name1
    return GetRequestTool

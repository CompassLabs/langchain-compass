import importlib
import json
import os
from functools import lru_cache
from typing import Any, Callable, List, Optional, Type

import requests
from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel
from pydantic._internal._model_construction import ModelMetaclass

from langchain_compass.params_converter import generate_pydantic_model


@lru_cache(maxsize=None)
def _get_request_cached(openapi_json_address: str) -> str:
    return requests.get(openapi_json_address).text


def snake_to_camel(snake_str: str) -> str:
    return "".join(
        word[:1].upper() + word[1:] for word in snake_str.strip("_").split("_")
    )


class PostRequestTool(BaseTool):
    name: str
    description: str
    url: str
    args_schema: Type[BaseModel]
    return_direct: bool
    verbose: bool
    response_type: Any
    example_args: Optional[dict]
    api_key: Optional[str] = None

    def _run(
        self,
        run_manager: CallbackManagerForToolRun | None = None,
        **kwargs: Any,
    ) -> dict:  # type: ignore
        """Use the tool."""

        headers = {"accept": "application/json", "Content-Type": "application/json"}
        if self.api_key is not None:
            headers["x-api-key"] = self.api_key

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


class GetRequestTool(BaseTool):
    name: str
    description: str
    url: str
    return_direct: bool
    args_schema: Any
    verbose: bool = True
    response_type: Any
    api_key: Optional[str] = None

    def _run(
        self, run_manager: CallbackManagerForToolRun | None = None, **kwargs: Any
    ) -> dict:  # type: ignore
        headers = {"accept": "application/json", "Content-Type": "application/json"}
        if self.api_key is not None:
            headers["x-api-key"] = self.api_key
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


def make_tools(
    openapi_json_address: str,
    api_key: Optional[str],
    func_check_direct_return: Callable[[ModelMetaclass], bool],
) -> List[BaseTool]:
    try:
        with open("temp.json", "w") as apifile:
            apifile.write(_get_request_cached(openapi_json_address))
        with open("temp.json", "r") as file:
            openapi_data = json.load(file)
        os.system(
            "datamodel-codegen --input temp.json --input-file-type \
            openapi --output-model-type pydantic_v2.BaseModel \
            --openapi-scopes=schemas  --output schemas.py "
        )
        import schemas  # type: ignore

        importlib.reload(schemas)
        # importlib.reload(paths)
    except:  # noqa: E722
        raise Exception(f"Failed to generate tools for {openapi_json_address}")

    def get_response_schema_name(endpoint: dict) -> str:
        return endpoint["responses"]["200"]["content"]["application/json"]["schema"][
            "$ref"
        ].split("/")[-1]

    tools = []
    for path in openapi_data["paths"].keys():
        if "patch" in openapi_data["paths"][path]:
            raise ValueError("We don't support patch requests yet.")
        if "update" in openapi_data["paths"][path]:
            raise ValueError("We don't support update requests yet.")

        if "post" in openapi_data["paths"][path]:
            endpoint = openapi_data["paths"][path]["post"]

            schema_name = endpoint["requestBody"]["content"]["application/json"][
                "schema"
            ]["$ref"].split("/")[-1]

            url: str = (
                openapi_data["servers"][0]["url"].rstrip("/") + "/" + path.lstrip("/")
            )
            tool_name = path.replace("/v0/", "").replace("/", "_") + "_"  # TODO
            description: str = (
                endpoint["description"]
                if "description" in endpoint
                else endpoint["summary"]
            )
            response_schema_name = get_response_schema_name(endpoint)
            response_type = getattr(schemas, snake_to_camel(response_schema_name))
            example_args = (
                openapi_data["components"]["schemas"][schema_name]["example"]
                if "example" in openapi_data["components"]["schemas"][schema_name]
                else None
            )

            return_direct: bool = (
                False
                if func_check_direct_return is None
                else func_check_direct_return(response_type)
            )

            tool = PostRequestTool(
                name=tool_name,
                description=description,
                url=url,
                args_schema=getattr(schemas, schema_name.replace("_", "")),
                return_direct=return_direct,
                verbose=False,
                response_type=response_type,
                example_args=example_args,
                api_key="123",
            )

            tool.__name__ = tool_name
            tools.append(tool)

        if "get" in openapi_data["paths"][path]:
            endpoint = openapi_data["paths"][path]["get"]

            response_schema_name = get_response_schema_name(endpoint)
            tool_name = path.replace("/v0/", "").replace("/", "_") + "_"  # TODO

            if "parameters" in endpoint:
                Params = generate_pydantic_model(
                    model_name="Params", parameters=endpoint["parameters"]
                )
            else:
                Params = None

            url = (
                openapi_data["servers"][0]["url"].rstrip("/") + "/" + path.lstrip("/"),
            )

            tool = GetRequestTool(
                name=tool_name,
                description=endpoint["description"],
                url=url,
                return_direct=False,
                args_schema=Params,
                response_type=getattr(schemas, response_schema_name.replace("_", "")),
                api_key="123",
            )

            tool.__name__ = tool_name
            tools.append(tool)

    os.remove("schemas.py")
    return tools


if __name__ == "__main__":
    make_tools(
        openapi_json_address="https://api.compasslabs.ai/openapi.json",
        api_key=None,
        func_check_direct_return=lambda x: True,
    )

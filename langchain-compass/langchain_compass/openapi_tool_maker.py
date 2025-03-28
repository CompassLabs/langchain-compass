import importlib

###########
import json
import os
from functools import lru_cache
from typing import Callable, List, Optional

import requests
from langchain_core.tools import BaseTool
from pydantic._internal._model_construction import ModelMetaclass

from langchain_compass.params_converter import generate_pydantic_model
from langchain_compass.rest_get_maker import make_get_tool
from langchain_compass.rest_post_maker import make_post_tool


@lru_cache(maxsize=None)
def _get_request_cached(openapi_json_address: str) -> str:
    return requests.get(openapi_json_address).text


def snake_to_camel(snake_str: str) -> str:
    return "".join(
        word[:1].upper() + word[1:] for word in snake_str.strip("_").split("_")
    )


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

            response_schema_name = get_response_schema_name(endpoint)
            tool_name = path.replace("/v0/", "").replace("/", "_") + "_"  # TODO
            response_type = getattr(schemas, snake_to_camel(response_schema_name))
            tools.append(
                make_post_tool(
                    url1=openapi_data["servers"][0]["url"].rstrip("/")
                    + "/"
                    + path.lstrip("/"),  # ugly but gets the job done
                    name1=tool_name,
                    description1=endpoint["description"]
                    if "description" in endpoint
                    else endpoint["summary"],
                    args_schema1=getattr(schemas, schema_name.replace("_", "")),
                    return_direct1=False
                    if func_check_direct_return is None
                    else func_check_direct_return(response_type),
                    response_type1=response_type,
                )()
            )
        if "get" in openapi_data["paths"][path]:
            endpoint = openapi_data["paths"][path]["get"]

            response_schema_name = get_response_schema_name(endpoint)
            tool_name = path.replace("/v0/", "").replace("/", "_") + "_"  # TODO

            if "parameters" in endpoint:
                # for parameter in endpoint['parameters']:
                #     print(parameter)
                #     print(parameter['schema'])
                Params = generate_pydantic_model(
                    model_name="Params", parameters=endpoint["parameters"]
                )
            else:
                Params = None

            tools.append(
                make_get_tool(
                    url1=openapi_data["servers"][0]["url"].rstrip("/")
                    + "/"
                    + path.lstrip("/"),  # ugly but gets the job done
                    name1=tool_name,
                    description1=endpoint["description"]
                    if "description" in endpoint
                    else endpoint["summary"],
                    args_schema1=Params,
                    return_direct1=False,
                    response_type1=getattr(
                        schemas, response_schema_name.replace("_", "")
                    ),
                )()
            )

    os.remove("schemas.py")
    return tools

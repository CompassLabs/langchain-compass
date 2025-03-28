from typing import Callable, List, Optional

from langchain_core.tools import BaseTool
from pydantic._internal._model_construction import ModelMetaclass


def make_tools(
    openapi_json_address: str,
    api_key: Optional[str],
    func_check_direct_return: Callable[[ModelMetaclass], bool],
) -> List[BaseTool]:
    return []

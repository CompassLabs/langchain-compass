from typing import Any

from langchain_tests.unit_tests import ToolsUnitTests

from langchain_compass.toolkits import LangchainCompassToolkit

tools = LangchainCompassToolkit(compass_api_key=None).get_tools()


for tool in tools:
    class_name = f"Test{tool.name.capitalize()}Tool"

    def make_class(tool: Any) -> type[ToolsUnitTests]:
        class _ToolTest(ToolsUnitTests):
            @property
            def tool_constructor(self) -> type[tool.__class__]:
                return tool.__class__

            @property
            def tool_constructor_params(self) -> dict:
                return {}

            @property
            def tool_invoke_params_example(self) -> dict:
                return tool.example_args or {}

        return _ToolTest

    # Dynamically add it to the module so pytest can discover it
    globals()[class_name] = make_class(tool)

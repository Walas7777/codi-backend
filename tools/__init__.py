from .base_tool import Tool, ToolManager, tool_manager
from .file_tool import FileTool
from .system_tool import SystemTool
from .code_tool import CodeTool

# Registrar herramientas en el ToolManager
tool_manager.register_tool(FileTool())
tool_manager.register_tool(SystemTool())
tool_manager.register_tool(CodeTool())

__all__ = ["Tool", "ToolManager", "tool_manager", "FileTool", "SystemTool", "CodeTool"]

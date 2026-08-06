"""
Application Use Case for Autonomous Agent Task Execution.
Orchestrates reasoning loops, memory lookup, LLM call, tool execution, and trajectory logging.
"""

from typing import List, Optional
from jarvis.domain.entities import AgentProcess, MemoryRecord
from jarvis.domain.exceptions import TaskExecutionError
from jarvis.domain.ports import LLMProviderPort, ToolRegistryPort, VectorStorePort
from jarvis.domain.value_objects import MemoryType, ProcessStatus


class ExecuteTaskUseCase:
    """
    Core Agent Task Orchestration Loop.
    Executes iterative ReAct / Tool-Use steps for an AgentProcess.
    """

    def __init__(
        self,
        llm_provider: LLMProviderPort,
        tool_registry: ToolRegistryPort,
        vector_store: Optional[VectorStorePort] = None
    ) -> None:
        self.llm_provider = llm_provider
        self.tool_registry = tool_registry
        self.vector_store = vector_store

    async def execute(self, process: AgentProcess) -> AgentProcess:
        process.update_status(ProcessStatus.RUNNING)
        ctx = process.task_context

        # 1. Retrieve relevant memory context if vector store available
        relevant_memories: List[MemoryRecord] = []
        if self.vector_store:
            try:
                relevant_memories = await self.vector_store.search_memory(ctx.goal, top_k=3)
            except Exception:
                pass  # Non-blocking memory retrieval fallback

        memory_context_str = ""
        if relevant_memories:
            memory_context_str = "\nRelevant Prior Memory Context:\n" + "\n".join(
                [f"- [{mem.memory_type.value}] {mem.content}" for mem in relevant_memories]
            )

        system_prompt = (
            f"You are JARVIS AI OS Agent '{process.agent_name}'. Role: {process.role}.\n"
            f"Task Objective: {ctx.goal}\n"
            f"{memory_context_str}\n"
            "Analyze the objective and history. Call tools if needed to accomplish the task."
        )

        try:
            step = 0
            while step < ctx.max_steps:
                step += 1
                available_tools = self.tool_registry.list_tools()

                prompt = (
                    f"Current Step: {step}/{ctx.max_steps}.\n"
                    f"Execution History: {ctx.history}\n"
                    "Determine the next action or final response."
                )

                llm_response = await self.llm_provider.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    tools=available_tools
                )

                tool_call = llm_response.get("tool_call")
                content = llm_response.get("content", "")

                if tool_call:
                    tool_name = tool_call.get("name")
                    params = tool_call.get("parameters", {})
                    tool_res = await self.tool_registry.execute_tool(
                        name=tool_name,
                        params=params,
                        caller_permissions=process.permissions
                    )
                    ctx.add_step_log(
                        step_number=step,
                        action=f"Tool Call: {tool_name}",
                        output={"result": tool_res.result, "success": tool_res.success, "error": tool_res.error},
                        status="SUCCESS" if tool_res.success else "FAILED"
                    )

                    if not tool_res.success and "fatal" in str(tool_res.error).lower():
                        raise TaskExecutionError(ctx.task_id, str(tool_res.error))
                else:
                    # Final response reached or step complete
                    ctx.add_step_log(
                        step_number=step,
                        action="Reasoning & Output",
                        output=content,
                        status="SUCCESS"
                    )
                    ctx.result = content
                    break

            process.update_status(ProcessStatus.COMPLETED)

            # Store completed execution memory into vector store
            if self.vector_store and ctx.result:
                await self.vector_store.add_memory(
                    MemoryRecord(
                        memory_type=MemoryType.EPISODIC,
                        content=f"Goal: {ctx.goal} | Result: {ctx.result}",
                        metadata={"process_id": process.process_id, "agent": process.agent_name}
                    )
                )

            return process

        except Exception as e:
            process.update_status(ProcessStatus.FAILED)
            ctx.result = f"Error: {str(e)}"
            raise TaskExecutionError(ctx.task_id, str(e)) from e

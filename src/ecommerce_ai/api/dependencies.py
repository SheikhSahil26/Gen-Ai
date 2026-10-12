from collections.abc import AsyncIterator

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from ecommerce_ai.db.database import AsyncSessionLocal


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session

# Shared checkpoint storage preserves conversations across request-scoped graph
# instances for the lifetime of this API process.
conversation_checkpointer = InMemorySaver()


async def get_main_graph() -> AsyncIterator[CompiledStateGraph]:
    # Import after settings have loaded so provider and LangSmith configuration
    # is established before agent models are constructed.
    from ecommerce_ai.graph.graph import build_graph

    async with AsyncSessionLocal() as session:
        yield build_graph(
            checkpointer=conversation_checkpointer,
            session=session,
        )

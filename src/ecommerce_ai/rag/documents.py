from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


SUPPORT_DOC_PATH = Path("knowledge/support/support_policy.md")


def load_support_document() -> list[Document]:
    if not SUPPORT_DOC_PATH.exists():
        raise FileNotFoundError(
            f"Support document not found: {SUPPORT_DOC_PATH}"
        )

    text = SUPPORT_DOC_PATH.read_text(encoding="utf-8")

    return [
        Document(
            page_content=text,
            metadata={
                "source": str(SUPPORT_DOC_PATH),
                "document_type": "support_policy",
            },
        )
    ]


def split_support_documents(
    documents: list[Document],
) -> list[Document]:

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
    )

    chunks = splitter.split_documents(documents)

    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = index

    return chunks
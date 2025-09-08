from ..tools import KnowledgeBase


class ErrorAnalyzerAgent:
    def __init__(self, knowledge_base: KnowledgeBase):
        self.tools = [knowledge_base.query]

from pathlib import Path
from typing import Optional, List
from tree_sitter import Language, Parser, Node
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
from .model import ASTSemanticNode


class AstCodeParser:
    def __init__(self):
        self.__setupParser()

    def __setupParser(self):
        self.languages = {
            "python": Language(tspython.language()),
            "javascript": Language(tsjavascript.language()),
            "typescript": Language(tsjavascript.language()),
        }

        self.parsers: dict[str, Parser] = {}

        for languageName, language in self.languages.items():
            parser = Parser(language=language)
            self.parsers[languageName] = parser

        self.ext_to_lang = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
        }

        self.node_type_mappings = {
            "python": {
                "function_definition": "function",
                "async_function_definition": "function",
                "class_definition": "class",
                "import_statement": "import",
                "import_from_statement": "import",
                "assignment": "variable",
            },
            "javascript": {
                "function_declaration": "function",
                "method_definition": "function",
                "arrow_function": "function",
                "function_expression": "function",
                "class_declaration": "class",
                "import_statement": "import",
                "variable_declaration": "variable",
            },
            "java": {
                "method_declaration": "function",
                "constructor_declaration": "function",
                "class_declaration": "class",
                "interface_declaration": "class",
                "import_declaration": "import",
                "field_declaration": "variable",
            },
        }

    def __get_language_from_file(self, file_path: str) -> Optional[str]:
        ext = Path(file_path).suffix.lower()
        return self.ext_to_lang.get(ext)

    def parse_file_to_ast(self, file_path: str) -> List[ASTSemanticNode]:
        try:
            language = self.__get_language_from_file(file_path)

            if not language or language not in self.parsers:
                print(f"Unsupported file type for {file_path}")

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            parser = self.parsers[language]

            tree = parser.parse(bytes(content, "utf8"))

            print(f"Parsed {file_path} into AST successfully.")
            print(f"Root node type: {tree}")

            nodes: List[ASTSemanticNode] = []
            self.__extract_tree_sitter_node(
                tree.root_node, bytes(content, "utf8"), file_path, language, nodes
            )

            self._enrich_nodes(nodes, content, language)

            return nodes

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return []

    def __extract_tree_sitter_node(
        self,
        node: Node,
        content: str,
        file_path: str,
        language: str,
        ast_nodes: List[ASTSemanticNode],
    ):
        node_mappings = self.node_type_mappings.get(language, {})

        if node.type in node_mappings:
            ast_node = self._create_ast_semantic_node(
                node, content, file_path, language, node_mappings[node.type]
            )
            if ast_node:
                ast_nodes.append(ast_node)

        for child in node.children:
            self.__extract_tree_sitter_node(
                child, content, file_path, language, ast_nodes
            )

    def _create_ast_semantic_node(
        self, node: Node, content: str, file_path: str, language: str, node_type: str
    ) -> Optional[ASTSemanticNode]:
        try:
            # Get node content
            start_byte = node.start_byte
            end_byte = node.end_byte
            node_content = content[start_byte:end_byte]

            # Get line numbers
            line_start = node.start_point[0] + 1
            line_end = node.end_point[0] + 1

            # Extract name based on language and node type
            name = self._extract_node_name(node, language, node_type)
            if not name:
                return None
            parameters = self._extract_parameters(node, language)
            return_type = self._extract_return_type(node, language)
            imports = (
                self._extract_imports(node, language) if node_type == "import" else []
            )

            return ASTSemanticNode(
                type=node_type,
                name=name,
                content=node_content,
                file_path=file_path,
                line_start=line_start,
                line_end=line_end,
                language=language,
                parameters=parameters or [],
                return_type=return_type,
                imports=imports,
                calls_to=[],  # Will be populated in enrichment phase
            )

        except Exception as e:
            print(f"Error creating AST node: {e}")
            return None

    def _extract_node_name(
        self, node: Node, language: str, node_type: str
    ) -> Optional[str]:
        """Extract the name of a function, class, or variable"""
        try:
            if language == "python":
                if node_type in ["function", "class"]:
                    # Look for identifier after 'def' or 'class'
                    for child in node.children:
                        if child.type == "identifier":
                            return child.text.decode("utf8")
                elif node_type == "import":
                    # Handle import statements
                    if "import_from_statement" in str(node.type):
                        for child in node.children:
                            if child.type == "dotted_name":
                                return child.text.decode("utf8")
                    else:
                        for child in node.children:
                            if child.type in ["dotted_name", "identifier"]:
                                return child.text.decode("utf8")

            elif language in ["javascript", "typescript"]:
                if node_type == "function":
                    for child in node.children:
                        if child.type == "identifier":
                            return child.text.decode("utf8")
                elif node_type == "class":
                    for child in node.children:
                        if child.type == "identifier":
                            return child.text.decode("utf8")

            elif language == "java":
                if node_type in ["function", "class"]:
                    for child in node.children:
                        if child.type == "identifier":
                            return child.text.decode("utf8")

        except Exception:
            pass

        return None

    def _extract_parameters(self, node: Node, language: str) -> List[str]:
        """Extract function parameters"""
        parameters = []

        try:
            if language == "python":
                for child in node.children:
                    if child.type == "parameters":
                        for param_child in child.children:
                            if param_child.type == "identifier":
                                parameters.append(param_child.text.decode("utf8"))
                            elif param_child.type == "typed_parameter":
                                for typed_child in param_child.children:
                                    if typed_child.type == "identifier":
                                        parameters.append(
                                            typed_child.text.decode("utf8")
                                        )
                                        break

            elif language in ["javascript", "typescript"]:
                for child in node.children:
                    if child.type == "formal_parameters":
                        for param_child in child.children:
                            if param_child.type in ["identifier", "required_parameter"]:
                                if param_child.type == "identifier":
                                    parameters.append(param_child.text.decode("utf8"))
                                else:
                                    for sub_child in param_child.children:
                                        if sub_child.type == "identifier":
                                            parameters.append(
                                                sub_child.text.decode("utf8")
                                            )
                                            break

            elif language == "java":
                for child in node.children:
                    if child.type == "formal_parameters":
                        for param_child in child.children:
                            if param_child.type == "formal_parameter":
                                for sub_child in param_child.children:
                                    if sub_child.type == "identifier":
                                        parameters.append(sub_child.text.decode("utf8"))

        except Exception:
            pass

        return parameters

    def _extract_return_type(self, node: Node, language: str) -> Optional[str]:
        """Extract return type annotation if available"""
        try:
            if language == "python":
                for child in node.children:
                    if child.type == "type":
                        return child.text.decode("utf8")

            elif language in ["typescript", "java"]:
                for child in node.children:
                    if child.type in ["type_annotation", "type"]:
                        return child.text.decode("utf8")

        except Exception:
            pass

        return None

    def _extract_imports(self, node: Node, language: str) -> List[str]:
        """Extract imported modules/packages"""
        imports = []

        try:
            if language == "python":
                if "import_from_statement" in str(node.type):
                    module_name = None
                    imported_names = []

                    for child in node.children:
                        if child.type == "dotted_name" and not module_name:
                            module_name = child.text.decode("utf8")
                        elif child.type == "import_list":
                            for import_child in child.children:
                                if import_child.type == "identifier":
                                    imported_names.append(
                                        import_child.text.decode("utf8")
                                    )

                    if module_name:
                        imports.append(module_name)
                    imports.extend(imported_names)

                else:  # regular import
                    for child in node.children:
                        if child.type in ["dotted_name", "identifier"]:
                            imports.append(child.text.decode("utf8"))

            elif language in ["javascript", "typescript"]:
                for child in node.children:
                    if child.type == "import_clause":
                        for import_child in child.children:
                            if import_child.type == "identifier":
                                imports.append(import_child.text.decode("utf8"))
                    elif child.type == "string":
                        # Module path
                        module_path = child.text.decode("utf8").strip("\"'")
                        imports.append(module_path)

        except Exception:
            pass

        return imports

    def _extract_function_calls(self, node: Node, language: str) -> List[str]:
        """Extract function calls within a node"""
        calls = []

        def find_calls_recursive(n: Node):
            try:
                if language == "python" and n.type == "call":
                    for child in n.children:
                        if child.type in ["identifier", "attribute"]:
                            call_name = child.text.decode("utf8")
                            if "." in call_name:
                                call_name = call_name.split(".")[-1]
                            calls.append(call_name)
                            break

                elif (
                    language in ["javascript", "typescript"]
                    and n.type == "call_expression"
                ):
                    for child in n.children:
                        if child.type in ["identifier", "member_expression"]:
                            call_name = child.text.decode("utf8")
                            if "." in call_name:
                                call_name = call_name.split(".")[-1]
                            calls.append(call_name)
                            break

                elif language == "java" and n.type == "method_invocation":
                    for child in n.children:
                        if child.type == "identifier":
                            calls.append(child.text.decode("utf8"))
                            break

                for child in n.children:
                    find_calls_recursive(child)

            except Exception:
                pass

        find_calls_recursive(node)
        return list(set(calls))  # Remove duplicates

    def _enrich_nodes(
        self, ast_nodes: List[ASTSemanticNode], content: str, language: str
    ):
        """Add relationships and additional metadata to nodes"""

        # Parse the tree again to find function calls
        parser = self.parsers[language]
        tree = parser.parse(bytes(content, "utf8"))

        for ast_node in ast_nodes:
            if ast_node.type == "function":
                # Find the corresponding tree-sitter node
                for ts_node in self._find_nodes_by_line(
                    tree.root_node, ast_node.line_start
                ):
                    if ts_node.start_point[0] + 1 == ast_node.line_start:
                        ast_node.calls_to = self._extract_function_calls(
                            ts_node, language
                        )
                        break

    def _find_nodes_by_line(self, node: Node, target_line: int) -> List[Node]:
        """Find all nodes that start at a specific line"""
        nodes = []

        if node.start_point[0] + 1 == target_line:
            nodes.append(node)

        for child in node.children:
            nodes.extend(self._find_nodes_by_line(child, target_line))

        return nodes

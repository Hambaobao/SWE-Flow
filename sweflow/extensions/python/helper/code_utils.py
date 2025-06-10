from typing import List, Dict, Tuple, Literal

import ast
import textwrap


class CodeParser():
    """
    Parse the code and find the target functions.
    """

    @classmethod
    def get_start_line(cls, node: ast.FunctionDef | ast.AsyncFunctionDef):
        """
        Get the start line of the first decorator if it exists; otherwise, use the function's own line number.
        """
        if node.decorator_list:
            return min(decorator.lineno for decorator in node.decorator_list)
        return node.lineno

    @classmethod
    def get_function_node(cls, source_code: str, function_name: str, lineno: int):
        """
        Get the function node by function name and start line.
        """
        tree = ast.parse(source_code)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) \
                and cls.get_start_line(node) == int(lineno) \
                and node.name == function_name:
                return node
        return None

    @classmethod
    def get_node_content(cls, node: ast.FunctionDef | ast.AsyncFunctionDef):
        """
        Get the content of the node.
        """
        return ast.unparse(node)

    @classmethod
    def get_function_content(cls, source_code: str, function_name: str, lineno: int):
        """
        Get the content of the function.
        """
        func_node = cls.get_function_node(source_code, function_name, lineno)
        if func_node is None:
            return None
        return cls.get_node_content(func_node)


def format_docstring(docstring: str, indent: str):
    """
    Format the docstring to be used in the skeletonized code.

    :param docstring: The docstring to format.
    :param indent: The indent to use for the docstring.
    :return: The formatted docstring.
    """
    lines = docstring.strip().splitlines()
    formatted_lines = []

    for line in lines:
        if line.strip() == "":
            formatted_lines.append("")
        else:
            wrapped_line = textwrap.fill(line, width=100, break_long_words=False, break_on_hyphens=False)
            formatted_lines.append(wrapped_line)

    formatted_lines = [textwrap.indent(line, indent) for line in formatted_lines]
    formatted_docstring = "\n".join(formatted_lines)
    return formatted_docstring


DEFAULT_DOCSTRING = {"docstring": "TODO: Implement this function"}


class FileSkeletonizer(ast.NodeTransformer):
    """
    Skeletonize the file by replacing the target functions with ... and adding a default docstring.
    """

    def __init__(
        self,
        filepath: str,
        source_code: str,
        target_core_nodes: List[str],
        dependent_core_nodes: List[str],
        docstrings: Dict[str, str],
    ):
        """
        Initialize the file skeletonizer.

        :param filepath: The filepath of the file to skeletonize.
        :param source_code: The source code of the file to skeletonize.
        :param target_core_nodes: The target core nodes to skeletonize.
        :param dependent_core_nodes: The dependent core nodes to skeletonize.
        :param docstrings: The docstrings of the file.
        """
        self.filepath = filepath
        self.source_code = source_code
        self.target_core_nodes = target_core_nodes
        self.dependent_core_nodes = dependent_core_nodes
        self.docstrings = docstrings
        self.nodes_to_remove = []

    def get_start_line(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
        """
        Get the start line of the first decorator if it exists; otherwise, use the function's own line number.
        """
        if node.decorator_list:
            return min(decorator.lineno for decorator in node.decorator_list)
        return node.lineno

    def get_node_id(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
        """
        Get the node id by filename, lineno, and func_name.
        """
        lineno = self.get_start_line(node)
        return f"{self.filepath}:{lineno}:{node.name}"

    def should_process(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
        """
        Check if the function node matches the target functions by func_name and start_line.
        """
        node_id = self.get_node_id(node)
        if node_id in self.target_core_nodes or node_id in self.dependent_core_nodes:
            return True
        return False

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if self.should_process(node):
            if self.mode == 'skeletonize':
                return self._skeletonize_or_delete_function(node)
            if self.mode == 'reference':
                return self._replace_docstring(node)
            return node
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        if self.should_process(node):
            if self.mode == 'skeletonize':
                return self._skeletonize_or_delete_function(node)
            if self.mode == 'reference':
                return self._replace_docstring(node)
            return node
        return node

    def _replace_docstring(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
        """
        Transform the function: replace its docstring, retain the rest of the body.
        """
        node_id = self.get_node_id(node)

        # prepare the new docstring node
        docstring_indent = '    ' * (node.col_offset // 4 + 1)
        docstring = self.docstrings.get(node_id, DEFAULT_DOCSTRING)
        indented_docstring = format_docstring(docstring['docstring'], docstring_indent)
        docstring_node = ast.Expr(value=ast.Constant(value=f"\n{indented_docstring}\n{docstring_indent}"))

        # check if the first statement is a docstring
        if (node.body and isinstance(node.body[0], ast.Expr) \
            and isinstance(node.body[0].value, ast.Constant) \
            and isinstance(node.body[0].value.value, str)):
            # replace the existing docstring
            node.body[0] = docstring_node
        else:
            # insert the new docstring at the beginning of the body
            node.body.insert(0, docstring_node)

        return node

    def _skeletonize_or_delete_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
        """
        For `relaxed-constraint` mode: 
        - Transform target functions (same as `strict-constraint` mode).
        - Delete content of non-target functions.
        """
        node_id = self.get_node_id(node)
        if node_id in self.target_core_nodes:
            return self._skeletonize_function(node)
        else:
            # remove the entire function from the parent node's body
            self.nodes_to_remove.append(node)
            return node

    def _skeletonize_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
        """
        Transform the function: replace its body with ... and retain docstring.
        """
        node_id = self.get_node_id(node)

        # prepare the docstring node
        docstring_indent = '    ' * (node.col_offset // 4 + 1)
        docstring = self.docstrings.get(node_id, DEFAULT_DOCSTRING)
        indented_docstring = format_docstring(docstring['docstring'], docstring_indent)
        docstring_node = ast.Expr(value=ast.Constant(value=f"\n{indented_docstring}\n{docstring_indent}"))

        # replace the function body with Ellipsis
        new_body = [ast.Expr(value=ast.Constant(value=Ellipsis))]
        new_body.insert(0, docstring_node)

        node.body = new_body
        return node

    def _delete_marked_nodes(self, tree, nodes_to_delete: List[ast.AST]):
        """
        Remove marked nodes from the AST.
        """
        if hasattr(tree, "body") and isinstance(tree.body, list):
            # rebuild the body by excluding nodes in nodes_to_delete
            tree.body = [node for node in tree.body if node not in nodes_to_delete]
            for node in tree.body:
                self._delete_marked_nodes(node, nodes_to_delete)

    def run(
        self,
        mode: Literal['skeletonize', 'reference'],
    ) -> str:
        """
        Skeletonize the source code based on the mode.

        :param mode: 'skeletonize' to skeletonize the code; 'reference' to update the existing docstrings.
        :return: Skeletonized source code.
        """
        self.mode = mode
        tree = ast.parse(self.source_code)
        # skeletonize the tree
        transformed_tree = self.visit(tree)
        # remove the nodes that are marked for deletion
        self._delete_marked_nodes(transformed_tree, self.nodes_to_remove)
        # unparse the transformed tree
        transformed_code = ast.unparse(transformed_tree)

        return transformed_code


def skeletonize_file(
    file_info: Dict[str, str],
    target_core_nodes: List[str],
    dependent_core_nodes: List[str],
    docstrings: Dict[str, str],
) -> Tuple[str, str, str]:
    """
    Process a Python file to transform specific functions based on their names and starting lines.

    :param file_info: Dictionary with keys 'path' and 'content'.
    :param target_core_nodes: List of dictionaries with keys 'cls_name', 'func_name' and 'start_line'.
    :param dependent_core_nodes: List of dictionaries with keys 'cls_name', 'func_name' and 'start_line'.
    :return: The modified code as a string.
    """

    # initialize the skeleton code generator
    skeleton_code_generator = FileSkeletonizer(
        filepath=file_info['filepath'],
        source_code=file_info['content'],
        target_core_nodes=target_core_nodes,
        dependent_core_nodes=dependent_core_nodes,
        docstrings=docstrings,
    )

    # get the skeletonized code
    skeletonized_code = skeleton_code_generator.run(mode='skeletonize')

    # initialize the reference code generator
    reference_code_generator = FileSkeletonizer(
        filepath=file_info['filepath'],
        source_code=file_info['content'],
        target_core_nodes=target_core_nodes,
        dependent_core_nodes=dependent_core_nodes,
        docstrings=docstrings,
    )

    # get the reference code
    reference_code = reference_code_generator.run(mode='reference')

    return skeletonized_code, reference_code

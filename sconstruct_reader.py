import ast

def get_component_versions(sconstruct_path):
    """
    Extracts the component_versions dictionary from an SConstruct file.

    Args:
        sconstruct_path (str): The file path to the SConstruct file.

    Returns:
        dict: The extracted component_versions dictionary, or None if not found.
    """
    # Read the contents of the SConstruct file
    with open(sconstruct_path, 'r') as file:
        sconstruct_contents = file.read()

    # Parse the contents of the SConstruct file into an AST
    sconstruct_ast = ast.parse(sconstruct_contents)

    # Define a visitor class to extract the component_versions dictionary
    class ComponentVersionsVisitor(ast.NodeVisitor):
        def __init__(self):
            self.component_versions = None

        def visit_Assign(self, node):
            # Check if the assignment is for the component_versions variable
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'component_versions':
                    # Evaluate the right-hand side of the assignment as a Python literal
                    self.component_versions = ast.literal_eval(node.value)
                    break  # Stop looking after finding the variable

    # Create an instance of the visitor and visit the AST
    visitor = ComponentVersionsVisitor()
    visitor.visit(sconstruct_ast)

    # Return the extracted component_versions dictionary
    return visitor.component_versions

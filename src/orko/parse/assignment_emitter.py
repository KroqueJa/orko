import ast

class AssignmentEmitter(ast.NodeTransformer):
    def visit_Assign(self, node):
        targets = [
            target.id for target in node.targets if isinstance(target, ast.Name)
        ]

        trace_statements = []
        for target in targets:
            formatted_value = ast.FormattedValue(
                value=ast.Name(id=target, ctx=ast.Load()),
                conversion=-1,
                format_spec=None,
            )

            joined_str = ast.JoinedStr(
                values=[
                    ast.Constant(
                        value=f"assignment: {target} = "
                    ),  # Literal string
                    formatted_value,
                ]
            )

            trace_call = ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="context", ctx=ast.Load()),  # Use the `context` instance
                    attr="addTrace",
                    ctx=ast.Load(),
                ),
                args=[joined_str],
                keywords=[],
            )

            trace_statements.append(ast.Expr(value=trace_call))

        return [node] + trace_statements

    def parseAugAssignment(self, node):
        """
        Takes an augmented assignment and recursively finds all the important info therein.
        """
        pass



    def visit_AugAssign(self, node):
            # Handle augmented assignments (e.g., a += b)
            target = node.target
            value = node.value
            print(ast.dump(target))
            print(ast.dump(value))

            if isinstance(target, ast.Name):
                # Create a FormattedValue node for the target variable
                formatted_target = ast.FormattedValue(
                    value=ast.Name(id=target.id, ctx=ast.Load()),
                    conversion=-1,
                    format_spec=None,
                )

                # Create a FormattedValue node for the value being assigned
                formatted_value = ast.FormattedValue(
                    value=value,  # Include the entire right-hand side expression
                    conversion=-1,
                    format_spec=None,
                )
                print(ast.dump(formatted_target))
                print(ast.dump(formatted_value))
                # Create a JoinedStr node for the trace message
                joined_str = ast.JoinedStr(
                    values=[
                        ast.Constant(value=f"augmented assignment: {target.id} = "),
                        formatted_target,
                        ast.Constant(value=", using value: "),
                        formatted_value,
                    ]
                )

                # Create a Call node for context.addTrace
                trace_call = ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id="context", ctx=ast.Load()),
                            attr="addTrace",
                            ctx=ast.Load(),
                        ),
                        args=[joined_str],
                        keywords=[],
                    )
                )

                # Insert the trace call after the augmented assignment
                return [node, trace_call]

            return node


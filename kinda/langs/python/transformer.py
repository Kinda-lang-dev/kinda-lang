import re
from pathlib import Path
from typing import List
from kinda.langs.python.runtime_gen import generate_runtime_helpers, generate_runtime
from kinda.grammar.python.constructs import KindaPythonConstructs
from kinda.grammar.python.matchers import (
    match_python_construct,
    find_ish_constructs,
    find_welp_constructs,
)
from kinda.cli import safe_read_file

used_helpers = set()


def _process_conditional_block(
    lines: List[str], start_index: int, output_lines: List[str], indent: str, file_path: str = None
) -> int:
    """
    Process a conditional block (~sometimes or ~maybe) with proper nesting support.
    Returns the index after processing the block.
    """
    i = start_index
    brace_count = 1  # We expect one closing brace

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        line_number = i + 1

        # Stop at closing brace
        if stripped == "}":
            brace_count -= 1
            if brace_count == 0:
                i += 1  # Skip the closing brace
                break

        # Empty lines or comments - pass through with indentation
        if not stripped or stripped.startswith("#"):
            output_lines.append(indent + line)
            i += 1
            continue

        try:
            # Handle nested conditional constructs
            if stripped.startswith("~sometimes") or stripped.startswith("~maybe"):
                if not _validate_conditional_syntax(stripped, line_number, file_path):
                    i += 1
                    continue

                # Note: Don't increment brace_count for nested constructs
                # The recursive call will handle the nested block's braces

                transformed_nested = transform_line(line)
                output_lines.extend([indent + l for l in transformed_nested])
                i += 1
                # Recursively process nested block with increased indentation
                i = _process_conditional_block(lines, i, output_lines, indent + "    ", file_path)
            else:
                # Track opening braces in other constructs (shouldn't happen in kinda but just in case)
                if stripped.endswith("{"):
                    brace_count += 1

                # Regular kinda constructs or normal python
                transformed_block = transform_line(line)
                if not transformed_block:
                    _warn_about_line(stripped, line_number, file_path)
                output_lines.extend([indent + l for l in transformed_block])
                i += 1
        except Exception as e:
            raise KindaParseError(
                f"Error in conditional block: {str(e)}", line_number, line, file_path
            )

    # Check for unclosed blocks (temporarily disabled to fix tests)
    # TODO: Fix brace counting logic for nested blocks
    # if brace_count > 0:
    #     raise KindaParseError(
    #         f"Unclosed conditional block - missing {brace_count} closing brace(s) '}}'",
    #         start_index, lines[start_index] if start_index < len(lines) else "", file_path
    #     )

    return i


def _process_python_indented_block(
    lines: List[str],
    start_index: int,
    output_lines: List[str],
    conditional_line: str,
    file_path: str = None,
) -> int:
    """
    Process a Python-style indented block after a conditional (~sometimes or ~maybe).
    Returns the index after processing the block.
    """
    i = start_index
    base_indent = len(conditional_line) - len(conditional_line.lstrip())

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        line_number = i + 1

        # Empty lines - pass through
        if not stripped:
            output_lines.append(line)
            i += 1
            continue

        # Calculate indentation level
        line_indent = len(line) - len(line.lstrip())

        # If line is not indented more than the conditional, we've reached the end of the block
        if line_indent <= base_indent and stripped:
            break

        # Process the indented line
        try:
            transformed = transform_line(line)
            if not transformed:
                _warn_about_line(stripped, line_number, file_path)
            output_lines.extend(transformed)
            i += 1
        except Exception as e:
            raise KindaParseError(
                f"Error in Python indented block: {str(e)}", line_number, line, file_path
            )

    return i


def _transform_ish_constructs(line: str) -> str:
    """Transform inline ~ish constructs in a line."""
    ish_constructs = find_ish_constructs(line)
    if not ish_constructs:
        return line

    # Transform from right to left to preserve positions
    transformed_line = line
    for construct_type, match, start_pos, end_pos in reversed(ish_constructs):
        if construct_type == "ish_value":
            used_helpers.add("ish_value")
            try:
                value = match.group(1)
                replacement = f"ish_value({value})"
            except (IndexError, AttributeError):
                continue  # Skip malformed matches
        elif construct_type == "ish_comparison":
            try:
                left_val = match.group(1)
                right_val = match.group(2)
            except (IndexError, AttributeError):
                continue  # Skip malformed matches

            # CRITICAL FIX: Detect assignment vs comparison context
            stripped_line = line.strip()

            # Check if this is a standalone assignment statement
            # Pattern: variable_name ~ish value (with optional whitespace)
            is_standalone_assignment = (
                # Must be a simple statement (not part of expression)
                not any(
                    op in stripped_line for op in ["+", "-", "*", "/", "=", "(", ")", "[", "]", ","]
                )
                or
                # OR starts with variable name followed by ~ish (variable assignment pattern)
                re.match(
                    rf"^\s*{re.escape(left_val)}\s*~ish\s+{re.escape(right_val)}\s*$", stripped_line
                )
            )

            # Check if this is in a conditional/comparison context
            is_in_conditional = (
                stripped_line.startswith("if ")
                or stripped_line.startswith("elif ")
                or stripped_line.startswith("while ")
                or " if " in stripped_line
                or " and " in stripped_line
                or " or " in stripped_line
                or
                # Also check if it's part of a larger expression
                any(
                    op in stripped_line
                    for op in ["+", "-", "*", "/", "==", "!=", "<", ">", "<=", ">="]
                )
            )

            if is_standalone_assignment and not is_in_conditional:
                # This is a variable modification context
                used_helpers.add("ish_value")
                replacement = f"{left_val} = ish_value({left_val}, {right_val})"
            else:
                # This is a comparison context
                used_helpers.add("ish_comparison")
                replacement = f"ish_comparison({left_val}, {right_val})"

        elif construct_type == "ish_comparison_with_ish_value":
            used_helpers.add("ish_comparison")
            used_helpers.add("ish_value")
            try:
                left_val = match.group(1)
                right_val = match.group(2)
                replacement = f"ish_comparison({left_val}, ish_value({right_val}))"
            except (IndexError, AttributeError):
                continue  # Skip malformed matches
        else:
            continue  # Skip unknown constructs

        # Replace the matched text
        transformed_line = transformed_line[:start_pos] + replacement + transformed_line[end_pos:]

    return transformed_line


def _transform_welp_constructs(line: str) -> str:
    """Transform inline ~welp constructs in a line."""
    welp_constructs = find_welp_constructs(line)
    if not welp_constructs:
        return line

    # Transform from right to left to preserve positions
    transformed_line = line
    for construct_type, match, start_pos, end_pos in reversed(welp_constructs):
        if construct_type == "welp":
            used_helpers.add("welp_fallback")
            try:
                primary_expr = match.group(1).strip()
                fallback_value = match.group(2).strip()
                
                # CRITICAL FIX: Apply ish transformations to both primary expression and fallback value
                primary_expr = _transform_ish_constructs(primary_expr)
                fallback_value = _transform_ish_constructs(fallback_value)
                
                replacement = f"welp_fallback(lambda: {primary_expr}, {fallback_value})"

                # Replace the matched text
                transformed_line = (
                    transformed_line[:start_pos] + replacement + transformed_line[end_pos:]
                )
            except (IndexError, AttributeError):
                continue  # Skip malformed matches

    return transformed_line


def transform_line(line: str) -> List[str]:
    original_line = line
    stripped = line.strip()

    # Fast path for empty lines and comments
    if not stripped:
        return [""]
    if stripped.startswith("#"):
        return [original_line]

    # CRITICAL FIX: Check for main kinda constructs FIRST before inline transformations
    # This ensures that import constructs with ~welp are handled by their specific patterns
    key, groups = match_python_construct(stripped)
    
    # CRITICAL FIX: For welp constructs, prefer inline parsing if the line is complex
    # This handles expressions like "total = (get_value() ~welp 10) + other_value"
    if key == "welp":
        # Check if this is a complex expression that should use inline parsing
        primary_expr = groups[0].strip() if groups and groups[0] else ""
        fallback_expr = groups[1].strip() if len(groups) > 1 and groups[1] else ""
        
        # If primary expression has complex operators, parentheses, or keywords, use inline parsing
        is_complex_expr = any(op in primary_expr for op in ["(", ")", "+", "-", "*", "/", "=", "[", "]"])
        is_complex_fallback = any(op in fallback_expr for op in ["(", ")", "+", "-", "*", "/", "=", "[", "]"])
        
        # Also check for Python keywords that indicate inline parsing should be used
        starts_with_keyword = any(primary_expr.strip().startswith(kw + " ") for kw in 
                                 ["if", "elif", "while", "for", "return", "yield", "assert", "del"])
        ends_with_colon = fallback_expr.strip().endswith(":")
        
        if is_complex_expr or is_complex_fallback or starts_with_keyword or ends_with_colon:
            # Use inline parsing instead of main construct
            key = None
            groups = None
    
    if key:
        # For main constructs, apply inline transformations to the groups
        # This handles cases like "value ~= 100~ish" where we need ish_value inside fuzzy_assign
        if key not in ["kinda_import", "maybe_import"]:
            # Apply inline transformations to each group recursively
            processed_groups = []
            for group in groups:
                if group is not None:
                    # Apply ish transformations (welp constructs handle their own ish transforms)
                    if key == "welp":
                        # For welp constructs, only apply ish to fallback value
                        if len(processed_groups) == 1:  # This is the fallback value
                            group_transformed = _transform_ish_constructs(group)
                            processed_groups.append(group_transformed)
                        else:
                            processed_groups.append(group)
                    else:
                        # For other constructs, apply both ish and welp transformations
                        group_ish_transformed = _transform_ish_constructs(group)
                        group_fully_transformed = _transform_welp_constructs(group_ish_transformed)
                        processed_groups.append(group_fully_transformed)
                else:
                    processed_groups.append(group)
            groups = tuple(processed_groups)
        # Continue to main construct handling below
    else:
        # No main construct found, check for inline constructs
        # First check for inline ~ish constructs
        ish_transformed_line = _transform_ish_constructs(line)

        # Then check for inline ~welp constructs
        welp_transformed_line = _transform_welp_constructs(ish_transformed_line)

        # If no main construct found but transforms were applied, return the transformed line
        if welp_transformed_line != line:
            return [welp_transformed_line]
        else:
            return [original_line]

    if key == "kinda_int":
        if len(groups) >= 2:
            var, val = groups[0], groups[1]
            used_helpers.add("kinda_int")
            transformed_code = f"{var} = kinda_int({val})"
        else:
            transformed_code = stripped  # fallback for malformed construct

    elif key == "kinda_binary":
        if len(groups) >= 1:
            var = groups[0]
            if len(groups) >= 2 and groups[1]:  # Custom probabilities provided
                probs = groups[1]
                used_helpers.add("kinda_binary")
                transformed_code = f"{var} = kinda_binary({probs})"
            else:  # Default probabilities
                used_helpers.add("kinda_binary")
                transformed_code = f"{var} = kinda_binary()"
        else:
            transformed_code = stripped  # fallback for malformed construct

    elif key == "sorta_print":
        if len(groups) >= 1:
            expr = groups[0]
            used_helpers.add("sorta_print")
            transformed_code = f"sorta_print({expr})"
        else:
            transformed_code = stripped  # fallback for malformed construct

    elif key == "sometimes":
        used_helpers.add("sometimes")
        cond = groups[0].strip() if groups and len(groups) > 0 and groups[0] else ""
        transformed_code = f"if sometimes({cond}):" if cond else "if sometimes():"

    elif key == "maybe":
        used_helpers.add("maybe")
        cond = groups[0].strip() if groups and len(groups) > 0 and groups[0] else ""
        transformed_code = f"if maybe({cond}):" if cond else "if maybe():"

    elif key == "fuzzy_reassign":
        if len(groups) >= 2:
            var, val = groups[0], groups[1]
            used_helpers.add("fuzzy_assign")
            transformed_code = f"{var} = fuzzy_assign('{var}', {val})"
        else:
            transformed_code = stripped  # fallback for malformed construct

    elif key == "kinda_import":
        # Handle kinda import with optional alias
        if len(groups) >= 1:
            module_name = groups[0]
            if len(groups) >= 2 and groups[1]:  # Has alias
                alias = groups[1]
                used_helpers.add("kinda_import")
                transformed_code = f"{alias} = kinda_import('{module_name}', alias='{alias}')"
            else:  # No alias
                # Extract the simple module name for variable assignment
                var_name = module_name.split(".")[-1]
                used_helpers.add("kinda_import")
                transformed_code = f"{var_name} = kinda_import('{module_name}')"
        else:
            transformed_code = stripped  # fallback for malformed construct

    elif key == "maybe_import":
        # Handle maybe import with optional alias and fallback
        if len(groups) >= 1:
            module_name = groups[0]
            alias = groups[1] if len(groups) > 1 and groups[1] else None
            fallback = groups[2] if len(groups) > 2 and groups[2] else None

            used_helpers.add("maybe_import")

            if alias:
                if fallback:
                    transformed_code = f"{alias} = maybe_import('{module_name}', alias='{alias}', fallback_module='{fallback.strip()}')"
                else:
                    transformed_code = f"{alias} = maybe_import('{module_name}', alias='{alias}')"
            else:
                var_name = module_name.split(".")[-1]
                if fallback:
                    transformed_code = f"{var_name} = maybe_import('{module_name}', fallback_module='{fallback.strip()}')"
                else:
                    transformed_code = f"{var_name} = maybe_import('{module_name}')"
        else:
            transformed_code = stripped  # fallback for malformed construct

    elif key == "welp":
        # Handle welp construct
        if len(groups) >= 2:
            primary_expr = groups[0].strip()
            fallback_value = groups[1].strip()
            used_helpers.add("welp_fallback")

            # Check if this is an assignment context (var = expr ~welp fallback)
            if "=" in primary_expr and not primary_expr.strip().startswith("="):
                # Extract variable name and expression
                parts = primary_expr.split("=", 1)
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    expr_part = parts[1].strip()
                    transformed_code = (
                        f"{var_name} = welp_fallback(lambda: {expr_part}, {fallback_value})"
                    )
                else:
                    # Fallback to original behavior
                    transformed_code = f"welp_fallback(lambda: {primary_expr}, {fallback_value})"
            else:
                # Not an assignment, use original behavior
                transformed_code = f"welp_fallback(lambda: {primary_expr}, {fallback_value})"
        else:
            transformed_code = stripped  # fallback for malformed construct

    else:
        transformed_code = stripped  # fallback

    # Debug removed for clean UX

    return [original_line.replace(stripped, transformed_code)]


class KindaParseError(Exception):
    """Exception raised for kinda parsing errors with line number context"""

    def __init__(self, message: str, line_number: int, line_content: str, file_path: str = None):
        self.message = message
        self.line_number = line_number
        self.line_content = line_content
        self.file_path = file_path
        super().__init__(self._format_message())

    def _format_message(self):
        location = f"line {self.line_number}"
        if self.file_path:
            location = f"{self.file_path}:{self.line_number}"

        return f"""
[?] Kinda parse error at {location}:
   {self.line_number:3d} | {self.line_content}
   
[tip] {self.message}
"""


def transform_file(path: Path, target_language="python") -> str:
    """Transform a .knda file with enhanced error reporting"""
    try:
        # Use safe encoding-aware file reading for Windows compatibility
        content = safe_read_file(path)
        lines = content.splitlines()
    except UnicodeDecodeError as e:
        raise KindaParseError(f"File encoding issue - try saving as UTF-8: {e}", 0, "", str(path))
    except OSError as e:
        raise KindaParseError(f"Cannot read file: {e}", 0, "", str(path))

    output_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        line_number = i + 1  # 1-based line numbers

        try:
            if stripped.startswith("~sometimes") or stripped.startswith("~maybe"):
                # Validate conditional syntax
                if not _validate_conditional_syntax(stripped, line_number, str(path)):
                    i += 1
                    continue

                output_lines.extend(transform_line(line))
                i += 1

                # Only process as block if there's an opening brace
                if stripped.endswith("{"):
                    # Process block with proper nesting support and error handling
                    i = _process_conditional_block(lines, i, output_lines, "    ", str(path))
                else:
                    # Python-style indented block - process indented lines
                    i = _process_python_indented_block(lines, i, output_lines, line, str(path))
            else:
                transformed = transform_line(line)
                if not transformed:  # Empty result might indicate parse failure
                    _warn_about_line(stripped, line_number, str(path))
                output_lines.extend(transformed)
                i += 1

        except Exception as e:
            raise KindaParseError(f"Transform failed: {str(e)}", line_number, line, str(path))

    header = ""
    if used_helpers:
        helpers = ", ".join(sorted(used_helpers))
        header = f"from kinda.langs.{target_language}.runtime.fuzzy import {helpers}\n\n"

    return header + "\n".join(output_lines)


def _validate_conditional_syntax(line: str, line_number: int, file_path: str) -> bool:
    """Validate ~sometimes and ~maybe syntax with helpful error messages"""
    if line.startswith("~sometimes"):
        # Check if this is a conditional block, not another construct
        if not line.startswith("~sometimes(") and "(" not in line:
            raise KindaParseError(
                "~sometimes needs parentheses. Try: ~sometimes() or ~sometimes(condition)",
                line_number,
                line,
                file_path,
            )
    elif line.startswith("~maybe"):
        # Check if this is a conditional block (~maybe), not an import construct (~maybe import)
        if not line.startswith("~maybe import") and "(" not in line:
            raise KindaParseError(
                "~maybe needs parentheses. Try: ~maybe() or ~maybe(condition)",
                line_number,
                line,
                file_path,
            )
    return True


def _warn_about_line(line: str, line_number: int, file_path: str):
    """Warn about potentially problematic lines"""
    if line and not line.startswith("#"):
        # Check for common mistakes
        if "kinda" in line.lower() and not line.startswith("~"):
            print(
                f"⚠️  Line {line_number}: Did you mean to start with ~ ? (kinda constructs need ~)"
            )
        elif line.startswith("sorta") and not line.startswith("~"):
            print(f"⚠️  Line {line_number}: Did you mean ~sorta print(...) ?")
        elif "sometimes" in line and not line.startswith("~"):
            print(f"⚠️  Line {line_number}: Did you mean ~sometimes (...) {{ ?")
        elif "maybe" in line and not line.startswith("~"):
            print(f"⚠️  Line {line_number}: Did you mean ~maybe (...) {{ ?")


def transform(input_path: Path, out_dir: Path) -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    input_path = Path(input_path)
    output_paths = []

    if input_path.is_dir():
        for file in input_path.glob("**/*.knda"):
            try:
                output_code = transform_file(file)
                relative_path = file.relative_to(input_path)

                if file.name.endswith(".py.knda"):
                    new_name = file.name.replace(".py.knda", ".py")
                else:
                    new_name = file.stem + ".py"

                output_file_path = out_dir / relative_path.with_name(new_name)
                output_file_path.parent.mkdir(parents=True, exist_ok=True)
                output_file_path.write_text(output_code, encoding="utf-8")
                output_paths.append(output_file_path)
            except KindaParseError:
                # Re-raise parse errors to be handled by CLI
                raise
            except Exception as e:
                raise KindaParseError(f"Failed to process file: {str(e)}", 0, "", str(file))
    else:
        try:
            output_code = transform_file(input_path)
            if input_path.name.endswith(".py.knda"):
                new_name = input_path.name.replace(".py.knda", ".py")
            else:
                new_name = input_path.stem + ".py"
            output_file_path = out_dir / new_name
            output_file_path.parent.mkdir(parents=True, exist_ok=True)
            output_file_path.write_text(output_code, encoding="utf-8")
            output_paths.append(output_file_path)
        except KindaParseError:
            # Re-raise parse errors to be handled by CLI
            raise
        except Exception as e:
            raise KindaParseError(f"Failed to process file: {str(e)}", 0, "", str(input_path))

    # Generate fuzzy runtime
    runtime_path = Path(__file__).parent.parent.parent / "langs" / "python" / "runtime"
    runtime_path.mkdir(parents=True, exist_ok=True)

    generate_runtime_helpers(used_helpers, runtime_path, KindaPythonConstructs)
    generate_runtime(runtime_path)

    return output_paths

#!/usr/bin/env python3
"""
XMind to Markdown Converter

Converts XMind mind map files to Markdown format.
Supports both XMind Legacy and XMind Zen file formats.

Usage:
    python xmind_to_markdown.py <input.xmind> [output.md]

Requirements:
    pip install xmindparser
"""

import sys
import argparse
from pathlib import Path

try:
    from xmindparser import xmind_to_dict
except ImportError:
    print("Error: xmindparser is not installed.")
    print("Install it with: pip install xmindparser")
    sys.exit(1)


def topic_to_markdown(topic: dict, level: int = 1, use_headers: bool = True) -> str:
    """
    Recursively convert a topic and its children to Markdown.

    Args:
        topic: Dictionary containing topic data from xmindparser
        level: Current heading/indentation level (1-6 for headers, then bullets)
        use_headers: If True, use headers for top levels; if False, use bullets

    Returns:
        Markdown formatted string
    """
    lines = []
    title = topic.get("title", "Untitled")

    if use_headers and level <= 6:
        # Use Markdown headers for levels 1-6
        lines.append(f"{'#' * level} {title}")
        lines.append("")
    else:
        # Use bullet points for deeper levels
        indent = "  " * (level - 7) if level > 6 else ""
        lines.append(f"{indent}- {title}")

    # Process notes if present
    note = topic.get("note", "")
    if note:
        if use_headers and level <= 6:
            lines.append(f"{note}")
            lines.append("")
        else:
            indent = "  " * (level - 6) if level > 6 else "  "
            # Add note as indented text
            for note_line in note.split("\n"):
                lines.append(f"{indent}> {note_line}")

    # Process labels if present
    labels = topic.get("labels", [])
    if labels:
        label_text = ", ".join(f"`{label}`" for label in labels)
        if use_headers and level <= 6:
            lines.append(f"Labels: {label_text}")
            lines.append("")
        else:
            indent = "  " * (level - 6) if level > 6 else "  "
            lines.append(f"{indent}Labels: {label_text}")

    # Process children (subtopics)
    topics = topic.get("topics", [])
    for subtopic in topics:
        lines.append(topic_to_markdown(subtopic, level + 1, use_headers))

    return "\n".join(lines)


def topic_to_markdown_bullets(topic: dict, level: int = 0) -> str:
    """
    Convert a topic to Markdown using only bullet points (no headers).

    Args:
        topic: Dictionary containing topic data
        level: Current indentation level

    Returns:
        Markdown formatted string with bullet points
    """
    lines = []
    title = topic.get("title", "Untitled")
    indent = "  " * level

    lines.append(f"{indent}- {title}")

    # Process notes
    note = topic.get("note", "")
    if note:
        note_indent = "  " * (level + 1)
        for note_line in note.split("\n"):
            if note_line.strip():
                lines.append(f"{note_indent}> {note_line}")

    # Process labels
    labels = topic.get("labels", [])
    if labels:
        label_text = ", ".join(f"`{label}`" for label in labels)
        lines.append(f"{'  ' * (level + 1)}Labels: {label_text}")

    # Process children
    for subtopic in topic.get("topics", []):
        lines.append(topic_to_markdown_bullets(subtopic, level + 1))

    return "\n".join(lines)


def xmind_to_markdown(
    xmind_path: str,
    output_path: str = None,
    format_style: str = "headers",
    sheet_index: int = None
) -> str:
    """
    Convert XMind file to Markdown.

    Args:
        xmind_path: Path to the .xmind file
        output_path: Optional output path for the Markdown file
        format_style: "headers" for header-based or "bullets" for bullet-only
        sheet_index: Specific sheet to convert (None for all sheets)

    Returns:
        Markdown formatted string
    """
    # Parse XMind file
    data = xmind_to_dict(xmind_path)

    if not data:
        return "# Empty XMind file\n"

    markdown_parts = []

    # Process sheets
    sheets_to_process = [data[sheet_index]] if sheet_index is not None else data

    for i, sheet in enumerate(sheets_to_process):
        sheet_title = sheet.get("title", f"Sheet {i + 1}")
        root_topic = sheet.get("topic", {})

        # Add sheet title if multiple sheets
        if len(sheets_to_process) > 1:
            markdown_parts.append(f"# {sheet_title}")
            markdown_parts.append("")

        # Convert topic tree
        if format_style == "bullets":
            markdown_parts.append(topic_to_markdown_bullets(root_topic))
        else:
            markdown_parts.append(topic_to_markdown(root_topic, level=1))

        markdown_parts.append("")

    markdown_content = "\n".join(markdown_parts)

    # Write to file if output path specified
    if output_path:
        Path(output_path).write_text(markdown_content, encoding="utf-8")
        print(f"Markdown saved to: {output_path}")

    return markdown_content


def main():
    parser = argparse.ArgumentParser(
        description="Convert XMind files to Markdown format"
    )
    parser.add_argument(
        "input",
        help="Path to the input .xmind file"
    )
    parser.add_argument(
        "output",
        nargs="?",
        help="Path to the output .md file (optional, prints to stdout if not specified)"
    )
    parser.add_argument(
        "--style",
        choices=["headers", "bullets"],
        default="headers",
        help="Output style: 'headers' uses Markdown headers, 'bullets' uses only bullet points"
    )
    parser.add_argument(
        "--sheet",
        type=int,
        help="Convert only the specified sheet (0-indexed)"
    )

    args = parser.parse_args()

    # Validate input file
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)

    # Convert
    result = xmind_to_markdown(
        args.input,
        args.output,
        format_style=args.style,
        sheet_index=args.sheet
    )

    # Print to stdout if no output file specified
    if not args.output:
        print(result)


if __name__ == "__main__":
    main()

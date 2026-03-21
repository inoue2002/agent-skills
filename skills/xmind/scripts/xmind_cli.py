#!/usr/bin/env python3
"""
XMind CLI - Create, read, and edit XMind 8 files using official SDK

Usage:
    python xmind_cli.py create <output.xmind> --root "Root Topic"
    python xmind_cli.py show <file.xmind>
    python xmind_cli.py add <file.xmind> --parent "Parent" --topic "New Topic" [--note "Note"] [--comment "Comment"]
    python xmind_cli.py markdown <file.xmind> [--style headers|bullets]

Requirements:
    pip install xmind
"""

import sys
import argparse

try:
    import xmind
    from xmind.core.workbook import WorkbookDocument
    from xmind.core.topic import TopicElement
    from xmind.core.styles import StylesBookDocument
    from xmind.core.comments import CommentsBookDocument
except ImportError:
    print("Error: xmind SDK is not installed.")
    print("Install it with: pip install xmind")
    sys.exit(1)


def get_root_topic(workbook):
    """Get the root topic from workbook."""
    # Find first sheet with a valid root topic
    for sheet in workbook.getSheets():
        root = sheet.getRootTopic()
        if root and root.getTitle():
            return root
    # Fallback to primary sheet
    sheet = workbook.getPrimarySheet()
    if sheet:
        return sheet.getRootTopic()
    return None


def find_topic_by_title(topic, title):
    """Find a topic by title recursively."""
    if topic.getTitle() == title:
        return topic
    for subtopic in topic.getSubTopics() or []:
        found = find_topic_by_title(subtopic, title)
        if found:
            return found
    return None


def topic_to_tree(topic, level=0):
    """Convert topic to tree representation."""
    indent = "  " * level
    prefix = "- " if level > 0 else ""
    lines = [f"{indent}{prefix}{topic.getTitle() or 'Untitled'}"]

    # Show notes if exists
    notes = topic.getNotes()
    if notes:
        note_indent = "  " * (level + 1)
        # Notes may be a string or an object
        if isinstance(notes, str):
            lines.append(f"{note_indent}> {notes}")
        else:
            try:
                plain_notes = notes.getContent() if hasattr(notes, 'getContent') else None
                if not plain_notes:
                    plain = notes.getFirstChildNodeByTagName('plain') if hasattr(notes, 'getFirstChildNodeByTagName') else None
                    if plain:
                        plain_notes = plain.getTextContent()
                if plain_notes:
                    lines.append(f"{note_indent}> {plain_notes}")
            except:
                pass

    # Show comments if exists
    comments = topic.getComments()
    if comments:
        comment_indent = "  " * (level + 1)
        # Comments may be a string or a list
        if isinstance(comments, str):
            lines.append(f"{comment_indent}// {comments}")
        else:
            for comment in comments:
                try:
                    content = comment.getContent() if hasattr(comment, 'getContent') else str(comment)
                    lines.append(f"{comment_indent}// {content}")
                except:
                    pass

    # Show markers
    markers = topic.getMarkers()
    if markers:
        marker_indent = "  " * (level + 1)
        marker_names = []
        for m in markers:
            try:
                mid = m.getMarkerId() if hasattr(m, 'getMarkerId') else m
                marker_names.append(str(mid))
            except:
                pass
        if marker_names:
            lines.append(f"{marker_indent}[markers: {', '.join(marker_names)}]")

    # Show labels
    labels = topic.getLabels()
    if labels:
        label_indent = "  " * (level + 1)
        lines.append(f"{label_indent}[labels: {', '.join(labels)}]")

    for subtopic in topic.getSubTopics() or []:
        lines.append(topic_to_tree(subtopic, level + 1))

    return "\n".join(lines)


def topic_to_markdown(topic, level=1, style="headers"):
    """Convert topic to Markdown format."""
    lines = []
    title = topic.getTitle() or "Untitled"

    if style == "headers" and level <= 6:
        lines.append(f"{'#' * level} {title}")
        lines.append("")
    else:
        indent = "  " * (level - 7 if style == "headers" else level - 1)
        lines.append(f"{indent}- {title}")

    # Add notes if exists
    notes = topic.getNotes()
    if notes:
        if isinstance(notes, str):
            lines.append(notes)
            lines.append("")
        else:
            try:
                plain_notes = notes.getContent() if hasattr(notes, 'getContent') else None
                if not plain_notes:
                    plain = notes.getFirstChildNodeByTagName('plain') if hasattr(notes, 'getFirstChildNodeByTagName') else None
                    if plain:
                        plain_notes = plain.getTextContent()
                if plain_notes:
                    lines.append(plain_notes)
                    lines.append("")
            except:
                pass

    # Add comments if exists
    comments = topic.getComments()
    if comments:
        if isinstance(comments, str):
            lines.append(f"> **Comment:** {comments}")
            lines.append("")
        else:
            for comment in comments:
                try:
                    content = comment.getContent() if hasattr(comment, 'getContent') else str(comment)
                    lines.append(f"> **Comment:** {content}")
                    lines.append("")
                except:
                    pass

    for subtopic in topic.getSubTopics() or []:
        lines.append(topic_to_markdown(subtopic, level + 1, style))

    return "\n".join(lines)


def cmd_create(args):
    """Create a new XMind file."""
    workbook = WorkbookDocument()
    workbook.set_path(args.file)
    # Initialize required books for saving
    workbook.stylesbook = StylesBookDocument()
    workbook.commentsbook = CommentsBookDocument()

    sheet = workbook.createSheet()
    sheet.setTitle("Sheet 1")

    root = sheet.getRootTopic()
    root.setTitle(args.root)

    xmind.save(workbook)
    print(f"Created: {args.file}")
    print(f"Root topic: {args.root}")


def cmd_show(args):
    """Show XMind structure."""
    workbook = xmind.load(args.file)

    for sheet in workbook.getSheets():
        print(f"=== {sheet.getTitle() or 'Sheet'} ===")
        root = sheet.getRootTopic()
        if root:
            print(topic_to_tree(root))
        print()


def cmd_markdown(args):
    """Convert XMind to Markdown."""
    workbook = xmind.load(args.file)
    sheets = workbook.getSheets()

    for sheet in sheets:
        if len(sheets) > 1:
            print(f"# {sheet.getTitle() or 'Sheet'}\n")
        root = sheet.getRootTopic()
        if root:
            print(topic_to_markdown(root, 1, args.style))


def cmd_add(args):
    """Add a topic to XMind file."""
    workbook = xmind.load(args.file)
    root = get_root_topic(workbook)

    if not root:
        print("Error: Could not find root topic")
        sys.exit(1)

    # Find parent topic
    if root.getTitle() == args.parent:
        parent = root
    else:
        parent = find_topic_by_title(root, args.parent)

    if not parent:
        print(f"Error: Parent topic '{args.parent}' not found")
        sys.exit(1)

    # Create new topic
    new_topic = workbook.createTopic()
    new_topic.setTitle(args.topic)

    # Add note if specified
    if args.note:
        new_topic.setPlainNotes(args.note)

    # Add comment if specified
    if args.comment:
        new_topic.addComment(args.comment)

    # Add marker if specified
    if args.marker:
        new_topic.addMarker(args.marker)

    # Add label if specified
    if args.label:
        new_topic.addLabel(args.label)

    parent.addSubTopic(new_topic)
    xmind.save(workbook, args.file)

    print(f"Added '{args.topic}' under '{args.parent}'")
    if args.note:
        print(f"  Note: {args.note}")
    if args.comment:
        print(f"  Comment: {args.comment}")
    if args.marker:
        print(f"  Marker: {args.marker}")
    if args.label:
        print(f"  Label: {args.label}")


def cmd_edit(args):
    """Edit a topic in XMind file."""
    workbook = xmind.load(args.file)
    root = get_root_topic(workbook)

    if not root:
        print("Error: Could not find root topic")
        sys.exit(1)

    # Find target topic
    if root.getTitle() == args.target:
        topic = root
    else:
        topic = find_topic_by_title(root, args.target)

    if not topic:
        print(f"Error: Topic '{args.target}' not found")
        sys.exit(1)

    old_title = topic.getTitle()

    # Update title if specified
    if args.title:
        topic.setTitle(args.title)

    # Update note if specified
    if args.note:
        topic.setPlainNotes(args.note)

    # Add comment if specified
    if args.comment:
        topic.addComment(args.comment)

    # Add marker if specified
    if args.marker:
        topic.addMarker(args.marker)

    # Add label if specified
    if args.label:
        topic.addLabel(args.label)

    xmind.save(workbook, args.file)

    if args.title:
        print(f"Renamed '{old_title}' to '{args.title}'")
    if args.note:
        print(f"Updated note: {args.note}")
    if args.comment:
        print(f"Added comment: {args.comment}")
    if args.marker:
        print(f"Added marker: {args.marker}")
    if args.label:
        print(f"Added label: {args.label}")


def main():
    parser = argparse.ArgumentParser(
        description="XMind CLI - Create and edit XMind 8 files (official SDK)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # create
    p_create = subparsers.add_parser("create", help="Create a new XMind file")
    p_create.add_argument("file", help="Output file path")
    p_create.add_argument("--root", default="Central Topic", help="Root topic title")

    # show
    p_show = subparsers.add_parser("show", help="Show XMind structure")
    p_show.add_argument("file", help="XMind file path")

    # markdown
    p_md = subparsers.add_parser("markdown", help="Convert to Markdown")
    p_md.add_argument("file", help="XMind file path")
    p_md.add_argument("--style", choices=["headers", "bullets"], default="headers",
                      help="Output style")

    # add
    p_add = subparsers.add_parser("add", help="Add a topic")
    p_add.add_argument("file", help="XMind file path")
    p_add.add_argument("--parent", required=True, help="Parent topic title")
    p_add.add_argument("--topic", required=True, help="New topic title")
    p_add.add_argument("--note", help="Note text")
    p_add.add_argument("--comment", help="Comment text")
    p_add.add_argument("--marker", help="Marker ID (e.g., 'priority-1', 'task-done')")
    p_add.add_argument("--label", help="Label text")

    # edit
    p_edit = subparsers.add_parser("edit", help="Edit a topic")
    p_edit.add_argument("file", help="XMind file path")
    p_edit.add_argument("--target", required=True, help="Target topic title")
    p_edit.add_argument("--title", help="New title")
    p_edit.add_argument("--note", help="Note text")
    p_edit.add_argument("--comment", help="Comment text")
    p_edit.add_argument("--marker", help="Marker ID")
    p_edit.add_argument("--label", help="Label text")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    commands = {
        "create": cmd_create,
        "show": cmd_show,
        "markdown": cmd_markdown,
        "add": cmd_add,
        "edit": cmd_edit,
    }

    try:
        commands[args.command](args)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

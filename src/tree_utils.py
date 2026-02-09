from pathlib import Path
import os

def get_dir_tree(startpath: Path):
    """
    Generates a dictionary representing the directory tree structure.
    """
    tree = {"name": startpath.name, "children": []}
    
    try:
        # Sort directories first, then files
        items = sorted(startpath.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        
        for item in items:
            if item.name.startswith('.'): # Skip hidden files
                continue
                
            if item.is_dir():
                # Recursively add directories, but limit depth to prevent infinite loops or huge trees
                # For this MVP, let's just go deep enough
                subtree = get_dir_tree(item)
                if subtree:
                    tree["children"].append(subtree)
            else:
                tree["children"].append({"name": item.name, "value": str(item.relative_to(startpath.parent))})
    except PermissionError:
        pass
        
    return tree

def format_tree_for_streamlit(tree, indent=0):
    """
    Formats the tree for display in Streamlit (text-based for now or recursive expanders).
    """
    # This is a placeholder. In app.py we will use recursive expanders.
    pass

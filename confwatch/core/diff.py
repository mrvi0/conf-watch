"""
Diff viewer module for comparing file versions.
"""

import difflib
from typing import List, Tuple


class DiffViewer:
    """Viewer for file differences."""
    
    @staticmethod
    def unified_diff(file1_content: str, file2_content: str, 
                    file1_name: str = "file1", file2_name: str = "file2") -> str:
        """Generate unified diff between two file contents."""
        diff = difflib.unified_diff(
            file1_content.splitlines(keepends=True),
            file2_content.splitlines(keepends=True),
            fromfile=file1_name,
            tofile=file2_name
        )
        return ''.join(diff)
    
    @staticmethod
    def side_by_side_diff(file1_content: str, file2_content: str) -> List[Tuple[str, str, str]]:
        """Generate side-by-side diff."""
        matcher = difflib.SequenceMatcher(None, file1_content.splitlines(), file2_content.splitlines())
        
        result = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Lines are the same
                for line in file1_content.splitlines()[i1:i2]:
                    result.append((line, line, 'equal'))
            elif tag == 'replace':
                # Lines are different
                lines1 = file1_content.splitlines()[i1:i2]
                lines2 = file2_content.splitlines()[j1:j2]
                max_len = max(len(lines1), len(lines2))
                
                for k in range(max_len):
                    line1 = lines1[k] if k < len(lines1) else ''
                    line2 = lines2[k] if k < len(lines2) else ''
                    result.append((line1, line2, 'replace'))
            elif tag == 'delete':
                # Lines deleted from file1
                for line in file1_content.splitlines()[i1:i2]:
                    result.append((line, '', 'delete'))
            elif tag == 'insert':
                # Lines inserted in file2
                for line in file2_content.splitlines()[j1:j2]:
                    result.append(('', line, 'insert'))
        
        return result
    
    @staticmethod
    def html_diff(file1_content: str, file2_content: str, 
                 file1_name: str = "file1", file2_name: str = "file2") -> str:
        """Generate HTML diff."""
        diff = difflib.HtmlDiff()
        return diff.make_file(
            file1_content.splitlines(),
            file2_content.splitlines(),
            file1_name,
            file2_name
        ) 
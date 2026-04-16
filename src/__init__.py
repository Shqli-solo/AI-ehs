"""
EHS 项目源代码包
"""

import sys
from pathlib import Path

# 添加 src 目录到路径，以便导入 ehs-ai 包
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

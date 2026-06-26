"""
文档解析模块
支持PDF/DOC/DOCX/TXT文件输入，提取文本内容
"""

import os
from pathlib import Path
from typing import List


class DocumentParser:
    """文档解析器"""
    
    SUPPORTED_FORMATS = ['.txt', '.pdf', '.doc', '.docx']
    
    def parse(self, file_path: str) -> str:
        """
        解析文档，提取文本内容
        
        Args:
            file_path: 文件路径
        
        Returns:
            提取的文本内容
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        ext = path.suffix.lower()
        
        if ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"不支持的格式: {ext}，支持: {', '.join(self.SUPPORTED_FORMATS)}")
        
        if ext == '.txt':
            return self._parse_txt(file_path)
        elif ext == '.pdf':
            return self._parse_pdf(file_path)
        elif ext in ['.doc', '.docx']:
            return self._parse_docx(file_path)
        else:
            raise ValueError(f"未实现的格式: {ext}")
    
    def _parse_txt(self, file_path: str) -> str:
        """解析TXT文件"""
        # 尝试多种编码
        for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        raise ValueError(f"无法解码文件: {file_path}")
    
    def _parse_pdf(self, file_path: str) -> str:
        """解析PDF文件"""
        try:
            import PyPDF2
        except ImportError:
            raise ImportError("需要安装PyPDF2: pip install PyPDF2")
        
        text_parts = []
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
        except Exception as e:
            raise ValueError(f"PDF解析失败: {e}")
        
        return '\n'.join(text_parts)
    
    def _parse_docx(self, file_path: str) -> str:
        """解析DOCX文件"""
        try:
            import docx
        except ImportError:
            raise ImportError("需要安装python-docx: pip install python-docx")
        
        try:
            doc = docx.Document(file_path)
            text_parts = []
            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text)
        except Exception as e:
            raise ValueError(f"DOCX解析失败: {e}")
        
        return '\n'.join(text_parts)
    
    def extract_knowledge_points(self, text: str, max_points: int = 50) -> List[str]:
        """
        从文本中提取知识点（按行分割）
        
        Args:
            text: 文档文本内容
            max_points: 最大知识点数量
        
        Returns:
            知识点列表
        """
        lines = text.strip().split('\n')
        points = []
        
        for line in lines:
            line = line.strip()
            if line and len(line) >= 2:  # 过滤空行和太短的行
                points.append(line)
                if len(points) >= max_points:
                    break
        
        return points

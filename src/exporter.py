"""
Markdown导出模块
将试卷和答案导出为Markdown格式
"""

from typing import List, Dict
import os


class MarkdownExporter:
    """Markdown导出器"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def export(self, questions: List[Dict], title: str = "试卷") -> Dict[str, str]:
        """
        导出试卷和答案
        
        Args:
            questions: 题目列表（包含分值）
            title: 试卷标题
        
        Returns:
            {"exam_path": "...", "answer_path": "..."}
        """
        exam_content = self._generate_exam_markdown(questions, title)
        answer_content = self._generate_answer_markdown(questions, title)
        
        exam_path = os.path.join(self.output_dir, f"{title}.md")
        answer_path = os.path.join(self.output_dir, f"{title}_答案.md")
        
        with open(exam_path, "w", encoding="utf-8") as f:
            f.write(exam_content)
        
        with open(answer_path, "w", encoding="utf-8") as f:
            f.write(answer_content)
        
        return {
            "exam_path": exam_path,
            "answer_path": answer_path
        }
    
    def _generate_exam_markdown(self, questions: List[Dict], title: str) -> str:
        """生成试卷Markdown"""
        lines = [f"# {title}\n"]
        
        # 按题型分组
        questions_by_type = {}
        for q in questions:
            q_type = q["type"]
            if q_type not in questions_by_type:
                questions_by_type[q_type] = []
            questions_by_type[q_type].append(q)
        
        # 生成各题型
        type_names = {
            "single_choice": "单选题",
            "true_false": "判断题",
            "short_answer": "简答题"
        }
        
        question_num = 1
        for q_type in ["single_choice", "true_false", "short_answer"]:
            if q_type not in questions_by_type:
                continue
            
            qs = questions_by_type[q_type]
            type_name = type_names.get(q_type, q_type)
            
            # 计算该题型总分
            type_total = sum(q["score"] for q in qs)
            lines.append(f"\n## {type_names.get(q_type, q_type)}（每题{qs[0]['score']}分，共{type_total}分）\n")
            
            for q in qs:
                lines.append(f"{question_num}. {q['question']}（{q['score']}分）")
                
                if q_type == "single_choice" and q.get("options"):
                    for opt in q["options"]:
                        lines.append(f"   {opt}")
                
                lines.append("")
                question_num += 1
        
        return "\n".join(lines)
    
    def _generate_answer_markdown(self, questions: List[Dict], title: str) -> str:
        """生成答案Markdown"""
        lines = [f"# {title} - 答案\n"]
        
        # 按题型分组
        questions_by_type = {}
        for q in questions:
            q_type = q["type"]
            if q_type not in questions_by_type:
                questions_by_type[q_type] = []
            questions_by_type[q_type].append(q)
        
        type_names = {
            "single_choice": "单选题",
            "true_false": "判断题",
            "short_answer": "简答题"
        }
        
        question_num = 1
        for q_type in ["single_choice", "true_false", "short_answer"]:
            if q_type not in questions_by_type:
                continue
            
            qs = questions_by_type[q_type]
            lines.append(f"\n## {type_names.get(q_type, q_type)}\n")
            
            for q in qs:
                lines.append(f"{question_num}. **答案：{q['answer']}**\n")
                question_num += 1
        
        return "\n".join(lines)

"""
AI出题模块
根据知识点生成题目
"""

from typing import List, Dict
from .llm_client import LLMClient


class QuestionGenerator:
    """题目生成器"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    def generate_questions(self, knowledge_points: List[str], 
                          question_types: List[str] = None) -> List[Dict]:
        """
        根据知识点生成题目
        
        Args:
            knowledge_points: 知识点列表
            question_types: 题型列表（single_choice, true_false, short_answer）
        
        Returns:
            题目列表，每个题目包含：type, question, options, answer, score
        """
        if not question_types:
            question_types = ["single_choice", "true_false", "short_answer"]
        
        questions = []
        
        # 为每个题型生成题目
        for q_type in question_types:
            prompt = self._build_prompt(knowledge_points, q_type)
            response = self.llm_client.generate(prompt)
            parsed = self._parse_response(response, q_type)
            questions.extend(parsed)
        
        return questions
    
    def _build_prompt(self, knowledge_points: List[str], q_type: str) -> str:
        """构建prompt"""
        kp_text = "\n".join([f"- {kp}" for kp in knowledge_points])
        
        if q_type == "single_choice":
            return f"""请根据以下知识点生成5道单选题。

知识点：
{kp_text}

要求：
1. 每道题必须有4个选项（A/B/C/D）
2. 只有一个正确答案
3. 题目要覆盖不同知识点
4. 输出格式：

题目1：[题目内容]
A. [选项A]
B. [选项B]
C. [选项C]
D. [选项D]
答案：[A/B/C/D]

---

请生成5道题："""

        elif q_type == "true_false":
            return f"""请根据以下知识点生成5道判断题。

知识点：
{kp_text}

要求：
1. 每道题只能判断"对"或"错"
2. 答案要准确
3. 题目要覆盖不同知识点
4. 输出格式：

题目1：[题目内容]
答案：[对/错]

---

请生成5道题："""

        elif q_type == "short_answer":
            return f"""请根据以下知识点生成2道简答题。

知识点：
{kp_text}

要求：
1. 题目要有深度，考察理解
2. 答案要包含关键知识点
3. 输出格式：

题目1：[题目内容]
答案：[参考答案]

---

请生成2道题："""
        
        return ""
    
    def _parse_response(self, response: str, q_type: str) -> List[Dict]:
        """解析AI响应"""
        questions = []
        
        # 简单解析逻辑（后续优化）
        lines = response.strip().split("\n")
        current_q = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith("题目") and "：" in line:
                if current_q:
                    questions.append(current_q)
                current_q = {
                    "type": q_type,
                    "question": line.split("：", 1)[1],
                    "options": [],
                    "answer": "",
                    "score": 0
                }
            elif current_q and q_type == "single_choice":
                if line.startswith(("A.", "B.", "C.", "D.")):
                    current_q["options"].append(line)
                elif line.startswith("答案："):
                    current_q["answer"] = line.split("：", 1)[1].strip()
            elif current_q and q_type == "true_false":
                if line.startswith("答案："):
                    current_q["answer"] = line.split("：", 1)[1].strip()
            elif current_q and q_type == "short_answer":
                if line.startswith("答案："):
                    current_q["answer"] = line.split("：", 1)[1].strip()
        
        if current_q:
            questions.append(current_q)
        
        return questions

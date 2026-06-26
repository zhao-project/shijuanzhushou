"""
AI出题模块
根据知识点生成题目
"""

from typing import List, Dict
from .llm_client import LLMClient
import json
import re


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
        """构建prompt（精简版，减少token消耗）"""
        kp_text = "、".join(knowledge_points[:5])  # 限制知识点数量
        
        if q_type == "single_choice":
            return f"""根据知识点出2道单选题。
知识点：{kp_text}
输出JSON格式：[{{"question":"题目","options":["A.x","B.x","C.x","D.x"],"answer":"A"}}]"""

        elif q_type == "true_false":
            return f"""根据知识点出2道判断题。
知识点：{kp_text}
输出JSON格式：[{{"question":"题目","answer":"对"}}]"""

        elif q_type == "short_answer":
            return f"""根据知识点出1道简答题。
知识点：{kp_text}
输出JSON格式：[{{"question":"题目","answer":"答案"}}]"""
        
        return ""
    
    def _parse_response(self, response: str, q_type: str) -> List[Dict]:
        """解析AI响应"""
        questions = []
        
        # 尝试JSON解析
        try:
            # 提取JSON部分
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_str = response
            
            parsed_data = json.loads(json_str)
            
            for item in parsed_data:
                question = {
                    "type": q_type,
                    "question": item.get("question", ""),
                    "options": item.get("options", []),
                    "answer": item.get("answer", ""),
                    "score": 0
                }
                questions.append(question)
                
        except (json.JSONDecodeError, KeyError) as e:
            # JSON解析失败，回退到文本解析
            questions = self._parse_text_response(response, q_type)
        
        return questions
    
    def _parse_text_response(self, response: str, q_type: str) -> List[Dict]:
        """文本解析（备用方案）"""
        questions = []
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

"""
规则校验模块
验证试卷格式、分值、覆盖率等
"""

from typing import List, Dict, Set


class ExamValidator:
    """试卷校验器"""
    
    def validate(self, questions: List[Dict], knowledge_points: List[str]) -> Dict:
        """
        校验试卷
        
        Returns:
            {
                "valid": True/False,
                "errors": [...],
                "warnings": [...],
                "coverage": {...}
            }
        """
        errors = []
        warnings = []
        
        # 1. 格式校验
        self._validate_format(questions, errors)
        
        # 2. 分值校验
        self._validate_scores(questions, errors)
        
        # 3. 去重检测
        self._validate_duplicates(questions, warnings)
        
        # 4. 知识点覆盖率
        coverage = self._calculate_coverage(questions, knowledge_points)
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "coverage": coverage
        }
    
    def _validate_format(self, questions: List[Dict], errors: List[str]):
        """格式校验"""
        for i, q in enumerate(questions, 1):
            q_type = q.get("type")
            
            if q_type == "single_choice":
                options = q.get("options", [])
                if len(options) != 4:
                    errors.append(f"题目{i}：单选题必须有4个选项，当前{len(options)}个")
                
                answer = q.get("answer", "")
                if answer not in ["A", "B", "C", "D"]:
                    errors.append(f"题目{i}：单选题答案必须是A/B/C/D，当前'{answer}'")
            
            elif q_type == "true_false":
                answer = q.get("answer", "")
                if answer not in ["对", "错"]:
                    errors.append(f"题目{i}：判断题答案必须是'对'或'错'，当前'{answer}'")
            
            elif q_type == "short_answer":
                answer = q.get("answer", "")
                if not answer:
                    errors.append(f"题目{i}：简答题必须有参考答案")
            
            # 通用检查
            if not q.get("question"):
                errors.append(f"题目{i}：题目内容不能为空")
            
            if q.get("score", 0) <= 0:
                errors.append(f"题目{i}：分值必须大于0")
    
    def _validate_scores(self, questions: List[Dict], errors: List[str]):
        """分值校验"""
        total = sum(q.get("score", 0) for q in questions)
        if total != 100:
            errors.append(f"分值总和={total}，不等于100")
    
    def _validate_duplicates(self, questions: List[Dict], warnings: List[str]):
        """去重检测（简单版本：完全相同的题目）"""
        seen = set()
        for i, q in enumerate(questions, 1):
            q_text = q.get("question", "")
            if q_text in seen:
                warnings.append(f"题目{i}：与前面题目重复")
            seen.add(q_text)
    
    def _calculate_coverage(self, questions: List[Dict], 
                           knowledge_points: List[str]) -> Dict:
        """计算知识点覆盖率"""
        # 合并所有题目文本
        all_text = " ".join([
            q.get("question", "") + " " + q.get("answer", "")
            for q in questions
        ])
        
        # 检查每个知识点是否出现
        covered = []
        not_covered = []
        
        for kp in knowledge_points:
            # 简单关键词匹配
            if kp.lower() in all_text.lower():
                covered.append(kp)
            else:
                not_covered.append(kp)
        
        coverage_rate = len(covered) / len(knowledge_points) if knowledge_points else 0
        
        return {
            "total": len(knowledge_points),
            "covered": len(covered),
            "not_covered": len(not_covered),
            "coverage_rate": coverage_rate,
            "covered_points": covered,
            "not_covered_points": not_covered
        }

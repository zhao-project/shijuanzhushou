"""
分值分配模块
根据题型和总分自动分配分值
"""

from typing import List, Dict


class ScoreAssembler:
    """分值分配器"""
    
    def __init__(self, total_score: int = 100):
        self.total_score = total_score
    
    def assign_scores(self, questions: List[Dict], 
                     question_config: List[Dict]) -> List[Dict]:
        """
        为题目分配分值
        
        Args:
            questions: 题目列表
            question_config: 题型配置（包含每种题型的分值）
        
        Returns:
            分配了分值的题目列表
        """
        # 按题型分组
        questions_by_type = {}
        for q in questions:
            q_type = q["type"]
            if q_type not in questions_by_type:
                questions_by_type[q_type] = []
            questions_by_type[q_type].append(q)
        
        # 计算每种题型应该分配的分值
        type_scores = self._calculate_type_scores(
            questions_by_type, 
            question_config
        )
        
        # 为每道题分配分值
        for q_type, qs in questions_by_type.items():
            score_per_question = type_scores.get(q_type, 0)
            for q in qs:
                q["score"] = score_per_question
        
        # 验证总分
        actual_total = sum(q["score"] for q in questions)
        if actual_total != self.total_score:
            # 调整最后一道题的分值
            diff = self.total_score - actual_total
            if questions:
                questions[-1]["score"] += diff
        
        return questions
    
    def _calculate_type_scores(self, questions_by_type: Dict[str, List],
                               question_config: List[Dict]) -> Dict[str, int]:
        """计算每种题型的分值"""
        type_scores = {}
        
        # 构建配置映射
        config_map = {c["type"]: c for c in question_config}
        
        # 计算总分中每种题型应该占的比例
        total_questions = sum(len(qs) for qs in questions_by_type.values())
        
        for q_type, qs in questions_by_type.items():
            if q_type in config_map:
                score_per_question = config_map[q_type]["score_per_question"]
                type_scores[q_type] = score_per_question
        
        return type_scores

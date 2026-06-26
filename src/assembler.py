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
        
        # 构建配置映射
        config_map = {c["type"]: c for c in question_config}
        
        # 为每道题分配分值
        for q_type, qs in questions_by_type.items():
            if q_type in config_map:
                score_per_question = config_map[q_type]["score_per_question"]
                for q in qs:
                    q["score"] = score_per_question
        
        # 计算当前总分
        actual_total = sum(q["score"] for q in questions)
        
        # 调整分值使总分等于目标值
        if actual_total != self.total_score:
            diff = self.total_score - actual_total
            # 调整最后一道题的分值
            if questions:
                questions[-1]["score"] += diff
        
        return questions

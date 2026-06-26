"""
自动化测试脚本
验证MVP核心功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.llm_client import create_llm_client
from src.generator import QuestionGenerator
from src.assembler import ScoreAssembler
from src.validator import ExamValidator
from src.exporter import MarkdownExporter


def test_mvp():
    """MVP功能测试"""
    print("=" * 60)
    print("MVP自动化测试")
    print("=" * 60)
    
    # 测试知识点
    knowledge_points = [
        "Python基础语法",
        "变量和数据类型",
        "条件语句",
        "循环语句",
        "函数定义和调用"
    ]
    
    print(f"\n✅ 测试知识点：{len(knowledge_points)}个")
    for kp in knowledge_points:
        print(f"   - {kp}")
    
    # 1. 创建LLM客户端
    print("\n[1/6] 创建LLM客户端...")
    try:
        llm_client = create_llm_client()
        print("   ✅ 客户端创建成功")
    except Exception as e:
        print(f"   ❌ 失败：{e}")
        return False
    
    # 2. 生成题目
    print("\n[2/6] 生成题目...")
    generator = QuestionGenerator(llm_client)
    question_types = ["single_choice", "true_false", "short_answer"]
    
    try:
        questions = generator.generate_questions(knowledge_points, question_types)
        print(f"   ✅ 生成{len(questions)}道题目")
        
        # 统计题型
        type_count = {}
        for q in questions:
            q_type = q["type"]
            type_count[q_type] = type_count.get(q_type, 0) + 1
        
        for q_type, count in type_count.items():
            print(f"   - {q_type}: {count}道")
    except Exception as e:
        print(f"   ❌ 失败：{e}")
        return False
    
    # 3. 分配分值
    print("\n[3/6] 分配分值...")
    total_score = 100
    question_config = [
        {"type": "single_choice", "score_per_question": 2},
        {"type": "true_false", "score_per_question": 1},
        {"type": "short_answer", "score_per_question": 10}
    ]
    
    assembler = ScoreAssembler(total_score)
    questions = assembler.assign_scores(questions, question_config)
    
    actual_total = sum(q["score"] for q in questions)
    print(f"   ✅ 总分：{actual_total}分（目标：{total_score}分）")
    
    if actual_total != total_score:
        print(f"   ❌ 分值不匹配")
        return False
    
    # 4. 校验试卷
    print("\n[4/6] 校验试卷...")
    validator = ExamValidator()
    result = validator.validate(questions, knowledge_points, total_score)
    
    print(f"   格式校验：{'✅ 通过' if not result['errors'] else '❌ 失败'}")
    print(f"   知识点覆盖率：{result['coverage']['coverage_rate']:.0%}（{result['coverage']['covered']}/{result['coverage']['total']}）")
    
    if result["errors"]:
        print(f"   ❌ 发现{len(result['errors'])}个错误：")
        for err in result["errors"]:
            print(f"      - {err}")
        return False
    
    if result["warnings"]:
        print(f"   ⚠️  {len(result['warnings'])}个警告：")
        for warn in result["warnings"]:
            print(f"      - {warn}")
    
    # 5. 导出试卷
    print("\n[5/6] 导出试卷...")
    exporter = MarkdownExporter("output")
    paths = exporter.export(questions, title="测试试卷")
    
    print(f"   ✅ 试卷文件：{paths['exam_path']}")
    print(f"   ✅ 答案文件：{paths['answer_path']}")
    
    # 检查文件是否存在
    if not os.path.exists(paths['exam_path']):
        print(f"   ❌ 试卷文件不存在")
        return False
    if not os.path.exists(paths['answer_path']):
        print(f"   ❌ 答案文件不存在")
        return False
    
    # 6. 显示API用量
    print("\n[6/6] API用量统计...")
    if hasattr(llm_client, 'get_total_usage'):
        usage = llm_client.get_total_usage()
        print(f"   调用次数：{usage['calls']}")
        print(f"   总Token：{usage['total_tokens']}")
        print(f"   输入Token：{usage['total_prompt_tokens']}")
        print(f"   输出Token：{usage['total_completion_tokens']}")
    
    print("\n" + "=" * 60)
    print("✅ MVP测试通过！")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = test_mvp()
    sys.exit(0 if success else 1)

"""
试卷助手 - 命令行入口
"""

import os
import sys
import yaml
from typing import List
from pathlib import Path

# 添加src到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.llm_client import create_llm_client
from src.generator import QuestionGenerator
from src.assembler import ScoreAssembler
from src.exporter import MarkdownExporter
from src.validator import ExamValidator


def load_config() -> dict:
    """加载配置文件"""
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_knowledge_points() -> List[str]:
    """获取用户输入的知识点（支持手动输入或文件导入）"""
    print("请选择输入方式：")
    print("1. 手动输入知识点")
    print("2. 从文件导入（支持txt/pdf/doc/docx）")
    
    try:
        choice = input("请输入选项（1/2）：").strip()
    except EOFError:
        choice = "1"
    
    if choice == "2":
        return _load_from_file()
    else:
        return _manual_input()


def _manual_input() -> List[str]:
    """手动输入知识点"""
    print("\n请输入知识点（每行一个，输入空行结束）：")
    points = []
    while True:
        try:
            line = input().strip()
            if not line:
                break
            points.append(line)
        except EOFError:
            break
    
    if not points:
        print("❌ 错误：请输入至少1个知识点")
        sys.exit(1)
    
    return _validate_points(points)


def _load_from_file() -> List[str]:
    """从文件加载知识点"""
    print("\n请输入文件路径：")
    try:
        file_path = input().strip()
    except EOFError:
        print("❌ 错误：未输入文件路径")
        sys.exit(1)
    
    if not file_path:
        print("❌ 错误：文件路径不能为空")
        sys.exit(1)
    
    try:
        from src.parser import DocumentParser
        parser = DocumentParser()
        text = parser.parse(file_path)
        points = parser.extract_knowledge_points(text)
        
        if not points:
            print("❌ 错误：文件中未提取到知识点")
            sys.exit(1)
        
        print(f"✅ 从文件提取到{len(points)}个知识点")
        return _validate_points(points)
        
    except FileNotFoundError as e:
        print(f"❌ 错误：{e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ 错误：{e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误：文件解析失败 - {e}")
        sys.exit(1)


def _validate_points(points: List[str]) -> List[str]:
    """验证知识点数量"""
    if len(points) < 3:
        print("⚠️  警告：建议输入10-50个知识点，当前只有{}个".format(len(points)))
    elif len(points) > 100:
        print("⚠️  警告：知识点过多（{}个），建议10-50个".format(len(points)))
        points = points[:100]
        print("已截取前100个知识点")
    
    return points


def get_total_score(default: int = 100) -> int:
    """获取总分"""
    print(f"请输入总分（默认{default}）：")
    try:
        line = input().strip()
        if not line:
            return default
        score = int(line)
        if score <= 0:
            print("❌ 错误：总分必须大于0")
            sys.exit(1)
        return score
    except ValueError:
        print("❌ 错误：总分必须是整数")
        sys.exit(1)
    except EOFError:
        return default


def main():
    """主流程"""
    print("=" * 60)
    print("试卷助手 v1.0")
    print("=" * 60)
    print()
    
    # 1. 加载配置
    config = load_config()
    
    # 2. 获取用户输入
    knowledge_points = get_knowledge_points()
    print(f"✅ 已输入{len(knowledge_points)}个知识点")
    print()
    
    total_score = get_total_score(config["exam"]["default_total_score"])
    print(f"✅ 总分：{total_score}分")
    print()
    
    # 3. 创建LLM客户端（从.env读取配置）
    try:
        llm_client = create_llm_client()
        print("✅ LLM客户端创建成功")
        print(f"   模型：{config.get('api', {}).get('model', 'qwen3.7-plus')}")
    except Exception as e:
        print(f"❌ 错误：{e}")
        sys.exit(1)
    
    # 4. 生成题目
    print("正在生成试卷，请稍候...")
    generator = QuestionGenerator(llm_client)
    question_types = [qt["type"] for qt in config["exam"]["question_types"]]
    questions = generator.generate_questions(knowledge_points, question_types)
    print(f"✅ 生成{len(questions)}道题目")
    print()
    
    # 5. 分配分值
    assembler = ScoreAssembler(total_score)
    questions = assembler.assign_scores(questions, config["exam"]["question_types"])
    print("✅ 分值分配完成")
    print()
    
    # 6. 校验试卷
    validator = ExamValidator()
    result = validator.validate(questions, knowledge_points, total_score)
    
    print("📊 校验结果：")
    print(f"   格式校验：{'✅ 通过' if not result['errors'] else '❌ 失败'}")
    print(f"   知识点覆盖率：{result['coverage']['coverage_rate']:.0%}（{result['coverage']['covered']}/{result['coverage']['total']}）")
    
    if result["errors"]:
        print("\n❌ 发现错误：")
        for err in result["errors"]:
            print(f"   - {err}")
        sys.exit(1)
    
    if result["warnings"]:
        print("\n⚠️  警告：")
        for warn in result["warnings"]:
            print(f"   - {warn}")
    
    print()
    
    # 7. 导出试卷
    exporter = MarkdownExporter(config["output"]["directory"])
    paths = exporter.export(questions, title="试卷")
    
    print("✅ 试卷生成完成！")
    print(f"   试卷文件：{paths['exam_path']}")
    print(f"   答案文件：{paths['answer_path']}")
    print()
    
    # 8. 展示预览
    print("=" * 60)
    print("试卷预览（前3道题）：")
    print("=" * 60)
    for i, q in enumerate(questions[:3], 1):
        print(f"{i}. {q['question']}（{q['score']}分）")
        if q["type"] == "single_choice" and q.get("options"):
            for opt in q["options"]:
                print(f"   {opt}")
        print()
    
    # 9. 显示API用量（如果有）
    if hasattr(llm_client, 'get_total_usage'):
        usage = llm_client.get_total_usage()
        print("=" * 60)
        print(f"📊 API用量统计：")
        print(f"   调用次数：{usage['calls']}")
        print(f"   总Token：{usage['total_tokens']}")
        print(f"   输入Token：{usage['total_prompt_tokens']}")
        print(f"   输出Token：{usage['total_completion_tokens']}")
    
    print("=" * 60)
    print("✅ 完成！")


if __name__ == "__main__":
    main()

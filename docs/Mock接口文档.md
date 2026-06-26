# Mock接口文档 - 试卷助手MVP

**版本：** v1.0  
**日期：** 2026-06-26  
**作者：** 开发主管

---

## 一、概述

本文档提供Mock接口说明，用于测试骨干在无API Key或API超时时进行测试。

---

## 二、MockClient使用方法

### 2.1 导入模块

```python
from src.llm_client import MockClient
from src.generator import QuestionGenerator
```

### 2.2 创建Mock客户端

```python
# 创建Mock客户端（不消耗API额度）
client = MockClient()
```

### 2.3 自定义Mock响应

```python
# 自定义响应列表
mock_responses = [
    # 第1次调用返回
    '''```json
[
    {"question": "Python中哪个是合法变量名？", "options": ["A. 2name", "B. my_name", "C. class", "D. my-name"], "answer": "B"},
    {"question": "以下哪个数据类型不可变？", "options": ["A. list", "B. dict", "C. tuple", "D. set"], "answer": "C"}
]
```''',
    
    # 第2次调用返回
    '''```json
[
    {"question": "Python函数可以有多个返回值", "answer": "对"}
]
```''',
    
    # 第3次调用返回
    '''```json
[
    {"question": "简述列表和元组的区别", "answer": "列表可变，元组不可变"}
]
'''
]

client = MockClient(mock_responses)
generator = QuestionGenerator(client)
```

---

## 三、Mock响应格式

### 3.1 单选题格式

```json
[
    {
        "question": "题目内容",
        "options": [
            "A. 选项A",
            "B. 选项B",
            "C. 选项C",
            "D. 选项D"
        ],
        "answer": "A"
    }
]
```

**要求：**
- `question`: 题目描述
- `options`: 必须4个选项，格式为 "A. xxx"
- `answer`: 必须是 A/B/C/D 之一

### 3.2 判断题格式

```json
[
    {
        "question": "题目内容",
        "answer": "对"
    }
]
```

**要求：**
- `question`: 题目描述
- `answer`: 必须是 "对" 或 "错"

### 3.3 简答题格式

```json
[
    {
        "question": "题目内容",
        "answer": "参考答案内容"
    }
]
```

**要求：**
- `question`: 题目描述
- `answer`: 参考答案（不能为空）

---

## 四、完整测试示例

### 4.1 基础测试（使用MockClient）

```python
import json
from src.llm_client import MockClient
from src.generator import QuestionGenerator
from src.assembler import ScoreAssembler
from src.validator import ExamValidator
from src.exporter import MarkdownExporter

# 1. 准备Mock数据
mock_single = json.dumps([
    {"question": "Python中哪个是合法变量名？", "options": ["A. 2name", "B. my_name", "C. class", "D. my-name"], "answer": "B"},
    {"question": "以下哪个数据类型不可变？", "options": ["A. list", "B. dict", "C. tuple", "D. set"], "answer": "C"}
])

mock_tf = json.dumps([
    {"question": "Python函数可以有多个返回值", "answer": "对"}
])

mock_sa = json.dumps([
    {"question": "简述列表和元组的区别", "answer": "列表可变，元组不可变"}
])

# 2. 创建Mock客户端
client = MockClient([mock_single, mock_tf, mock_sa])
generator = QuestionGenerator(client)

# 3. 生成题目
knowledge_points = ["Python基础语法", "变量和数据类型", "条件语句"]
questions = generator.generate_questions(knowledge_points, ["single_choice", "true_false", "short_answer"])

# 4. 分配分值
config = [
    {"type": "single_choice", "score_per_question": 2},
    {"type": "true_false", "score_per_question": 1},
    {"type": "short_answer", "score_per_question": 10}
]
assembler = ScoreAssembler(100)
questions = assembler.assign_scores(questions, config)

# 5. 校验试卷
validator = ExamValidator()
result = validator.validate(questions, knowledge_points, 100)
print("格式校验:", "通过" if not result["errors"] else "失败")
print("覆盖率:", result["coverage"]["coverage_rate"])

# 6. 导出试卷
exporter = MarkdownExporter("output")
paths = exporter.export(questions, title="测试试卷")
print("试卷文件:", paths["exam_path"])
print("答案文件:", paths["answer_path"])
```

### 4.2 真实API测试（需要API Key）

```python
from src.llm_client import create_llm_client
from src.generator import QuestionGenerator

# 创建真实客户端（从.env读取配置）
client = create_llm_client()
generator = QuestionGenerator(client)

# 生成题目（注意：长prompt可能超时）
knowledge_points = ["Python基础语法"]
questions = generator.generate_questions(knowledge_points, ["single_choice"])

# 查看API用量
usage = client.get_total_usage()
print("Token消耗:", usage["total_tokens"])
```

---

## 五、测试用例建议

### 5.1 单元测试

| 测试项 | 输入 | 期望输出 |
|--------|------|----------|
| 单选题格式 | 4个选项 | 校验通过 |
| 单选题格式 | 3个选项 | 校验失败 |
| 判断题答案 | "对" | 校验通过 |
| 判断题答案 | "是" | 校验失败 |
| 简答题答案 | 空字符串 | 校验失败 |
| 分值总和 | 100分 | 校验通过 |
| 分值总和 | 90分 | 校验失败 |
| 重复题目 | 2道相同题 | 警告 |

### 5.2 集成测试

| 测试项 | 输入 | 期望输出 |
|--------|------|----------|
| 完整流程 | 5个知识点，100分 | 生成试卷+答案文件 |
| 知识点覆盖 | 3个知识点 | 覆盖率≥60% |
| 文件导出 | 生成试卷 | output/试卷.md 存在 |

### 5.3 边界测试

| 测试项 | 输入 | 期望输出 |
|--------|------|----------|
| 空知识点 | [] | 提示错误 |
| 超长文本 | 10万字 | 截断提示 |
| 知识点过少 | 2个 | 警告提示 |
| 知识点过多 | 100个 | 截取前100个 |

---

## 六、API用量控制

### 6.1 用量统计

```python
from src.llm_client import create_llm_client

client = create_llm_client()
# ... 执行一些操作 ...

usage = client.get_total_usage()
print("调用次数:", usage["calls"])
print("总Token:", usage["total_tokens"])
print("输入Token:", usage["total_prompt_tokens"])
print("输出Token:", usage["total_completion_tokens"])
```

### 6.2 用量日志

API调用会自动记录到 `output/api_usage.log`，格式：

```json
{"timestamp": "2026-06-26 10:30:15", "model": "qwen3.7-plus", "prompt_tokens": 150, "completion_tokens": 80, "total_tokens": 230, "duration_seconds": 2.5}
```

---

## 七、常见问题

### Q1: API超时怎么办？

**A:** 使用MockClient进行测试，或减少单次生成的题目数量。

### Q2: 如何测试不消耗API额度？

**A:** 使用MockClient替代真实客户端：

```python
client = MockClient()  # 不消耗API
# 而不是
client = create_llm_client()  # 消耗API
```

### Q3: Mock响应格式错误怎么办？

**A:** 确保JSON格式正确，使用 ```json 代码块包裹。

---

**文档结束**

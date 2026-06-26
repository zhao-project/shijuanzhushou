# Mock接口文档

## 概述

本文档提供Mock接口说明，供测试骨干在没有真实API Key或需要控制成本时使用。

## MockClient使用

### 1. 创建Mock客户端

```python
from src.llm_client import MockClient

# 创建Mock客户端（不调用真实API）
client = MockClient()
```

### 2. Mock响应格式

MockClient返回预设的JSON格式响应，支持三种题型：

#### 单选题响应
```json
[
  {
    "question": "Python中哪个是合法变量名？",
    "options": ["A. 2name", "B. my_name", "C. class", "D. my-name"],
    "answer": "B"
  },
  {
    "question": "以下哪个数据类型不可变？",
    "options": ["A. list", "B. dict", "C. tuple", "D. set"],
    "answer": "C"
  }
]
```

#### 判断题响应
```json
[
  {
    "question": "Python函数可以有多个返回值",
    "answer": "对"
  },
  {
    "question": "列表是可变的，元组是不可变的",
    "answer": "对"
  }
]
```

#### 简答题响应
```json
[
  {
    "question": "简述列表和元组的区别",
    "answer": "列表可变，元组不可变。列表用[]，元组用()。"
  }
]
```

### 3. 完整测试流程

```python
from src.llm_client import MockClient
from src.generator import QuestionGenerator
from src.assembler import ScoreAssembler
from src.validator import ExamValidator
from src.exporter import MarkdownExporter

# 1. 创建Mock客户端
client = MockClient()

# 2. 生成题目
generator = QuestionGenerator(client)
knowledge_points = ["Python基础语法", "变量", "条件语句"]
questions = generator.generate(knowledge_points, 2, 1, 1)

# 3. 分配分值
assembler = ScoreAssembler(total_score=100)
questions = assembler.assign_scores(questions)

# 4. 校验试卷
validator = ExamValidator()
validation_result = validator.validate(questions, knowledge_points)

# 5. 导出试卷
exporter = MarkdownExporter()
exporter.export(questions, "output/试卷.md", "output/答案.md")
```

### 4. 预期输出

#### 试卷文件（output/试卷.md）
```markdown
# 试卷

**总分：100分**

---

## 一、单选题（每题10分，共20分）

1. Python中哪个是合法变量名？（ ）
   A. 2name
   B. my_name
   C. class
   D. my-name

   **分值：10分**

2. 以下哪个数据类型不可变？（ ）
   A. list
   B. dict
   C. tuple
   D. set

   **分值：10分**

---

## 二、判断题（每题20分，共20分）

1. Python函数可以有多个返回值（ ）

   **分值：20分**

---

## 三、简答题（每题60分，共60分）

1. 简述列表和元组的区别

   **分值：60分**

---

_生成时间：2026-06-26 10:30:15_
_知识点覆盖：3/3 (100%)_
```

#### 答案文件（output/答案.md）
```markdown
# 答案

## 一、单选题
1. B
2. C

## 二、判断题
1. 对

## 三、简答题
1. 列表可变，元组不可变。列表用[]，元组用()。
```

### 5. 测试用例建议

#### 测试用例1：基础功能测试
- 输入：3个知识点
- 题型：2单选 + 1判断 + 1简答
- 预期：生成4道题，总分100分

#### 测试用例2：边界条件测试
- 输入：1个知识点
- 题型：1单选 + 1判断 + 1简答
- 预期：生成3道题，总分100分

#### 测试用例3：覆盖率测试
- 输入：10个知识点
- 题型：5单选 + 3判断 + 2简答
- 预期：生成10道题，覆盖率≥90%

### 6. 注意事项

1. **MockClient不调用真实API**，不会产生费用
2. **响应内容是固定的**，每次调用返回相同结果
3. **JSON格式严格**，确保解析正确
4. **分值分配**会自动调整确保总分=100

### 7. 切换到真实API

测试完成后，切换到真实API：

```python
from src.llm_client import create_llm_client

# 从.env读取配置
client = create_llm_client()

# 后续代码相同
generator = QuestionGenerator(client)
# ...
```

---

**文档版本：** v1.0  
**最后更新：** 2026-06-26  
**维护人：** 开发主管

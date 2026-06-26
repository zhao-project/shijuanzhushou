# 试卷助手

AI驱动的自动出卷工具，帮助老师/培训师快速生成高质量试卷。

## 功能特性

- ✅ 支持单选题、判断题、简答题
- ✅ 智能分值分配（总分100分）
- ✅ 知识点覆盖率检测（≥90%）
- ✅ Markdown格式输出
- ✅ 命令行工具

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API Key

设置环境变量：
```bash
export QWEN_API_KEY="your_api_key_here"
```

或修改 `config.yaml`：
```yaml
api:
  api_key: your_api_key_here
```

### 3. 运行

```bash
python main.py
```

按提示输入知识点和总分，自动生成试卷。

## 项目结构

```
shijuanzhushou/
├── main.py              # 命令行入口
├── config.yaml          # 配置文件
├── requirements.txt     # 依赖
├── src/
│   ├── llm_client.py    # 大模型API封装
│   ├── generator.py     # AI出题模块
│   ├── assembler.py     # 分值分配模块
│   ├── exporter.py      # Markdown导出模块
│   └── validator.py     # 规则校验模块
├── tests/               # 单元测试
├── output/              # 生成的试卷
└── docs/
    └── PRD.md           # 产品需求文档
```

## 验收标准

- ✅ 选择题4个选项（A/B/C/D）
- ✅ 判断题只能"对"或"错"
- ✅ 简答题有参考答案
- ✅ 分值总和=100
- ✅ 知识点覆盖率≥90%
- ✅ 无重复题目

## 开发计划

- **第1-3天**：开发核心功能
- **第4天**：提测
- **第5-6天**：测试+修复Bug+产品验收

## 文档

- [PRD](docs/PRD.md) - 产品需求文档

## License

MIT

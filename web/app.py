"""
Flask Web应用
试卷助手Web界面
"""

import os
import sys
import time
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm_client import create_llm_client
from src.generator import QuestionGenerator
from src.assembler import ScoreAssembler
from src.validator import ExamValidator
from src.exporter import MarkdownExporter
from src.parser import DocumentParser

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['UPLOAD_FOLDER'] = Path(__file__).parent / 'uploads'
app.config['OUTPUT_FOLDER'] = Path(__file__).parent.parent / 'output'

# 确保目录存在
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)
app.config['OUTPUT_FOLDER'].mkdir(exist_ok=True)


@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """上传文件并解析知识点"""
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400
    
    # 检查文件扩展名
    ext = Path(file.filename).suffix.lower()
    if ext not in ['.txt', '.pdf', '.doc', '.docx']:
        return jsonify({'error': f'不支持的格式: {ext}'}), 400
    
    # 保存文件
    filename = f"{int(time.time())}{ext}"
    filepath = app.config['UPLOAD_FOLDER'] / filename
    file.save(filepath)
    
    # 解析文件
    try:
        parser = DocumentParser()
        text = parser.parse(str(filepath))
        points = parser.extract_knowledge_points(text)
        
        return jsonify({
            'success': True,
            'points': points,
            'count': len(points)
        })
    except Exception as e:
        return jsonify({'error': f'解析失败: {str(e)}'}), 500


@app.route('/generate', methods=['POST'])
def generate_exam():
    """生成试卷"""
    data = request.json
    
    # 获取参数
    knowledge_points = data.get('knowledge_points', [])
    total_score = int(data.get('total_score', 100))
    question_config = data.get('question_config', [
        {'type': 'single_choice', 'count': 5, 'score_per_question': 2},
        {'type': 'true_false', 'count': 5, 'score_per_question': 1},
        {'type': 'short_answer', 'count': 2, 'score_per_question': 10}
    ])
    
    if not knowledge_points:
        return jsonify({'error': '知识点为空'}), 400
    
    try:
        # 1. 创建LLM客户端
        llm_client = create_llm_client()
        
        # 2. 生成题目
        generator = QuestionGenerator(llm_client)
        question_types = [qc['type'] for qc in question_config]
        questions = generator.generate_questions(knowledge_points, question_types)
        
        # 3. 分配分值
        assembler = ScoreAssembler(total_score)
        questions = assembler.assign_scores(questions, question_config)
        
        # 4. 校验试卷
        validator = ExamValidator()
        result = validator.validate(questions, knowledge_points, total_score)
        
        if not result['valid']:
            return jsonify({
                'error': '试卷校验失败',
                'details': result['errors']
            }), 400
        
        # 5. 导出试卷
        timestamp = int(time.time())
        title = f"试卷_{timestamp}"
        exporter = MarkdownExporter(str(app.config['OUTPUT_FOLDER']))
        paths = exporter.export(questions, title=title)
        
        # 6. 返回结果
        exam_content = Path(paths['exam_path']).read_text(encoding='utf-8')
        answer_content = Path(paths['answer_path']).read_text(encoding='utf-8')
        
        return jsonify({
            'success': True,
            'exam_content': exam_content,
            'answer_content': answer_content,
            'exam_file': paths['exam_path'],
            'answer_file': paths['answer_path'],
            'coverage': result['coverage'],
            'warnings': result['warnings']
        })
        
    except Exception as e:
        return jsonify({'error': f'生成失败: {str(e)}'}), 500


@app.route('/download/<filename>')
def download_file(filename):
    """下载文件"""
    filepath = app.config['OUTPUT_FOLDER'] / filename
    if not filepath.exists():
        return jsonify({'error': '文件不存在'}), 404
    
    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename
    )


if __name__ == '__main__':
    print("=" * 60)
    print("试卷助手 Web界面")
    print("=" * 60)
    print(f"访问地址: http://localhost:5000")
    print("按 Ctrl+C 停止服务")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, request, render_template_string, send_from_directory
import os
from werkzeug.utils import secure_filename

# 配置 - 直接上传到F盘根目录
UPLOAD_FOLDER = 'F:/'  # F盘根目录
# 不限制文件类型，移除ALLOWED_EXTENSIONS检查

# 初始化Flask应用
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 最大上传文件大小：100MB（可根据需要调整）

# 主页面HTML模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Web文件传输系统</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px; 
            background-color: #f0f0f0;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 { color: #333; }
        .upload-form { margin-bottom: 30px; }
        input[type="file"] { margin: 10px 0; }
        input[type="submit"] {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        input[type="submit"]:hover { background-color: #45a049; }
        .file-list { list-style-type: none; padding: 0; }
        .file-item {
            padding: 10px;
            margin: 5px 0;
            background-color: #f9f9f9;
            border-radius: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .file-link { text-decoration: none; color: #2196F3; }
        .file-link:hover { text-decoration: underline; }
        .delete-btn {
            background-color: #f44336;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 3px;
            cursor: pointer;
        }
        .message {
            padding: 10px;
            margin: 15px 0;
            border-radius: 4px;
        }
        .success { background-color: #dff0d8; color: #3c763d; }
        .error { background-color: #f2dede; color: #a94442; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Web文件传输系统</h1>
        
        {% if message %}
            <div class="message {{ message_type }}">{{ message }}</div>
        {% endif %}
        
        <div class="upload-form">
            <h2>上传文件</h2>
            <form method="POST" enctype="multipart/form-data">
                <input type="file" name="file" multiple>
                <br>
                <input type="submit" value="上传文件">
            </form>
            <p><small>提示：支持所有类型的文件上传</small></p>
        </div>
        
        <div class="file-list-section">
            <h2>F盘文件列表</h2>
            {% if files %}
                <ul class="file-list">
                    {% for file in files %}
                        <li class="file-item">
                            <a href="{{ url_for('download_file', filename=file) }}" class="file-link">{{ file }}</a>
                            <form action="{{ url_for('delete_file', filename=file) }}" method="POST" style="display: inline;">
                                <button type="submit" class="delete-btn" onclick="return confirm('确定要删除这个文件吗？')">删除</button>
                            </form>
                        </li>
                    {% endfor %}
                </ul>
            {% else %}
                <p>F盘中暂无文件或无法访问F盘</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
'''

# 主页面路由
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    message = None
    message_type = None
    
    if request.method == 'POST':
        # 检查是否有文件被上传
        if 'file' not in request.files:
            message = '没有文件被选中'
            message_type = 'error'
        else:
            files = request.files.getlist('file')
            for file in files:
                # 如果用户没有选择文件，浏览器也会提交一个空的部分
                if file.filename == '':
                    message = '没有选择文件'
                    message_type = 'error'
                    continue
                
                # 不检查文件类型，允许所有文件上传
                filename = secure_filename(file.filename)
                # 处理同名文件
                counter = 1
                name, ext = os.path.splitext(filename)
                while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
                    filename = f"{name}_{counter}{ext}"
                    counter += 1
                
                try:
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    message = f'文件上传成功: {filename}'
                    message_type = 'success'
                except Exception as e:
                    message = f'文件上传失败: {str(e)}。请检查F盘权限和状态。'
                    message_type = 'error'
    
    # 获取F盘根目录的文件列表
    try:
        # 列出F盘根目录的所有文件（不包括目录）
        uploaded_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) 
                         if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]
    except Exception as e:
        uploaded_files = []
        message = f'无法访问F盘: {str(e)}。请检查F盘是否存在且有权限访问。'
        message_type = 'error'
    
    return render_template_string(HTML_TEMPLATE, 
                                 files=uploaded_files,
                                 message=message,
                                 message_type=message_type)

# 下载文件路由
@app.route('/uploads/<filename>')
def download_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, 
                                     files=[],
                                     message=f'下载失败: {str(e)}',
                                     message_type='error')

# 删除文件路由
@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            os.remove(file_path)
            message = f'文件已删除: {filename}'
            message_type = 'success'
        else:
            message = f'文件不存在: {filename}'
            message_type = 'error'
    except Exception as e:
        message = f'删除失败: {str(e)}。可能是权限不足。'
        message_type = 'error'
    
    try:
        uploaded_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) 
                         if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]
    except:
        uploaded_files = []
    
    return render_template_string(HTML_TEMPLATE, 
                                 files=uploaded_files,
                                 message=message,
                                 message_type=message_type)

if __name__ == '__main__':
    # 允许外部访问
    app.run(host='0.0.0.0', port=5000, debug=True)
    
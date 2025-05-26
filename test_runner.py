from flask import Flask, request, jsonify, send_from_directory
import subprocess
import threading
import os
import time
import shutil
from datetime import datetime
import json

app = Flask(__name__)
test_running = False
last_test_result = None

def archive_previous_results():
    """归档上一次的测试结果"""
    if os.path.exists('reports/allure-results'):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_dir = f'reports/archive/results_{timestamp}'
        if os.path.exists('reports/allure-results'):
            shutil.copytree('reports/allure-results', archive_dir)
        return timestamp
    return None

def update_history():
    """更新历史记录"""
    if not os.path.exists('reports/history'):
        os.makedirs('reports/history')
    
    if os.path.exists('reports/allure-report/history'):
        for file in os.listdir('reports/allure-report/history'):
            src = os.path.join('reports/allure-report/history', file)
            dst = os.path.join('reports/history', file)
            if os.path.isfile(src):
                shutil.copy2(src, dst)

def run_test(test_path):
    global test_running, last_test_result
    test_running = True
    try:
        # 归档之前的结果
        archive_timestamp = archive_previous_results()
        
        # 更新历史记录
        update_history()
        
        # 清理当前测试结果目录
        if os.path.exists('reports/allure-results'):
            shutil.rmtree('reports/allure-results')
        os.makedirs('reports/allure-results')
        
        # 复制历史记录到新的测试结果目录
        if os.path.exists('reports/history'):
            shutil.copytree('reports/history', 'reports/allure-results/history', dirs_exist_ok=True)
        
        # 运行测试
        cmd = f"pytest {test_path} -v --alluredir=reports/allure-results"
        process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # 生成报告
        subprocess.run("allure generate reports/allure-results -o reports/allure-report --clean", 
                      shell=True)
        
        # 保存测试结果
        result = {
            "success": process.returncode == 0,
            "return_code": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "archive_timestamp": archive_timestamp
        }
        
        # 保存结果到JSON文件
        result_file = f'reports/archive/result_{archive_timestamp}.json'
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        last_test_result = result
        
    except Exception as e:
        last_test_result = {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    test_running = False

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ERP AUTOTEST</title>
        <!-- 内联关键CSS以提高性能 -->
        <style>
            :root {
                --primary-color: #555555;
                --primary-hover: #444444;
                --secondary-color: #777777;
                --success-color: #4a9d4a;
                --success-hover: #3d8b3d;
                --danger-color: #d44c47;
                --danger-hover: #c13c37;
                --light-color: #f8f9fa;
                --border-color: #e0e0e0;
                --text-color: #333333;
                --bg-color: #f5f5f5;
                --card-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
                --content-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
            }
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                background-color: var(--bg-color);
                color: var(--text-color);
                line-height: 1.5;
                padding: 20px 10px 40px;
                margin: 0;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }
            .app-container {
                max-width: 1000px;
                margin: 0 auto;
                background-color: white;
                border-radius: 6px;
                box-shadow: var(--card-shadow);
                overflow: hidden;
            }
            .app-header {
                background-color: var(--primary-color);
                color: white;
                padding: 18px 25px;
                text-align: center;
            }
            .app-title {
                margin: 0;
                font-weight: 600;
                letter-spacing: 0.5px;
                font-size: 22px;
            }
            .app-body {
                padding: 20px 25px;
            }
            .card {
                border: 1px solid var(--border-color);
                border-radius: 6px;
                margin-bottom: 18px;
                background-color: white;
                overflow: hidden;
                box-shadow: var(--content-shadow);
            }
            .card-header {
                background-color: #f8f9fa;
                border-bottom: 1px solid var(--border-color);
                padding: 12px 18px;
                font-weight: 600;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 15px;
            }
            .card-body {
                padding: 18px;
            }
            .btn {
                padding: 8px 16px;
                border-radius: 4px;
                border: 1px solid transparent;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                display: inline-flex;
                align-items: center;
                transition: all 0.15s ease;
                margin-right: 8px;
                position: relative;
                overflow: hidden;
                text-align: center;
            }
            .btn i {
                margin-right: 6px;
                font-size: 16px;
            }
            .btn::after {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 5px;
                height: 5px;
                background: rgba(255, 255, 255, 0.4);
                opacity: 0;
                border-radius: 100%;
                transform: scale(1, 1) translate(-50%);
                transform-origin: 50% 50%;
            }
            .btn:active::after {
                animation: ripple 0.5s ease-out;
            }
            @keyframes ripple {
                0% {
                    transform: scale(0, 0);
                    opacity: 0.5;
                }
                100% {
                    transform: scale(30, 30);
                    opacity: 0;
                }
            }
            .btn-primary {
                background-color: var(--primary-color);
                color: white;
            }
            .btn-primary:hover {
                background-color: var(--primary-hover);
                box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
            }
            .btn-success {
                background-color: var(--success-color);
                color: white;
            }
            .btn-success:hover {
                background-color: var(--success-hover);
                box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
            }
            .btn-outline {
                background-color: transparent;
                color: var(--primary-color);
                border: 1px solid var(--border-color);
            }
            .btn-outline:hover {
                background-color: #f0f0f0;
            }
            .btn-danger-outline {
                background-color: transparent;
                color: var(--danger-color);
                border: 1px solid var(--danger-color);
            }
            .btn-danger-outline:hover {
                background-color: rgba(212, 76, 71, 0.08);
            }
            .badge {
                display: inline-block;
                padding: 3px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 600;
                color: white;
            }
            .badge-primary {
                background-color: var(--primary-color);
            }
            .badge-success {
                background-color: var(--success-color);
            }
            .badge-danger {
                background-color: var(--danger-color);
            }
            .badge-secondary {
                background-color: var(--secondary-color);
            }
            .form-group {
                margin-bottom: 15px;
            }
            .form-label {
                display: block;
                margin-bottom: 6px;
                font-weight: 500;
                color: #444;
            }
            .form-select {
                width: 100%;
                padding: 8px 12px;
                border: 1px solid var(--border-color);
                border-radius: 4px;
                background-color: white;
                font-size: 14px;
                appearance: none;
                background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23555' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
                background-repeat: no-repeat;
                background-position: right 10px center;
                background-size: 16px;
            }
            .form-select:focus {
                outline: none;
                border-color: var(--primary-color);
                box-shadow: 0 0 0 2px rgba(85, 85, 85, 0.15);
            }
            .status-header {
                font-weight: 600;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 1px solid var(--border-color);
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            .refresh-indicator {
                display: inline-block;
                opacity: 0;
                transition: opacity 0.3s ease;
                font-size: 13px;
                color: #777;
                margin-left: 10px;
            }
            .refresh-indicator.show {
                opacity: 1;
            }
            .status-content {
                max-height: 400px;
                overflow-y: auto;
                min-height: 30px;
            }
            .history-item {
                border-left: 4px solid #e0e0e0;
                padding: 15px;
                margin-bottom: 12px;
                background-color: #fcfcfc;
                border-radius: 4px;
                transition: transform 0.15s ease, box-shadow 0.15s ease;
            }
            .history-item:hover {
                transform: translateY(-2px);
                box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
            }
            .history-item.success {
                border-left-color: var(--success-color);
            }
            .history-item.failure {
                border-left-color: var(--danger-color);
            }
            .output-container {
                border: 1px solid var(--border-color);
                border-radius: 4px;
                margin-bottom: 10px;
                overflow: hidden;
            }
            .output-header {
                padding: 10px 15px;
                background-color: #f8f9fa;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 14px;
                user-select: none;
                transition: background-color 0.15s ease;
            }
            .output-header:hover {
                background-color: #f1f1f1;
            }
            .output-content {
                padding: 0;
                max-height: 0;
                overflow: hidden;
                transition: max-height 0.25s ease;
                background-color: #fcfcfc;
            }
            .output-content pre {
                margin: 15px;
                white-space: pre-wrap;
                font-size: 13px;
                font-family: Menlo, Monaco, 'Courier New', monospace;
                color: #444;
                overflow-x: auto;
            }
            .hidden {
                display: none;
            }
            .flex {
                display: flex;
            }
            .flex-col {
                flex-direction: column;
            }
            .items-center {
                align-items: center;
            }
            .justify-between {
                justify-content: space-between;
            }
            .mt-3 {
                margin-top: 12px;
            }
            .mb-3 {
                margin-bottom: 12px;
            }
            .status-indicator {
                display: inline-block;
                width: 8px;
                height: 8px;
                border-radius: 50%;
                margin-right: 8px;
            }
            .status-indicator.success {
                background-color: var(--success-color);
                box-shadow: 0 0 0 2px rgba(74, 157, 74, 0.2);
            }
            .status-indicator.error {
                background-color: var(--danger-color);
                box-shadow: 0 0 0 2px rgba(212, 76, 71, 0.2);
            }
            .status-indicator.running {
                background-color: var(--primary-color);
                box-shadow: 0 0 0 2px rgba(85, 85, 85, 0.2);
                animation: pulse 1.5s infinite;
            }
            @keyframes pulse {
                0% {
                    opacity: 1;
                    transform: scale(1);
                }
                50% {
                    opacity: 0.5;
                    transform: scale(1.2);
                }
                100% {
                    opacity: 1;
                    transform: scale(1);
                }
            }
            .spinner {
                display: inline-block;
                width: 16px;
                height: 16px;
                border: 2px solid rgba(255,255,255,.3);
                border-radius: 50%;
                border-top-color: #fff;
                animation: spin 0.6s linear infinite;
                margin-right: 8px;
                vertical-align: middle;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            .toast {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 12px 16px;
                background-color: #333;
                color: white;
                border-radius: 4px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                z-index: 9999;
                font-size: 14px;
                max-width: 300px;
                opacity: 0;
                transform: translateY(-10px);
                transition: opacity 0.2s ease, transform 0.2s ease;
            }
            .toast.success {
                background-color: var(--success-color);
            }
            .toast.error {
                background-color: var(--danger-color);
            }
            .toast.info {
                background-color: var(--primary-color);
            }
            .toast.show {
                opacity: 1;
                transform: translateY(0);
            }
            .alert {
                padding: 12px;
                margin-bottom: 15px;
                border-radius: 4px;
                font-size: 14px;
            }
            .alert-info {
                background-color: #f0f7fb;
                color: #0c5496;
            }
            .alert-danger {
                background-color: #fdefef;
                color: #b13d31;
            }
            .fade-in {
                animation: fadeIn 0.3s ease forwards;
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            .empty-state {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 30px;
                color: #888;
                text-align: center;
            }
            .empty-icon {
                font-size: 30px;
                margin-bottom: 10px;
            }
            .btn-group {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }
            /* Shadow utilities */
            .hover-shadow:hover {
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            }
            /* Optimized loading animation */
            @keyframes shimmer {
                0% { background-position: -1000px 0; }
                100% { background-position: 1000px 0; }
            }
            .shimmer {
                background: linear-gradient(to right, #f0f0f0 4%, #e0e0e0 25%, #f0f0f0 36%);
                background-size: 1000px 100%;
                animation: shimmer 2s infinite linear;
            }
            @media (max-width: 768px) {
                .app-body {
                    padding: 15px;
                }
                .btn {
                    padding: 6px 12px;
                    font-size: 13px;
                }
                .btn-group {
                    justify-content: center;
                }
            }
        </style>
    </head>
    <body>
        <div class="app-container">
            <div class="app-header">
                <h1 class="app-title">ERP AUTOTEST</h1>
            </div>
            
            <div class="app-body">
                <!-- 控制面板 -->
                <div class="card hover-shadow">
                    <div class="card-header">
                        <span>测试控制</span>
                    </div>
                    <div class="card-body">
                        <div class="form-group">
                            <label for="test-path" class="form-label">选择测试目录</label>
                            <select id="test-path" class="form-select">
                                <option value="">加载中...</option>
                            </select>
                        </div>
                        <div class="btn-group mt-3">
                            <button id="runTestBtn" class="btn btn-primary">
                                <i>▶</i> 运行测试
                            </button>
                            <button id="checkStatusBtn" class="btn btn-outline">
                                <i>↻</i> 检查状态
                            </button>
                            <button id="openReportBtn" class="btn btn-success">
                                <i>📊</i> 查看报告
                            </button>
                            <button id="viewHistoryBtn" class="btn btn-outline">
                                <i>🕒</i> 历史记录
                            </button>
                        </div>
                    </div>
                </div>

                <!-- 状态面板 -->
                <div class="card hover-shadow">
                    <div class="card-header">
                        <span>执行状态</span>
                        <span id="status-badge" class="badge badge-secondary">未开始</span>
                    </div>
                    <div class="card-body">
                        <div id="status">
                            <div class="status-header">
                                <div>
                                    <span class="status-indicator"></span>
                                    <span id="status-title">等待测试执行...</span>
                                </div>
                                <div class="refresh-indicator" id="refresh-indicator">已更新</div>
                            </div>
                            <div class="status-content"></div>
                        </div>
                    </div>
                </div>

                <!-- 历史记录面板 -->
                <div class="card hidden hover-shadow" id="history-card">
                    <div class="card-header">
                        <span>历史测试记录</span>
                    </div>
                    <div class="card-body">
                        <div id="history"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 简化的Toast消息系统 -->
        <div id="toast-container"></div>
        
        <script>
            // 优化DOM访问 - 缓存DOM元素
            const elements = {
                testPath: document.getElementById('test-path'),
                statusBadge: document.getElementById('status-badge'),
                statusTitle: document.getElementById('status-title'),
                statusContent: document.querySelector('#status .status-content'),
                refreshIndicator: document.getElementById('refresh-indicator'),
                historyCard: document.getElementById('history-card'),
                history: document.getElementById('history'),
                statusIndicator: document.querySelector('.status-indicator'),
                runTestBtn: document.getElementById('runTestBtn'),
                checkStatusBtn: document.getElementById('checkStatusBtn'),
                openReportBtn: document.getElementById('openReportBtn'),
                viewHistoryBtn: document.getElementById('viewHistoryBtn'),
                toastContainer: document.getElementById('toast-container')
            };
            
            // 页面状态管理
            const state = {
                isRunning: false,
                lastResult: null,
                lastCheckTime: 0
            };

            // 页面加载完成后执行
            document.addEventListener('DOMContentLoaded', function() {
                fetchTestDirectories();
                // 自动检查初始状态
                setTimeout(updateStatus, 500);
            });

            // Toast消息封装
            const Toast = {
                show: function(message, type = 'info', duration = 3000) {
                    const toast = document.createElement('div');
                    toast.className = `toast ${type}`;
                    toast.textContent = message;
                    
                    elements.toastContainer.appendChild(toast);
                    
                    // 强制回流以触发动画
                    void toast.offsetWidth;
                    toast.classList.add('show');
                    
                    setTimeout(() => {
                        toast.classList.remove('show');
                        setTimeout(() => toast.remove(), 300); // 等待淡出动画完成
                    }, duration);
                }
            };

            // 获取测试目录
            function fetchTestDirectories() {
                fetch('/test-directories')
                .then(res => res.json())
                .then(data => {
                    elements.testPath.innerHTML = '';
                    
                    data.forEach(dir => {
                        const option = document.createElement('option');
                        option.value = dir.path;
                        option.textContent = dir.name;
                        elements.testPath.appendChild(option);
                    });
                })
                .catch(err => {
                    console.error('获取测试目录失败:', err);
                    Toast.show('获取测试目录失败', 'error');
                });
            }

            // 事件监听器
            elements.runTestBtn.addEventListener('click', function() {
                const testPath = elements.testPath.value;
                if (!testPath) {
                    Toast.show('请选择测试目录', 'error');
                    return;
                }
                
                // 更新状态
                elements.statusBadge.className = 'badge badge-primary';
                elements.statusBadge.innerHTML = '<span class="spinner"></span>执行中';
                elements.statusTitle.innerText = '测试正在执行中...';
                elements.statusContent.innerHTML = '';
                elements.statusIndicator.className = 'status-indicator running';
                
                fetch('/run-test', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({test_path: testPath})
                })
                .then(res => res.json())
                .then(data => {
                    Toast.show(data.message, 'info');
                    pollStatus();
                })
                .catch(err => {
                    elements.statusBadge.className = 'badge badge-danger';
                    elements.statusBadge.innerText = '错误';
                    elements.statusTitle.innerText = `错误: ${err.message}`;
                    elements.statusIndicator.className = 'status-indicator error';
                    Toast.show('执行测试失败', 'error');
                });
            });

            elements.checkStatusBtn.addEventListener('click', function() {
                // 添加获取状态的视觉反馈
                this.disabled = true;
                const originalText = this.innerHTML;
                this.innerHTML = '<span class="spinner" style="border-color: rgba(85,85,85,.3); border-top-color: #555;"></span> 检查中...';
                
                updateStatus()
                .then(() => {
                    // 显示刷新指示器
                    elements.refreshIndicator.classList.add('show');
                    setTimeout(() => {
                        elements.refreshIndicator.classList.remove('show');
                    }, 2000);
                })
                .finally(() => {
                    this.disabled = false;
                    this.innerHTML = originalText;
                });
            });

            elements.openReportBtn.addEventListener('click', function() {
                window.open('/allure-report/', '_blank');
            });

            elements.viewHistoryBtn.addEventListener('click', function() {
                if (elements.historyCard.classList.contains('hidden')) {
                    elements.historyCard.classList.remove('hidden');
                    elements.historyCard.classList.add('fade-in');
                    this.innerHTML = '<i>✕</i> 关闭历史';
                    this.classList.remove('btn-outline');
                    this.classList.add('btn-danger-outline');
                    fetchHistory();
                } else {
                    elements.historyCard.classList.add('hidden');
                    this.innerHTML = '<i>🕒</i> 历史记录';
                    this.classList.remove('btn-danger-outline');
                    this.classList.add('btn-outline');
                }
            });

            // 获取历史记录
            function fetchHistory() {
                elements.history.innerHTML = '<div style="text-align: center; padding: 20px;"><div class="spinner" style="border-color: rgba(0,0,0,.2); border-top-color: #555;"></div> 加载历史记录...</div>';
                
                fetch('/test-history')
                .then(res => res.json())
                .then(data => {
                    if (data.length === 0) {
                        elements.history.innerHTML = `
                            <div class="empty-state">
                                <div class="empty-icon">📝</div>
                                <p>暂无历史记录</p>
                            </div>
                        `;
                        return;
                    }
                    
                    elements.history.innerHTML = '';
                    data.forEach((item, index) => {
                        const itemDiv = document.createElement('div');
                        itemDiv.className = `history-item ${item.success ? 'success' : 'failure'} fade-in`;
                        itemDiv.style.animationDelay = `${index * 50}ms`;
                        
                        const date = new Date(item.timestamp);
                        const formattedDate = date.toLocaleString('zh-CN');
                        
                        itemDiv.innerHTML = `
                            <div class="flex justify-between items-center">
                                <span>
                                    <strong>${formattedDate}</strong>
                                    <span class="badge ${item.success ? 'badge-success' : 'badge-danger'}">
                                        ${item.success ? '成功' : '失败'}
                                    </span>
                                </span>
                                <button class="btn btn-primary view-report-btn" data-timestamp="${item.archive_timestamp}">
                                    查看报告
                                </button>
                            </div>
                        `;
                        elements.history.appendChild(itemDiv);
                        
                        // 添加查看报告按钮事件
                        const reportBtn = itemDiv.querySelector('.view-report-btn');
                        reportBtn.addEventListener('click', function() {
                            const timestamp = this.getAttribute('data-timestamp');
                            openHistoryReport(timestamp);
                        });
                    });
                })
                .catch(err => {
                    elements.history.innerHTML = '<div class="alert alert-danger">加载历史记录失败</div>';
                    console.error('获取历史记录失败:', err);
                    Toast.show('获取历史记录失败', 'error');
                });
            }

            // 打开历史报告
            function openHistoryReport(timestamp) {
                // 禁用按钮防止重复点击
                const buttons = document.querySelectorAll('.view-report-btn');
                buttons.forEach(btn => {
                    if (btn.getAttribute('data-timestamp') === timestamp) {
                        btn.disabled = true;
                        btn.innerHTML = '<span class="spinner"></span> 生成中...';
                    }
                });
                
                Toast.show('正在生成报告...', 'info');
                
                // 先重新生成报告，然后再打开
                fetch(`/generate-report/${timestamp}`)
                    .then(res => res.json())
                    .then(data => {
                        if (data.status === 'success') {
                            // 使用时间戳参数避免缓存问题
                            const cacheBuster = new Date().getTime();
                            window.open(`/archive-report/${timestamp}?_=${cacheBuster}`, '_blank');
                        } else {
                            Toast.show(data.message || '生成报告失败', 'error');
                        }
                    })
                    .catch(err => {
                        console.error('生成报告失败:', err);
                        Toast.show('生成历史报告失败', 'error');
                    })
                    .finally(() => {
                        // 恢复按钮状态
                        buttons.forEach(btn => {
                            if (btn.getAttribute('data-timestamp') === timestamp) {
                                btn.disabled = false;
                                btn.innerHTML = '查看报告';
                            }
                        });
                    });
            }

            // 轮询测试状态
            function pollStatus() {
                const interval = setInterval(() => {
                    fetch('/test-status')
                    .then(res => res.json())
                    .then(data => {
                        state.isRunning = data.running;
                        state.lastResult = data.last_result;
                        state.lastCheckTime = Date.now();
                        
                        updateStatusUI(data);
                        
                        if (!data.running) {
                            clearInterval(interval);
                            
                            const statusBadge = elements.statusBadge;
                            if (data.last_result && data.last_result.success) {
                                statusBadge.className = 'badge badge-success';
                                statusBadge.innerText = '成功';
                                elements.statusIndicator.className = 'status-indicator success';
                                Toast.show('测试执行成功', 'success');
                            } else if (data.last_result) {
                                statusBadge.className = 'badge badge-danger';
                                statusBadge.innerText = '失败';
                                elements.statusIndicator.className = 'status-indicator error';
                                Toast.show('测试执行失败', 'error');
                            }
                        }
                    })
                    .catch(err => console.error('轮询状态失败:', err));
                }, 2000);
            }
            
            // 更新状态 - 返回Promise以支持链式操作
            function updateStatus() {
                return fetch('/test-status')
                .then(res => res.json())
                .then(data => {
                    state.isRunning = data.running;
                    state.lastResult = data.last_result;
                    state.lastCheckTime = Date.now();
                    
                    updateStatusUI(data);
                    return data;
                })
                .catch(err => {
                    Toast.show('获取状态失败', 'error');
                    throw err;
                });
            }
            
            // 更新状态UI
            function updateStatusUI(data) {
                const statusBadge = elements.statusBadge;
                let statusHeader = '';
                let statusContent = '';
                
                if (data.running) {
                    statusBadge.className = 'badge badge-primary';
                    statusBadge.innerHTML = '<span class="spinner"></span>执行中';
                    elements.statusTitle.innerText = '测试正在执行中...';
                    elements.statusIndicator.className = 'status-indicator running';
                } else if (data.last_result) {
                    if (data.last_result.success) {
                        statusBadge.className = 'badge badge-success';
                        statusBadge.innerText = '成功';
                        elements.statusTitle.innerText = `测试执行成功 (${data.last_result.timestamp})`;
                        elements.statusIndicator.className = 'status-indicator success';
                    } else {
                        statusBadge.className = 'badge badge-danger';
                        statusBadge.innerText = '失败';
                        elements.statusTitle.innerText = `测试执行失败 (${data.last_result.timestamp})`;
                        elements.statusIndicator.className = 'status-indicator error';
                    }
                    
                    if (data.last_result.stdout) {
                        statusContent += createOutputSection('标准输出', data.last_result.stdout);
                    }
                    if (data.last_result.stderr) {
                        statusContent += createOutputSection('错误输出', data.last_result.stderr, true);
                    }
                } else {
                    statusBadge.className = 'badge badge-secondary';
                    statusBadge.innerText = '未开始';
                    elements.statusTitle.innerText = '等待测试执行...';
                    elements.statusIndicator.className = 'status-indicator';
                    elements.statusIndicator.style.backgroundColor = '#aaa';
                }
                
                elements.statusContent.innerHTML = statusContent;
                
                // 添加可折叠区域的事件处理
                setupOutputSections();
            }
            
            // 创建输出部分
            function createOutputSection(title, content, isError = false) {
                return `
                    <div class="output-container">
                        <div class="output-header">
                            <span>${isError ? '⚠️' : '📄'} ${title}</span>
                            <span>▼</span>
                        </div>
                        <div class="output-content">
                            <pre>${content}</pre>
                        </div>
                    </div>
                `;
            }
            
            // 设置可折叠区域的事件
            function setupOutputSections() {
                const headers = document.querySelectorAll('.output-header');
                headers.forEach(header => {
                    // 移除旧事件监听器
                    const newHeader = header.cloneNode(true);
                    header.parentNode.replaceChild(newHeader, header);
                    
                    newHeader.addEventListener('click', function() {
                        const content = this.nextElementSibling;
                        const arrow = this.querySelector('span:last-child');
                        
                        if (content.style.maxHeight) {
                            content.style.maxHeight = null;
                            arrow.textContent = '▼';
                        } else {
                            content.style.maxHeight = content.scrollHeight + 'px';
                            arrow.textContent = '▲';
                        }
                    });
                });
            }
            
            // 默认打开第一个输出区域
            function openFirstOutput() {
                const firstHeader = document.querySelector('.output-header');
                if (firstHeader) {
                    firstHeader.click();
                }
            }
        </script>
    </body>
    </html>
    """

@app.route('/run-test', methods=['POST'])
def start_test():
    global test_running
    if test_running:
        return jsonify({"status": "error", "message": "测试已在运行中"}), 400
    
    data = request.json
    test_path = data.get('test_path', 'testcases/gen/')
    
    thread = threading.Thread(target=run_test, args=(test_path,))
    thread.start()
    
    return jsonify({"status": "success", "message": f"开始运行测试: {test_path}"})

@app.route('/test-status', methods=['GET'])
def get_status():
    return jsonify({
        "running": test_running,
        "last_result": last_test_result
    })

@app.route('/test-history', methods=['GET'])
def get_history():
    history = []
    archive_dir = 'reports/archive'
    if os.path.exists(archive_dir):
        for file in os.listdir(archive_dir):
            if file.startswith('result_') and file.endswith('.json'):
                with open(os.path.join(archive_dir, file), 'r') as f:
                    history.append(json.load(f))
    return jsonify(sorted(history, key=lambda x: x['timestamp'], reverse=True))

@app.route('/allure-report/<path:path>')
def serve_report(path):
    return send_from_directory('reports/allure-report', path)

@app.route('/allure-report/')
def serve_report_index():
    return send_from_directory('reports/allure-report', 'index.html')

@app.route('/archive-report/<timestamp>')
def serve_archive_report(timestamp):
    """提供历史报告的入口页面"""
    # 修复路径模式，确保生成的报告使用绝对路径
    try:
        generate_temp_report(timestamp)
        print(f"准备提供历史报告: {timestamp}")
        return serve_archive_report_page(timestamp)
    except Exception as e:
        print(f"提供历史报告时出错: {str(e)}")
        return f"加载历史报告失败: {str(e)}", 500

def serve_archive_report_page(timestamp):
    """专门处理历史报告入口页面并修正资源路径"""
    temp_report_dir = f'reports/temp_report_{timestamp}'
    index_path = os.path.join(temp_report_dir, 'index.html')
    
    if not os.path.exists(index_path):
        print(f"历史报告不存在: {index_path}")
        return "历史报告不存在", 404
        
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 修正基础URL
        base_url = f'/archive-report/{timestamp}'
            
        # 修正资源路径 - 使用正则表达式进行更精确的替换
        import re
        
        # 替换CSS和JavaScript资源路径
        content = re.sub(r'href="(?!http|\/)(.*?)\.css"', f'href="{base_url}/\\1.css"', content)
        content = re.sub(r'src="(?!http|\/)(.*?)\.js"', f'src="{base_url}/\\1.js"', content)
        
        # 替换图片路径
        content = re.sub(r'src="(?!http|\/)(.*?)\.(png|jpg|svg|gif)"', f'src="{base_url}/\\1.\\2"', content)
        
        # 替换数据文件路径
        content = re.sub(r'src="(?!http|\/)(.*?)\.json"', f'src="{base_url}/\\1.json"', content)
        content = re.sub(r'data-src="(?!http|\/)(.*?)"', f'data-src="{base_url}/\\1"', content)
        
        # 替换插件路径
        content = re.sub(r'(src|href)="plugin\/(.*?)"', f'\\1="{base_url}/plugin/\\2"', content)
        
        # 添加基础URL元标记，帮助浏览器解析相对路径
        base_tag = f'<base href="{base_url}/">'
        content = content.replace('</head>', f'{base_tag}</head>')
        
        return content
    except Exception as e:
        print(f"处理报告页面失败: {str(e)}")
        return f"处理报告页面失败: {str(e)}", 500

@app.route('/archive-report/<timestamp>/<path:path>')
def serve_archive_report_files(timestamp, path):
    """提供历史报告的静态资源文件"""
    # 打印请求路径以便调试
    print(f"请求历史报告资源: timestamp={timestamp}, path={path}")
    
    temp_report_dir = f'reports/temp_report_{timestamp}'
    archive_dir = f'reports/archive/results_{timestamp}'
    
    # 尝试从临时报告目录提供文件
    if os.path.exists(os.path.join(temp_report_dir, path)):
        return send_from_directory(temp_report_dir, path)
    
    # 尝试从原始结果目录提供JSON数据文件
    if path.endswith('.json') and os.path.exists(os.path.join(archive_dir, os.path.basename(path))):
        return send_from_directory(archive_dir, os.path.basename(path))
    
    # 尝试从最新报告提供插件文件
    if path.startswith('plugin/') and os.path.exists(os.path.join('reports/allure-report', path)):
        return send_from_directory('reports/allure-report', path)
    
    # 尝试从最新报告提供其他静态资源
    if os.path.exists(os.path.join('reports/allure-report', path)):
        return send_from_directory('reports/allure-report', path)
    
    # 特殊处理，尝试猜测路径
    normalized_path = path.replace('data/', '')
    if os.path.exists(os.path.join(archive_dir, normalized_path)):
        return send_from_directory(archive_dir, normalized_path)
    
    print(f"找不到资源: {path}")
    return f"找不到资源: {path}", 404

def generate_temp_report(timestamp):
    """生成或更新临时报告"""
    archive_dir = f'reports/archive/results_{timestamp}'
    temp_report_dir = f'reports/temp_report_{timestamp}'
    
    if not os.path.exists(archive_dir):
        print(f"历史结果目录不存在: {archive_dir}")
        return False
        
    # 创建临时目录
    os.makedirs(temp_report_dir, exist_ok=True)
    
    try:
        # 生成报告
        print(f"为历史结果生成报告: {timestamp}")
        result = subprocess.run(
            f'allure generate {archive_dir} -o {temp_report_dir} --clean', 
            shell=True, capture_output=True, text=True
        )
        
        if result.returncode != 0:
            print(f"生成报告失败: {result.stderr}")
            return False
            
        print(f"报告生成成功，输出目录: {temp_report_dir}")
        
        # 添加allure的历史趋势数据
        if os.path.exists('reports/history'):
            history_dir = os.path.join(temp_report_dir, 'history')
            os.makedirs(history_dir, exist_ok=True)
            # 复制历史数据
            for item in os.listdir('reports/history'):
                src = os.path.join('reports/history', item)
                dst = os.path.join(history_dir, item)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                    print(f"复制历史文件: {src} -> {dst}")
        
        # 确保原始测试结果文件可访问
        # 创建data目录和软链接指向原始结果文件
        data_dir = os.path.join(temp_report_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # 复制原始JSON文件到data目录
        for item in os.listdir(archive_dir):
            if item.endswith('.json'):
                src = os.path.join(archive_dir, item)
                dst = os.path.join(data_dir, item)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                    print(f"复制数据文件: {src} -> {dst}")
        
        # 确保静态资源完整
        if os.path.exists('reports/allure-report'):
            # 复制常用静态资源
            for resource in ['app.js', 'styles.css', 'favicon.ico']:
                src = os.path.join('reports/allure-report', resource)
                dst = os.path.join(temp_report_dir, resource)
                if os.path.exists(src) and not os.path.exists(dst):
                    shutil.copy2(src, dst)
                    print(f"复制静态资源: {resource}")
            
            # 复制插件目录
            src_plugin = os.path.join('reports/allure-report', 'plugin')
            dst_plugin = os.path.join(temp_report_dir, 'plugin')
            if os.path.exists(src_plugin) and not os.path.exists(dst_plugin):
                shutil.copytree(src_plugin, dst_plugin)
                print("复制插件目录")
                
            # 复制关键目录
            for dir_name in ['widgets', 'export', 'executor']:
                src_dir = os.path.join('reports/allure-report', dir_name)
                dst_dir = os.path.join(temp_report_dir, dir_name)
                if os.path.exists(src_dir) and not os.path.exists(dst_dir):
                    shutil.copytree(src_dir, dst_dir)
                    print(f"复制目录: {dir_name}")
        
        return True
    except Exception as e:
        print(f"生成临时报告失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

@app.route('/generate-report/<timestamp>')
def generate_report(timestamp):
    """提前生成历史报告"""
    archive_dir = f'reports/archive/results_{timestamp}'
    if os.path.exists(archive_dir):
        # 清理旧的临时报告
        temp_report_dir = f'reports/temp_report_{timestamp}'
        if os.path.exists(temp_report_dir):
            shutil.rmtree(temp_report_dir)
            print(f"清理旧的临时报告: {temp_report_dir}")
        
        # 生成新报告
        success = generate_temp_report(timestamp)
        if success:
            return jsonify({"status": "success", "message": "报告已生成"})
        else:
            return jsonify({
                "status": "error", 
                "message": "生成报告失败，请查看服务器日志"
            }), 500
    return jsonify({"status": "error", "message": "找不到历史结果数据"}), 404

@app.route('/test-directories', methods=['GET'])
def test_directories():
    """返回测试目录列表"""
    return jsonify(get_test_directories())

def get_test_directories():
    """获取测试目录列表"""
    base_dir = 'testcases'
    dirs = []
    
    # 添加所有测试用例选项
    dirs.append({"name": "所有测试用例", "path": base_dir})
    
    # 添加每个子目录
    if os.path.exists(base_dir) and os.path.isdir(base_dir):
        for item in os.listdir(base_dir):
            full_path = os.path.join(base_dir, item)
            if os.path.isdir(full_path) and not item.startswith('__') and not item.startswith('.'):
                dirs.append({
                    "name": f"测试用例 - {item}目录", 
                    "path": f"{base_dir}/{item}"
                })
    return dirs

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True) 
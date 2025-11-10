from flask import Flask, render_template, request, jsonify
import json
import os

# 创建Flask应用实例
app = Flask(__name__)

# 全局变量存储数据
antibiotic_data = None

# 加载JSON数据
def load_data():
    global antibiotic_data
    json_path = 'antibiotic_data.json'
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            antibiotic_data = json.load(f)
        print("数据加载成功")
    else:
        print("警告：JSON数据文件不存在")

# 主页路由
@app.route('/')
def index():
    return render_template('index.html')

# 获取所有细菌名称的API
@app.route('/api/bacteria', methods=['GET'])
def get_bacteria():
    if antibiotic_data:
        return jsonify({
            'success': True,
            'bacteria': antibiotic_data.get('bacteria_list', [])
        })
    else:
        return jsonify({'success': False, 'error': '数据未加载'})

# 获取所有药物名称的API
@app.route('/api/drugs', methods=['GET'])
def get_drugs():
    if antibiotic_data:
        # 返回所有药物名称，保持Excel中的原始顺序（从左到右）
        return jsonify({
            'success': True,
            'drugs': antibiotic_data.get('drug_list', [])
        })
    else:
        return jsonify({'success': False, 'error': '数据未加载'})

# 按细菌搜索API
@app.route('/api/search/bacteria', methods=['GET'])
def search_by_bacteria():
    bacteria_name = request.args.get('name', '').strip()
    
    if not bacteria_name:
        return jsonify({'success': False, 'error': '请提供细菌名称'})
    
    if not antibiotic_data:
        return jsonify({'success': False, 'error': '数据未加载'})
    
    # 转换搜索词为小写用于模糊匹配
    search_term_lower = bacteria_name.lower()
    
    # 在数据中查找对应的细菌，支持模糊匹配
    for record in antibiotic_data.get('data', []):
        record_bacteria = record.get('bacteria', '')
        # 去除换行符并转换为小写进行比较
        normalized_bacteria = record_bacteria.replace('\n', ' ').lower()
        search_term_normalized = search_term_lower.replace('\n', ' ')
        
        # 如果记录中的细菌名称包含搜索词，或者搜索词包含记录中的细菌名称（去除拉丁名部分）
        if search_term_normalized in normalized_bacteria or normalized_bacteria.split(' ')[0] in search_term_normalized:
            return jsonify({
                'success': True,
                'bacteria': record_bacteria,
                'antibiotics': record.get('antibiotics', {})
            })
    
    return jsonify({'success': False, 'error': '未找到该细菌的记录'})

# 按药物搜索API
@app.route('/api/search/drug', methods=['GET'])
def search_by_drug():
    drug_name = request.args.get('name', '').strip()
    
    if not drug_name:
        return jsonify({'success': False, 'error': '请提供药物名称'})
    
    if not antibiotic_data:
        return jsonify({'success': False, 'error': '数据未加载'})
    
    # 使用药物索引查找数据，确保按原始Excel从上到下的顺序返回结果
    if 'drug_indexed' in antibiotic_data and drug_name in antibiotic_data['drug_indexed']:
        # drug_indexed中的结果已经按照原始Excel中的细菌顺序存储
        results = antibiotic_data['drug_indexed'][drug_name]
        return jsonify({
            'success': True,
            'drug': drug_name,
            'bacteria_results': results
        })
    
    # 如果药物索引不存在，使用替代方法查找
    alternative_results = []
    for record in antibiotic_data.get('data', []):
        if drug_name in record.get('antibiotics', {}):
            alternative_results.append({
                'bacteria': record.get('bacteria'),
                'sensitivity': record['antibiotics'][drug_name]
            })
    
    if alternative_results:
        return jsonify({
            'success': True,
            'drug': drug_name,
            'bacteria_results': alternative_results
        })
    
    return jsonify({'success': False, 'error': '未找到该药物的记录'})

# 获取统计信息API
@app.route('/api/stats', methods=['GET'])
def get_stats():
    if antibiotic_data:
        return jsonify({
            'success': True,
            'bacteria_count': len(antibiotic_data.get('bacteria_list', [])),
            'drug_count': len(antibiotic_data.get('drug_list', [])),
            'record_count': len(antibiotic_data.get('data', []))
        })
    else:
        return jsonify({'success': False, 'error': '数据未加载'})

# 比较多个细菌的API
@app.route('/api/compare/bacteria', methods=['GET'])
def compare_bacteria():
    # 获取查询参数中的细菌名称列表
    bacteria_names = request.args.getlist('name')
    
    if not bacteria_names or len(bacteria_names) < 2:
        return jsonify({'success': False, 'error': '请至少提供两个细菌名称'})
    
    if not antibiotic_data:
        return jsonify({'success': False, 'error': '数据未加载'})
    
    results = {
        'success': True,
        'bacteria': [],  # 将在下面填充找到的实际细菌名称
        'comparison_data': []
    }
    
    # 收集所有涉及的药物
    all_drugs = set()
    bacteria_data = {}
    found_bacteria_names = []  # 存储找到的实际细菌名称
    
    # 为每个细菌获取数据
    for bacteria_name in bacteria_names:
        search_term_lower = bacteria_name.lower()
        found = False
        
        for record in antibiotic_data.get('data', []):
            record_bacteria = record.get('bacteria', '')
            normalized_bacteria = record_bacteria.replace('\n', ' ').lower()
            
            if search_term_lower in normalized_bacteria or normalized_bacteria.split(' ')[0] in search_term_lower:
                bacteria_data[record_bacteria] = record.get('antibiotics', {})
                found_bacteria_names.append(record_bacteria)  # 添加找到的实际细菌名称
                # 添加所有药物到集合
                for drug in record.get('antibiotics', {}).keys():
                    all_drugs.add(drug)
                found = True
                break
        
        if not found:
            # 如果找不到某个细菌，返回错误信息
            return jsonify({'success': False, 'error': f'未找到细菌 "{bacteria_name}" 的记录'})
    
    # 更新results中的细菌名称列表为找到的实际名称
    results['bacteria'] = found_bacteria_names
    
    # 构建比较数据
    # 按照原始药物列表顺序
    for drug in antibiotic_data.get('drug_list', []):
        if drug in all_drugs:
            drug_data = {'drug': drug, 'bacteria_results': {}}
            for bacteria in found_bacteria_names:  # 使用找到的实际细菌名称
                if bacteria in bacteria_data and drug in bacteria_data[bacteria]:
                    drug_data['bacteria_results'][bacteria] = bacteria_data[bacteria][drug]
                else:
                    drug_data['bacteria_results'][bacteria] = '未知'
            results['comparison_data'].append(drug_data)
    
    return jsonify(results)

# 比较多个药物的API
@app.route('/api/compare/drug', methods=['GET'])
def compare_drugs():
    # 获取查询参数中的药物名称列表
    drug_names = request.args.getlist('name')
    
    if not drug_names or len(drug_names) < 2:
        return jsonify({'success': False, 'error': '请至少提供两个药物名称'})
    
    if not antibiotic_data:
        return jsonify({'success': False, 'error': '数据未加载'})
    
    results = {
        'success': True,
        'drugs': drug_names,
        'comparison_data': []
    }
    
    # 收集所有涉及的细菌
    all_bacteria = set()
    
    # 为每个药物获取数据
    for drug_name in drug_names:
        if 'drug_indexed' in antibiotic_data and drug_name in antibiotic_data['drug_indexed']:
            for record in antibiotic_data['drug_indexed'][drug_name]:
                all_bacteria.add(record['bacteria'])
    
    # 构建比较数据
    for bacteria in antibiotic_data.get('bacteria_list', []):
        if bacteria in all_bacteria:
            bacteria_data = {'bacteria': bacteria, 'drug_results': {}}
            
            # 为每个药物查找对该细菌的敏感性
            for drug in drug_names:
                bacteria_data['drug_results'][drug] = '未知'
                
                # 在drug_indexed中查找
                if 'drug_indexed' in antibiotic_data and drug in antibiotic_data['drug_indexed']:
                    for record in antibiotic_data['drug_indexed'][drug]:
                        if record['bacteria'] == bacteria:
                            bacteria_data['drug_results'][drug] = record['sensitivity']
                            break
                
                # 如果在drug_indexed中找不到，在原始数据中查找
                if bacteria_data['drug_results'][drug] == '未知':
                    for record in antibiotic_data.get('data', []):
                        if record.get('bacteria') == bacteria and drug in record.get('antibiotics', {}):
                            bacteria_data['drug_results'][drug] = record['antibiotics'][drug]
                            break
            
            results['comparison_data'].append(bacteria_data)
    
    return jsonify(results)

# 应用启动时加载数据
if __name__ == '__main__':
    load_data()
    # 在开发环境中运行，debug=True便于调试
    app.run(debug=True, host='0.0.0.0', port=5000)
import pandas as pd
import json
import os

# 文件路径
file_path = 'e:\\中心医院\\中大附一进修\\32\\53版热病.xlsx'
output_path = 'e:\\中心医院\\中大附一进修\\32\\antibiotic_data.json'

def convert_excel_to_json():
    """
    将Excel抗菌谱数据转换为结构化JSON格式
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        
        # 提取细菌名称列表（第一列）
        bacteria_list = df.iloc[:, 0].tolist()
        
        # 提取药物名称列表（第一行，从第二列开始）
        drug_list = df.columns[1:].tolist()
        
        # 创建结构化数据
        structured_data = {
            "bacteria_list": bacteria_list,
            "drug_list": drug_list,
            "data": []
        }
        
        # 构建数据记录
        for idx, row in df.iterrows():
            bacteria_name = row.iloc[0]
            record = {
                "bacteria": bacteria_name,
                "antibiotics": {}
            }
            
            # 添加每种药物的敏感性数据
            for drug_idx, drug_name in enumerate(drug_list):
                # 跳过第一列（细菌名称），所以索引要+1
                sensitivity = row.iloc[drug_idx + 1]
                # 确保数据类型为字符串并去除空白
                if pd.notna(sensitivity):
                    record["antibiotics"][drug_name] = str(sensitivity).strip()
                else:
                    record["antibiotics"][drug_name] = "未知"
            
            structured_data["data"].append(record)
        
        # 构建按药物索引的数据结构，便于按药物搜索
        drug_indexed_data = {}
        for drug_name in drug_list:
            drug_indexed_data[drug_name] = []
            
        # 填充按药物索引的数据
        for record in structured_data["data"]:
            bacteria_name = record["bacteria"]
            for drug_name, sensitivity in record["antibiotics"].items():
                drug_indexed_data[drug_name].append({
                    "bacteria": bacteria_name,
                    "sensitivity": sensitivity
                })
        
        # 将按药物索引的数据添加到主数据结构中
        structured_data["drug_indexed"] = drug_indexed_data
        
        # 保存为JSON文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(structured_data, f, ensure_ascii=False, indent=2)
        
        print(f"数据成功转换为JSON格式并保存至: {output_path}")
        print(f"包含细菌种类数: {len(bacteria_list)}")
        print(f"包含药物种类数: {len(drug_list)}")
        print(f"总数据记录数: {len(structured_data['data'])}")
        
        return structured_data
        
    except Exception as e:
        print(f"转换过程中出错: {e}")
        return None

if __name__ == "__main__":
    convert_excel_to_json()
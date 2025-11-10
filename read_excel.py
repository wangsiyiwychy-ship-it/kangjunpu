import pandas as pd

# 文件路径
file_path = 'e:\\中心医院\\中大附一进修\\32\\53版热病.xlsx'

# 读取Excel文件
try:
    # 读取Excel文件的所有sheet
    excel_file = pd.ExcelFile(file_path)
    print(f"Excel文件包含的工作表: {excel_file.sheet_names}")
    
    # 读取第一个工作表
    df = pd.read_excel(file_path)
    
    # 显示数据的行数和列数
    print(f"\n总行数: {len(df)}")
    print(f"总列数: {len(df.columns)}")
    print(f"数据形状: {df.shape}")
    
    # 显示非空行数（去除完全空的行）
    non_empty_rows = len(df.dropna(how='all'))
    print(f"非空行数: {non_empty_rows}")
    
    # 显示列名
    print("\n列名:", df.columns.tolist())
    
    print("\n数据前5行:")
    print(df.head())
    
except Exception as e:
    print(f"读取文件时出错: {e}")
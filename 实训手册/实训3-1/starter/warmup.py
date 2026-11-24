# 语法热身：字典与列表
#
# 运行：python warmup.py
# 先读一遍，再按文件末尾的 TODO 改一改，最后看输出。

# 1. 创建一个嵌套字典：键是单位编码，值是一条记录
departments = {
    "D001": {"dept_code": "D001", "full_name": "一中队", "address": "人民路1号"},
}

# 2. 按键取值
print("D001 的记录：", departments["D001"])

# 3. 用 get 取一个不存在的键：不会报错，返回 None
print("D99 的记录：", departments.get("D99"))

# 4. 判断键是否存在
print("D001 在字典里吗？", "D001" in departments)
print("D99 在字典里吗？", "D99" in departments)

# 5. 取出所有记录，变成列表
print("所有记录：", list(departments.values()))

# 6. 记录条数
print("记录条数：", len(departments))

# 7. 新增一条
departments["D002"] = {"dept_code": "D002", "full_name": "二中队", "address": "建设街2号"}
print("新增后条数：", len(departments))

# 8. 遍历
for code, item in departments.items():
    print(code, "->", item["full_name"])

# 9. 删除
del departments["D002"]
print("删除后条数：", len(departments))

# TODO 1：把 D001 的 full_name 改成 "第一中队"，再打印一次。
# TODO 2：新增 D03，再删除 D001，看看剩余记录。
# TODO 3：把第 4 步的两个判断改成 if 语句，分别打印"存在"和"不存在"。

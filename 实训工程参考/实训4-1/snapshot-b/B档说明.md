# B 档快照说明

本目录是课堂达标（B 档）产物，供上一实训未完成或需要快速接续时使用；不是教师完整版 `项目/`。

## 4-1 B 档范围

- 六文件骨架 + 根 `main.py`
- GET `/departments` 列表，返回 `{items, total}`
- POST `/departments` 新增，成功 201、重复编码 400、缺字段 422
- 不含详情/修改/删除路由，不含 204/404 验收

## 启动

```bash
python -m pip install -r requirements.txt
uvicorn main:app --port 8000
```

## 冒烟验证

GET `/departments` 200；POST 完整记录 201；重复 POST 400；缺 `full_name` 422。

## 承接

作为 5-1 起点的 B 档六文件版本；5-1 只补工程化配置与 Git，不补做课堂未写的三个接口。

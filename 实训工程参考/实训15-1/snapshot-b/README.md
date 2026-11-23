# 实训 15-1 起点项目

本目录是第 14 章完成后的单页骨架，作为 15-1 的起点。只有一个 `app.py`，包含页面配置、标题与待完成提示；假数据、指标、表格、筛选、空态与新增表单都要在本实训中补上。

详见 [起点说明.md](起点说明.md)。

## 运行

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

默认地址 <http://127.0.0.1:8501>。

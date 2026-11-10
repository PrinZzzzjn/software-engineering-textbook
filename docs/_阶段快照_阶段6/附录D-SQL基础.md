# 附录 D SQL 基础（最小可用集）

本书用 SQLite 做本地数据库，SQL 语句在 MySQL / PostgreSQL 上大体通用。先看懂这四类语句，就能读懂第 7–15 章的 ORM 在做什么。

## D.1 表、行与字段

一张表像一个二维清单：每**行**是一条记录，每**列**是一个字段。主键（`PRIMARY KEY`）唯一标识一行；外键（`REFERENCES`）指向另一张表的主键，用来表达「这条记录属于谁」。

```sql
CREATE TABLE departments (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL
);
```

## D.2 增删改查（CRUD）

```sql
-- 增
INSERT INTO departments (code, name) VALUES ('D01', '一中队');
-- 查
SELECT id, code, name FROM departments WHERE code = 'D01';
-- 改
UPDATE departments SET name = '一中队（新）' WHERE id = 1;
-- 删
DELETE FROM departments WHERE id = 1;
```

**没有 WHERE 的 UPDATE / DELETE 会作用于整张表**，写之前先单独跑一遍同条件的 SELECT，确认命中范围。

## D.3 条件、排序与分页

```sql
SELECT * FROM departments
WHERE name LIKE '%中队%' AND id > 0
ORDER BY id DESC
LIMIT 10 OFFSET 20;
```

- `LIKE '%中队%'` 做模糊匹配；`AND` / `OR` 组合条件，混用时加括号。
- `ORDER BY ... DESC` 倒序；分页用 `LIMIT 每页条数 OFFSET 偏移量`，偏移量 = (页码 - 1) × 每页条数。
- 排序字段如果允许重复，追加主键做次级排序，避免翻页时顺序跳动。

## D.4 关联查询

```sql
SELECT u.name, d.name AS dept_name
FROM users u
JOIN departments d ON u.dept_id = d.id
WHERE d.code = 'D01';
```

`JOIN ... ON ...` 把两张表按外键拼起来；`AS` 给结果列起别名。`LEFT JOIN` 会保留左表全部行，右表没有匹配时补 `NULL`——统计「每个部门有多少人」时要用它，否则零人的部门会消失。

## D.5 统计与去重

```sql
SELECT dept_id, COUNT(*) AS total FROM users GROUP BY dept_id;
SELECT COUNT(DISTINCT dept_id) FROM users;
```

`GROUP BY` 先分组再聚合；`COUNT(*)` 数行数，`COUNT(DISTINCT 列)` 数不重复的值。统计口径要先说清「按什么去重」，否则同名不同义。

## D.6 事务

```sql
BEGIN;
INSERT INTO departments (code, name) VALUES ('D02', '二中队');
-- 后面的步骤失败时：
ROLLBACK;
-- 全部成功时：
COMMIT;
```

事务把多步操作捆成一个整体：要么全生效，要么全撤销。第 12 章的「事务边界」、第 15 章的异常改造都围绕这一点。

## D.7 从 SQL 到 ORM

ORM（对象关系映射）让你用 Python 对象代替手写 SQL：`session.query(Department).filter_by(code="D01").first()` 大致等价于 `SELECT * FROM departments WHERE code='D01' LIMIT 1`。**SQL 是底下的事实，ORM 只是写法**。查询结果不符预期时，先写出等价 SQL 想清楚，再看 ORM 代码，比逐行猜快得多。

## D.8 排错顺序

1. 表是否存在、字段名是否拼对（SQLite 对列名大小写敏感程度与建表语句一致）；
2. 单独执行同条件 `SELECT COUNT(*)`，确认命中行数；
3. 检查 `NULL`：`WHERE col = NULL` 永远不成立，要用 `IS NULL`；
4. 检查事务是否已提交、连接是否指向了同一个数据库文件。

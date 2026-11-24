# 值班数据统计服务 API 说明文档

> **文档修订**：2026-10-26 按后端实际代码校正了接口路径、查询参数与响应字段，
> 并移除了代码中不存在的分析接口。后续如接口有变更，请以 `/docs`（Swagger）为准。

> **基础地址**：`http://127.0.0.1:8000`。除登录接口与健康检查外，所有业务接口都需要请求头
> `Authorization: Bearer <access_token>`。
>
> **通用接口**：
> - `GET /health`：健康检查，返回 `{"status": "healthy"}`。
> - `GET /`：根路径，返回服务名称、版本与文档地址。

## 1. 用户认证功能模块

### 1.1 登录接口

**路径**: `/api/v1/auth/login`
**方法**: `POST`
**功能**: 用户登录获取访问令牌和刷新令牌

**请求体**:
```json
{
  "username": "string",
  "password": "string"
}
```

**响应体 (200 OK)**:
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "string",
    "role": "string"
  }
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "用户名或密码错误"
}

### 1.2 刷新令牌接口

**路径**: `/api/v1/auth/refresh`
**方法**: `POST`
**功能**: 使用刷新令牌获取新的访问令牌

**请求体**:
```json
{
  "refresh_token": "string"
}
```

**响应体 (200 OK)**:
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "无效的刷新令牌"
}

### 1.3 登出接口

**路径**: `/api/v1/auth/logout`
**方法**: `POST`
**功能**: 用户登出，将令牌加入黑名单

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应体 (200 OK)**:
```json
{
  "message": "登出成功"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}

### 1.4 获取当前用户信息

**路径**: `/api/v1/auth/me`
**方法**: `GET`
**功能**: 获取当前登录用户的详细信息

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应体 (200 OK)**:
```json
{
  "id": 1,
  "username": "string",
  "role": "string",
  "create_time": "2024-01-01T00:00:00Z",
  "update_time": "2024-01-01T00:00:00Z"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}

### 1.5 修改密码

**路径**: `/api/v1/auth/change-password`

### 1.6 OAuth2兼容登录接口

**路径**: `/api/v1/auth/login/form`
**方法**: `POST`
**功能**: 提供OAuth2兼容的登录接口，支持表单方式提交

**请求体**: 
```
username: 用户名（字符串）
password: 密码（字符串）
```

**响应体 (200 OK)**: 
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

**错误响应**: 
- **401 Unauthorized**: {
  "detail": "用户名或密码错误"
}
**方法**: `POST`
**功能**: 修改当前用户密码

**请求头**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "old_password": "string",
  "new_password": "string",
  "confirm_password": "string"
}
```

**响应体 (200 OK)**:
```json
{
  "message": "密码修改成功"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **400 Bad Request**: {
  "detail": "原密码错误"
}
- **400 Bad Request**: {
  "detail": "新密码与确认密码不一致"
}

## 2. 系统用户管理模块

### 2.1 获取用户列表

**路径**: `/api/v1/users/`
**方法**: `GET`
**功能**: 获取系统用户列表（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `page`: 页码，默认1
- `page_size`: 每页数量，默认10
- `username`: 用户名搜索（可选）
- `role`: 角色筛选（可选）

**响应体 (200 OK)**:
```json
{
  "items": [
    {
      "id": 1,
      "username": "string",
      "role": "string",
      "is_active": 1,
      "personnel_id": null,
      "create_time": "2024-01-01T00:00:00Z",
      "update_time": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 10,
  "pages": 10
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}

### 2.2 创建用户

**路径**: `/api/v1/users/`
**方法**: `POST`
**功能**: 创建新用户（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "username": "string",
  "password": "string",
  "role": "string",
  "is_active": 1,
  "personnel_id": null
}
```

**响应体 (201 Created)**:
```json
{
  "id": 1,
  "username": "string",
  "role": "string",
  "is_active": 1,
  "personnel_id": null,
  "create_time": "2024-01-01T00:00:00Z",
  "update_time": "2024-01-01T00:00:00Z"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}
- **400 Bad Request**: {
  "detail": "用户名已存在"
}

### 2.3 获取单个用户信息

**路径**: `/api/v1/users/{user_id}`
**方法**: `GET`
**功能**: 获取指定用户的详细信息（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `user_id`: 用户ID

**响应体 (200 OK)**:
```json
{
  "id": 1,
  "username": "string",
  "role": "string",
  "is_active": 1,
  "personnel_id": null,
  "create_time": "2024-01-01T00:00:00Z",
  "update_time": "2024-01-01T00:00:00Z"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}
- **404 Not Found**: {
  "detail": "用户不存在"
}

### 2.4 更新用户信息

**路径**: `/api/v1/users/{user_id}`
**方法**: `PUT`
**功能**: 更新指定用户的信息（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `user_id`: 用户ID

**请求体**:
```json
{
  "role": "string",
  "is_active": 1,
  "personnel_id": null
}
```

**响应体 (200 OK)**:
```json
{
  "id": 1,
  "username": "string",
  "role": "string",
  "is_active": 1,
  "personnel_id": null,
  "create_time": "2024-01-01T00:00:00Z",
  "update_time": "2024-01-01T00:00:00Z"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}
- **404 Not Found**: {
  "detail": "用户不存在"
}

### 2.5 删除用户

**路径**: `/api/v1/users/{user_id}`
**方法**: `DELETE`
**功能**: 删除指定用户（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `user_id`: 用户ID

**响应体 (200 OK)**:
```json
{
  "message": "用户删除成功"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}
- **404 Not Found**: {
  "detail": "用户不存在"
}
- **400 Bad Request**: {
  "detail": "不能删除当前登录用户"
}

### 2.6 重置用户密码

**路径**: `/api/v1/users/{user_id}/reset-password`
**方法**: `POST`
**功能**: 重置指定用户的密码（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `user_id`: 用户ID

**请求体**:
```json
{
  "new_password": "string"
}
```

**响应体 (200 OK)**:
```json
{
  "message": "密码重置成功"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}
- **404 Not Found**: {
  "detail": "用户不存在"
}

## 3. 部门管理功能模块

### 3.1 获取部门列表

**路径**: `/api/v1/departments/`
**方法**: `GET`
**功能**: 获取部门列表，支持分页、搜索和排序

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `page`: 页码，默认1
- `page_size`: 每页数量，默认10
- `full_name`: 部门名称搜索（可选）
- `parent_dept_code`: 父部门编码筛选（可选）
- `sort_by`: 排序字段，默认"create_time"
- `sort_order`: 排序方式，默认"desc"（升序为"asc"）

**响应体 (200 OK)**:
```json
{
  "items": [
    {
      "dept_code": "1001",
      "full_name": "部门名称",
      "address": "部门地址",
      "longitude": 116.397,
      "latitude": 39.908,
      "parent_dept_code": null,
      "create_time": "2024-01-01T00:00:00Z",
      "update_time": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 10,
  "pages": 5
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}

### 3.2 获取部门树形结构

**路径**: `/api/v1/departments/tree`
**方法**: `GET`
**功能**: 获取部门的树形结构数据

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `root_dept_code`: 根部门编码（可选，不提供则从顶级部门开始）

**响应体 (200 OK)**:
```json
[
  {
    "dept_code": "1001",
    "full_name": "一级部门",
    "parent_dept_code": null,
    "children": [
      {
        "dept_code": "1002",
        "full_name": "二级部门1",
        "parent_dept_code": "1001",
        "children": []
      },
      {
        "dept_code": "1003",
        "full_name": "二级部门2",
        "parent_dept_code": "1001",
        "children": []
      }
    ]
  }
]
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}

### 3.3 创建部门

**路径**: `/api/v1/departments/`
**方法**: `POST`
**功能**: 创建新部门（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "dept_code": "1001",
  "full_name": "部门名称",
  "address": "部门地址",
  "longitude": 116.397,
  "latitude": 39.908,
  "parent_dept_code": null
}
```

**响应体 (201 Created)**:
```json
{
  "dept_code": "1001",
  "full_name": "部门名称",
  "address": "部门地址",
  "longitude": 116.397,
  "latitude": 39.908,
  "parent_dept_code": null,
  "create_time": "2024-01-01T00:00:00Z",
  "update_time": "2024-01-01T00:00:00Z"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}
- **400 Bad Request**: {
  "detail": "部门名称已存在"
}
- **400 Bad Request**: {
  "detail": "父部门不存在"
}

### 3.4 获取单个部门信息

**路径**: `/api/v1/departments/{dept_code}`
**方法**: `GET`
**功能**: 获取指定部门的详细信息

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `dept_code`: 部门编码（字符串类型）

**响应体 (200 OK)**:
```json
{
  "dept_code": "1001",
  "full_name": "部门名称",
  "address": "部门地址",
  "longitude": 116.397,
  "latitude": 39.908,
  "parent_dept_code": null,
  "parent_dept_name": null,
  "child_count": 2,
  "create_time": "2024-01-01T00:00:00Z",
  "update_time": "2024-01-01T00:00:00Z"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **404 Not Found**: {
  "detail": "部门不存在"
}

### 3.5 更新部门信息

**路径**: `/api/v1/departments/{dept_code}`
**方法**: `PUT`
**功能**: 更新指定部门的信息（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `dept_code`: 部门编码

**请求体**:
```json
{
  "full_name": "新部门名称",
  "address": "新部门地址",
  "longitude": 116.398,
  "latitude": 39.909,
  "parent_dept_code": "1000"
}
```

**响应体 (200 OK)**:
```json
{
  "dept_code": "1001",
  "full_name": "新部门名称",
  "address": "新部门地址",
  "longitude": 116.398,
  "latitude": 39.909,
  "parent_dept_code": "1000",
  "create_time": "2024-01-01T00:00:00Z",
  "update_time": "2024-01-02T00:00:00Z"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}
- **404 Not Found**: {
  "detail": "部门不存在"
}
- **400 Bad Request**: {
  "detail": "不能将部门设置为自身的子部门"
}
- **400 Bad Request**: {
  "detail": "父部门不存在"
}

### 3.6 删除部门

**路径**: `/api/v1/departments/{dept_code}`
**方法**: `DELETE`
**功能**: 删除指定部门（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `dept_code`: 部门编码

**响应体 (200 OK)**:
```json
{
  "message": "部门删除成功"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}
- **404 Not Found**: {
  "detail": "部门不存在"
}
- **400 Bad Request**: {
  "detail": "部门下有子部门，不能删除"
}
- **400 Bad Request**: {
  "detail": "部门下有人员，不能删除"
}

### 3.7 获取部门下的人员列表（通过人员列表接口过滤）

后端未单独提供该路径，使用人员列表接口并传入 `dept_code` 查询参数即可。

**路径**: `/api/v1/personnel`
**方法**: `GET`
**功能**: 获取指定部门下的人员列表

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `dept_code`: 部门编码（必填）
- `page`: 页码，默认1
- `page_size`: 每页数量，默认10
- `name`: 人员姓名搜索（可选）

**响应体 (200 OK)**:
同 [4.1 获取人员列表](#41-获取人员列表)。

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}


## 4. 人员管理功能模块

### 4.1 获取人员列表

**路径**: `/api/v1/personnel`
**方法**: `GET`
**功能**: 获取人员列表，支持分页、搜索和排序

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `page`: 页码，默认1
- `page_size`: 每页数量，默认10
- `name`: 人员姓名搜索（可选）
- `dept_code`: 部门编码筛选（可选）
- `position`: 职位搜索（可选）
- `sort_by`: 排序字段，默认"created_at"
- `order`: 排序方式，默认"desc"（升序为"asc"）

**响应体 (200 OK)**:
```json
{
  "items": [
    {
      "id": 1,
      "name": "string",
      "certificate_number": "string",
      "id_card_number": "string",
      "position": "string",
      "rank": "string",
      "hire_date": "2020-01-01",
      "dept_code": "1001",
      "department_name": "string",
      "create_time": "2024-01-01T00:00:00Z",
      "update_time": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 200,
  "page": 1,
  "page_size": 10,
  "pages": 20
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}

### 4.2 创建人员

**路径**: `/api/v1/personnel`
**方法**: `POST`
**功能**: 创建新人员信息（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
```

**请求体**:
```json
{
  "name": "string",
  "certificate_number": "string",
  "id_card_number": "string",
  "position": "string",
  "rank": "string",
  "hire_date": "2020-01-01",
  "dept_code": "1001"
}
```

**响应体 (201 Created)**:
```json
{
  "id": 1,
  "name": "string",
  "certificate_number": "string",
  "id_card_number": "string",
  "position": "string",
  "rank": "string",
  "hire_date": "2020-01-01",
  "dept_code": "1001",
  "department_name": "string",
  "create_time": "2024-01-01T00:00:00Z",
  "update_time": "2024-01-01T00:00:00Z"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}
- **400 Bad Request**: {
  "detail": "工号已存在"
}
- **400 Bad Request**: {
  "detail": "身份证号已存在"
}
- **400 Bad Request**: {
  "detail": "部门不存在"
}

### 4.3 获取单个人员信息

**路径**: `/api/v1/personnel/{certificate_number}`
**方法**: `GET`
**功能**: 获取指定人员的详细信息

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `certificate_number`: 人员证件号/工号（字符串类型）

**响应体 (200 OK)**:
```json
{
  "id": 1,
  "name": "string",
  "certificate_number": "string",
  "id_card_number": "string",
  "position": "string",
  "rank": "string",
  "hire_date": "2020-01-01",
  "dept_code": "1001",
  "department_name": "string",
  "create_time": "2024-01-01T00:00:00Z",
  "update_time": "2024-01-01T00:00:00Z"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **404 Not Found**: {
  "detail": "人员不存在"
}

### 4.4 更新人员信息

**路径**: `/api/v1/personnel/{certificate_number}`
**方法**: `PUT`
**功能**: 更新指定人员的信息（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `certificate_number`: 人员证件号/工号

**请求体**:
```json
{
  "name": "string",
  "position": "string",
  "rank": "string",
  "dept_code": "1001"
}
```

**响应体 (200 OK)**:
```json
{
  "id": 1,
  "name": "string",
  "certificate_number": "string",
  "id_card_number": "string",
  "position": "string",
  "rank": "string",
  "hire_date": "2020-01-01",
  "dept_code": "1001",
  "department_name": "string",
  "create_time": "2024-01-01T00:00:00Z",
  "update_time": "2024-01-02T00:00:00Z"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}
- **404 Not Found**: {
  "detail": "人员不存在"
}
- **400 Bad Request**: {
  "detail": "部门不存在"
}

### 4.5 删除人员

**路径**: `/api/v1/personnel/{certificate_number}`
**方法**: `DELETE`
**功能**: 删除指定人员（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `certificate_number`: 人员证件号/工号

**响应体 (200 OK)**:
```json
{
  "message": "人员删除成功"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}
- **404 Not Found**: {
  "detail": "人员不存在"
}
- **400 Bad Request**: {
  "detail": "人员存在值班记录，不能删除"
}

### 4.6 导入人员信息

**路径**: `/api/v1/personnel/import`
**方法**: `POST`
**功能**: 批量导入人员信息（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**请求体**:
```
file: [文件类型: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet]
```

**响应体 (200 OK)**:
```json
{
  "success_count": 50,
  "failed_count": 5,
  "failed_details": [
    {
      "row": 10,
      "error": "工号已存在"
    }
  ]
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}
- **400 Bad Request**: {
  "detail": "文件格式不正确"
}

### 4.7 导出人员信息

**路径**: `/api/v1/personnel/export`
**方法**: `GET`
**功能**: 导出人员信息

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `dept_code`: 部门编码筛选（可选）
- `start_date`: 入职开始日期（可选，格式：YYYY-MM-DD）
- `end_date`: 入职结束日期（可选，格式：YYYY-MM-DD）

**响应体 (200 OK)**:
文件下载 (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}

## 5.值班记录功能模块

### 5.1 获取值班记录列表

**路径**: `/api/v1/duty-records`
**方法**: `GET`
**功能**: 获取值班记录列表（支持分页和筛选）

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认10）
- `start_time`: 开始日期（可选）
- `end_time`: 结束日期（可选）
- `personnel_certificate_number`: 值班人员证件号（可选）
- `workstation_id`: 工作地点ID（可选）
- `status`: 值班状态（可选）

**响应体 (200 OK)**:
```json
{
  "total": 100,
  "page": 1,
  "page_size": 10,
  "items": [
    {
      "id": 1,
      "personnel_certificate_number": "string",
      "personnel_name": "string",
      "workstation_id": "string",
      "workstation_name": "string",
      "start_time": "2024-01-01T08:00:00Z",
      "end_time": "2024-01-01T17:00:00Z",
      "status": "normal",
      "remark": "string",
      "created_by": "string",
      "create_time": "2024-01-01T00:00:00Z",
      "update_time": "2024-01-01T00:00:00Z"
    }
  ],
  "pages": 10
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}

### 5.2 创建值班记录

**路径**: `/api/v1/duty-records`
**方法**: `POST`
**功能**: 创建新的值班记录（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:
```json
{
  "personnel_certificate_number": "string",
  "successor_certificate_number": "string",
  "workstation_id": "string",
  "start_time": "2024-01-01T08:00:00Z",
  "end_time": "2024-01-01T17:00:00Z",
  "remark": "string"
}
```

**响应体 (201 Created)**:
```json
{
  "id": 1,
  "personnel_certificate_number": "string",
  "successor_certificate_number": "string",
  "workstation_id": "string",
  "start_time": "2024-01-01T08:00:00Z",
  "end_time": "2024-01-01T17:00:00Z",
  "status": "normal",
  "remark": "string",
  "created_by": "string",
  "create_time": "2024-01-01T00:00:00Z",
  "update_time": "2024-01-01T00:00:00Z"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}
- **400 Bad Request**: {
  "detail": "人员不存在"
}
- **400 Bad Request**: {
  "detail": "工作地点不存在"
}
- **400 Bad Request**: {
  "detail": "该时间段已存在值班记录"
}

### 5.3 获取单个值班记录

**路径**: `/api/v1/duty-records/{id}`
**方法**: `GET`
**功能**: 获取指定值班记录的详细信息

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `id`: 值班记录ID

**响应体 (200 OK)**:
```json
{
  "id": 1,
  "personnel_certificate_number": "string",
  "personnel_name": "string",
  "personnel_info": {
    "position": "string",
    "department": "string"
  },
  "successor_certificate_number": "string",
  "successor_name": "string",
  "workstation_id": "string",
  "workstation_name": "string",
  "start_time": "2024-01-01T08:00:00Z",
  "end_time": "2024-01-01T17:00:00Z",
  "status": "normal",
  "remark": "string",
  "created_by": "string",
  "create_time": "2024-01-01T00:00:00Z",
  "update_time": "2024-01-01T00:00:00Z",
  "inspection_records": [
    {
      "id": 1,
      "inspection_time": "2024-01-01T10:00:00Z",
      "inspector_name": "string",
      "result": "normal"
    }
  ]
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **404 Not Found**: {
  "detail": "值班记录不存在"
}

### 5.4 更新值班记录

**路径**: `/api/v1/duty-records/{id}`
**方法**: `PUT`
**功能**: 更新值班记录信息（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**路径参数**:
- `id`: 值班记录ID

**请求体**:
```json
{
  "personnel_certificate_number": "string",
  "successor_certificate_number": "string",
  "workstation_id": "string",
  "start_time": "2024-01-01T08:00:00Z",
  "end_time": "2024-01-01T17:00:00Z",
  "status": "normal",
  "remark": "string"
}
```

**响应体 (200 OK)**:
```json
{
  "id": 1,
  "personnel_certificate_number": "string",
  "successor_certificate_number": "string",
  "workstation_id": "string",
  "start_time": "2024-01-01T08:00:00Z",
  "end_time": "2024-01-01T17:00:00Z",
  "status": "normal",
  "remark": "string",
  "created_by": "string",
  "create_time": "2024-01-01T00:00:00Z",
  "update_time": "2024-01-01T00:00:00Z"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}
- **404 Not Found**: {
  "detail": "值班记录不存在"
}
- **400 Bad Request**: {
  "detail": "该时间段已存在值班记录"
}

### 5.5 删除值班记录

**路径**: `/api/v1/duty-records/{id}`
**方法**: `DELETE`
**功能**: 删除指定的值班记录（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `id`: 值班记录ID

**响应体 (200 OK)**: 
```json
{
  "message": "值班记录删除成功"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}
- **404 Not Found**: {
  "detail": "值班记录不存在"
}
- **400 Bad Request**: {
  "detail": "值班记录已存在查班记录，不能删除"
}

### 5.6 获取值班统计信息

**路径**: `/api/v1/duty-records/statistics/summary`
**方法**: `GET`
**功能**: 获取值班统计信息

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `start_date`: 统计开始日期（格式：YYYY-MM-DD）（可选）
- `end_date`: 统计结束日期（格式：YYYY-MM-DD）（可选）
- `department_id`: 部门ID（可选）

**响应体 (200 OK)**: 
```json
{
  "total_records": 100,
  "total_persons": 20,
  "department_statistics": [
    {
      "department_id": "1001",
      "department_name": "技术部",
      "record_count": 50
    }
  ],
  "daily_statistics": [
    {
      "date": "2024-01-01",
      "record_count": 5
    }
  ]
}

## 6.查班记录功能模块

### 6.1 获取查班记录列表

**路径**: `/api/v1/inspection-records`
**方法**: `GET`
**功能**: 获取查班记录列表（支持分页和筛选）

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认10）
- `start_date`: 开始日期（可选）
- `end_date`: 结束日期（可选）
- `inspector_certificate_number`: 查班人员证件号（可选）
- `duty_record_id`: 执勤记录ID（可选）
- `inspection_type`: 查班类型（可选，值为：ONLINE/网络 或 ON_SITE/实地）
- `evaluation_level`: 评价等级（可选，值为：GOOD/好 或 MEDIUM/中 或 POOR/差）

**响应体 (200 OK)**:
```json
{
  "total": 50,
  "page": 1,
  "page_size": 10,
  "items": [
    {
      "id": 1,
      "duty_record_id": 100,
      "inspector_certificate_number": "P001",
      "inspector_name": "张伟",
      "start_time": "2024-01-01T10:00:00Z",
      "end_time": "2024-01-01T10:15:00Z",
      "inspection_type": "ONLINE",
      "inspection_type_text": "网络",
      "evaluation_level": "GOOD",
      "evaluation_level_text": "好",
      "violation_type_code": "",
      "create_time": "2024-01-01T10:00:00Z",
      "update_time": "2024-01-01T10:00:00Z"
    }
  ]
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}

### 6.2 创建查班记录

**路径**: `/api/v1/inspection-records`
**方法**: `POST`
**功能**: 创建新的查班记录

**请求头**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:
```json
{
  "duty_record_id": 100,
  "start_time": "2024-01-01T10:00:00Z",
  "end_time": "2024-01-01T10:15:00Z",
  "inspection_type": "ONLINE",
  "evaluation_level": "GOOD",
  "violation_type_code": ""
}
```

**响应体 (201 Created)**:
```json
{
  "id": 1,
  "duty_record_id": 100,
  "inspector_certificate_number": "P001",
  "inspector_name": "张伟",
  "start_time": "2024-01-01T10:00:00Z",
  "end_time": "2024-01-01T10:15:00Z",
  "inspection_type": "ONLINE",
  "inspection_type_text": "网络",
  "evaluation_level": "GOOD",
  "evaluation_level_text": "好",
  "violation_type_code": "",
  "create_time": "2024-01-01T10:00:00Z",
  "update_time": "2024-01-01T10:00:00Z"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **400 Bad Request**: {
  "detail": "值班记录不存在"
}
- **400 Bad Request**: {
  "detail": "非值班时间不能进行查班"
}

### 6.3 获取单个查班记录

**路径**: `/api/v1/inspection-records/{id}`
**方法**: `GET`
**功能**: 获取指定查班记录的详细信息

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `id`: 查班记录ID

**响应体 (200 OK)**:
```json
{
  "id": 1,
  "duty_record_id": 100,
  "duty_info": {
      "start_time": "2024-01-01T08:00:00Z",
      "end_time": "2024-01-01T17:00:00Z",
      "workstation_id": "WS001",
      "personnel_certificate_number": "P002",
      "personnel_name": "李四"
    },
  "inspector_certificate_number": "P001",
  "inspector_name": "张伟",
  "start_time": "2024-01-01T10:00:00Z",
  "end_time": "2024-01-01T10:15:00Z",
  "inspection_type": "ONLINE",
  "inspection_type_text": "网络",
  "evaluation_level": "GOOD",
  "evaluation_level_text": "好",
  "violation_type_code": "",
  "create_time": "2024-01-01T10:00:00Z",
  "update_time": "2024-01-01T10:00:00Z"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **404 Not Found**: {
  "detail": "查班记录不存在"
}

### 6.4 更新查班记录

**路径**: `/api/v1/inspection-records/{id}`
**方法**: `PUT`
**功能**: 更新查班记录信息（仅管理员或创建者）

**请求头**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**路径参数**:
- `id`: 查班记录ID

**请求体**:
```json
{
  "start_time": "2024-01-01T10:00:00Z",
  "end_time": "2024-01-01T10:20:00Z",
  "inspection_type": "ON_SITE",
  "evaluation_level": "MEDIUM",
  "violation_type_code": "V001"
}
```

**响应体 (200 OK)**:
```json
{
  "id": 1,
  "duty_record_id": 100,
  "inspector_certificate_number": "P001",
  "start_time": "2024-01-01T10:00:00Z",
  "end_time": "2024-01-01T10:20:00Z",
  "inspection_type": "ON_SITE",
  "inspection_type_text": "实地",
  "evaluation_level": "MEDIUM",
  "evaluation_level_text": "中",
  "violation_type_code": "V001",
  "update_time": "2024-01-01T10:30:00Z"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}
- **404 Not Found**: {
  "detail": "查班记录不存在"
}

### 6.5 删除查班记录

**路径**: `/api/v1/inspection-records/{id}`
**方法**: `DELETE`
**功能**: 删除指定的查班记录（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `id`: 查班记录ID

**响应体 (200 OK)**: 
```json
{
  "message": "查班记录删除成功"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}
- **404 Not Found**: {
  "detail": "查班记录不存在"
}

### 6.6 获取查班统计信息

**路径**: `/api/v1/inspection-records/statistics/summary`
**方法**: `GET`
**功能**: 获取查班统计信息

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `start_date`: 统计开始日期（格式：YYYY-MM-DD）（可选）
- `end_date`: 统计结束日期（格式：YYYY-MM-DD）（可选）
- `department_id`: 部门ID（可选）

**响应体 (200 OK)**: 
```json
{
  "total_records": 100,
  "total_inspectors": 15,
  "department_statistics": [
    {
      "department_id": "1001",
      "department_name": "技术部",
      "record_count": 60
    }
  ],
  "daily_statistics": [
    {
      "date": "2024-01-01",
      "record_count": 8
    }
  ]
}

## 7. 数据分析功能模块

> **说明**：本节按后端实际代码整理。原文档中的 `shift-change-stats`、`inspection-stats`、
> `site-duty-stats` 三个接口在代码中并不存在；站点维度统计请使用
> `workstation-duty-yearly`。所有接口均需要请求头
> `Authorization: Bearer <access_token>`，年份参数格式为 `YYYY`，格式错误返回 400。

### 7.1 统计指定人员特定年份值班情况

**路径**: `/api/v1/analytics/staff-duty-yearly`
**方法**: `GET`
**功能**: 统计指定人员在特定年份的总值班天数、总时长与月度分布

**查询参数**:
- `personnel_certificate_number`: 人员证件号（必填）
- `year`: 年份（必填，格式：YYYY）

**响应体 (200 OK)**:
```json
{
  "personnel_certificate_number": "ZHANG001",
  "personnel_name": "张伟",
  "year": "2025",
  "total_duty_days": 18,
  "total_duty_hours": 30.0,
  "duty_by_month": [
    { "month": 1, "days": 2, "hours": 4 },
    { "month": 2, "days": 1, "hours": 2 },
    { "month": 3, "days": 1, "hours": 2 }
  ]
}
```

**错误响应**:
- **401 Unauthorized**: { "detail": "未授权访问" }
- **400 Bad Request**: { "detail": "年份格式错误，请使用YYYY格式" }

### 7.2 统计值班时间段分布

**路径**: `/api/v1/analytics/duty-time-distribution`
**方法**: `GET`
**功能**: 统计指定人员一年内值班记录在 24 小时内的分布

**查询参数**:
- `personnel_certificate_number`: 人员证件号（必填）
- `year`: 年份（必填，格式：YYYY）

**响应体 (200 OK)**:
```json
{
  "year": "2025",
  "personnel_certificate_number": "ZHANG001",
  "personnel_name": "张伟",
  "time_distribution": [
    { "hour": 0, "count": 2 },
    { "hour": 1, "count": 1 },
    { "hour": 2, "count": 0 }
  ],
  "peak_hours": [0, 4, 11],
  "total_records": 21
}
```

**错误响应**:
- **401 Unauthorized**: { "detail": "未授权访问" }
- **400 Bad Request**: { "detail": "年份格式错误，请使用YYYY格式" }

### 7.3 统计节假日执勤记录

**路径**: `/api/v1/analytics/holiday-duty`
**方法**: `GET`
**功能**: 统计指定人员在特定年份的节假日值班情况，分页返回节假日执勤记录

**查询参数**:
- `year`: 年份（必填，格式：YYYY）
- `personnel_certificate_number`: 人员证件号（必填）
- `page`: 页码，默认 1
- `page_size`: 每页数量，默认 10

**响应体 (200 OK)**:
```json
{
  "total": 1,
  "page": 1,
  "page_size": 10,
  "year": "2025",
  "total_duty_records": 21,
  "total_holiday_records": 3,
  "total_holiday_duty_days": 3,
  "total_holiday_duty_hours": 6.0,
  "items": [
    {
      "duty_id": "1",
      "staff_certificate_number": "ZHANG001",
      "staff_name": "张伟",
      "start_time": "2025-01-01T08:00:00",
      "end_time": "2025-01-01T10:00:00",
      "holiday_name": "元旦",
      "site_name": "总部"
    }
  ]
}
```

**错误响应**:
- **401 Unauthorized**: { "detail": "未授权访问" }
- **400 Bad Request**: { "detail": "年份格式错误" }
- **400 Bad Request**: { "detail": "人员不存在" }

### 7.4 计算值班贡献度和排名

**路径**: `/api/v1/analytics/contribution-ranking`
**方法**: `GET`
**功能**: 计算指定人员在特定年份值班时长在团队中的贡献度和排名

**查询参数**:
- `personnel_certificate_number`: 人员证件号（必填）
- `year`: 年份（必填，格式：YYYY）

**响应体 (200 OK)**:
```json
{
  "personnel_certificate_number": "ZHANG001",
  "personnel_name": "张伟",
  "year": "2025",
  "total_duty_hours": 30.15,
  "dept_total_hour": 42.18,
  "dept_average_hours": 21.09,
  "contribution_rate": 1.43,
  "contribution_percentage": "71.48%",
  "ranking": 1,
  "total_staff_count": 2,
  "dept_id": "DEPT001",
  "dept_name": "测试部门"
}
```

**错误响应**:
- **401 Unauthorized**: { "detail": "未授权访问" }
- **400 Bad Request**: { "detail": "年份格式错误，请使用YYYY格式" }

### 7.5 统计极端天气值班记录

**路径**: `/api/v1/analytics/extreme-weather-duty`
**方法**: `GET`
**功能**: 统计指定人员在特定年份的极端天气值班记录

**查询参数**:
- `personnel_certificate_number`: 人员证件号（必填；也接受别名 `personnel_id`）
- `year`: 年份（必填，格式：YYYY）

**响应体 (200 OK)**:
```json
{
  "personnel_id": "ZHANG001",
  "personnel_name": "张伟",
  "year": "2025",
  "total_duty_days": 18,
  "total_duty_hours": 30.0,
  "total_duty_records": 21,
  "extreme_duty_records": [
    { "duty_id": "1", "duty_date": "2025-01-18T04:04:00" }
  ],
  "weather_type_summary": [
    { "type": "大雨", "count": 2 }
  ]
}
```

**错误响应**:
- **401 Unauthorized**: { "detail": "未授权访问" }
- **400 Bad Request**: { "detail": "年份格式错误，请使用YYYY格式" }

### 7.6 统计值班天气极值

**路径**: `/api/v1/analytics/weather-extreme-stats`
**方法**: `GET`
**功能**: 统计指定人员在特定年份值班记录中的天气极值

**查询参数**:
- `personnel_certificate_number`: 人员证件号（必填）
- `year`: 年份（必填，格式：YYYY）

**响应体 (200 OK)**:
```json
{
  "personnel_certificate_number": "ZHANG001",
  "personnel_name": "张伟",
  "year": "2025",
  "max_temperature": { "value": 38.5, "record_time": "2025-07-20T14:00:00", "duty_id": "1" },
  "min_temperature": { "value": -12.0, "record_time": "2025-01-18T04:04:00", "duty_id": "2" },
  "max_rainfall": { "value": 56.2, "record_time": "2025-08-01T10:00:00", "duty_id": "3" },
  "max_snowfall": { "value": 8.0, "record_time": "2025-01-20T08:00:00", "duty_id": "4" },
  "max_wind_speed": { "value": 24.0, "record_time": "2025-03-15T09:00:00", "duty_id": "5" },
  "total_duty_days": 18,
  "total_duty_hours": 30.0
}
```

**错误响应**:
- **401 Unauthorized**: { "detail": "未授权访问" }
- **400 Bad Request**: { "detail": "年份格式错误，请使用YYYY格式" }

### 7.7 统计指定工位特定年份值班情况

**路径**: `/api/v1/analytics/workstation-duty-yearly`
**方法**: `GET`
**功能**: 统计指定工位在特定年份的总值班天数、总时长与月度分布。
这是原文档"站点值班情况"的实际接口；它按工位统计，不按人员跨站点统计。

**查询参数**:
- `workstation_id`: 工位 ID（必填）
- `year`: 年份（必填，格式：YYYY）

**响应体 (200 OK)**:
```json
{
  "workstation_id": "WS001",
  "workstation_name": "总部",
  "year": "2025",
  "total_duty_days": 25,
  "total_duty_hours": 50.0,
  "duty_by_month": [
    { "month": 1, "days": 3, "hours": 6 },
    { "month": 2, "days": 2, "hours": 4 }
  ]
}
```

**错误响应**:
- **401 Unauthorized**: { "detail": "未授权访问" }
- **400 Bad Request**: { "detail": "年份格式错误，请使用YYYY格式" }

## 8.保险箱记录管理功能模块

### 8.1 获取保险箱记录列表

**路径**: `/api/v1/safe-records/`
**方法**: `GET`
**功能**: 获取保险箱操作记录列表（支持分页和筛选）

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认10）
- `start_time`: 开始时间（可选）
- `end_time`: 结束时间（可选）
- `dept_code`: 部门编码（可选）
- `device_id`: 设备ID（可选）
- `applicant_certificate_number`: 申请人证书编号（可选）
- `application_type`: 申请类型（可选）
- `authorizer_certificate_number`: 授权人证书编号（可选）
- `authorization_result`: 授权结果（可选）

**响应体 (200 OK)**:
```json
{
  "total": 80,
  "page": 1,
  "page_size": 10,
  "items": [
    {
      "id": 1,
      "dept_code": "1001",
      "dept_name": "测试部门",
      "device_id": "SAFE001",
      "applicant_certificate_number": "123456",
      "applicant_name": "张伟",
      "application_time": "2024-01-01T08:30:00Z",
      "application_type": "01",
      "application_type_name": "工位申请",
      "authorizer_certificate_number": "654321",
      "authorizer_name": "李四",
      "authorization_type": "01",
      "authorization_type_name": "值班室授权",
      "authorization_result": "01",
      "authorization_result_name": "成功",
      "open_time": "2024-01-01T08:30:00Z",
      "close_time": "2024-01-01T09:00:00Z",
      "is_test_mode": false,
      "created_at": "2024-01-01T08:30:00Z",
      "updated_at": "2024-01-01T09:00:00Z"
    }
  ]
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}

### 8.2 创建保险箱记录

**路径**: `/api/v1/safe-records/`
**方法**: `POST`
**功能**: 创建新的保险箱操作记录，完整记录保险箱的开启和关闭信息

**请求头**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:
```json
{
  "dept_code": "1001",
  "device_id": "SAFE001",
  "applicant_certificate_number": "123456",
  "application_time": "2024-01-01T08:30:00Z",
  "application_type": "01",
  "authorizer_certificate_number": "654321",
  "authorization_type": "01",
  "authorization_result": "01",
  "open_time": "2024-01-01T08:30:00Z",
  "close_time": "2024-01-01T09:00:00Z",
  "is_test_mode": false
}
```

**响应体 (201 Created)**:
```json
{
  "id": 1,
  "dept_code": "1001",
  "device_id": "SAFE001",
  "applicant_certificate_number": "123456",
  "application_time": "2024-01-01T08:30:00Z",
  "application_type": "01",
  "authorizer_certificate_number": "654321",
  "authorization_type": "01",
  "authorization_result": "01",
  "open_time": "2024-01-01T08:30:00Z",
  "close_time": "2024-01-01T09:00:00Z",
  "is_test_mode": false,
  "created_at": "2024-01-01T08:30:00Z",
  "updated_at": "2024-01-01T08:30:00Z"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **400 Bad Request**: {
  "detail": "部门不存在"
}
- **400 Bad Request**: {
  "detail": "申请人不存在"
}
- **400 Bad Request**: {
  "detail": "授权人不存在"
}
- **400 Bad Request**: {
  "detail": "申请类型无效"
}
- **400 Bad Request**: {
  "detail": "授权类型无效"
}
- **400 Bad Request**: {
  "detail": "授权结果无效"
}

### 8.3 获取单个保险箱记录

**路径**: `/api/v1/safe-records/{id}`
**方法**: `GET`
**功能**: 获取指定保险箱记录的详细信息

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `id`: 保险箱记录ID（整数类型）

**响应体 (200 OK)**:
```json
{
  "id": 1,
  "dept_code": "1001",
  "dept_name": "测试部门",
  "device_id": "SAFE001",
  "applicant_certificate_number": "123456",
  "applicant_name": "张伟",
  "applicant_position": "主任",
  "application_time": "2024-01-01T08:30:00Z",
  "application_type": "01",
  "application_type_name": "工位申请",
  "authorizer_certificate_number": "654321",
  "authorizer_name": "李四",
  "authorizer_position": "副主任",
  "authorization_type": "01",
  "authorization_type_name": "值班室授权",
  "authorization_result": "01",
  "authorization_result_name": "成功",
  "open_time": "2024-01-01T08:30:00Z",
  "close_time": "2024-01-01T09:00:00Z",
  "duration": "30分钟",
  "is_test_mode": false,
  "created_at": "2024-01-01T08:30:00Z",
  "updated_at": "2024-01-01T08:30:00Z"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **404 Not Found**: {
  "detail": "记录不存在"
}

### 8.4 更新保险箱记录

**路径**: `/api/v1/safe-records/{id}`
**方法**: `PUT`
**功能**: 更新保险箱记录信息

**请求头**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**路径参数**:
- `id`: 保险箱记录ID（整数类型）

**请求体**:
```json
{
  "dept_code": "1001",
  "device_id": "SAFE001",
  "applicant_certificate_number": "123456",
  "application_time": "2024-01-01T08:30:00Z",
  "application_type": "01",
  "authorizer_certificate_number": "654321",
  "authorization_type": "01",
  "authorization_result": "01",
  "open_time": "2024-01-01T08:30:00Z",
  "close_time": "2024-01-01T09:00:00Z",
  "is_test_mode": false
}
```

**响应体 (200 OK)**:
```json
{
  "id": 1,
  "dept_code": "1001",
  "device_id": "SAFE001",
  "applicant_certificate_number": "123456",
  "application_time": "2024-01-01T08:30:00Z",
  "application_type": "01",
  "authorizer_certificate_number": "654321",
  "authorization_type": "01",
  "authorization_result": "01",
  "open_time": "2024-01-01T08:30:00Z",
  "close_time": "2024-01-01T09:00:00Z",
  "is_test_mode": false,
  "created_at": "2024-01-01T08:30:00Z",
  "updated_at": "2024-01-01T09:30:00Z"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **404 Not Found**: {
  "detail": "记录不存在"
}
- **400 Bad Request**: {
  "detail": "部门不存在"
}
- **400 Bad Request**: {
  "detail": "申请人不存在"
}
- **400 Bad Request**: {
  "detail": "授权人不存在"
}
- **400 Bad Request**: {
  "detail": "申请类型无效"
}
- **400 Bad Request**: {
  "detail": "授权类型无效"
}
- **400 Bad Request**: {
  "detail": "授权结果无效"
}

### 8.5 删除保险箱记录

**路径**: `/api/v1/safe-records/{id}`
**方法**: `DELETE`
**功能**: 删除指定的保险箱记录

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `id`: 保险箱记录ID（整数类型）

**响应体 (204 No Content)**:
无响应体

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **404 Not Found**: {
  "detail": "记录不存在"
}

### 8.6 获取申请类型列表

**路径**: `/api/v1/safe-records/application_types`
**方法**: `GET`
**功能**: 获取所有可用的申请类型

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应体 (200 OK)**:
```json
{
  "items": [
    { "code": "01", "name": "工位申请" },
    { "code": "02", "name": "值班室供应" },
    { "code": "03", "name": "联动申请" },
    { "code": "04", "name": "保险箱控制器" },
    { "code": "05", "name": "钥匙开启" }
  ]
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}

### 8.7 获取授权类型列表

**路径**: `/api/v1/safe-records/authorization_types`
**方法**: `GET`
**功能**: 获取所有可用的授权类型

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应体 (200 OK)**:
```json
{
  "items": [
    { "code": "01", "name": "值班室授权" },
    { "code": "02", "name": "联动授权" },
    { "code": "03", "name": "保险箱控制器" },
    { "code": "04", "name": "保险箱钥匙" },
    { "code": "05", "name": "实地供应" }
  ]
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}

### 8.8 获取授权结果列表

**路径**: `/api/v1/safe-records/authorization_results`
**方法**: `GET`
**功能**: 获取所有可用的授权结果

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应体 (200 OK)**:
```json
{
  "items": [
    { "code": "01", "name": "成功" },
    { "code": "02", "name": "失败" },
    { "code": "03", "name": "超时" },
    { "code": "04", "name": "拒绝" }
  ]
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}

## 9.设备柜记录管理功能模块

### 9.1 获取设备柜记录列表

**路径**: `/api/v1/equipment-cabinet-records/`
**方法**: `GET`
**功能**: 获取设备柜操作记录列表（支持分页和筛选）

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认10）
- `sort_by`: 排序字段（可选，默认按申请时间倒序）
- `sort_order`: 排序方向（可选，asc/desc）
- `dept_code`: 部门编码（可选）
- `device_id`: 设备ID（可选）
- `applicant_certificate_number`: 申请人证书编号（可选）
- `start_time`: 申请开始时间（可选）
- `end_time`: 申请结束时间（可选）
- `open_type`: 开柜类型（可选，01:值班室开启, 02:钥匙开启, 03:终端控制开启）
- `open_result`: 开柜结果（可选，01:正常, 02:拒绝, 03:钥匙开柜）

**响应体 (200 OK)**:
```json
{
  "total": 120,
  "page": 1,
  "page_size": 10,
  "items": [
    {
      "id": 1,
      "dept_code": "DEP001",
      "dept_name": "技术部",
      "device_id": "DEV123456",
      "applicant_certificate_number": "PER001",
      "applicant_name": "张伟",
      "authorizer_certificate_number": "PER002",
      "authorizer_name": "李四",
      "application_time": "2024-01-01T09:00:00Z",
      "open_reason_type": "01",
      "open_type": "01",
      "open_result": "01",
      "cabinet_open_time": "2024-01-01T09:05:00Z",
      "cabinet_close_time": "2024-01-01T09:15:00Z",
      "device_quantity_change": "1->2",
      "create_time": "2024-01-01T09:00:00Z",
      "update_time": "2024-01-01T09:15:00Z"
    }
  ]
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}

### 9.2 获取设备柜记录详情

**路径**: `/api/v1/equipment-cabinet-records/{id}`
**方法**: `GET`
**功能**: 获取单个设备柜操作记录的详细信息

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `id`: 设备柜记录ID

**响应体 (200 OK)**:
```json
{
  "id": 1,
  "dept_code": "DEP001",
  "dept_name": "技术部",
  "device_id": "DEV123456",
  "applicant_certificate_number": "PER001",
  "applicant_name": "张伟",
  "authorizer_certificate_number": "PER002",
  "authorizer_name": "李四",
  "application_time": "2024-01-01T09:00:00Z",
  "open_reason_type": "01",
  "open_type": "01",
  "open_result": "01",
  "cabinet_open_time": "2024-01-01T09:05:00Z",
  "cabinet_close_time": "2024-01-01T09:15:00Z",
  "device_quantity_change": "1->2",
  "create_time": "2024-01-01T09:00:00Z",
  "update_time": "2024-01-01T09:15:00Z"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **404 Not Found**: {
  "detail": "记录不存在"
}

### 9.3 创建设备柜记录

**路径**: `/api/v1/equipment-cabinet-records/`
**方法**: `POST`
**功能**: 创建新的设备柜操作记录

**请求头**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:
```json
{
  "dept_code": "DEP001",
  "device_id": "DEV123456",
  "open_reason_type": "01",
  "applicant_certificate_number": "PER001",
  "application_time": "2024-01-01T09:00:00Z",
  "authorizer_certificate_number": "PER002",
  "open_type": "01",
  "open_result": "01",
  "cabinet_open_time": "2024-01-01T09:05:00Z",
  "device_quantity_change": "1->2"
}
```

**响应体 (201 Created)**:
```json
{
  "id": 1,
  "dept_code": "DEP001",
  "device_id": "DEV123456",
  "open_reason_type": "01",
  "applicant_certificate_number": "PER001",
  "application_time": "2024-01-01T09:00:00Z",
  "authorizer_certificate_number": "PER002",
  "open_type": "01",
  "open_result": "01",
  "cabinet_open_time": "2024-01-01T09:05:00Z",
  "device_quantity_change": "1->2",
  "create_time": "2024-01-01T09:00:00Z",
  "update_time": "2024-01-01T09:00:00Z"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **400 Bad Request**: {
  "detail": "请求参数错误"
}
- **422 Unprocessable Entity**: {
  "detail": "数据验证失败"
}

### 9.4 更新设备柜记录

**路径**: `/api/v1/equipment-cabinet-records/{id}`
**方法**: `PUT`
**功能**: 更新设备柜操作记录信息，主要用于关闭设备柜时更新

**请求头**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**路径参数**:
- `id`: 设备柜记录ID

**请求体**:
```json
{
  "cabinet_close_time": "2024-01-01T09:15:00Z",
  "device_quantity_change": "1->2"
}
```

**响应体 (200 OK)**:
```json
{
  "id": 1,
  "dept_code": "DEP001",
  "device_id": "DEV123456",
  "open_reason_type": "01",
  "applicant_certificate_number": "PER001",
  "application_time": "2024-01-01T09:00:00Z",
  "authorizer_certificate_number": "PER002",
  "open_type": "01",
  "open_result": "01",
  "cabinet_open_time": "2024-01-01T09:05:00Z",
  "cabinet_close_time": "2024-01-01T09:15:00Z",
  "device_quantity_change": "1->2",
  "create_time": "2024-01-01T09:00:00Z",
  "update_time": "2024-01-01T09:15:00Z"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **404 Not Found**: {
  "detail": "记录不存在"
}
- **400 Bad Request**: {
  "detail": "记录已关闭"
}

### 9.5 删除设备柜记录

**路径**: `/api/v1/equipment-cabinet-records/{id}`
**方法**: `DELETE`
**功能**: 删除指定的设备柜操作记录

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `id`: 设备柜记录ID

**响应体 (204 No Content)**:
无内容

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **404 Not Found**: {
  "detail": "记录不存在"
}

### 9.6 枚举类型列表

三个只读接口返回前端下拉框所需的枚举项，响应结构相同：

**路径**:
- `/api/v1/equipment-cabinet-records/open_reason_types`：开启原因类型
- `/api/v1/equipment-cabinet-records/open_types`：开柜类型
- `/api/v1/equipment-cabinet-records/open_results`：开柜结果

**方法**: `GET`

**请求头**:
```
Authorization: Bearer <access_token>
```

**响应体 (200 OK)**:
```json
{
  "items": [
    { "code": "01", "name": "类型01" },
    { "code": "02", "name": "类型02" }
  ]
}
```

**枚举取值说明**:

开启原因类型 (OpenReasonType):
- `01`: 类型01
- `02`: 类型02
- `03`: 类型03

开柜类型 (CabinetOpenType):
- `01`: 值班室开启
- `02`: 钥匙开启
- `03`: 终端控制开启

开柜结果 (CabinetOpenResult):
- `01`: 正常
- `02`: 拒绝
- `03`: 钥匙开柜


## 10. 工位管理功能模块

> 说明：本节按后端实际代码整理。原文档把工位写成了"工作地点"，字段为
> `name/address/description`；实际模型的字段是
> `workstation_id/workstation_name/dept_code/category_code/longitude/latitude/remark`。

### 10.1 获取工位列表

**路径**: `/api/v1/workstation/`
**方法**: `GET`
**功能**: 获取工位列表，支持分页、筛选和排序

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `page`: 页码，默认 1
- `page_size`: 每页数量，默认 10，最大 100
- `workstation_name`: 工位名称，支持模糊搜索（可选）
- `dept_code`: 单位内码（可选）
- `category_code`: 类别代码（可选）
- `sort_by`: 排序字段，默认 `create_time`
- `order`: 排序方向，`asc` / `desc`，默认 `desc`

**响应体 (200 OK)**:
```json
{
  "total": 20,
  "page": 1,
  "page_size": 10,
  "pages": 2,
  "items": [
    {
      "id": 1,
      "workstation_id": "WS001",
      "workstation_name": "总部值班室",
      "dept_code": "DEPT001",
      "category_code": "01",
      "longitude": 116.397,
      "latitude": 39.908,
      "remark": "主工位",
      "create_time": "2024-01-01T00:00:00Z",
      "update_time": "2024-01-01T00:00:00Z"
    }
  ]
}
```

**错误响应**:
- **401 Unauthorized**: { "detail": "未授权访问" }

### 10.2 创建工位

**路径**: `/api/v1/workstation/`
**方法**: `POST`
**功能**: 创建新工位（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:
```json
{
  "workstation_id": "WS001",
  "workstation_name": "总部值班室",
  "dept_code": "DEPT001",
  "category_code": "01",
  "longitude": 116.397,
  "latitude": 39.908,
  "remark": "主工位"
}
```

**响应体 (201 Created)**:
```json
{
  "id": 1,
  "workstation_id": "WS001",
  "workstation_name": "总部值班室",
  "dept_code": "DEPT001",
  "category_code": "01",
  "longitude": 116.397,
  "latitude": 39.908,
  "remark": "主工位",
  "create_time": "2024-01-01T00:00:00Z",
  "update_time": "2024-01-01T00:00:00Z"
}
```

**错误响应**:
- **401 Unauthorized**: { "detail": "未授权访问" }
- **403 Forbidden**: { "detail": "权限不足" }
- **400 Bad Request**: { "detail": "工位id已存在" }

### 10.3 获取单个工位

**路径**: `/api/v1/workstation/{workstation_id}`
**方法**: `GET`
**功能**: 根据工位 ID 获取工位详情

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `workstation_id`: 工位 ID（字符串）

**响应体 (200 OK)**:
同 10.2 的响应体。

**错误响应**:
- **401 Unauthorized**: { "detail": "未授权访问" }
- **404 Not Found**: { "detail": "工位不存在" }

### 10.4 更新工位

**路径**: `/api/v1/workstation/{workstation_id}`
**方法**: `PUT`
**功能**: 更新工位信息（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**路径参数**:
- `workstation_id`: 工位 ID

**请求体**（字段均可选）:
```json
{
  "workstation_name": "总部值班室",
  "dept_code": "DEPT001",
  "category_code": "01",
  "longitude": 116.397,
  "latitude": 39.908,
  "remark": "主工位"
}
```

**响应体 (200 OK)**:
同 10.2 的响应体。

**错误响应**:
- **401 Unauthorized**: { "detail": "未授权访问" }
- **403 Forbidden**: { "detail": "权限不足" }
- **404 Not Found**: { "detail": "工位不存在" }

### 10.5 删除工位

**路径**: `/api/v1/workstation/{workstation_id}`
**方法**: `DELETE`
**功能**: 删除指定工位（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `workstation_id`: 工位 ID

**响应体 (200 OK)**:
```json
{
  "message": "工位删除成功"
}
```

**错误响应**:
- **401 Unauthorized**: { "detail": "未授权访问" }
- **403 Forbidden**: { "detail": "权限不足" }
- **404 Not Found**: { "detail": "工位不存在" }
- **400 Bad Request**: { "detail": "工位存在关联记录，不能删除" }

## 11. 天气记录管理功能模块

### 11.1 获取天气记录列表

**路径**: `/api/v1/weather-records`
**方法**: `GET`
**功能**: 获取天气记录列表（支持分页和筛选）

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认10）
- `start_time`: 开始时间（可选，格式：YYYY-MM-DDTHH:MM:SS）
- `end_time`: 结束时间（可选，格式：YYYY-MM-DDTHH:MM:SS）
- `longitude_min`: 最小经度（可选）
- `longitude_max`: 最大经度（可选）
- `latitude_min`: 最小纬度（可选）
- `latitude_max`: 最大纬度（可选）

**响应体 (200 OK)**:
```json
{
  "total": 365,
  "page": 1,
  "page_size": 10,
  "items": [
    {
      "id": 1,
      "record_time": "2024-01-01T12:00:00Z",
      "dept_code": "DEPT001",
      "temperature": 10.5,
      "humidity": 65.0,
      "rainfall": 0.0,
      "snowfall": 0.0,
      "wind_speed": 3.5,
      "weather_conditions": ["舒适", "舒适湿度", "无风/微风"]
    }
  ]
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}

### 11.2 创建天气记录

**路径**: `/api/v1/weather-records`
**方法**: `POST`
**功能**: 创建新的天气记录（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:
```json
{
  "record_time": "2024-01-01T12:00:00Z",
  "dept_code": "DEPT001",
  "temperature": 10.5,
  "humidity": 65.0,
  "rainfall": 0.0,
  "snowfall": 0.0,
  "wind_speed": 3.5
}
```

**响应体 (201 Created)**:
```json
{
  "id": 1,
  "record_time": "2024-01-01T12:00:00Z",
  "dept_code": "DEPT001",
  "temperature": 10.5,
  "humidity": 65.0,
  "rainfall": 0.0,
  "snowfall": 0.0,
  "wind_speed": 3.5,
  "weather_conditions": ["舒适", "舒适湿度", "无风/微风"]
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}
- **400 Bad Request**: {
  "detail": "该时间点该位置已存在天气记录"
}

### 11.3 获取单个天气记录

**路径**: `/api/v1/weather-records/{id}`
**方法**: `GET`
**功能**: 获取指定天气记录的详细信息

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `id`: 天气记录ID

**响应体 (200 OK)**:
```json
{
  "id": 1,
  "record_time": "2024-01-01T12:00:00Z",
  "dept_code": "DEPT001",
  "temperature": 10.5,
  "humidity": 65.0,
  "rainfall": 0.0,
  "snowfall": 0.0,
  "wind_speed": 3.5,
  "weather_conditions": ["舒适", "舒适湿度", "无风/微风"]
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **404 Not Found**: {
  "detail": "天气记录不存在"
}

### 11.4 更新天气记录

**路径**: `/api/v1/weather-records/{id}`
**方法**: `PUT`
**功能**: 更新天气记录信息（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**路径参数**:
- `id`: 天气记录ID

**请求体**:
```json
{
  "temperature": 12.5,
  "humidity": 70.0,
  "rainfall": 0.5,
  "snowfall": 0.0,
  "wind_speed": 4.0
}
```

**响应体 (200 OK)**:
```json
{
  "id": 1,
  "record_time": "2024-01-01T12:00:00Z",
  "dept_code": "DEPT001",
  "temperature": 12.5,
  "humidity": 70.0,
  "rainfall": 0.5,
  "snowfall": 0.0,
  "wind_speed": 4.0,
  "weather_conditions": ["舒适", "潮湿", "小雨", "和风"]
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}
- **404 Not Found**: {
  "detail": "天气记录不存在"
}

### 11.5 删除天气记录

**路径**: `/api/v1/weather-records/{id}`
**方法**: `DELETE`
**功能**: 删除指定的天气记录（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `id`: 天气记录ID

**响应体 (200 OK)**:
```json
{
  "message": "天气记录删除成功"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}
- **404 Not Found**: {
  "detail": "天气记录不存在"
}

### 11.6 批量导入天气数据

**路径**: `/api/v1/weather-records/import`
**方法**: `POST`
**功能**: 从Excel文件批量导入天气数据（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**请求体**:
- `file`: Excel文件（xlsx格式）

**Excel文件格式要求**:
- 第一行必须包含以下列标题：record_time, longitude, latitude, temperature, humidity, rainfall, snowfall, wind_speed
- record_time列格式：YYYY-MM-DD HH:MM:SS
- 所有数值类型字段不能为空

**响应体 (200 OK)**:
```json
{
  "message": "导入成功",
  "success_count": 30,
  "failed_count": 2,
  "failed_records": [
    {
      "row": 5,
      "error": "该时间点该位置已存在天气记录"
    },
    {
      "row": 10,
      "error": "必填字段不能为空"
    }
  ]
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}
- **400 Bad Request**: {
  "detail": "无效的文件格式，请上传xlsx格式的Excel文件"
}

### 11.7 按部门删除天气记录

**路径**: `/api/v1/weather-records/by-dept/`
**方法**: `DELETE`
**功能**: 按部门代码删除天气记录，可选时间范围（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `dept_code`: 部门代码（必填）
- `start_time`: 开始时间（可选，格式：YYYY-MM-DD HH:MM:SS）
- `end_time`: 结束时间（可选，格式：YYYY-MM-DD HH:MM:SS）

**响应体 (200 OK)**:
```json
{
  "deleted_count": 10,
  "message": "成功删除部门 DEPT001 的天气记录 10 条"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}


## 12.节假日管理功能模块

### 12.1 获取节假日列表

**路径**: `/api/v1/holidays`
**方法**: `GET`
**功能**: 获取节假日列表（支持分页和筛选）

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认10）
- `start_date`: 开始日期（可选）
- `end_date`: 结束日期（可选）

**响应体 (200 OK)**:
```json
{
  "total": 20,
  "page": 1,
  "page_size": 10,
  "items": [
    {
      "id": 1,
      "date": "2024-01-01",
      "is_holiday": true,
      "holiday_type": "01",
      "name": "元旦",
      "description": "法定节假日",
      "create_time": "2024-01-01T00:00:00Z",
      "update_time": "2024-01-01T00:00:00Z"
    }
  ]
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}

### 12.2 创建节假日

**路径**: `/api/v1/holidays`
**方法**: `POST`
**功能**: 创建新的节假日（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求体**:
```json
{
  "date": "2024-01-01",
  "is_holiday": true,
  "holiday_type": "01",
  "name": "元旦",
  "description": "法定节假日"
}
```

**响应体 (201 Created)**:
```json
{
  "id": 1,
  "date": "2024-01-01",
  "is_holiday": true,
  "holiday_type": "01",
  "name": "元旦",
  "description": "法定节假日",
  "create_time": "2024-01-01T00:00:00Z",
  "update_time": "2024-01-01T00:00:00Z"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}
- **400 Bad Request**: {
  "detail": "该日期已存在节假日记录"
}

### 12.3 获取单个节假日

**路径**: `/api/v1/holidays/{holiday_id}`
**方法**: `GET`
**功能**: 获取指定节假日的详细信息

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `holiday_id`: 节假日ID（整数类型）

**响应体 (200 OK)**:
```json
{
  "id": 1,
  "date": "2024-01-01",
  "is_holiday": true,
  "holiday_type": "01",
  "name": "元旦",
  "description": "法定节假日",
  "create_time": "2024-01-01T00:00:00Z",
  "update_time": "2024-01-01T00:00:00Z"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **404 Not Found**: {
  "detail": "节假日不存在"
}

### 12.4 更新节假日

**路径**: `/api/v1/holidays/{holiday_id}`
**方法**: `PUT`
**功能**: 更新节假日信息（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**路径参数**:
- `holiday_id`: 节假日ID

**请求体**:
```json
{
  "is_holiday": true,
  "holiday_type": "01",
  "name": "元旦",
  "description": "法定节假日"
}
```

**响应体 (200 OK)**:
```json
{
  "id": 1,
  "date": "2024-01-01",
  "is_holiday": true,
  "holiday_type": "01",
  "name": "元旦",
  "description": "法定节假日",
  "create_time": "2024-01-01T00:00:00Z",
  "update_time": "2024-01-01T00:00:00Z"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}
- **404 Not Found**: {
  "detail": "节假日不存在"
}

### 12.5 删除节假日

**路径**: `/api/v1/holidays/{holiday_id}`
**方法**: `DELETE`
**功能**: 删除指定的节假日（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
```

**路径参数**:
- `holiday_id`: 节假日ID（整数类型）

**响应体 (200 OK)**:
```json
{
  "message": "节假日删除成功"
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}
- **404 Not Found**: {
  "detail": "节假日不存在"
}

### 12.6 批量导入节假日

**路径**: `/api/v1/holidays/import/excel`
**方法**: `POST`
**功能**: 批量导入节假日（仅管理员）

**请求头**:
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**请求体**:
```
file: [文件类型: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet]
```

**响应体 (200 OK)**:
```json
{
  "success_count": 20,
  "failed_count": 2,
  "failed_details": [
    {
      "row": 5,
      "error": "日期格式不正确"
    }
  ]
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **403 Forbidden**: {
  "detail": "权限不足"
}
- **400 Bad Request**: {
  "detail": "文件格式不正确"
}

### 12.7 检查日期是否为节假日

**路径**: `/api/v1/holidays/check/date`
**方法**: `GET`
**功能**: 检查指定日期是否为节假日

**请求头**:
```
Authorization: Bearer <access_token>
```

**查询参数**:
- `date`: 要检查的日期（格式：YYYY-MM-DD）

**响应体 (200 OK)**:
```json
{
  "date": "2024-01-01",
  "is_holiday": true,
  "holiday_info": {
    "id": 1,
    "name": "元旦",
    "description": "法定节假日"
  }
}
```

**错误响应**:
- **401 Unauthorized**: {
  "detail": "未授权访问"
}
- **400 Bad Request**: {
  "detail": "日期格式不正确"
}
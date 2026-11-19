"""用户模块的数据访问：只取用户与写入，不判断规则（教材 6.1）。

第 8 章换库时五个函数都会多出 db: Session 参数，职责与调用方式不变。
"""

from . import model


def get_by_username(username: str) -> model.User | None:
    for item in model.TABLE:
        if item.username == username:
            return item
    return None


def get_by_id(user_id: int) -> model.User | None:
    for item in model.TABLE:
        if item.id == user_id:
            return item
    return None


def list_all() -> list[model.User]:
    return model.TABLE


def create(username: str, password_hash: str) -> model.User:
    user = model.User(
        id=len(model.TABLE) + 1,
        username=username,
        password_hash=password_hash,
    )
    model.TABLE.append(user)
    return user


def update(user: model.User, data: dict) -> model.User:
    for key, value in data.items():
        setattr(user, key, value)
    return user

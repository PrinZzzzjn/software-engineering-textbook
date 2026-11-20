from . import model


def list_all() -> list[model.Department]:
    return model.TABLE


def get(dept_code: str) -> model.Department | None:
    for item in model.TABLE:
        if item.dept_code == dept_code:
            return item
    return None


def create(item: model.Department) -> model.Department:
    model.TABLE.append(item)
    return item


def update(item: model.Department, data: dict) -> model.Department:
    for key, value in data.items():
        setattr(item, key, value)
    return item


def delete(item: model.Department) -> None:
    model.TABLE.remove(item)

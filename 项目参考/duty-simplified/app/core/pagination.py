def paginate(query, offset: int, limit: int):
    """对一个已过滤、已排序的查询分页，返回 (items, total)。"""
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    return items, total

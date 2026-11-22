def paginate(query, offset: int, limit: int):
    """对已经过滤、已经排好序的查询取一页，并返回总数。

    对应教材 13.3 的代码 13-3-1：换一个模型仍然一字不改，所以可以抽；
    页码到偏移量的换算仍由各模块的 service 完成，参数名与返回结构不变。
    """
    total = query.count()
    items = query.offset(offset).limit(limit).all()
    return items, total

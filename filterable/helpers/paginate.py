from typing import List, Dict, Union
from sqlalchemy.orm.query import Query
from filterable.request import RequestHandler


def paginate(query: Query, _session = None) -> Dict[str, Union[int, List[dict]]]:
    """
    Paginates the given database query.

    Args:
        query (sqlalchemy.orm.query.Query): The SQLAlchemy query object.
        _session (sqlalchemy.session): [Optional] The SQLAlchemy session to be 
            closed after pagination.

    Returns:
        dict: A dictionary containing pagination information and a list of
            serialized items.
            The dictionary has the following keys:
            - 'page' (int): The current page number. If the 'pageSize' is
                negative, the page number is set to 1.
            - 'pageSize' (int): The number of items per page. If the
                'pageSize' is negative, all items are returned.
            - 'totalRows' (int): The total number of items in the query
                before pagination.
            - 'rows' (List[dict]): A list of dictionaries, each representing
                a serialized item.

    Example:
        # Running it from a Controller Class and assuming 'query' is a valid
            SQLAlchemy query object:
        ```
        from filterable import paginate
        paginated_result = paginate(query)
        ```
    """
    _request = RequestHandler.request()
    _page = int(_request.args.get('page', 1))
    _page_size = min(int(_request.args.get('pageSize', 25)), 250)
    total_count = query.count()
    if _page_size >= 0:
        query_data = query.offset(
            (_page - 1) * _page_size).limit(_page_size).all()
    else:
        _page = 1
        query_data = query.all()
    if _session:
        _session.close()

    return {
        'page': _page,
        'pageSize': _page_size,
        'totalRows': total_count,
        'rows': get_cast_rows(query_data)
    }
        
def get_cast_rows(query_data) -> list:
    try:
        return [data.jsonable() for data in query_data]
    except Exception:
        return query_data
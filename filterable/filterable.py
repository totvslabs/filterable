import re
import json
from sqlalchemy import String, and_, Boolean
from sqlalchemy.orm import DeclarativeBase
from filterable.exceptions.filtering_exception import FilteringException
from filterable.request import RequestHandler
from filterable.types import JSONB, ARRAY


class Filterable(RequestHandler):
    """ Decorator Class to handle filtering and sorting data query """

    def __init__(self, Model:DeclarativeBase):
        self.__Model = Model

    def __call__(self, func):
        def wrapped_func(*args, **kwargs):
            """
            Process the filter and sort parameters before executing the
                decorated method.

            Args:
                *args: Positional arguments.
                **kwargs: Keyword arguments.

            Returns:
                The result of the decorated method.

            Raises:
                FilteringException: If there is an error while processing
                    the filter parameters.
                Exception: If there is any other unexpected error.

            Note:
                Do not forget to unpack the sort conditions with "*" in
                    your query, for example:
                ``` query = query.order_by(*_filtered.sort) ```
            """
            try:
                self.__process_filter()
                self.__process_sort()
            except FilteringException as e:
                return {'error':e.args[0], 'code': 400}, 400
            except Exception as e:
                return {'error':f'Malformed filtering data ({str(e)}).',
                        'code': 400 }, 400
            return func(*args, **kwargs, _filtered=self)
        return wrapped_func

    def __process_filter(self):
        """
        Process the filter information received in the request and set
        the appropriate condition for the SQLAlchemy query.

        The filtering format in the request must be a list of dictionaries,
        where each dictionary contains:
            'f': The field to filter by (string).
            'o': The contition operator (string)(optional, default is 'eq').
            'v': Value to be considered on condition.

        Sort URL usage example:
            ?filter=[
                {"f":"name","o":"eq","v":"alert"},
                {"f":"data.app","o":"neq","v":"carol"}
            ]

        Raises:
            FilteringException: If the 'filter' attribute is present in
                the request, but it's not a valid list of filtering rules,
                or if a filter rule contains an invalid entity field.

        Note:
            This method uses the __get_filter_condition method internally to
            load query conditions dinamically
        """
        request_args = RequestHandler.request().args
        if 'filter' in request_args:
            filters_data = json.loads(request_args['filter'])
            if isinstance(filters_data, list):
                self.filter = self.__get_filter_condition(filters_data)
            else:
                raise FilteringException(
                    'Filters attribute must be a list/array of objects')
        else:
            self.filter = True

    def __process_sort(self):
        """
        Process the sort information received in the request and set
            the appropriate sorting for the SQLAlchemy query.

        The sorting format in the request must be a list of dictionaries,
            where each dictionary contains:
            'f': The field to sort by (string).
            'o': The order direction to sort ('asc' or 'desc')
                                             (optional, default is 'asc').

        Sort URL usage example:
            ?sort=[{"f":"age","o":"desc"},{"f":"name"}],

        Raises:
            FilteringException: If the 'sort' attribute is present in
                the request, but it's not a valid list of sorting rules,
                or if a sorting rule contains an invalid entity field.

        Note:
            This method uses the __get_sort_filter method internally to
                handle sorting for JSONB fields.
        """
        request_args = RequestHandler.request().args
        if 'sort' in request_args:
            sorted_data = json.loads(request_args['sort'])
            if type(sorted_data) == list:
                _filter_list = []
                for sorting in sorted_data:
                    _filter_list.append(self.__get_sort_filter(sorting))
                self.sort = _filter_list if len(_filter_list) > 0 \
                    else self.__Model.created_at.desc()
            else :
                raise FilteringException('Sort attribute must be a list/array')
        else:
            self.sort = [self.__Model.created_at.desc()] # Default sort is 'created_at' date

    def __get_filter_condition(self, filters: list) -> any:
        """
        Process filter conditions and create the SQLAlchemy filter for the query.

        Args:
            filters (list): List of filter conditions.

        Returns:
            The SQLAlchemy filter to be used in the query.

        Raises:
            FilteringException: If there is an error while processing the
                filter conditions.
        """
        filter_clauses = []
        for filter_data in filters:
            field = str(filter_data.get('f'))
            json_key = False
            if '.' in field:
                field, json_key = re.split(r'\.', field, 1)
            if hasattr(self.__Model, field):
                operation = filter_data.get('o', 'eq')  # Default 'eq' if 'o' wasn't provided
                filter_condition = self.__get_condition_operation(
                    self.__get_column_from_model(field, json_key),
                    filter_data.get('v'),
                    operation
                )
                if filter_condition is None:
                    raise FilteringException(
                        f"Invalid operation '{operation}' for field '{field}'")
                filter_clauses.append(filter_condition)
            else:
                raise FilteringException(
                    "A filter must have an 'f' attribute with a valid entity Field")
        return and_(*filter_clauses)

    def __get_column_from_model(self, field:str, json_key:str) -> any:
        """
        Prepare a column of JSON type to be filtered.

        Args:
            field (str): The SQLAlchemy column model to filter by.
            json_key (str): JSON key inside the column.

        Returns:
            Model JSON column ready to be filtered

        Raises:
            FilteringException: If wasn't provided key for the JSON filter
        """
        column = getattr(self.__Model, field)
        if isinstance(column.type, JSONB()):
            if json_key and json_key != '':
                column = column[json_key].astext.cast(String)
            else:
                raise FilteringException(
                    "A key is mandatory filtering JSON fields. "\
                        +f"Eg: '{field}.some_key'")
        return column

    def __get_condition_operation(self,
                                  column:any,
                                  value:str|list,
                                  operation:str):
        """
        Get the SQLAlchemy filter for a given field and operation.

        Args:
            column (any): The SQLAlchemy column to filter by.
            value (str|list): The value to filter by.
            operation (str): The operation to be applied.

        Returns:
            The SQLAlchemy filter to be used in the query.

        Raises:
            FilteringException: If the operation is invalid or the value does
                not match the operation's requirements.
        """
        if operation in ['in', 'nin', 'btw'] and isinstance(value, list) == False:
            raise FilteringException(f'Operation "{operation}" must have a list')

        if operation == 'btw' and len(value) != 2:
            raise FilteringException(
                f'Operation "btw" must be a list with two values (from/to)')

        if isinstance(column.type, Boolean):
            # Boolean validation
            if operation not in ['eq', 'neq']:
                raise FilteringException(
                    f'Only "eq" and "neq" is allowed for boolean columns')
            value = True if str(value) in ['True', 'true', '1'] else False
            operation_map = {'eq': column == value, 'neq': column != value}
            return operation_map.get(operation)

        operation_map = {
            'eq':   column == value,
            'neq':  column != value,
            'gt':   column > value,
            'gte':  column >= value,
            'lt':   column < value,
            'lte':  column <= value,
            'in':   column.in_([value] if isinstance(value, str) else value),
            'nin': ~column.in_([value] if isinstance(value, str) else value),
            'has':  column.contains([value] if isinstance(value, str) else value),
            'hasn':~column.contains([value] if isinstance(value, str) else value),
            'lk':   column.like(f"%{value}%"),
            'nlk': ~column.like(f"%{value}%"),
            'btw':  column.between(value[0], value[1] if len(value) > 1 else '')
        }
        return operation_map.get(operation)

    def __get_sort_filter(self, sorting:dict) -> any:
        """
        Get the sorting filter for a given field and direction.

        Args:
            sorting (dict): Sorting format with the following keys:
                'f': The field to sort by (string).
                'o': The order direction to sort ('asc' or 'desc') (optional,
                    default is 'asc').

        Returns:
            The sorting filter to be used in the SQLAlchemy query.

        Raises:
            FilteringException: If the field specified in 'f' is not a valid
                entity field.
        """
        field = str(sorting.get('f'))
        json_key = False
        if '.' in sorting.get('f'):
            field, json_key = re.split(r'\.', field, 1)
        if hasattr(self.__Model, field):
            column = getattr(self.__Model, field)
            # If column is a JSON type and field requested have a json key ("column.json_key"):
            if isinstance(column.type, JSONB()) and json_key:
                # Prepare json key to work as a query index
                json_key = column[json_key].astext.cast(String)
                return json_key.desc() if sorting.get('o') == 'desc' else json_key.asc()
            return column.desc() if sorting.get('o') == 'desc' else column.asc()
        else:
            raise FilteringException(
                "A sort must have a 'f' attribute with a valid entity Field")

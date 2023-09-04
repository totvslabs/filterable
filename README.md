Filterable
![PyPI - Version](https://img.shields.io/pypi/v/filterable?color=blue)
![PyPI - Dependencies](https://img.shields.io/librariesio/release/pypi/filterable?color=green)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/filterable?color=purple)
=======
**Standardize filters and pagination in your Python API**

Filterable is a Python library that simplifies the application of filters, pagination, and sorting to SQLAlchemy queries based on HTTP requests. It provides a convenient way to process request parameters and apply these filters and sorts to SQLAlchemy queries, enabling standardization of filters used by client integrations with your Python API across all routes.

Anchors:
- [Dependencies](#dependencies)
- [Introduction](#introduction)
- [Installation](#installation)
- [Filters](#filters)
    - [Default schema](#default-schema)
    - [Filtering data](#filtering-data)
    - [Filter example usage](#filter-example-usage)
    - [Query engine](#query-engine)
- [Sorting](#sorting)
    - [Sort example usage](#sort-example-usage)
- [The `Filterable` class](#the-filterable-class)
    - [Handling Pagination](#handling-pagination)
      

## Dependencies
- [Python](https://www.python.org/) >= 3.7
- [SqlAlchemy](https://github.com/sqlalchemy/sqlalchemy) >= 2.0

## Introduction
Filterable is a class decorator method that applies filters to SQLAlchemy queries based on the arguments passed in the request. Simply decorate your method with Filterable, and it will inject a dictionary called `_filtered` with the applied filters, sorting, and pagination.

```python
from filterable import Filterable
from your_app.models import UserModel

class YourController():

    @Filterable(UserModel)
    def get_users(self, _filtered):
        users_query = session().query(UserModel).filter(
            _filtered.filter
        ).order_by(*_filtered.sort)

        return users_query.all(), 200
```

## Installation
You can install it using pip:
```
pip install filterable
```

## Filters
Requests must follow the following pattern:

```url
https://your-aplication.com?page=1&pageSize=10&sort=GENERIC_REQUEST_SORT&filters=GENERIC_REQUEST_FILTER
```

### Default Schema
```javascript
{
    /** default: 0 **/
    /** noLimit: -1, optional support to return all entities **/
    "page"?: 1

    /** default: 25 **/
    "pageSize"?: 10,

    /** optional **/
    /** description: sorting by one or multiple criteria **/
    "sort"?: GENERIC_REQUEST_SORT | GENERIC_REQUEST_SORT[],

    /** optional **/
    /** description: multiple filters list **/
    "filters":? GENERIC_REQUEST_FILTER[],

    /** your endpoint custom args **/
    ** : **
}
```
> NOTE: Below is more information about the GENERIC_REQUEST_SORT and GENERIC_REQUEST_FILTER schema for sorting and filters.

### Filtering Data
#### `[GENERIC_REQUEST_FILTER]`
In the filters attribute of the JSON request object, you define the conditions that will be applied to the SQLAlchemy query. This is the standard structure of a filter:

```javascript
{
    /** description: field to filter by **/
    "f": string,

    /** description: operation to be applied **/
    /** default: 'eq' **/
    "o"?:
        | 'eq'   // eq  : equals
        | 'neq'  // neq : not equals
        | 'gt'   // gt  : greater than
        | 'gte'  // gte : greater than or equal
        | 'lt'   // lt  : lower than
        | 'lte'  // lte : lower than or equal
        | 'in'   // in  : any value in a given list (value is a list)
        | 'nin'  // nin : any value not in a given list (value is a list)
        | 'has'  // has : list has a given value (for entity list attributes )
        | 'hasn' // hasn: list has not a given value (for entity list attributes )
        | 'lk'   // lk  : like or contains (may support widlcard '%')
        | 'nlk'  // nlk : not like or contains (may support widlcard '%')
        | 'btw'  // btw : value between two given values (value is a tuple [min, max]),    	

    /** description: value to filter by - depends on field type and operation **/
    "v": unknown,
}
```

### Filter example usage:

Basic usage:
```url
https://your-aplication.com?filters=[{"f":"first_name","o":"eq","v": "Steve"}]
```

Filter schema:
```json
[
    { "f":"first_name", "o":"eq", "v": "Steve" }
]
```

Multiple filters:
```json
[
    { "f":"name", "o":"eq", "v": "Steve" },
    { "f":"code", "o":"eq", "v": 55 }
]
```

Specific filter types:
```json
[
    { "f":"first_name", "o":"eq",  "v": "Steve" },
    { "f":"last_name",  "o":"neq", "v": "Jobs" },
    { "f":"age",        "o":"btw", "v": [10, 50] },
    { "f":"city",       "o":"in",  "v": ["São Paulo", "New York"] }
]
```

### Query Engine:

A request like this:
```url
    ?filter=[
        {f:'fieldA', o:'eq' ,v:10},
        {f:'fieldB', o:'lt' ,v:100},
        {f:'fieldC', o:'btw',v:[50,100]},
        {f:'fieldD', o:'lk' ,v:'del%'},
        {f:'fieldE', o:'in' ,v:['BRT','MX','USA']},
    ]
```

Internally produces a SQL query like this:
```sql
    WHERE fieldA = 10
        AND fieldB < 100
        AND fieldC BETWEEN 50 AND 100
        AND fieldD LIKE 'del%'
        AND fieldE IN ('BRT','MX','USA')
```


## Sorting
#### [GENERIC_REQUEST_SORT]
Just like the filter attribute to define query conditions, you can also send the sort attribute to define the order of the query result.

```javascript
{
    /** description: field to filter by **/
    "f": string,

    /** description: operation to be applied **/
    /** default: 'eq' **/
    "o"?:
        | 'asc'   // ascending sort
        | 'desc'  // desceding sort
}
```

### Sort example usage:

Basic usage:
```url
https://your-aplication.com?sort=[{"f":"name"}]
```

Sort schema:
```json
[
    { "f":"name" }
]
```
> NOTE: Since the o attribute was not passed, it will assume the default ascending sorting (asc).

Multiple sorting:
```json
[
    { "f":"name",      "o":"asc" },
    { "f":"birthday",  "o":"desc" },
    { "f":"last_seen", "o":"asc" },
]
```

## The `Filterable` Class
When decorating your class method with Filterable, you need to provide the respective Model for the query:

```python
from filterable import Filterable
from your_app.models import YourModel

class YourClass:
    @Filterable(YourModel)
    def get_users(self, _filtered):
        pass
```

Notice that the _filtered parameter has been injected into the decorated method. This parameter is of type dict and contains the queries and sorting created according to the arguments sent in the request to your API. Now you just need to incorporate it into your SQLAlchemy query:

```python
    @Filterable(YourModel)
    def get_users(self, _filtered):
        session = Session()
        users_query = self.session.query(YourModel).filter(
            _filtered.filter,
            YourModel.deleted === False
        ).order_by(*_filtered.sort)

        return users_query.all(), 200
```
> NOTE: You can still add other custom conditions to the query while incorporating the conditions that Filterable created.
> NOTE: It is necessary to unpack (*) the sorting data.

### Handling Pagination
Additionally, `Filterable` supports pagination. It handles and applies the pagination information received in the request and returns a pattern that is easy to implement for front-end clients.

Example Usage:
```python
from filterable import Filterable, paginate
from your_app.models import YourModel

class YourClass:
    @Filterable(YourModel)
    def get_users(self, _filtered):
        users_query = session().query(YourModel).filter(
            _filtered.filter,
            YourModel.deleted === False
        ).order_by(*_filtered.sort)

        return paginate(users_query), 200
```

When making a call to this endpoint, you will receive the following response:

```json
{
    "page": 1,
    "pageSize": 15,
    "rows": [],
    "totalRows": 265,
}
```

Summary:
| Parameter | Type | Description |
|-----------|------|-----------|
| page | ``int`` | Current page |
| pageSize | ``int`` | Number of items displayed per page |
| rows | ``list`` | List of entities (models) returned in the query |
| totalRows | ``int`` | Total number of items that this query returns |

## License
MIT (LICENSE)

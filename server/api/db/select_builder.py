from werkzeug.exceptions import BadRequest
from typing import Iterable
from sqlalchemy.orm import Session, Query

import logging


def select(session: Session, columns: Iterable, column_mapping: dict, join_mapping: dict=None,
           join_tables: dict=None, item_name: str="show") -> Query:
    args = []
    joins = set()

    for column in columns:
        if column in column_mapping:
            args.append(column_mapping[column])
        else:
            raise BadRequest("Bad '%s' value '%s'. Can be one of '%s'." %
                             (item_name, column, ", ".join(column_mapping.keys())))

        if join_mapping is not None and column in join_mapping:
            joins = joins.union(join_mapping[column])

    query = session.query(*args)

    for join_name in joins:
        join = join_tables[join_name]
        if hasattr(join, "__iter__"):
            query = query.outerjoin(*join)
        else:
            query = query.outerjoin(join)

    return query

import asyncio
import dataclasses
import inspect
import random
import time
from contextlib import AbstractContextManager
from enum import Enum
from functools import wraps
from typing import (
    AbstractSet,
    Any,
    Callable,
    Deque,
    Dict,
    FrozenSet,
    List,
    Mapping,
    MutableMapping,
    MutableSet,
    Set,
    Type,
    TypeVar,
    Union,
    cast,
)

from spanlib.common.exceptions import DataClassConversionError

T = TypeVar("T")

# Decorators to preserve function signature using this pattern:
# https://github.com/python/mypy/issues/1927
FuncT = TypeVar("FuncT", bound=Callable[..., Any])


class reraise(AbstractContextManager):
    """
    Context manager to reraise one exception from another
    """

    def __init__(self, exc_a: Type[BaseException], exc_b: Type[Exception], **kwargs):
        self.exc_a = exc_a
        self.exc_b = exc_b
        self.kwargs = kwargs

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type and issubclass(exc_type, self.exc_a):
            raise self.exc_b(**self.kwargs) from exc_value

    def __call__(self, func: FuncT) -> FuncT:
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_decorated(*args, **kwargs):
                with self:
                    return await func(*args, **kwargs)

            return cast(FuncT, async_decorated)

        @wraps(func)
        def decorated(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return cast(FuncT, decorated)


def retry_on_exception(  # noqa: C901
    exc: Union[Exception, Type[Exception]], wait: int, tries: int
):
    """
    Decorator to retry a function if an exception `exc` occurs.
    :param exc: Exception to catch.
    :param wait: Random wait between 0 and `wait` seconds between retries.
    :param tries: Number of retries. Set to -1 for infinite retries.
    """

    def decorator(func: FuncT) -> FuncT:
        if asyncio.iscoroutinefunction(func):

            @wraps(func)
            async def async_decorated(*args, **kwargs):
                attempt = tries
                while attempt != 0:
                    attempt -= 1
                    try:
                        return await func(*args, **kwargs)
                    except exc:
                        if attempt == 0:
                            raise
                    if wait:
                        await asyncio.sleep(random.random() * wait)

            return async_decorated  # type: ignore

        @wraps(func)
        def decorated(*args, **kwargs):
            attempt = tries
            while attempt != 0:
                attempt -= 1
                try:
                    return func(*args, **kwargs)
                except exc:
                    if attempt == 0:
                        raise
                if wait:
                    time.sleep(random.random() * wait)

        return decorated  # type: ignore

    return decorator


def as_dataclass(obj: Any, dataclass_: Type[T], **kwargs) -> T:
    """Cast object to a dataclass

    :param Any obj: Object to cast
    :param Type[T] dataclass_: Target dataclass
    :param kwargs: Fields => override values; will not override fields of nested dataclasses
    :raises DataClassConversionError: Failed to convert object to given type
    :return T: Casted object

    FIXME: [BDRK-326] Convert to an iterative solution to avoid stack overflow.
    FIXME: [BDRK-327] mypy complains that `cast_type` is being fed too many arguments
    """

    if not dataclasses.is_dataclass(dataclass_):
        raise DataClassConversionError(
            f"as_dataclass: Attempted to convert object {obj} to non-dataclass type {dataclass_}"
        )

    try:
        return _cast_object_to_type(obj=obj, type_=dataclass_, field_name="", **kwargs)
    except DataClassConversionError as ex:
        raise DataClassConversionError(
            f"Failed to convert obj={obj} to dataclass={dataclass_}"
        ) from ex


def _cast_object_to_type(obj: Any, type_: Type[T], field_name: str, **kwargs) -> T:
    """
    Helper function to convert an object to the given type.

    Notes on conversion:
    - If type_ is a Dataclass, conversion uses duck typing by recursing on the field.
    - If type_ is an enum, conversion succeeds if the enum object can be initialised using
      the field value.
    - If type_ is a Union, conversion is attempted for each of the type parameters,
      in the same order as the Union definition (nested Unions are flattened). The first
      successful conversion is returned.
    - If type_ is some other Generic (e.g. List[T], Dict[T, U]), recursively check the type
      parameters and perform conversion. User defined generics are not supported.
    - For other types_, conversion succeeds if isinstance(value, type_) is True.
    - kwarg overrides are type checked against type_ for the top level object only.

    :param Any obj: Object to cast
    :param Type[T] type_: Field type
    :param str field_name: Field name for debugging purposes
    :param kwargs: Fields => override values; will not override fields of nested dataclasses
    :raises DataClassConversionError: Failed to convert field to given type
    :return T: Casted object
    """

    # NOTE: some generic dictionary types from the typing package, ie. typing.Counter,
    # typing.DefaultDict, typing.OrderedDict, typing.ChainMap, etc. are not supported.
    # Please use their respective aliased types found in collections package as type hints.
    if type_ is Any or type(type_) is TypeVar:
        # Handle unspecialized generic type
        return obj
    elif not hasattr(type_, "__origin__") and isinstance(obj, type_):
        # We can only call isinstance on non-generic types
        return obj
    elif dataclasses.is_dataclass(type_):
        return _cast_object_to_dataclass(obj=obj, type_=type_, field_name=field_name, **kwargs)
    elif hasattr(type_, "__origin__"):
        # NOTE: __origin__ is the best way to get the original type for now:
        # https://github.com/python/typing/issues/136#issuecomment-138392956
        return _cast_object_to_generic_class(obj=obj, type_=type_, field_name=field_name)
    if issubclass(type_, Enum):
        try:
            # mypy error: Incompatible return value type (got "Enum", expected "T")
            return type_(obj)  # type: ignore
        except ValueError as ex:
            raise DataClassConversionError(
                f"_cast_object_to_type: Could not convert field_name={field_name}, object={obj} "
                f"to enum={type_} with kwargs={kwargs}"
            ) from ex
    else:
        # Consider handling other conversions by default, ie. str to float / str to UUID
        raise DataClassConversionError(
            f"_cast_object_to_type: Could not convert field_name={field_name}, object={obj} "
            f"to type={type_} with kwargs={kwargs}"
        )


def _cast_object_to_dataclass(obj: Any, type_: Type, field_name: str, **kwargs):
    temp = {}
    for field in dataclasses.fields(type_):
        field_value = _get_field_value(obj=obj, field_name=field.name, **kwargs)
        temp[field.name] = _cast_object_to_type(
            obj=field_value, type_=field.type, field_name=field.name
        )

    try:
        return type_(**temp)
    except TypeError as ex:
        raise DataClassConversionError(
            f"_cast_object_to_type: Could not convert field_name={field_name}, object={obj} to "
            f"dataclass={type_} with kwargs={kwargs} from_temp={temp}"
        ) from ex


# mypy error: "Type[Mapping[Any, Any]]" has no attribute "__origin__"
uniform_collection = [
    t.__origin__  # type: ignore
    for t in [Set, FrozenSet, AbstractSet, MutableSet, List, Deque]
]
# Current version of mypy (0.720) doesn't include new type hints defined in the typing package
# for python 3.7.4, such as OrderedDict, so disable type checking for now.
dictionary = [
    t.__origin__  # type: ignore
    for t in [Dict, Mapping, MutableMapping]
]


def _cast_object_to_generic_class(obj: Any, type_: Type, field_name: str, **kwargs):
    if type_.__origin__ is Union:
        return _cast_object_to_union(obj=obj, type_=type_, field_name=field_name)
    elif type_.__origin__ is tuple:
        return _cast_object_to_tuple(obj=obj, type_=type_, field_name=field_name)
    elif type_.__origin__ in uniform_collection:
        return _cast_object_to_collection(obj=obj, type_=type_, field_name=field_name)
    elif type_.__origin__ in dictionary:
        return _cast_object_to_dict(obj=obj, type_=type_, field_name=field_name)
    else:
        # Unsupported type conversion
        raise DataClassConversionError(
            f"_cast_object_to_type: Could not convert field_name={field_name}, object={obj} to "
            f"generic={type_} with kwargs={kwargs}"
        )


def _cast_object_to_union(obj: Any, type_: Type, field_name: str, **kwargs):
    for arg in type_.__args__:
        try:
            return _cast_object_to_type(obj=obj, type_=arg, field_name=field_name)
        except DataClassConversionError:
            continue

    value_type = type(obj)
    dict_repr = None
    if hasattr(obj, "__dict__"):
        dict_repr = obj.__dict__

    raise DataClassConversionError(
        f"_cast_object_to_type: Could not match any types for field_name={field_name}, "
        f"object=({obj}, {dict_repr}) of type={value_type} to target_type={type_} with "
        f"kwargs={kwargs}"
    )


def _cast_object_to_collection(obj: Any, type_: Type, field_name: str, **kwargs):
    if isinstance(obj, str) or isinstance(obj, bytes) or not hasattr(obj, "__iter__"):
        raise DataClassConversionError(
            f"_cast_object_to_type: Could not convert object={obj} to collection={type_} "
            f"with kwargs={kwargs}"
        )
    temp = [
        _cast_object_to_type(obj=v, type_=type_.__args__[0], field_name=field_name) for v in obj
    ]
    try:
        # There is no abstract collection type for list and deque
        return set(temp) if inspect.isabstract(type_.__origin__) else type_.__origin__(temp)
    except TypeError as ex:
        raise DataClassConversionError(
            f"_cast_object_to_type: Could not convert field_name={field_name}, object={obj} "
            f"to collection={type_} with kwargs={kwargs}"
        ) from ex


def _cast_object_to_tuple(obj: Any, type_: Type, field_name: str, **kwargs):
    if not hasattr(obj, "__len__") or len(obj) != len(type_.__args__):
        raise DataClassConversionError(
            f"_cast_object_to_type: Could not convert field_name={field_name}, object={obj} "
            f"to tuple={type_} with kwargs={kwargs}"
        )
    return type_.__origin__(
        _cast_object_to_type(obj=elem_value, type_=elem_type, field_name=field_name)
        for elem_value, elem_type in zip(obj, type_.__args__)
    )


def _cast_object_to_dict(obj: Any, type_: Type, field_name: str, **kwargs):
    if not hasattr(obj, "__getitem__"):
        raise DataClassConversionError(
            f"_cast_object_to_type: Could not convert field_name={field_name}, object={obj} "
            f"to dict={type_} with kwargs={kwargs}"
        )
    temp = {
        _cast_object_to_type(
            obj=k, type_=type_.__args__[0], field_name=field_name
        ): _cast_object_to_type(obj=v, type_=type_.__args__[1], field_name=field_name)
        for k, v in obj.items()
    }
    try:
        return temp if inspect.isabstract(type_.__origin__) else type_.__origin__(**temp)
    except TypeError as ex:
        raise DataClassConversionError(
            f"_cast_object_to_type: Could not convert field_name={field_name}, object={obj} "
            f"to dict={type_} with kwargs={kwargs}"
        ) from ex


def _get_field_value(obj: Any, field_name: str, **kwargs):
    # Try to get the value from the object
    if isinstance(obj, dict):
        field_value = obj.get(field_name, None)
    else:
        field_value = getattr(obj, field_name, None)
    # Replace it with kwargs if it is present
    return kwargs.get(field_name, field_value)

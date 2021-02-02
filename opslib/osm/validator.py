from typing import Any, Optional, Generic, get_origin, get_args, Union, List
from collections.abc import Iterable

__all__ = ["ValidationError", "Validator"]


class ValidationError(Exception):
    _message = "Error{} found in {}"

    def __init__(self, invalid: List[str], missing: List[str], extra: List[str]):
        self.invalid = invalid
        self.missing = missing
        self.extra = extra

    @property
    def message(self):
        error_attrs = []
        error_attrs.extend(self.invalid)
        error_attrs.extend(self.missing)
        error_attrs.extend(self.extra)
        return self._message.format(
            "s" if len(error_attrs) > 1 else "",
            " ".join(error_attrs),
        )


class Validator:
    def __init__(self, **data: Any):
        model_attributes = self.get_all_attributes()

        invalid_attributes = []
        missing_attributes = []
        extra_attributes = [key for key in data if key not in model_attributes]

        for attr_name, attr_type in model_attributes.items():
            optional = _is_optional_type(attr_type)
            type_to_check = _safe_get_type(attr_type)
            args_type = _safe_get_args(attr_type)

            data_value = data.get(attr_name)
            if not data_value and not optional:
                missing_attributes.append(attr_name)
            else:
                try:
                    _validate(data_value, type_to_check, args_type)
                except Exception as e:
                    invalid_attributes.append(attr_name)
                    continue
                self.__setattr__(attr_name, data_value)

        if invalid_attributes or missing_attributes or extra_attributes:
            raise ValidationError(
                invalid=invalid_attributes,
                missing=missing_attributes,
                extra=extra_attributes,
            )

    @classmethod
    def get_all_attributes(cls):
        return getattr(cls, "__dict__")["__annotations__"]

    @classmethod
    def get_mandatory_attributes(cls):
        mandatory_fields = []
        for attr_name, attr_type in cls.get_all_attributes().items():
            if not _is_optional_type(attr_type):
                mandatory_fields.append(attr_name)
        return mandatory_fields


def _safe_get_type(obj_type):
    if _is_optional_type(obj_type):
        return _safe_get_type(get_args(obj_type)[0])
    else:
        origin = get_origin(obj_type)
        return origin if origin is not None else obj_type


def _safe_get_args(obj_type):
    if _is_optional_type(obj_type):
        return _safe_get_args(get_args(obj_type)[0])
    else:
        return get_args(obj_type)


def _is_optional_type(obj_type):
    origin = get_origin(obj_type)
    args = get_args(obj_type)
    return origin == Union and len(args) == 2 and args[1] is type(None)


def _validate(data_value, type_to_check, args_type):
    if data_value:
        if not isinstance(data_value, type_to_check):
            raise Exception()
        elif args_type and isinstance(data_value, Iterable):
            for v in data_value:
                tuple_of_types = (
                    (type(v), type(data_value[v]))
                    if isinstance(data_value, dict)
                    else (type(v),)
                )
                if tuple_of_types != args_type:
                    raise Exception()

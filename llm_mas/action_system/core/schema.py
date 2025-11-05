"""Defines the schema for a dictionary."""

from typing import Any, Union, get_args, get_origin


def value_matches_type(value: Any, expected_type: Any) -> bool:  # noqa: ANN401, PLR0911
    """Recursively check if a value matches a (possibly generic) type."""
    origin = get_origin(expected_type)
    args = get_args(expected_type)

    # base case — simple type (int, str, float, etc.)
    if origin is None:
        return isinstance(value, expected_type)

    # handle Union[...] (e.g. str | int)
    if origin is Union:
        return any(value_matches_type(value, arg) for arg in args)

    # handle list[...] and tuple[...]
    if origin in (list, tuple):
        if not isinstance(value, origin):
            return False
        if not args:  # tuple or list with no specified types
            return True

        if origin is list:
            # e.g. list[int]  # noqa: ERA001
            return all(value_matches_type(v, args[0]) for v in value)

        # e.g. tuple[str, str]  # noqa: ERA001
        if len(value) != len(args):
            return False
        return all(value_matches_type(v, t) for v, t in zip(value, args, strict=True))

    # handle dict[K, V]
    if origin is dict:
        if not isinstance(value, dict):
            return False
        key_type, val_type = args
        return all(value_matches_type(k, key_type) and value_matches_type(v, val_type) for k, v in value.items())

    # fallback
    return isinstance(value, expected_type)


def type_to_str(tp: Any) -> str:  # noqa: ANN401
    """Convert a Python type (including generics) into a readable string."""
    origin = get_origin(tp)
    args = get_args(tp)

    if origin is None:
        # it's a simple type (like int, str, float)
        return tp.__name__ if hasattr(tp, "__name__") else str(tp)

    # it's a generic type like list[int] or tuple[str, str]
    args_str = ", ".join(type_to_str(a) for a in args)
    return f"{origin.__name__}[{args_str}]"


class DictSchema:
    """Defines a schema for a dictionary with specific properties."""

    def __init__(self, props: list["SchemaProp"] | None = None) -> None:
        """Initialize the schema with a list of properties."""
        self.props = props if props is not None else []

    def add_prop(self, prop: "SchemaProp") -> None:
        """Add a property to the schema."""
        self.props.append(prop)

    def get_props(self) -> list["SchemaProp"]:
        """Return the list of properties."""
        return self.props

    def get_prop_by_key(self, key: str) -> "SchemaProp | None":
        """Get the property by its key."""
        for prop in self.props:
            if prop.key == key:
                return prop
        return None

    def to_json_schema(self) -> dict[str, Any]:
        """Return the JSON schema representation of the schema."""
        return {
            "type": "object",
            "properties": {p.key: {"type": type_to_str(p.value_type)} for p in self.props},
            "required": [p.key for p in self.props if p.required],
        }

    def is_prop_required(self, key: str) -> bool:
        """Check if a property is required by its key."""
        prop = self.get_prop_by_key(key)
        return prop.required if prop is not None else False

    def has_prop(self, key: str) -> bool:
        """Check if the schema has a property by its key."""
        return self.get_prop_by_key(key) is not None

    def get_prop_type(self, key: str) -> type | None:
        """Get the type of a property by its key."""
        prop = self.get_prop_by_key(key)
        return prop.value_type if prop is not None else None

    def dict_satisfies_schema(self, data: dict[str, Any]) -> bool:
        """Check if a given dictionary satisfies the schema."""
        for prop in self.props:
            if prop.required and prop.key not in data:
                return False
            if prop.key in data and not value_matches_type(data[prop.key], prop.value_type):
                return False
        return True

    def get_default_values(self) -> dict[str, Any]:
        """Get a dictionary of default values for the properties."""
        defaults: dict[str, Any] = {}
        for prop in self.props:
            if prop.default is not None:
                defaults[prop.key] = prop.default
        return defaults

    def fill_defaults(self, data: dict[str, Any]) -> dict[str, Any]:
        """Mutate the given data dictionary to fill in default values for missing properties."""
        filled_data = data
        for prop in self.props:
            if prop.key not in filled_data and prop.default is not None:
                filled_data[prop.key] = prop.default
        return filled_data


class SchemaProp:
    """Defines a property in a schema."""

    def __init__(
        self,
        key: str,
        value_type: type,
        required: bool = False,  # noqa: FBT001, FBT002
        default: Any = None,  # noqa: ANN401
        description: str | None = None,
    ) -> None:
        """Initialize the schema property."""
        self.key = key
        self.value_type = value_type
        self.required = required
        self.default = default
        self.description = description

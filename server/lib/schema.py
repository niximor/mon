"""
JSONSchema Python bindings
"""

from typing import Dict, List, Union
from enum import Enum


class Type(Enum):
    """
    Data types.
    """
    String = "string"
    Integer = "integer"
    Number = "number"
    Object = "object"
    Array = "array"
    Boolean = "boolean"
    Null = "null"


class JsonSchema:
    """
    Base abstract class that should be used as base class for everything that can generate valid JSON Schema.
    """
    def __call__(self, update: dict=None) -> dict:
        raise NotImplementedError("You must explicitly implement %s.__call__." % (self.__class__.__name__, ))


class BaseType(JsonSchema):
    """
    Generic type specification.
    """
    def __init__(self, type_: Type=None, enum: List[any]=None, title: str=None, description: str=None,
                 default: any=None):
        """
        :param type_: Type specification.
        :param enum: The enum keyword is used to restrict a value to a fixed set of values. It must be an array with at
         least one element, where each element is unique.
        :param title: The title and description keywords must be strings. A “title” will preferably be short, whereas a
         “description” will provide a more lengthy explanation about the purpose of the data described by the schema.
         Neither are required, but they are encouraged for good practice.
        :param description: The title and description keywords must be strings. A “title” will preferably be short,
         whereas a “description” will provide a more lengthy explanation about the purpose of the data described by the
         schema. Neither are required, but they are encouraged for good practice.
        :param default: The default keyword specifies a default value for an item. JSON processing tools may use this
         information to provide a default value for a missing key/value pair, though many JSON schema validators simply
         ignore the default keyword. It should validate against the schema in which it resides, but that isn’t required.
        """
        self.type = type_
        self.enum = enum
        self.title = title
        self.description = description
        self.default = default

    def __call__(self, update: dict=None) -> dict:
        out = {}

        if update is not None:
            out.update(update)

        if self.type is not None:
            out["type"] = self.type.value

        if self.enum is not None:
            out["enum"] = self.enum

        if self.title is not None:
            out["title"] = self.title

        if self.description is not None:
            out["description"] = self.description

        if self.default is not None:
            out["default"] = self.default

        return out


class String(BaseType):
    """
    The string type is used for strings of text. It may contain Unicode characters.
    """
    def __init__(self, min_length: int=None, max_length: int=None, pattern: str=None, format: str=None,
                 enum: List[any]=None, title: str=None, description: str=None, default: any=None):
        """
        The string type is used for strings of text. It may contain Unicode characters.
        :param min_length: Minimum length of a string.
        :param max_length: Maximum length of a string.
        :param pattern: The pattern keyword is used to restrict a string to a particular regular expression.
        :param format_: The format keyword allows for basic semantic validation on certain kinds of string values that
         are commonly used. This allows values to be constrained beyond what the other tools in JSON Schema, including
         Regular Expressions can do.
         There is a bias toward networking-related formats in the JSON Schema specification, most likely due to its
         heritage in web technologies. However, custom formats may also be used, as long as the parties exchanging the
         JSON documents also exchange information about the custom format types. A JSON Schema validator will ignore any
         format type that it does not understand.
         The following is the list of formats specified in the JSON Schema specification.
            "date-time": Date representation, as defined by RFC 3339, section 5.6.
            "email": Internet email address, see RFC 5322, section 3.4.1.
            "hostname": Internet host name, see RFC 1034, section 3.1.
            "ipv4": IPv4 address, according to dotted-quad ABNF syntax as defined in RFC 2673, section 3.2.
            "ipv6": IPv6 address, as defined in RFC 2373, section 2.2.
            "uri": A universal resource identifier (URI), according to RFC3986.
        :param enum: The enum keyword is used to restrict a value to a fixed set of values. It must be an array with at
         least one element, where each element is unique.
        :param title: The title and description keywords must be strings. A “title” will preferably be short, whereas a
         “description” will provide a more lengthy explanation about the purpose of the data described by the schema.
         Neither are required, but they are encouraged for good practice.
        :param description: The title and description keywords must be strings. A “title” will preferably be short,
         whereas a “description” will provide a more lengthy explanation about the purpose of the data described by the
         schema. Neither are required, but they are encouraged for good practice.
        :param default: The default keyword specifies a default value for an item. JSON processing tools may use this
         information to provide a default value for a missing key/value pair, though many JSON schema validators simply
         ignore the default keyword. It should validate against the schema in which it resides, but that isn’t required.
        """
        super(String, self).__init__(Type.String, enum=enum, title=title, description=description, default=default)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = pattern
        self.format = format

    def __call__(self, update: dict=None) -> dict:
        out = {}

        if update is not None:
            out.update(update)

        if self.min_length is not None:
            out["minLength"] = self.min_length

        if self.max_length is not None:
            out["maxLength"] = self.max_length

        if self.pattern is not None:
            out["pattern"] = self.pattern

        if self.format is not None:
            out["format"] = self.format

        return super(String, self).__call__(out)


class NumberBase(BaseType):
    """
    Base type for numeric types.
    """
    def __init__(self, type_: Type, multiple_of: float=None, minimum: int=None, exclusive_minimum: bool=None,
                 maximum: int=None, exclusive_maximum: bool=None, enum: List[any]=None, title: str=None,
                 description: str=None, default: any=None):
        """
        :param multiple_of: Numbers can be restricted to a multiple of a given number, using the multipleOf keyword.
         It may be set to any positive number.
        :param minimum: minimum specifies a minimum numeric value.
        :param exclusive_minimum: exclusiveMinimum is a boolean. When true, it indicates that the range excludes the
         minimum value, i.e., x>minx>min. When false (or not included), it indicates that the range includes the
         minimum value, i.e., x≥minx≥min.
        :param maximum: maximum specifies a maximum numeric value.
        :param exclusive_maximum: exclusiveMaximum is a boolean. When true, it indicates that the range excludes the
         maximum value, i.e., x<maxx<max. When false (or not included), it indicates that the range includes the
         maximum value, i.e., x≤maxx≤max.
        :param enum: The enum keyword is used to restrict a value to a fixed set of values. It must be an array with at
         least one element, where each element is unique.
        :param title: The title and description keywords must be strings. A “title” will preferably be short, whereas a
         “description” will provide a more lengthy explanation about the purpose of the data described by the schema.
         Neither are required, but they are encouraged for good practice.
        :param description: The title and description keywords must be strings. A “title” will preferably be short,
         whereas a “description” will provide a more lengthy explanation about the purpose of the data described by the
         schema. Neither are required, but they are encouraged for good practice.
        :param default: The default keyword specifies a default value for an item. JSON processing tools may use this
         information to provide a default value for a missing key/value pair, though many JSON schema validators simply
         ignore the default keyword. It should validate against the schema in which it resides, but that isn’t required.
        """
        super(NumberBase, self).__init__(type_, enum=enum, title=title, description=description, default=default)

        self.type = type_
        self.multiple_of = multiple_of
        self.minimum = minimum
        self.exclusive_minimum = exclusive_minimum
        self.maximum = maximum
        self.exclusive_maximum = exclusive_maximum

    def __call__(self, update: dict=None) -> dict:
        out = {}

        if update is not None:
            out.update(update)

        if self.multiple_of is not None:
            out["multipleOf"] = self.multiple_of

        if self.minimum is not None:
            out["minimum"] = self.minimum

        if self.exclusive_minimum is not None:
            out["exclusiveMinimum"] = self.exclusive_minimum

        if self.maximum is not None:
            out["maximum"] = self.maximum

        if self.exclusive_maximum is not None:
            out["exclusiveMaximum"] = self.exclusive_maximum

        return super(NumberBase, self).__call__(out)


class Integer(NumberBase):
    """
    The integer type is used for integral numbers.
    """
    def __init__(self, multiple_of: float = None, minimum: int = None, exclusive_minimum: bool = None,
                 maximum: int = None, exclusive_maximum: bool = None, enum: List[any]=None, title: str=None,
                 description: str=None, default: any=None):
        """
        :param multiple_of: Numbers can be restricted to a multiple of a given number, using the multipleOf keyword.
         It may be set to any positive number.
        :param minimum: minimum specifies a minimum numeric value.
        :param exclusive_minimum: exclusiveMinimum is a boolean. When true, it indicates that the range excludes the
         minimum value, i.e., x>minx>min. When false (or not included), it indicates that the range includes the
         minimum value, i.e., x≥minx≥min.
        :param maximum: maximum specifies a maximum numeric value.
        :param exclusive_maximum: exclusiveMaximum is a boolean. When true, it indicates that the range excludes the
         maximum value, i.e., x<maxx<max. When false (or not included), it indicates that the range includes the
         maximum value, i.e., x≤maxx≤max.
        :param enum: The enum keyword is used to restrict a value to a fixed set of values. It must be an array with at
         least one element, where each element is unique.
        :param title: The title and description keywords must be strings. A “title” will preferably be short, whereas a
         “description” will provide a more lengthy explanation about the purpose of the data described by the schema.
         Neither are required, but they are encouraged for good practice.
        :param description: The title and description keywords must be strings. A “title” will preferably be short,
         whereas a “description” will provide a more lengthy explanation about the purpose of the data described by the
         schema. Neither are required, but they are encouraged for good practice.
        :param default: The default keyword specifies a default value for an item. JSON processing tools may use this
         information to provide a default value for a missing key/value pair, though many JSON schema validators simply
         ignore the default keyword. It should validate against the schema in which it resides, but that isn’t required.
        """
        super(Integer, self).__init__(Type.Integer, multiple_of, minimum, exclusive_minimum, maximum, exclusive_maximum,
                                      enum=enum, title=title, description=description, default=default)


class Number(NumberBase):
    """
    The integer type is used for integral numbers.
    """
    def __init__(self, multiple_of: float = None, minimum: float = None, exclusive_minimum: bool = None,
                 maximum: float = None, exclusive_maximum: bool = None, enum: List[any]=None, title: str=None,
                 description: str=None, default: any=None):
        """
        :param multiple_of: Numbers can be restricted to a multiple of a given number, using the multipleOf keyword.
         It may be set to any positive number.
        :param minimum: minimum specifies a minimum numeric value.
        :param exclusive_minimum: exclusiveMinimum is a boolean. When true, it indicates that the range excludes the
         minimum value, i.e., x>minx>min. When false (or not included), it indicates that the range includes the
         minimum value, i.e., x≥minx≥min.
        :param maximum: maximum specifies a maximum numeric value.
        :param exclusive_maximum: exclusiveMaximum is a boolean. When true, it indicates that the range excludes the
         maximum value, i.e., x<maxx<max. When false (or not included), it indicates that the range includes the
         maximum value, i.e., x≤maxx≤max.
        :param enum: The enum keyword is used to restrict a value to a fixed set of values. It must be an array with at
         least one element, where each element is unique.
        :param title: The title and description keywords must be strings. A “title” will preferably be short, whereas a
         “description” will provide a more lengthy explanation about the purpose of the data described by the schema.
         Neither are required, but they are encouraged for good practice.
        :param description: The title and description keywords must be strings. A “title” will preferably be short,
         whereas a “description” will provide a more lengthy explanation about the purpose of the data described by the
         schema. Neither are required, but they are encouraged for good practice.
        :param default: The default keyword specifies a default value for an item. JSON processing tools may use this
         information to provide a default value for a missing key/value pair, though many JSON schema validators simply
         ignore the default keyword. It should validate against the schema in which it resides, but that isn’t required.
        """
        super(Number, self).__init__(Type.Number, multiple_of, minimum, exclusive_minimum, maximum, exclusive_maximum,
                                     enum=enum, title=title, description=description, default=default)


class Schema(BaseType):
    """
    Schema is base for defining object and it's properties.
    """
    def __init__(self, properties: Dict[str, BaseType]=None, additional_properties: Union[bool, BaseType]=True,
                 required: List[str]=None, min_properties: int=None, max_properties: int=None,
                 dependencies: Dict[str, Union[List[str], "Schema"]]=None,
                 pattern_properties: Dict[str, BaseType]=None, enum: List[any]=None, title: str=None,
                 description: str=None, default: any=None):
        """
        :param properties: The properties (key-value pairs) on an object are defined using the properties keyword.
         The value of properties is an object, where each key is the name of a property and each value is a JSON schema
         used to validate that property.
        :param additional_properties: The additionalProperties keyword is used to control the handling of extra stuff,
         that is, properties whose names are not listed in the properties keyword. By default any additional properties
         are allowed.
         The additionalProperties keyword may be either a boolean or an object. If additionalProperties is a boolean
         and set to false, no additional properties will be allowed.
         If additionalProperties is an object, that object is a schema that will be used to validate any additional
         properties not listed in properties.
        :param required: By default, the properties defined by the properties keyword are not required. However, one
         can provide a list of required properties using the required keyword.
         The required keyword takes an array of one or more strings. Each of these strings must be unique.
        :param min_properties: The number of properties on an object can be restricted using the minProperties and
         maxProperties keywords. Each of these must be a non-negative integer.
        :param max_properties: The number of properties on an object can be restricted using the minProperties and
         maxProperties keywords. Each of these must be a non-negative integer.
        :param dependencies: The dependencies keyword allows the schema of the object to change based on the presence
         of certain special properties. There are two forms of dependencies in JSON Schema:
            * Property dependencies declare that certain other properties must be present if a given property is
              present.
            * Schema dependencies declare that the schema changes when a given property is present.
        :param pattern_properties: As we saw above, additionalProperties can restrict the object so that it either has
         no additional properties that weren’t explicitly listed, or it can specify a schema for any additional
         properties on the object. Sometimes that isn’t enough, and you may want to restrict the names of the extra
         properties, or you may want to say that, given a particular kind of name, the value should match a particular
         schema. That’s where patternProperties comes in: it is a new keyword that maps from regular expressions to
         schemas. If an additional property matches a given regular expression, it must also validate against the
         corresponding schema.
        :param enum: The enum keyword is used to restrict a value to a fixed set of values. It must be an array with at
         least one element, where each element is unique.
        :param title: The title and description keywords must be strings. A “title” will preferably be short, whereas a
         “description” will provide a more lengthy explanation about the purpose of the data described by the schema.
         Neither are required, but they are encouraged for good practice.
        :param description: The title and description keywords must be strings. A “title” will preferably be short,
         whereas a “description” will provide a more lengthy explanation about the purpose of the data described by the
         schema. Neither are required, but they are encouraged for good practice.
        :param default: The default keyword specifies a default value for an item. JSON processing tools may use this
         information to provide a default value for a missing key/value pair, though many JSON schema validators simply
         ignore the default keyword. It should validate against the schema in which it resides, but that isn’t required.
        """
        super(Schema, self).__init__(enum=enum, title=title, description=description, default=default)

        self.properties = properties
        self.additional_properties = additional_properties
        self.required = required
        self.min_properties = min_properties
        self.max_properties = max_properties
        self.dependencies = dependencies
        self.pattern_properties = pattern_properties

    def __call__(self, update: dict=None) -> dict:
        out = {}

        if update is not None:
            out.update(update)

        if self.properties is not None:
            out["properties"] = {
                name: property_def()
                for name, property_def in self.properties.items()
            }

        if self.additional_properties is not None:
            if isinstance(self.additional_properties, bool):
                out["additionalProperties"] = self.additional_properties
            else:
                out["additionalProperties"] = self.additional_properties()

        if self.required is not None:
            out["required"] = self.required

        if self.min_properties is not None:
            out["minProperties"] = self.min_properties

        if self.max_properties is not None:
            out["maxProperties"] = self.max_properties

        if self.dependencies is not None:
            out["dependencies"] = self.dependencies

        if self.pattern_properties is not None:
            out["patternProperties"] = self.pattern_properties

        return super(Schema, self).__call__(out)


class Object(Schema):
    """
    Objects are the mapping type in JSON. They map “keys” to “values”. In JSON, the “keys” must always be strings.
    Each of these pairs is conventionally referred to as a “property”.
    """
    def __init__(self, properties: Dict[str, BaseType]=None, additional_properties: Union[bool, BaseType]=True,
                 required: List[str]=None, min_properties: int=None, max_properties: int=None,
                 dependencies: Dict[str, Union[List[str], Schema]]=None,
                 pattern_properties: Dict[str, BaseType]=None, enum: List[any]=None, title: str=None,
                 description: str=None, default: any=None):
        """
        :param properties: The properties (key-value pairs) on an object are defined using the properties keyword.
         The value of properties is an object, where each key is the name of a property and each value is a JSON schema
         used to validate that property.
        :param additional_properties: The additionalProperties keyword is used to control the handling of extra stuff,
         that is, properties whose names are not listed in the properties keyword. By default any additional properties
         are allowed.
         The additionalProperties keyword may be either a boolean or an object. If additionalProperties is a boolean
         and set to false, no additional properties will be allowed.
         If additionalProperties is an object, that object is a schema that will be used to validate any additional
         properties not listed in properties.
        :param required: By default, the properties defined by the properties keyword are not required. However, one
         can provide a list of required properties using the required keyword.
         The required keyword takes an array of one or more strings. Each of these strings must be unique.
        :param min_properties: The number of properties on an object can be restricted using the minProperties and
         maxProperties keywords. Each of these must be a non-negative integer.
        :param max_properties: The number of properties on an object can be restricted using the minProperties and
         maxProperties keywords. Each of these must be a non-negative integer.
        :param dependencies: The dependencies keyword allows the schema of the object to change based on the presence
         of certain special properties. There are two forms of dependencies in JSON Schema:
            * Property dependencies declare that certain other properties must be present if a given property is
              present.
            * Schema dependencies declare that the schema changes when a given property is present.
        :param pattern_properties: As we saw above, additionalProperties can restrict the object so that it either has
         no additional properties that weren’t explicitly listed, or it can specify a schema for any additional
         properties on the object. Sometimes that isn’t enough, and you may want to restrict the names of the extra
         properties, or you may want to say that, given a particular kind of name, the value should match a particular
         schema. That’s where patternProperties comes in: it is a new keyword that maps from regular expressions to
         schemas. If an additional property matches a given regular expression, it must also validate against the
         corresponding schema.
        :param enum: The enum keyword is used to restrict a value to a fixed set of values. It must be an array with at
         least one element, where each element is unique.
        :param title: The title and description keywords must be strings. A “title” will preferably be short, whereas a
         “description” will provide a more lengthy explanation about the purpose of the data described by the schema.
         Neither are required, but they are encouraged for good practice.
        :param description: The title and description keywords must be strings. A “title” will preferably be short,
         whereas a “description” will provide a more lengthy explanation about the purpose of the data described by the
         schema. Neither are required, but they are encouraged for good practice.
        :param default: The default keyword specifies a default value for an item. JSON processing tools may use this
         information to provide a default value for a missing key/value pair, though many JSON schema validators simply
         ignore the default keyword. It should validate against the schema in which it resides, but that isn’t required.
        """
        super(Object, self).__init__(properties, additional_properties, required, min_properties, max_properties,
                                     dependencies, pattern_properties, enum, title, description, default)
        self.type = Type.Object


class ExplicitObject(Object):
    """
    Object that has additional_properties set to False, so all properties must be declared.
    """
    def __init__(self, properties: Dict[str, BaseType]=None,
                 required: List[str]=None, min_properties: int=None, max_properties: int=None,
                 dependencies: Dict[str, Union[List[str], Schema]]=None,
                 pattern_properties: Dict[str, BaseType]=None, enum: List[any]=None, title: str=None,
                 description: str=None, default: any=None):
        """
        :param properties: The properties (key-value pairs) on an object are defined using the properties keyword.
         The value of properties is an object, where each key is the name of a property and each value is a JSON schema
         used to validate that property.
        :param required: By default, the properties defined by the properties keyword are not required. However, one
         can provide a list of required properties using the required keyword.
         The required keyword takes an array of one or more strings. Each of these strings must be unique.
        :param min_properties: The number of properties on an object can be restricted using the minProperties and
         maxProperties keywords. Each of these must be a non-negative integer.
        :param max_properties: The number of properties on an object can be restricted using the minProperties and
         maxProperties keywords. Each of these must be a non-negative integer.
        :param dependencies: The dependencies keyword allows the schema of the object to change based on the presence
         of certain special properties. There are two forms of dependencies in JSON Schema:
            * Property dependencies declare that certain other properties must be present if a given property is
              present.
            * Schema dependencies declare that the schema changes when a given property is present.
        :param pattern_properties: As we saw above, additionalProperties can restrict the object so that it either has
         no additional properties that weren’t explicitly listed, or it can specify a schema for any additional
         properties on the object. Sometimes that isn’t enough, and you may want to restrict the names of the extra
         properties, or you may want to say that, given a particular kind of name, the value should match a particular
         schema. That’s where patternProperties comes in: it is a new keyword that maps from regular expressions to
         schemas. If an additional property matches a given regular expression, it must also validate against the
         corresponding schema.
        :param enum: The enum keyword is used to restrict a value to a fixed set of values. It must be an array with at
         least one element, where each element is unique.
        :param title: The title and description keywords must be strings. A “title” will preferably be short, whereas a
         “description” will provide a more lengthy explanation about the purpose of the data described by the schema.
         Neither are required, but they are encouraged for good practice.
        :param description: The title and description keywords must be strings. A “title” will preferably be short,
         whereas a “description” will provide a more lengthy explanation about the purpose of the data described by the
         schema. Neither are required, but they are encouraged for good practice.
        :param default: The default keyword specifies a default value for an item. JSON processing tools may use this
         information to provide a default value for a missing key/value pair, though many JSON schema validators simply
         ignore the default keyword. It should validate against the schema in which it resides, but that isn’t required.
        """
        super(ExplicitObject, self).__init__(properties, False, required, min_properties, max_properties,
                                             dependencies, pattern_properties, enum, title, description, default)


class Array(BaseType):
    """
    Arrays are used for ordered elements. In JSON, each element in an array may be of a different type.
    """
    def __init__(self, items: Union[BaseType, List[BaseType]]=None, additional_items: bool=None, min_items: int=None,
                 max_items: int=None, unique_items: bool=None, enum: List[any]=None, title: str=None,
                 description: str=None, default: any=None):
        """
        :param items: By default, the elements of the array may be anything at all. However, it’s often useful to
         validate the items of the array against some schema as well. This is done using the items and additionalItems
         keywords. There are two ways in which arrays are generally used in JSON:
            * List validation: a sequence of arbitrary length where each item matches the same schema.
              List validation is useful for arrays of arbitrary length where each item matches the same schema.
              For this kind of array, set the items keyword to a single schema that will be used to validate all of
              the items in the array.
            * Tuple validation: a sequence of fixed length where each item may have a different schema. In this usage,
              the index (or location) of each item is meaningful as to how the value is interpreted. (This usage is
              often given a whole separate type in some programming languages, such as Python’s tuple).
              To do this, we set the items keyword to an array, where each item is a schema that corresponds to each
              index of the document’s array. That is, an array where the first element validates the first element of
              the input array, the second element validates the second element of the input array, etc.
        :param additional_items: The additionalItems keyword controls whether it’s valid to have additional items in
         the array beyond what is defined in the schema. Here, we’ll reuse the example schema above, but set
         additionalItems to false, which has the effect of disallowing extra items in the array.
        :param min_items: The length of the array can be specified using the minItems and maxItems keywords. The value
         of each keyword must be a non-negative number. These keywords work whether doing List validation or Tuple
         validation.
        :param max_items: The length of the array can be specified using the minItems and maxItems keywords. The value
         of each keyword must be a non-negative number. These keywords work whether doing List validation or Tuple
         validation.
        :param unique_items: A schema can ensure that each of the items in an array is unique. Simply set the
         uniqueItems keyword to true.
        :param enum: The enum keyword is used to restrict a value to a fixed set of values. It must be an array with at
         least one element, where each element is unique.
        :param title: The title and description keywords must be strings. A “title” will preferably be short, whereas a
         “description” will provide a more lengthy explanation about the purpose of the data described by the schema.
         Neither are required, but they are encouraged for good practice.
        :param description: The title and description keywords must be strings. A “title” will preferably be short,
         whereas a “description” will provide a more lengthy explanation about the purpose of the data described by the
         schema. Neither are required, but they are encouraged for good practice.
        :param default: The default keyword specifies a default value for an item. JSON processing tools may use this
         information to provide a default value for a missing key/value pair, though many JSON schema validators simply
         ignore the default keyword. It should validate against the schema in which it resides, but that isn’t required.
        """
        super(Array, self).__init__(Type.Array, enum=enum, title=title, description=description, default=default)
        self.items = items
        self.additional_items = additional_items
        self.min_items = min_items
        self.max_items = max_items
        self.unique_items = unique_items

    def __call__(self, update: dict=None) -> dict:
        out = {}

        if update is not None:
            out.update(update)

        if self.items is not None:
            if isinstance(self.items, BaseType):
                out["items"] = self.items()
            elif isinstance(self.items, list):
                out["items"] = [item() for item in self.items]

        if self.additional_items is not None:
            out["additionalItems"] = self.additional_items

        if self.max_items is not None:
            out["maxItems"] = self.max_items

        if self.min_items is not None:
            out["minItems"] = self.min_items

        if self.unique_items is not None:
            out["uniqueItems"] = self.unique_items

        return super(Array, self).__call__(out)


class ExplicitArray(Array):
    """
    Array that has additionalItems set to False, so all items must be explicitly declared.
    """
    def __init__(self, items: Union[BaseType, List[BaseType]]=None, min_items: int=None, max_items: int=None,
                 unique_items: bool=None, enum: List[any]=None, title: str=None, description: str=None,
                 default: any=None):
        """
        :param items: By default, the elements of the array may be anything at all. However, it’s often useful to
         validate the items of the array against some schema as well. This is done using the items and additionalItems
         keywords. There are two ways in which arrays are generally used in JSON:
            * List validation: a sequence of arbitrary length where each item matches the same schema.
              List validation is useful for arrays of arbitrary length where each item matches the same schema.
              For this kind of array, set the items keyword to a single schema that will be used to validate all of
              the items in the array.
            * Tuple validation: a sequence of fixed length where each item may have a different schema. In this usage,
              the index (or location) of each item is meaningful as to how the value is interpreted. (This usage is
              often given a whole separate type in some programming languages, such as Python’s tuple).
              To do this, we set the items keyword to an array, where each item is a schema that corresponds to each
              index of the document’s array. That is, an array where the first element validates the first element of
              the input array, the second element validates the second element of the input array, etc.
        :param min_items: The length of the array can be specified using the minItems and maxItems keywords. The value
         of each keyword must be a non-negative number. These keywords work whether doing List validation or Tuple
         validation.
        :param max_items: The length of the array can be specified using the minItems and maxItems keywords. The value
         of each keyword must be a non-negative number. These keywords work whether doing List validation or Tuple
         validation.
        :param unique_items: A schema can ensure that each of the items in an array is unique. Simply set the
         uniqueItems keyword to true.
        :param enum: The enum keyword is used to restrict a value to a fixed set of values. It must be an array with at
         least one element, where each element is unique.
        :param title: The title and description keywords must be strings. A “title” will preferably be short, whereas a
         “description” will provide a more lengthy explanation about the purpose of the data described by the schema.
         Neither are required, but they are encouraged for good practice.
        :param description: The title and description keywords must be strings. A “title” will preferably be short,
         whereas a “description” will provide a more lengthy explanation about the purpose of the data described by the
         schema. Neither are required, but they are encouraged for good practice.
        :param default: The default keyword specifies a default value for an item. JSON processing tools may use this
         information to provide a default value for a missing key/value pair, though many JSON schema validators simply
         ignore the default keyword. It should validate against the schema in which it resides, but that isn’t required.
        """
        super(ExplicitArray, self).__init__(items, False, min_items, max_items, unique_items, enum, title,
                                            description, default)


class Boolean(BaseType):
    """
    The boolean type matches only two special values: true and false. Note that values that evaluate to true or false,
    such as 1 and 0, are not accepted by the schema.
    """
    def __init__(self, enum: List[any]=None, title: str=None, description: str=None, default: any=None):
        """
        :param enum: The enum keyword is used to restrict a value to a fixed set of values. It must be an array with at
         least one element, where each element is unique.
        :param title: The title and description keywords must be strings. A “title” will preferably be short, whereas a
         “description” will provide a more lengthy explanation about the purpose of the data described by the schema.
         Neither are required, but they are encouraged for good practice.
        :param description: The title and description keywords must be strings. A “title” will preferably be short,
         whereas a “description” will provide a more lengthy explanation about the purpose of the data described by the
         schema. Neither are required, but they are encouraged for good practice.
        :param default: The default keyword specifies a default value for an item. JSON processing tools may use this
         information to provide a default value for a missing key/value pair, though many JSON schema validators simply
         ignore the default keyword. It should validate against the schema in which it resides, but that isn’t required.
        """
        super(Boolean, self).__init__(Type.Boolean, enum=enum, title=title, description=description, default=default)


class Null(BaseType):
    """
    The null type is generally used to represent a missing value. When a schema specifies a type of null, it has only
    one acceptable value: null.
    """
    def __init__(self, enum: List[any]=None, title: str=None, description: str=None):
        """
        :param enum: The enum keyword is used to restrict a value to a fixed set of values. It must be an array with at
         least one element, where each element is unique.
        :param title: The title and description keywords must be strings. A “title” will preferably be short, whereas a
         “description” will provide a more lengthy explanation about the purpose of the data described by the schema.
         Neither are required, but they are encouraged for good practice.
        :param description: The title and description keywords must be strings. A “title” will preferably be short,
         whereas a “description” will provide a more lengthy explanation about the purpose of the data described by the
         schema. Neither are required, but they are encouraged for good practice.
        """
        super(Null, self).__init__(Type.Null, enum=enum, title=title, description=description)


class CompoundSchema(JsonSchema):
    """
    Compound schema is base class for joining schemas together. Do not instance it directly, instead, instance one
    of subclasses - AnyOf, AllOf, OneOf.
    """

    class Operation(Enum):
        """
        Compound operation.
        """
        AnyOf = "anyOf"
        AllOf = "allOf"
        OneOf = "oneOf"

    def __init__(self, op: Operation, *schemas: JsonSchema):
        """
        :param op: Combine operation.
        :param schemas:
        """
        self.op = op
        self.schemas = schemas

    def __call__(self, update: dict=None) -> dict:
        return {
            self.op.value: [schema() for schema in self.schemas]
        }


class AnyOf(CompoundSchema):
    """
    To validate against anyOf, the given data must be valid against any (one or more) of the given subschemas.
    """
    def __init__(self, *schemas: JsonSchema):
        super(AnyOf, self).__init__(CompoundSchema.Operation.AnyOf, *schemas)


class AllOf(CompoundSchema):
    """
    To validate against allOf, the given data must be valid against all of the given subschemas.
    """
    def __init__(self, *schemas: JsonSchema):
        super(AllOf, self).__init__(CompoundSchema.Operation.AllOf, *schemas)


class OneOf(CompoundSchema):
    """
    To validate against oneOf, the given data must be valid against exactly one of the given subschemas.
    """
    def __init__(self, *schemas: JsonSchema):
        super(OneOf, self).__init__(CompoundSchema.Operation.OneOf, *schemas)


class Not(JsonSchema):
    """
    The not keyword declares that a instance validates if it doesn’t validate against the given subschema.
    """
    def __init__(self, schema: JsonSchema):
        """
        :param schema: Schema to negate.
        """
        self.schema = schema

    def __call__(self, update: dict=None) -> dict:
        out = {}

        if update is not None:
            out.update(update)

        out["not"] = self.schema()

        return out

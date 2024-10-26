from typing import Any


# class DomainException(Exception):
#     pass
#
#
# class BusinessRuleValidationException(DomainException):
#     def __init__(self, rule):
#         self.rule = rule
#
#     def __str__(self):
#         return str(self.rule)


class EntityNotFoundException(Exception):
    def __init__(self, identifier: Any):

        message = f"Entity with {identifier} not found"
        super().__init__(message)
        self.identifier = identifier

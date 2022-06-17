# -*- coding: utf-8 -*-
"""Template tag to format the string filters to something human readable."""


# Standard Library
from ast import literal_eval

# 3rd-party
from django import template

register = template.Library()


def ast_literal_eval(value, key=None):
    """Turns a string into a dict."""
    eval_dict = literal_eval(value)
    if key:
        return eval_dict[key]
    return eval_dict


register.filter("literal_eval", ast_literal_eval)

import re
from typing import List
from collections import Counter
from luqum.visitor import TreeTransformer
from luqum.parser import parser, lexer
from luqum.auto_head_tail import auto_head_tail

from apps.constants import (
    FULL_TEXT_SEARCH_FIELD_NAME,
    DEFAULT_FIELD_OPERATOR,
    FIELD_GROUP_OPERATOR,
    NOT_OPERATOR,
    PLUS_OPERATOR,
    PROHIBIT_OPERATOR,
    LOW_CHAR,
    HIGH_CHAR,
    LuceneSyntaxEnum,
)


def get_node_lucene_syntax(node):
    """获取该节点lucene语法类型"""
    return node.__class__.__name__


class LuceneField(object):
    """Lucene解析出的Field类"""

    def __init__(
        self,
        pos: int = 0,
        field_name: str = "",
        field_type: str = "",
        operator: str = DEFAULT_FIELD_OPERATOR,
        field_value: str = "",
    ):
        self.pos = pos
        self.field_name = field_name
        self.field_type = field_type
        self.operator = operator
        self.field_value = field_value

    def to_dict(self) -> dict:
        return {
            "pos": self.pos,
            "field_name": self.field_name,
            "field_type": self.field_type,
            "operator": self.operator,
            "field_value": self.field_value,
        }


class LuceneParser(object):
    """lucene语法的解析类"""

    def __init__(self, keyword: str) -> None:
        self.keyword = keyword

    def parsing(self) -> List[LuceneField]:
        """解析lucene语法入口函数"""
        fields = self._get_method(self.keyword)
        if isinstance(fields, list):
            # 以下逻辑为同名字段增加额外标识符
            field_names = Counter([field["name"] for field in fields])
            if not field_names:
                return fields
            for field_name, cnt in field_names.items():
                if cnt > 1:
                    number = 1
                    for field in fields:
                        if field["name"] == field_name:
                            field["name"] = f"{field_name}({number})"
                            number += 1
            return fields
        else:
            return [fields]

    def _get_method(self, node):
        """获取解析方法"""
        node_type = get_node_lucene_syntax(node)
        method_name = "parsing_{}".format(node_type.lower())
        return getattr(self, method_name)(node)

    @staticmethod
    def parsing_word(node):
        """解析单词"""
        field = LuceneField(
            pos=node.pos,
            field_name=FULL_TEXT_SEARCH_FIELD_NAME,
            operator="~=",
            field_type=LuceneSyntaxEnum.WORD,
            field_value=node.value,
        )
        match = re.search(r"<=|>=|<|>", node.value)
        if match:
            operator = match.group(0)
            field.operator = operator
            field.field_value = node.value.split(operator)[-1]
        return field

    @staticmethod
    def parsing_phrase(node):
        """解析短语"""
        field = LuceneField(
            pos=node.pos,
            field_name=FULL_TEXT_SEARCH_FIELD_NAME,
            operator="=",
            field_type=LuceneSyntaxEnum.PHRASE,
            field_value=node.value,
        )
        return field

    def parsing_searchfield(self, node):
        """解析搜索字段"""
        field = LuceneField(pos=node.pos, field_name=node.name, field_type=LuceneSyntaxEnum.SEARCH_FIELD)
        new_field = self._get_method(node.expr)
        field.field_type = new_field.field_type
        field.operator = new_field.operator
        field.field_value = new_field.field_value
        return field

    @staticmethod
    def parsing_fieldgroup(node):
        """解析字段组"""
        field = LuceneField(
            pos=node.pos,
            field_type=LuceneSyntaxEnum.FIELD_GROUP,
            operator=FIELD_GROUP_OPERATOR,
            field_value=str(node.expr),
        )
        return field

    def parsing_group(self, node):
        """"""
        fields = []
        for children in node.children:
            children_fields = self._get_method(children)
            if isinstance(children_fields, list):
                fields.extend(children_fields)
            else:
                fields.append(children_fields)
        return fields

    @staticmethod
    def parsing_range(node):
        """"""
        field = LuceneField(pos=node.pos, field_type=LuceneSyntaxEnum.RANGE, field_value=str(node))
        field.operator = "{}{}".format(LOW_CHAR[node.include_low], HIGH_CHAR[node.include_high])
        return field

    @staticmethod
    def parsing_fuzzy(node):
        """"""
        field = LuceneField(
            pos=node.pos, operator=DEFAULT_FIELD_OPERATOR, field_type=LuceneSyntaxEnum.FUZZY, field_value=str(node)
        )
        return field

    @staticmethod
    def parsing_regex(node):
        """"""
        field = LuceneField(
            pos=node.pos, operator=DEFAULT_FIELD_OPERATOR, field_type=LuceneSyntaxEnum.REGEX, field_value=str(node)
        )
        return field

    def parsing_oroperation(self, node):
        """解析或操作"""
        fields = []
        for operand in node.operands:
            operand_fields = self._get_method(operand)
            if isinstance(operand_fields, list):
                fields.extend(operand_fields)
            else:
                fields.append(operand_fields)
        return fields

    def parsing_andoperation(self, node):
        """"""
        fields = []
        for operand in node.operands:
            operand_fields = self._get_method(operand)
            if isinstance(operand_fields, list):
                fields.extend(operand_fields)
            else:
                fields.append(operand_fields)
        return fields

    def parsing_not(self, node):
        """"""
        field = LuceneField(
            pos=node.pos,
            field_name=FULL_TEXT_SEARCH_FIELD_NAME,
            operator=NOT_OPERATOR,
            field_type=LuceneSyntaxEnum.NOT,
            field_value=self._get_method(node.a).field_value,
        )
        return field

    def parsing_plus(self, node):
        """"""
        field = LuceneField(
            pos=node.pos,
            field_name=FULL_TEXT_SEARCH_FIELD_NAME,
            operator=PLUS_OPERATOR,
            field_type=LuceneSyntaxEnum.PLUS,
            field_value=self._get_method(node.a).field_value,
        )
        return field

    def parsing_prohibit(self, node):
        """解析减号"""
        field = LuceneField(
            pos=node.pos,
            field_name=FULL_TEXT_SEARCH_FIELD_NAME,
            operator=PROHIBIT_OPERATOR,
            field_type=LuceneSyntaxEnum.PROHIBIT,
            field_value=self._get_method(node.a).field_value,
        )
        return field

    def parsing_unknownoperation(self, node):
        """解析未知操作"""
        raise Exception("Unknown operation: {}".format(str(node)))


class LuceneTransformer(TreeTransformer):
    """Lucene语句转换器"""

    def visit_search_field(self, node, context):
        """SEARCH_FIELD 类型转换"""
        if node.pos == context["pos"]:
            field_name = node.name
            value = context["value"]
            node = parser.parse(f"{field_name}: {value}", lexer=lexer)

        yield from self.generic_visit(node, context)

    def visit_word(self, node, context):
        """WORD 类型转换"""
        if node.pos == context["pos"]:
            node.value = str(context["value"])
        yield from self.generic_visit(node, context)

    def transform(self, keyword: str, params: list) -> str:
        """转换Lucene语句"""
        query_tree = parser.parse(keyword, lexer=lexer)
        for param in params:
            query_tree = self.visit(query_tree, param)
        return str(auto_head_tail(query_tree))

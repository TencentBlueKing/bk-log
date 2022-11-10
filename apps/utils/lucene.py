import re
from dataclasses import dataclass
from typing import List
from collections import Counter, deque

from luqum.exceptions import ParseSyntaxError, IllegalCharacterError
from luqum.visitor import TreeTransformer
from luqum.parser import parser, lexer
from luqum.auto_head_tail import auto_head_tail
from luqum.utils import UnknownOperationResolver

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
    WORD_RANGE_OPERATORS,
    BRACKET_DICT,
    UNEXPECTED_WORD_RE,
    UNEXPECTED_UNMATCHED_EXCEPTION,
    UNEXPECTED_RANGE_RE,
    ILLEGAL_CHARACTER_RE,
    MAX_RESOLVE_TIMES,
    UNEXPECTED_SINGLE_RANGE_RE,
)

from apps.exceptions import IllegalLuceneSyntaxException


def get_node_lucene_syntax(node):
    """获取该节点lucene语法类型"""
    return node.__class__.__name__


@dataclass
class LuceneField(object):
    """Lucene解析出的Field类"""

    pos: int = 0
    name: str = ""
    type: str = ""
    operator: str = DEFAULT_FIELD_OPERATOR
    value: str = ""


class LuceneParser(object):
    """lucene语法的解析类"""

    def __init__(self, keyword: str) -> None:
        self.keyword = keyword

    def parsing(self) -> List[LuceneField]:
        """解析lucene语法入口函数"""
        tree = parser.parse(self.keyword, lexer=lexer)
        fields = self._get_method(tree)
        if isinstance(fields, list):
            # 以下逻辑为同名字段增加额外标识符
            names = Counter([field.name for field in fields])
            if not names:
                return fields
            for name, cnt in names.items():
                if cnt > 1:
                    number = 1
                    for field in fields:
                        if field.name == name:
                            field.name = f"{name}({number})"
                            number += 1
            return fields

        return [fields]

    def inspect(self) -> dict:
        result = {"is_legal": False, "keyword": self.keyword, "message": ""}
        origin_keyword = self.keyword
        try:
            parser.parse(self.keyword, lexer=lexer)
        except Exception:
            resolve_result = LuceneResolver(self.keyword).resolve()
            if resolve_result["is_legal"]:
                self.keyword = resolve_result["keyword"]
            else:
                result["message"] = resolve_result["message"]
                return result

        try:
            self.parsing()
        except IllegalLuceneSyntaxException:
            resolver = UnknownOperationResolver()
            self.keyword = str(resolver(parser.parse(self.keyword, lexer=lexer)))

        if origin_keyword != self.keyword:
            result["is_legal"] = False
            result["keyword"] = self.keyword

        return result

    def _get_method(self, node):
        """获取解析方法"""
        node_type = get_node_lucene_syntax(node)
        method_name = "parsing_{}".format(node_type.lower())
        return getattr(self, method_name)(node)

    def parsing_word(self, node):
        """解析单词"""
        field = LuceneField(
            pos=node.pos,
            name=FULL_TEXT_SEARCH_FIELD_NAME,
            operator="~=",
            type=LuceneSyntaxEnum.WORD,
            value=node.value,
        )
        match = re.search(WORD_RANGE_OPERATORS, node.value)
        if match:
            operator = match.group(0)
            field.operator = operator
            field.value = node.value.split(operator)[-1]
        return field

    def parsing_phrase(self, node):
        """解析短语"""
        field = LuceneField(
            pos=node.pos,
            name=FULL_TEXT_SEARCH_FIELD_NAME,
            operator="=",
            type=LuceneSyntaxEnum.PHRASE,
            value=node.value,
        )
        return field

    def parsing_searchfield(self, node):
        """解析搜索字段"""
        field = LuceneField(pos=node.pos, name=node.name, type=LuceneSyntaxEnum.SEARCH_FIELD)
        new_field = self._get_method(node.expr)
        field.type = new_field.type
        field.operator = new_field.operator
        field.value = new_field.value
        return field

    def parsing_fieldgroup(self, node):
        """解析字段组"""
        field = LuceneField(
            pos=node.pos,
            type=LuceneSyntaxEnum.FIELD_GROUP,
            operator=FIELD_GROUP_OPERATOR,
            value="({})".format(str(node.expr)),
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

    def parsing_range(self, node):
        """"""
        field = LuceneField(pos=node.pos, type=LuceneSyntaxEnum.RANGE, value=str(node))
        field.operator = "{}{}".format(LOW_CHAR[node.include_low], HIGH_CHAR[node.include_high])
        return field

    def parsing_fuzzy(self, node):
        """"""
        field = LuceneField(pos=node.pos, operator=DEFAULT_FIELD_OPERATOR, type=LuceneSyntaxEnum.FUZZY, value=str(node))
        return field

    def parsing_regex(self, node):
        """"""
        field = LuceneField(pos=node.pos, operator=DEFAULT_FIELD_OPERATOR, type=LuceneSyntaxEnum.REGEX, value=str(node))
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
            name=FULL_TEXT_SEARCH_FIELD_NAME,
            operator=NOT_OPERATOR,
            type=LuceneSyntaxEnum.NOT,
            value=self._get_method(node.a).value,
        )
        return field

    def parsing_plus(self, node):
        """"""
        field = LuceneField(
            pos=node.pos,
            name=FULL_TEXT_SEARCH_FIELD_NAME,
            operator=PLUS_OPERATOR,
            type=LuceneSyntaxEnum.PLUS,
            value=self._get_method(node.a).value,
        )
        return field

    def parsing_prohibit(self, node):
        """解析减号"""
        field = LuceneField(
            pos=node.pos,
            name=FULL_TEXT_SEARCH_FIELD_NAME,
            operator=PROHIBIT_OPERATOR,
            type=LuceneSyntaxEnum.PROHIBIT,
            value=self._get_method(node.a).value,
        )
        return field

    def parsing_unknownoperation(self, node):
        """解析未知操作"""
        raise IllegalLuceneSyntaxException()


class LuceneTransformer(TreeTransformer):
    """Lucene语句转换器"""

    def visit_search_field(self, node, context):
        """SEARCH_FIELD 类型转换"""
        if node.pos == context["pos"]:
            name, value = node.name, context["value"]
            if get_node_lucene_syntax(node.expr) == LuceneSyntaxEnum.WORD:
                operator = LuceneParser(keyword=str(node)).parsing()[0].operator
                if operator in WORD_RANGE_OPERATORS:
                    node = parser.parse(f"{name}: {operator}{value}", lexer=lexer)
                else:
                    node = parser.parse(f"{name}: {value}", lexer=lexer)
            else:
                node = parser.parse(f"{name}: {value}", lexer=lexer)

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


class LuceneResolver(object):
    """Lucene错误语句转换器"""

    def __init__(self, keyword: str) -> None:
        self.keyword = keyword

    def resolve(self) -> dict:
        result = {"is_legal": False, "keyword": self.keyword, "message": ""}
        # resolve_range 放这里是因为SearchField类型解析错误的range格式会解析成 unexpected 'TO'
        # resolve_range 里会一次性把所有的异常Range语法都转换成功
        self.resolve_range()
        # 最多执行 MAX_RESOLVE_TIMES 次转换
        for i in range(MAX_RESOLVE_TIMES):
            once_result = self.resolve_once()
            if isinstance(once_result, Exception):
                result["message"] = str(once_result)
                break
            if once_result:
                result["is_legal"] = True
                result["keyword"] = self.keyword
                break

        return result

    def resolve_once(self):
        """解析异常"""
        try:
            parser.parse(self.keyword, lexer=lexer)
            return True
        except ParseSyntaxError as e:
            if str(e) == UNEXPECTED_UNMATCHED_EXCEPTION:
                self.resolve_colon()
                self.resolve_bracket()
                return False
            match = re.search(UNEXPECTED_WORD_RE, str(e))
            if match:
                self.resolve_unexpected_word(match)
                return False
            # 此时抛出异常是因为这种情况语句已经没办法转换了
            raise Exception(f"无法转换的语句: {self.keyword}")
        except IllegalCharacterError as e:
            match = re.search(ILLEGAL_CHARACTER_RE, str(e))
            if match:
                self.resolve_unexpected_word(match)
            return False
        except Exception:
            raise Exception(f"无法转换的语句: {self.keyword}")

    def resolve_unexpected_word(self, match):
        """修复异常单词"""
        unexpect_word_len = len(match[1])
        position = int(str(match[2]))
        self.keyword = self.keyword[:position] + self.keyword[position + unexpect_word_len :]

    def resolve_colon(self):
        """修复异常的:"""
        if self.keyword.find(":") == len(self.keyword) - 1:
            self.keyword = self.keyword[:-1]

    def resolve_range(self):
        """修复Range语法"""
        # 可能存在多个非法Range语法
        match_groups = []
        p = re.compile(UNEXPECTED_RANGE_RE)
        for m in p.finditer(self.keyword):
            match_groups.append([m.start(), m.end()])

        remain_keyword = []
        for i in range(len(match_groups)):
            if i == 0:
                remain_keyword.append(self.keyword[: match_groups[i][0]])
            else:
                remain_keyword.append(self.keyword[match_groups[i - 1][1] : match_groups[i][0]])
            # 进行单个Range语法的修复
            match = re.search(UNEXPECTED_SINGLE_RANGE_RE, self.keyword[match_groups[i][0] : match_groups[i][1]])
            if match:
                start = match.group(1).strip()
                end = match.group(2).strip()
                if start and end:
                    continue
                if not start:
                    start = "*"
                if not end:
                    end = "*"
                remain_keyword.append(f"[{start} TO {end}]")

            if i == len(match_groups) - 1:
                remain_keyword.append(self.keyword[match_groups[i][1] :])

        self.keyword = "".join(remain_keyword)

    def resolve_bracket(self):
        """修复括号不匹配"""
        s = deque()
        for index in range(len(self.keyword)):
            symbol = self.keyword[index]
            # 左括号入栈
            if symbol in BRACKET_DICT.keys():
                s.append({"symbol": symbol, "index": index})
                continue
            if symbol in BRACKET_DICT.values():
                if s and symbol == BRACKET_DICT.get(s[-1]["symbol"], ""):
                    # 右括号出栈
                    s.pop()
                    continue
                s.append({"symbol": symbol, "index": index})
                # 如果栈首尾匹配, 则异常的括号是栈顶向下第二个
                if s[-1]["symbol"] == BRACKET_DICT.get(s[0]["symbol"], ""):
                    self.keyword = self.keyword[: s[-2]["index"]] + self.keyword[s[-2]["index"] + 1 :]
                # 否则异常的括号是栈顶元素
                else:
                    self.keyword = self.keyword[: s[-1]["index"]] + self.keyword[s[-1]["index"] + 1 :]
                return

        if s:
            self.keyword = self.keyword[: s[-1]["index"]] + self.keyword[s[-1]["index"] + 1 :]

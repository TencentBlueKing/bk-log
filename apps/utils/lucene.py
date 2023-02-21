import re
from dataclasses import dataclass, asdict
from typing import List
from collections import Counter, deque

from luqum.exceptions import ParseSyntaxError, IllegalCharacterError
from luqum.visitor import TreeTransformer
from luqum.parser import parser, lexer
from luqum.auto_head_tail import auto_head_tail
from luqum.utils import UnknownOperationResolver
from django.utils.translation import ugettext_lazy as _

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
    MAX_RESOLVE_TIMES,
)

from apps.exceptions import UnknownLuceneOperatorException
from apps.log_databus.constants import TargetNodeTypeEnum
from apps.log_search.constants import DEFAULT_BK_CLOUD_ID, OperatorEnum


def get_node_lucene_syntax(node):
    """获取该节点lucene语法类型"""
    return node.__class__.__name__


@dataclass
class LuceneField(object):
    """Lucene解析出的Field类"""

    pos: int = 0
    name: str = ""
    # 此处type为Lucene语法的type
    type: str = ""
    operator: str = DEFAULT_FIELD_OPERATOR
    value: str = ""
    # 标识是否为全文检索字段
    is_full_text_field: bool = False
    # 标识同名字段出现的次数
    repeat_count: int = 0


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
                            field.repeat_count = number
                            number += 1
            return fields

        return [fields]

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
            operator=DEFAULT_FIELD_OPERATOR,
            type=LuceneSyntaxEnum.WORD,
            value=node.value,
            is_full_text_field=True,
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
            is_full_text_field=True,
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

    def parsing_proximity(self, node):
        """"""
        field = LuceneField(
            pos=node.pos,
            name=FULL_TEXT_SEARCH_FIELD_NAME,
            operator=DEFAULT_FIELD_OPERATOR,
            type=LuceneSyntaxEnum.PROXIMITY,
            value=str(node),
            is_full_text_field=True,
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
            name=FULL_TEXT_SEARCH_FIELD_NAME,
            operator=NOT_OPERATOR,
            type=LuceneSyntaxEnum.NOT,
            value=self._get_method(node.a).value,
            is_full_text_field=True,
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
            is_full_text_field=True,
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
            is_full_text_field=True,
        )
        return field

    def parsing_unknownoperation(self, node):
        """解析未知操作"""
        raise UnknownLuceneOperatorException()


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


@dataclass
class InspectResult(object):
    is_legal: bool = True
    message: str = ""


class BaseInspector(object):
    """检查器基类"""

    syntax_error_message = ""

    def __init__(self, keyword: str):
        self.keyword = keyword
        self.result = InspectResult()

    def get_result(self):
        return self.result

    def set_illegal(self):
        """设置检查结果为非法"""
        self.result.is_legal = False
        self.result.message = self.syntax_error_message

    def inspect(self):
        """检查"""
        raise NotImplementedError

    def remove_unexpected_character(self, match):
        """根据RE match来移除异常字符"""
        unexpect_word_len = len(match[1])
        position = int(str(match[2]))
        # "127.0.0.1 这种单个引号在开头的情况，需要移除引号
        if match[1].startswith('"') and not match[1].endswith('"'):
            self.keyword = self.keyword[:position] + self.keyword[position + 1 :]
            return
        if match[1].startswith("'") and not match[1].endswith("'"):
            self.keyword = self.keyword[:position] + self.keyword[position + 1 :]
            return
        self.keyword = self.keyword[:position] + self.keyword[position + unexpect_word_len :]
        self.keyword = self.keyword.strip()

    def replace_unexpected_character(self, pos: int, char: str):
        """替换字符"""
        self.keyword[pos] = char


class ChinesePunctuationInspector(BaseInspector):
    """中文引号转换"""

    syntax_error_message = _("中文标点异常")

    chinese_punctuation_re = r"(“.*?”)"

    def inspect(self):
        p = re.compile(self.chinese_punctuation_re)
        match_groups = [m for m in p.finditer(self.keyword)]
        if not match_groups:
            return
        for m in p.finditer(self.keyword):
            self.replace_unexpected_character(m.start(), '"')
            self.replace_unexpected_character(m.end(), '"')
        self.set_illegal()


class IllegalCharacterInspector(BaseInspector):
    """非法字符检查"""

    syntax_error_message = _("异常字符")

    # 非法字符正则
    illegal_character_re = r"Illegal character '(.*)' at position (\d+)"
    # 非预期字符正则
    unexpect_word_re = r"Syntax error in input : unexpected  '(.*)' at position (\d+)"

    def inspect(self):
        try:
            parser.parse(self.keyword, lexer=lexer)
        except IllegalCharacterError as e:
            match = re.search(self.illegal_character_re, str(e))
            if match:
                self.remove_unexpected_character(match)
                self.set_illegal()
        except ParseSyntaxError as e:
            match = re.search(self.unexpect_word_re, str(e))
            if match:
                self.remove_unexpected_character(match)
                self.set_illegal()
        except Exception:
            return


class IllegalRangeSyntaxInspector(BaseInspector):
    """非法RANGE语法检查"""

    syntax_error_message = _("非法RANGE语法")

    # RANGE语法正则
    range_re = r":[\s]?[\[]?.*?TO.*"

    def inspect(self):
        try:
            parser.parse(self.keyword, lexer=lexer)
        except Exception:
            new_keyword = self.keyword
            for i in self.keyword.split("AND"):
                for keyword_slice in i.split("OR"):
                    match = re.search(self.range_re, keyword_slice)
                    if not match:
                        continue
                    match_range_str = match.string.split(":")[-1].strip()
                    new_match_range_str = match_range_str
                    if not new_match_range_str.startswith("["):
                        new_match_range_str = "[" + new_match_range_str
                    if not new_match_range_str.endswith("]"):
                        new_match_range_str = new_match_range_str + "]"
                    start, end = new_match_range_str[1:-1].split("TO")
                    start = start.strip()
                    end = end.strip()
                    if not start:
                        start = "*"
                    if not end:
                        end = "*"
                    new_range_str = f"[{start} TO {end}]"
                    new_keyword = new_keyword.replace(match_range_str, new_range_str).strip()

            if self.keyword != new_keyword:
                self.set_illegal()
            self.keyword = new_keyword


class IllegalBracketInspector(BaseInspector):
    """修复括号不匹配"""

    syntax_error_message = _("括号不匹配")
    # 非预期语法re
    unexpect_unmatched_re = (
        "Syntax error in input : unexpected end of expression (maybe due to unmatched parenthesis) at the end!"
    )

    def inspect(self):
        try:
            parser.parse(self.keyword, lexer=lexer)
        except ParseSyntaxError as e:
            if str(e) == self.unexpect_unmatched_re:
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
                        self.set_illegal()
                        return
                if not s:
                    return
                self.keyword = self.keyword[: s[-1]["index"]] + self.keyword[s[-1]["index"] + 1 :].strip()
                self.set_illegal()
        except Exception:
            return


class IllegalColonInspector(BaseInspector):
    """修复冒号不匹配"""

    syntax_error_message = _("多余的冒号")
    # 非预期语法re
    unexpect_unmatched_re = (
        "Syntax error in input : unexpected end of expression (maybe due to unmatched parenthesis) at the end!"
    )

    def inspect(self):
        try:
            parser.parse(self.keyword, lexer=lexer)
        except ParseSyntaxError as e:
            if str(e) == self.unexpect_unmatched_re:
                if self.keyword.find(":") == len(self.keyword) - 1:
                    self.keyword = self.keyword[:-1].strip()
                    self.set_illegal()
        except Exception:
            return


class IllegalOperatorInspector(BaseInspector):
    """修复非法运算符"""

    syntax_error_message = _("非法逻辑运算符(AND, OR, NOT)")
    unexpect_operators = ["AND", "OR", "NOT"]
    # 非预期语法re
    unexpect_unmatched_re = (
        "Syntax error in input : unexpected end of expression (maybe due to unmatched parenthesis) at the end!"
    )

    def inspect(self):
        try:
            parser.parse(self.keyword, lexer=lexer)
        except ParseSyntaxError as e:
            if str(e) != self.unexpect_unmatched_re:
                return
            for operator in self.unexpect_operators:
                if operator not in self.keyword:
                    continue
                _operator_pos = self.keyword.find(operator)
                if _operator_pos == len(self.keyword) - len(operator):
                    self.keyword = self.keyword[:_operator_pos].strip()
                    self.set_illegal()
                    # 单次修复
                    break
        except Exception:
            return


class UnknownOperatorInspector(BaseInspector):
    """修复未知运算符"""

    syntax_error_message = _("未知操作符")

    def inspect(self):
        try:
            parser.parse(self.keyword, lexer=lexer)
        except UnknownLuceneOperatorException:
            resolver = UnknownOperationResolver()
            self.keyword = str(resolver(parser.parse(self.keyword, lexer=lexer)))
            self.set_illegal()
        except Exception:
            return


class DefaultInspector(BaseInspector):
    """默认检查器, 用于最后检查语法错误是否被修复"""

    syntax_error_message = _("未知异常")

    def inspect(self):
        try:
            parser.parse(self.keyword, lexer=lexer)
            LuceneParser(keyword=self.keyword).parsing()
        except Exception:
            self.set_illegal()


class LuceneSyntaxResolver(object):
    """lucene语法检查以及修复器"""

    REGISTERED_INSPECTORS = [
        ChinesePunctuationInspector,
        # IllegalRangeInspector得放在前面是因为 RANGE 的语法会和 IllegalCharacterInspector 中的 TO 冲突
        IllegalRangeSyntaxInspector,
        IllegalCharacterInspector,
        IllegalColonInspector,
        IllegalBracketInspector,
        IllegalOperatorInspector,
        UnknownOperatorInspector,
        DefaultInspector,
    ]

    def __init__(self, keyword: str):
        self.keyword = keyword
        self.messages = []

    def inspect(self):
        messages = []
        for inspector_class in self.REGISTERED_INSPECTORS:
            inspector = inspector_class(self.keyword)
            inspector.inspect()
            self.keyword = inspector.keyword
            result = inspector.get_result()
            if not result.is_legal:
                messages.append(str(asdict(result)["message"]))
        if not messages:
            return True
        self.messages.extend(messages)

    def resolve(self):
        is_resolved = False
        for i in range(MAX_RESOLVE_TIMES):
            if self.inspect():
                is_resolved = True
                break
        self.messages = set(self.messages)
        if is_resolved and str(DefaultInspector.syntax_error_message) in self.messages:
            self.messages.remove(str(DefaultInspector.syntax_error_message))
        return {
            "is_legal": False if self.messages else True,
            "is_resolved": is_resolved,
            "message": "\n".join(self.messages),
            "keyword": self.keyword,
        }


def generate_query_string(params: dict) -> str:
    """生成查询字符串"""
    key_word = params.get("keyword", "")
    if key_word is None:
        key_word = ""
    query_string = key_word
    # 保留host_scopes相关逻辑是为了兼容旧版本
    host_scopes = params.get("host_scopes", {})
    target_nodes = host_scopes.get("target_nodes", [])

    if target_nodes:
        if host_scopes["target_node_type"] == TargetNodeTypeEnum.INSTANCE.value:
            query_string += " AND ({})".format(
                ",".join([f"{target_node['bk_cloud_id']}:{target_node['ip']}" for target_node in target_nodes])
            )
        elif host_scopes["target_node_type"] == TargetNodeTypeEnum.DYNAMIC_GROUP.value:
            dynamic_name_list = [str(target_node["name"]) for target_node in target_nodes]
            query_string += " AND (dynamic_group_name:" + ",".join(dynamic_name_list) + ")"
        else:
            first_node, *_ = target_nodes
            target_list = [str(target_node["bk_inst_id"]) for target_node in target_nodes]
            query_string += f" AND ({first_node['bk_obj_id']}:" + ",".join(target_list) + ")"

    if host_scopes.get("modules"):
        modules_list = [str(_module["bk_inst_id"]) for _module in host_scopes["modules"]]
        query_string += " AND (modules:" + ",".join(modules_list) + ")"
        host_scopes["target_node_type"] = TargetNodeTypeEnum.TOPO.value
        host_scopes["target_nodes"] = host_scopes["modules"]

    if host_scopes.get("ips"):
        query_string += " AND (ips:" + host_scopes["ips"] + ")"
        host_scopes["target_node_type"] = TargetNodeTypeEnum.INSTANCE.value
        host_scopes["target_nodes"] = [
            {"ip": ip, "bk_cloud_id": DEFAULT_BK_CLOUD_ID} for ip in host_scopes["ips"].split(",")
        ]

    ipchooser = params.get("ip_chooser", {})
    for node_type, node_value in ipchooser.items():
        if node_type == "host_list":
            _host_slice = []
            _host_id_slice = []
            for _node in node_value:
                if _node.get("id"):
                    _host_id_slice.append(str(_node["id"]))
                    continue
                # 这里key值是参考了format_hosts方法的返回值
                _host_slice.append(f"{_node['cloud_area']['id']}:{_node['ip']}")
            # 分开以便于前端展示
            query_string += " AND (host_id: " + ",".join(_host_id_slice) + " AND (host: " + ",".join(_host_slice) + ")"
        elif node_type == "node_list":
            for _node in node_value:
                query_string += " AND ({}: {})".format(_node["object_id"], _node["instance_id"])
        else:
            node_type_name = node_type.split("_list")[0].lower()
            query_string += " AND ({}: {})".format(node_type_name, ",".join([str(i["id"]) for i in node_value]))

    additions = params.get("addition", [])
    if additions:
        str_additions = []
        for addition in additions:
            if addition["operator"] in [OperatorEnum.IS_TRUE["operator"], OperatorEnum.IS_FALSE["operator"]]:
                str_additions.append(f'{addition["field"]} {addition["operator"]}')
            else:
                str_additions.append(f'{addition["field"]} {addition["operator"]} {addition["value"]}')

        query_string += " AND (" + " AND ".join(str_additions) + ")"
    return query_string

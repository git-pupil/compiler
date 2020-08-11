import pprint


class TreeNode:
    '''
    语法树结点
    '''

    def __init__(self, id, parent, token_info=(True, None, 'e', None, None), statute_count=-1):
        self.id = id  # 唯一id
        self.parent = parent  # 父节点id
        self.child = []  # 存储子节点id

        self.is_terminal = token_info[0]  # 是否是终结符，即叶子节点，值为True或False
        self.value = token_info[1]  # 节点的值，即字符串，如'abcd'
        self.token = token_info[2]  # 记号，如id
        self.row = token_info[3]  # 终结符的行号
        self.column = token_info[4]  # 终结符的列号

        self.statute = statute_count  # 规约文法序号，非叶子节点必有规约文法，序号为 1 ~ 34;若为叶子节点，默认为-1；


class GrammarTree:
    '''
    语法树
    '''

    def __init__(self, start_token):
        self.grammar_tree = {0: TreeNode(0, None, (False, None, start_token, None, None), 1)}  # 存储语法树全部节点
        self.current_node = 0  # 当前节点 - 仅用于构建语法树，使用语法树时无需关注
        self.next_id = 1  # 当前可赋值给新节点的id - 语法树构建结束时，该值为节点个数，即 0 ~ next_id-1
        self.production = {  # Pascal语言 文法产生式 对应序号
            # 'S': 0,
            'programstruct': 1,
            'program_head': 2,
            'program_body': 3,
            'idlist': 4,
            'const_declarations': 5,
            'const_declaration': 6,
            'const_value': 7,
            'var_declarations': 8,
            'var_declaration': 9,
            'type': 10,
            'basic_type': 11,
            'period': 12,
            'subprogram_declarations': 13,
            'subprogram': 14,
            'subprogram_head': 15,
            'formal_parameter': 16,
            'parameter_list': 17,
            'parameter': 18,
            'var_parameter': 19,
            'value_parameter': 20,
            'subprogram_body': 21,
            'compound_statement': 22,
            'statement_list': 23,
            'statement': 24,
            'variable_list': 25,
            'variable': 26,
            'id_varpart': 27,
            'procedure_call': 28,
            'else_part': 29,
            'expression_list': 30,
            'expression': 31,
            'simple_expression': 32,
            'term': 33,
            'factor': 34
        }

    def insert_node(self, nodes):
        # 当前节点为e
        if not nodes:
            self.grammar_tree[self.next_id] = TreeNode(self.next_id, self.current_node)
            self.grammar_tree[self.current_node].child.append(self.next_id)
            self.next_id += 1

        # 添加节点
        for node in nodes:
            statute = -1 if node[0] else self.production.get(node[2])  # 规约文法序号
            self.grammar_tree[self.next_id] = TreeNode(self.next_id, self.current_node, node, statute)
            self.grammar_tree[self.current_node].child.append(self.next_id)
            self.next_id += 1

        # 自右向左、自下向上，寻找第一个非终结符符，作为下次插入的节点
        temp_id = self.next_id - 1
        if (not self.grammar_tree[temp_id].is_terminal):  # 如果产生式右部的最后一个符号为非终结符，则该非终结符就是当前节点
            self.current_node = temp_id
        else:  # 否则，就向左遍历，直到找到第一个产生式右部的非终结符
            while True:
                if (temp_id - 1) in self.grammar_tree[self.grammar_tree[temp_id].parent].child:  # 判断temp_id是否还有左兄弟节点
                    temp_id -= 1
                    if (not self.grammar_tree[temp_id].is_terminal):
                        self.current_node = temp_id
                        break
                else:  # 说明当前产生式的所有右部符号已经遍历，但无满足要求的符号可作为当前节点，则进入上一层
                    temp_id = self.grammar_tree[temp_id].parent
                    if temp_id == 0:  # 此时temp_id为根节点，而且说明该树的构造已完成
                        self.current_node = 0
                        break

    def output(self):
        print("语法树：")
        print("节点个数：" + str(len(self.grammar_tree)))
        print("节点属性：id，记号，字符串，父母id，孩子id，是否为叶子节点，行号，列号，该节点的规约文法序号（叶子节点无规约文法，默认为-1；文法与序号的对应关系见GrammarTree类的production属性）")
        for i in range(self.next_id):
            print('\tid =', self.grammar_tree[i].id, ', token =', self.grammar_tree[i].token,
                  ', value =', self.grammar_tree[i].value, ', parent =', self.grammar_tree[i].parent,
                  ', child :', self.grammar_tree[i].child, ', is_terminal =', self.grammar_tree[i].is_terminal,
                  ', row =', self.grammar_tree[i].row, ', column =', self.grammar_tree[i].column,
                  ', statute =', self.grammar_tree[i].statute)

    def find_child_node(self, node_id, child_pos):
        """
        返回TreeNode
        """
        return self.grammar_tree[self.grammar_tree[node_id].child[child_pos]]


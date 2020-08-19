# coding=utf-8
# from grammar_tree import *
from grammar_tree import GrammarTree
import pprint

"""" ==========================================================================
# _author_  = "李志成"
#
# 模块名： 语法分析模块
#
# 模块描述：
#    输入：一个word_analyse_result,其中的元素为list，里层list存储每个单词的信息
#    输出：语法树 + 错误信息
#
# 输入：word_analyse_result
# 输入示例
#   [
#       [True or False, 字符串, 字符串记号, 行, 列],
#       [True, 'program', 'program', '3', '5'],
#       [True, 'date', 'id', '7', '4'],
#       [True, '+', 'addop', '7', '9'],
#       [True, 'B_!as', 'error', '12', '3']
#   ]
#
# 输出：grammar_tree
# 输出示例
# 
# 
# 
# 步骤：
#   1.获取文法（'ε'用'e'代替）
#       '$'属于非终结符，'e'不属于非终结符
#   2.构造拓广文法
#   3.记录终结符，非终结符（不要漏掉$）
#   4.计算FIRST集
#   5.构造识别活前缀的项目集规范族
#       (1)构造闭包closure
#       (2)构造转移函数go
#		(3)合并展望符
#   6.产生LR1分析表
#   7.LR1动作分析
#	8.生成语法树
# 
# 
# 
# 外界可调用函数 grammar_analyse(word_analyse_result),详见外部函数块
=========================================================================== """


class GrammarAnalysis:
    '''
    语法分析
    '''

    def __init__(self):
        self.terminal_set = []  # 终结符
        self.non_terminal_set = []  # 非终结符
        self.charset = []  # 终结符+非终结符
        self.tokens = []    # 全部记号，list类型
        self.first_set = {}  # FIRST集
        self.closure = {}  # 闭包closure
        self.goto = {}  # 转移函数go
        self.table = {}  # LR1分析表
        self.stack_action=[]    # 对Pascal代码的分析动作
        self.reduce_nodes = []  # 规约结点
        self.status = []  # 项目规范集族
        '''项目规范集族格式
        [                           # 带活前缀的项目集规范族
            [                       # 一个有效项目集 I0，I1，...,In
                [                   # 项目集中的一个项目        [['S', '->', '~', 'programstruct'], ['$']]
                    [],             # 项目内容  ~代表圆点·      ['S', '->', '~', 'programstruct']
                    []              # 活前缀                   ['$']
                ]
            ]
        ]
        '''
        
        self.expanded_grammar=['S', '->', '~', 'programstruct']  # 开始文法
        self.accept_grammar=['S', '->', 'programstruct', '~']    # 结束文法
        self.begin_symbol='S' # 开始符号
        self.actions_record=[]  # 对符号串的分析动作记录
        # self.actions_record_simple=[]   # 对符号串的简单分析动作记录
        self.grammar_tree=None  # 语法树

        self.production = {  # Pascal语言 文法产生式
            # 'S': ['programstruct'],
            'programstruct': ['program_head ; program_body .'],
            'program_head': ['program id ( idlist )', 'program id'],
            'program_body': ['const_declarations var_declarations subprogram_declarations compound_statement'],
            'idlist': ['idlist , id', 'id'],
            'const_declarations': ['const const_declaration ;', 'e'],
            'const_declaration': ['const_declaration ; id assignop const_value', 'id assignop const_value'],
            'const_value': ['addop int_num', 'int_num', 'addop real_num', 'real_num', '\' letter \''],
            'var_declarations': ['var var_declaration ;', 'e'],
            'var_declaration': ['var_declaration ; idlist : type', 'idlist : type'],
            'type': ['basic_type', 'array [ period ] of basic_type'],
            'basic_type': ['integer', 'real', 'boolean', 'char'],
            'period': ['period ， int_num .. int_num', 'int_num .. int_num'],
            'subprogram_declarations': ['subprogram_declarations subprogram ;', 'e'],
            'subprogram': ['subprogram_head ; subprogram_body'],
            'subprogram_head': ['procedure id formal_parameter', 'function id formal_parameter : basic_type'],
            'formal_parameter': ['( parameter_list )', 'e'],
            'parameter_list': ['parameter_list ; parameter', 'parameter'],
            'parameter': ['var_parameter', 'value_parameter'],
            'var_parameter': ['var value_parameter'],
            'value_parameter': ['idlist : basic_type'],
            'subprogram_body': ['const_declarations var_declarations compound_statement'],
            'compound_statement': ['begin statement_list end'],
            'statement_list': ['statement_list ; statement', 'statement'],
            'statement': ['variable assignop expression', 'procedure_call', 'compound_statement',
                          'if expression then statement else_part',
                          'for id assignop expression to expression do statement', 'read ( variable_list )',
                          'write ( expression_list )', 'while expression do statement', 'e'],
            'variable_list': ['variable_list , variable', 'variable'],
            'variable': ['id id_varpart'],
            'id_varpart': ['[ expression_list ]', 'e'],
            'procedure_call': ['id', 'id ( expression_list )'],
            'else_part': ['else statement', 'e'],
            'expression_list': ['expression_list , expression', 'expression'],
            'expression': ['simple_expression relop simple_expression', 'simple_expression'],
            'simple_expression': ['simple_expression addop term', 'term'],
            'term': ['term mulop factor', 'factor'],
            'factor': ['int_num', 'real_num', 'variable', 'id ( expression_list )', '( expression )', 'not factor', 'uminus factor']
        }

    def run(self,tokens):  # 进行语法分析

        self.get_terminal_and_nonterminal_set()
        self.get_first_set()
        self.get_DFA()  # 产生自动机
        self.get_LR1_table()  # 产生LR1分析表
        self.get_tokens(tokens)  # 词法分析获取token
        self.LR1()  # 进行LR1分析
        self.get_analysis_tree()  # 生成语法树
        return self.grammar_tree


    def get_terminal_and_nonterminal_set(self):  # 获取终结符和非终结符
        # 获取非终结符
        self.non_terminal_set = sorted(list(set(self.production.keys())))

        # pp = pprint.PrettyPrinter(indent=4,width=190,compact=True)
        # print("非终结符：")
        # pp.pprint(self.non_terminal_set)

        # 获取终结符
        temp_set = set()
        for items in list(self.production.values()):  # 获取文法右半部分
            for item in items:
                for symbol in item.split():  # 获取所有文法符号
                    temp_set.add(symbol.strip())

        self.terminal_set = sorted(list(temp_set - set(self.non_terminal_set) - {'e'}))
        self.terminal_set.append('$')

        # print("终结符：")
        # pp.pprint(self.terminal_set)

        # 获取所有文法符号
        self.charset = self.non_terminal_set + self.terminal_set

        # print("所有文法符号：")
        # pp.pprint(self.charset)

    def is_increase(self, length):
        for nt in self.non_terminal_set:
            if length[nt] != len(self.first_set[nt]):
                return True
        return False

    def get_first_set(self):  # 获取FIRST集（不计算终结符的FIRST集）
        length = {}
        
        # 若文法第一个符号为终结符，则此处获取FIRST集
        # 若不是，则只进行初始化
        for nt in self.non_terminal_set:  # 添加终结符、e
            # 初始化
            self.first_set[nt]=set()
            length[nt] = 0

            # 遍历该非终结符的所有文法
            for prods in self.production.get(nt):
                # 提取该文法后半部分的第一个文法符号
                first_symbol = prods.split()[0].strip()
                # 若第一个str为终结符 或 e，加入FIRST集
                if first_symbol in self.terminal_set or first_symbol == 'e':
                    self.first_set[nt].add(first_symbol)

        # 若文法第一个符号为非终结符，则此处获取FIRST集
        while self.is_increase(length):  # 若FIRST集仍在增长
            for nt in self.non_terminal_set:  # 遍历所有非终结符
                length[nt] = len(self.first_set[nt])  # 更新length
                for prods in self.production.get(nt):  # 遍历非终结符的所有文法，更新FIRST集
                    # 提取该文法后半部分的str
                    symbols = [p.strip() for p in prods.split()]

                    # 若第一个str为非终结符
                    if symbols[0] in self.non_terminal_set:
                        self.first_set[nt] = self.first_set[nt] | (self.first_set[symbols[0]] - {'e'})

                        # 若前i+1个str为非终结符，且前i个非终结符的FIRST集包含e
                        i = 1
                        while i < len(symbols) and symbols[i] in self.non_terminal_set and 'e' in self.first_set[symbols[i - 1]]:
                            self.first_set[nt] = self.first_set[nt] | (self.first_set[symbols[i]] - {'e'})
                            i += 1

                        # 若全部str为非终结符
                        if i == len(symbols) and 'e' in self.first_set[symbols[i - 1]]:
                            self.first_set[nt].add('e')

        # print("FIRST集：")
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(self.first_set)

    def get_first_set_of_sentence(self, sentence):  # 从句子中获取FIRST集
        if sentence[0] in self.terminal_set:  # 终结符
            return {sentence[0]}

        if sentence[0] in self.non_terminal_set:  # 非终结符
            if 'e' in self.first_set.get(sentence[0]) and len(sentence) > 1:
                return self.first_set.get(sentence[0]) | self.get_first_set_of_sentence(sentence[1:])
            return self.first_set.get(sentence[0])

    def get_closure(self, J):  # 获取闭包closure
        K = []
        while K != J:  # 若closure还在增长
            K = J.copy()  # K         - 一个有效项目集		    [[['S', '->', '~', 'programstruct'], ['$']]]
            for item in K:  # item	    - 遍历每个项目            [['S', '->', '~', 'programstruct'], ['$']]
                index = item[0].index('~')  # item[0]   - 项目内容	    ['S', '->', '~', 'programstruct']

                # 若圆点后为非终结符
                if index < len(item[0]) - 1 and item[0][index + 1] in self.non_terminal_set:
                    b = set()

                    # 更新活前缀
                    for a in item[1]:
                        if a != 'e':
                            if index < len(item[0]) - 2:
                                b = b | self.get_first_set_of_sentence(item[0][index + 2:] + [a])
                            else:
                                b = b | self.get_first_set_of_sentence([a])

                    # 遍历该终结符所有文法，更新项目
                    for prod in self.production.get(item[0][index + 1]):
                        prod = [p.strip() for p in prod.split()]

                        if prod == ['e']:  # 若为e
                            prod = []

                        temp = [item[0][index + 1], '->', '~'] + prod
                        if [temp, list(b)] not in K:
                            J.append([temp, list(b)])
        return K

    def get_go(self, I, X):  # 获取后继项目
        J = []

        # 遍历每个项目
        for item in I:
            index = item[0].index('~')

            # 若圆点后有终结符或非终结符，圆点向后移动一位
            if index < len(item[0]) - 1 and item[0][index + 1] == X:
                # 构造后继项目
                if index < len(item[0]) - 2:
                    temp = self.get_closure(
                        [[item[0][:index] + [item[0][index + 1]] + ['~'] + item[0][index + 2:], item[1]]])
                    if temp not in J:  # 添加后继项目
                        J = J + temp
                else:
                    temp = self.get_closure([[item[0][:index] + [item[0][index + 1]] + ['~'], item[1]]])
                    if temp not in J:  # 添加后继项目
                        J = J + temp

        return J

    def merge(self, P):  # 合并展望符(向前看符号串)
        products_set = []
        result = []

        # 找出所有项目
        for items in P:
            if items[0] not in products_set:
                products_set.append(items[0])

        # 对每个项目，合并展望符
        for prod in products_set:
            lookahead_str = []
            for items in P:
                if prod == items[0]:
                    lookahead_str += items[1]
            lookahead_str = sorted(list(set(lookahead_str)))
            result.append([prod, lookahead_str])

        return result

    def get_DFA(self):  # 获取项目规范集族（及转移函数）
        status_num = 0  # 状态数
        self.status.append(self.merge(self.get_closure([[self.expanded_grammar, ['$']]])))  # 扩展文法

        while len(self.status) != status_num:  # 当项目集规范族仍在增长时

            # 更新状态数
            status_num = len(self.status)

            # 更新项目集规范族
            for statu in self.status:  # 遍历所有项目集
                for i in range(len(self.charset)):  # 遍历所有文法符号
                    # 构造新项目集
                    J = self.merge(self.get_go(statu, self.charset[i]))

                    if J and J not in self.status:
                        # 添加新项目集
                        self.status.append(J)
                        # 添加转移函数
                        # self.goto[(str(self.status.index(statu)), self.charset[i])] = str(self.status.index(J))

        for i in range(len(self.status)):
            for symbol in self.charset:
                tup = (str(i), symbol)
                the_statu = self.merge(self.get_go(self.status[i], symbol))
                if the_statu != []:
                    self.goto[tup] = str(self.status.index(the_statu))

        # pp = pprint.PrettyPrinter(indent=4, width=120, compact=True)
        # print("项目规范集族：")
        # print("数量："+str(len(self.status)))
        # print('''项目规范集族格式
        # [                           # 带活前缀的项目集规范族
        #     [                       # 一个有效项目集 I0，I1，...,In
        #         [                   # 项目集中的一个项目        [['S', '->', '~', 'programstruct'], ['$']]
        #             [],             # 项目内容  ~代表圆点·      ['S', '->', '~', 'programstruct']
        #             []              # 活前缀                   ['$']
        #         ]
        #     ]
        # ]
        # ''')
        # for statu in self.status:
        #     print("序号："+str(self.status.index(statu)))
        #     pp.pprint(statu)
        #
        # print("转移函数：")
        # print("数量："+str(len(self.goto)))
        # print("(有效项目集序号，文法符号)：后继项目序号")
        # pp.pprint(self.goto)

    def get_LR1_table(self):  # 产生LR1分析表

        # 初始化
        self.table = {}
        for i in range(len(self.status)):
            self.table[str(i)] = {}
            for j in self.charset:
                self.table[str(i)][j] = ''

        # 填LR1分析表
        for statu in self.status:  # 遍历每个项目集
            for prod in statu:  # 遍历项目集中的每个项目

                index = prod[0].index('~')
                index_statu = str(self.status.index(statu))

                # 对终结符，若[A->α~aβ，b]∈I，且go（Ii，a）= Ij，则置table[i,a] = ['Shift','j']
                if index < len(prod[0]) - 1 and prod[0][index + 1] in self.terminal_set:
                    new_state=self.goto.get((index_statu, prod[0][index + 1]))
                    self.table[index_statu][prod[0][index + 1]] = ['Shift', new_state]

                # 对非终结符，若go（Ii，a）= Ij，则置table[i,a] = ['goto','j']
                if index < len(prod[0]) - 1 and prod[0][index + 1] in self.non_terminal_set:
                    new_state = self.goto.get((index_statu, prod[0][index + 1]))
                    self.table[index_statu][prod[0][index + 1]] = ['goto', new_state]

                # 若[A->α~，a]∈I，且A != S'(即S)，则置table[i,a] = ['Reduce'] + 规约文法
                if index == len(prod[0]) - 1 and prod[0][0] != self.begin_symbol:
                    for a in prod[1]:
                        self.table[index_statu][a] = ['Reduce'] + list(prod[0][:-1])

            # 若为接受项目，则置table[i,$] = ['ACC']
            if [self.accept_grammar, ['$']] in statu:
                self.table[str(self.status.index(statu))]['$'] = ['ACC']

        # print("LR1分析表：")
        # print("\t",end='')
        # for k in self.charset:
        #     print(k,end=',')
        # print()
        # for i in range(len(self.status)):  # 初始化
        #     print("\t",end='')
        #     for j in self.charset:
        #         print(self.table[str(i)][j], end=',')
        #     print()

    def get_tokens(self, tokens):   # 获取全部记号
        if tokens != []:
            self.tokens = tokens
            return True
        return False

    def LR1(self):  # 进行LR1分析
        stack = [('0', (True,'','',0,0))]  # 分析栈 --- 状态栈 + 符号栈(True or False，字符串，记号，行号，列号)
        self.tokens.append([True,'$','$',self.tokens[-1][3],self.tokens[-1][4]+1])
        ip = 0

        while True:
            S = stack[-1][0]  # 栈顶状态号
            a = self.tokens[ip][2]  # 待输入字符
            action = self.table.get(S).get(a)  # 分析动作
            self.actions_record.append([stack.copy(),action])

            if action:
                if action[0] == 'Shift':  # 移进
                    stack.append((action[1], tuple(self.tokens[ip])))
                    ip += 1
                elif action[0] == 'Reduce':  # 规约
                    reduce_node = []

                    # 弹出符号
                    for i in range(len(action[3:])):
                        reduce_node.insert(0, stack.pop()[1])

                    # 压入符号
                    stack.append((self.table[stack[-1][0]][action[1]][1], (False,None,self.table[S][a][1],None,None)))

                    # 添加规约节点（可能为空，即e）
                    self.reduce_nodes.insert(0, reduce_node)

                elif action == ['ACC']:  # 接受
                    print('语法分析正确')
                    break
            else:
                print('语法分析错误')
                print('错误位置:'+str(self.tokens[ip][3])+'行'+str(self.tokens[ip][4])+'列')
                exit(1)
                break

        # print("对符号串的分析动作：")
        # print("分析次数："+str(len(self.actions_record)))
        # print("[[(状态, (是否为叶子节点（即非规约节点）, 字符串, 记号, 行号, 列号)), (...)], [分析动作]]")
        # for item in self.actions_record:
        #     print('\t' + str(item))
        #
        # print("规约节点：")
        # print("规约节点个数（包含根节点）："+str(len(self.reduce_nodes)))
        # print("下列信息不包含根节点信息")
        # print("每个元组为一个节点，元组属性：是否为叶子节点，字符串，记号，行号，列号")
        # for item in self.reduce_nodes:
        #     print('\t'+str(item))

    def get_analysis_tree(self):  # 生成语法树
        self.grammar_tree=GrammarTree('programstruct')
        
        # 构造语法树
        for nodes in self.reduce_nodes:
            self.grammar_tree.insert_node(nodes)
            
        # self.grammar_tree.output()


def grammar_analyse(tokens):
    tree = GrammarAnalysis()
    return tree.run(tokens)



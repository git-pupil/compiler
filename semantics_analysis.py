from symbol_table import *
from analysis_tree import *


class SemanticAnalyzer:
    def __init__(self, analysis_tree=AnalysisTree(), st_manager=STManager()):
        self.result = True  # 分析结果，false or true
        self.tree = analysis_tree  # 分析树
        self.st_manager = st_manager  # 符号表操作

    """
        语法分析过程中分析过的内容在此不做检查
    """

    def S(self):
        """
        S -> programstruct
        不需要进行检查
        """
        current_node_id = self.tree.find_child_node(0, 0).id
        current_node = self.tree.analysis_tree[current_node_id]  # 找到当前节点
        self.programstruct(current_node.child[0])

    def programstruct(self, node_id):
        """
        programstruct -> program_head ; program_body .
        不需要进行检查
        """
        current_node = self.tree.analysis_tree[node_id]
        self.program_head(current_node.child[0])
        self.program_body(current_node.child[2])

    def program_head(self, node_id):
        """
        program_head → program id ( idlist ){parameters=idlist;make_table('main',False,None,parameters)}
        建表，将idlist插入
        program_head → program id{make_table('main',False,None,[])}
        建表
        """
        current_node = self.tree.analysis_tree[node_id]
        parameter_list = []
        if current_node.child_num == 2:
            self.st_manager.make_table('main', parameter_list, False, None)
        elif current_node.child_num == 5:
            parameter_list = self.idlist(current_node.child[3])
            self.st_manager.make_table('main', parameter_list, False, None)
        else:
            self.result = False

    def program_body(self, node_id):
        """
        program_body → const_declarations var_declarations subprogram_declarations compound_statement
        不需要检查
        """
        current_node = self.tree.analysis_tree[node_id]
        self.const_declarations(current_node.child[0])
        self.var_declarations(current_node.child[1])
        self.subprogram_declarations(current_node.child[2])
        self.compound_statement(current_node.child[3])

    def idlist(self, node_id):
        """
        idlist → idlist , id{parameters.append((id.name,id.type))}
        将id和idlist的返回值加入参数表
        idlist → id{parameters.append((id.name,id.type))}
        将id加入参数表
        """
        current_node = self.tree.analysis_tree[node_id]
        parameters = []
        if current_node.child_num == 1:
            child_node = current_node.find_child_node(node_id, 0)
            parameters.append(Parameter(child_node.value, None, child_node.row, child_node.column, False))
        else:
            parameters.extend(self.idlist(current_node.child[0]))
            child_node = current_node.find_child_node(node_id, 2)
            parameters.append(Parameter(child_node.value, None, child_node.row, child_node.column, False))
        return parameters

    def const_declarations(self, node_id):
        """
        const_declarations → const const_declaration ;
        const_declarations → ε
        不需要检查
        """
        current_node = self.tree.analysis_tree[node_id]
        if current_node.child_num == 3:
            self.const_declaration(current_node.child[1])

    def const_declaration(self, node_id):
        """
        const_declaration → const_declaration ; id relop const_value{insert_item()}
        const_declaration → id relop const_value{insert_item()}
        将标识符id插入符号表
        """
        current_node = self.tree.analysis_tree[node_id]
        if current_node.child_num == 3:
            id_node = current_node.find_child_node(node_id, 0)
            relop_node = current_node.find_child_node(node_id, 1)
            const_value_type = self.const_value(current_node.child[2])
        else:
            self.const_declaration(current_node.child[0])
            id_node = current_node.find_child_node(node_id, 2)
            relop_node = current_node.find_child_node(node_id, 3)
            const_value_type = self.const_value(current_node.child[4])

        if relop_node.value != '=':
            print("语义错误：第{0}行, 第{1}列: 常量定义应使用‘=’".format(id_node.row, id_node.column))
            self.result = False
            return

        new_item = Item(id_node.value, "const", const_value_type[0],
                        const_value_type[1], None, [], id_node.row, [])
        if not self.st_manager.insert_item(new_item, self.st_manager.current_table_name):
            print("语义错误：第{0}行, 第{1}列: {2}重定义或该符号表不存在".format(id_node.row, id_node.column, id_node.value))
            self.result = False

    def const_value(self, node_id):
        """
        const_value → addop num{const_value.type=num}
        const_value → num {const_value.type=num}
        const_value → ' letter '{const_value.type=char}
        返回 const_value_type = (value, type)
        """
        current_node = self.tree.analysis_tree[node_id]
        const_value = None
        const_type = None
        if current_node.child_num == 2:  # const_value → addop num{const_value.type=num}
            addop_node = self.tree.find_child_node(node_id, 0)
            num_node = self.tree.find_child_node(node_id, 1)
            if addop_node.value == '+':
                const_value = num_node.value
            elif addop_node.value == '-':
                const_value = num_node.value.__neg__()
            elif addop_node.value == 'or':
                print("语义错误：第{0}行, 第{1}列: or不能给const赋值".format(addop_node.row, addop_node.column))
                const_value_type = (None, None)
                return const_value_type
            if isinstance(const_value, int):
                const_type = 'integer'
            if isinstance(const_value, float):
                const_type = 'real'
        elif current_node.child_num == 1:  # const_value → num {const_value.type=num}
            num_node = self.tree.find_child_node(node_id, 0)
            const_value = num_node.value
            if isinstance(const_value, int):
                const_type = 'integer'
            if isinstance(const_value, float):
                const_type = 'real'
        else:  # const_value → ' letter '{const_value.type=char}
            letter_node = self.tree.find_child_node(node_id, 1)
            const_value = letter_node.value
            const_type = 'char'
        const_value_type = (const_value, const_type)
        return const_value_type

    def var_declarations(self, node_id):
        """
        var_declarations → var var_declaration ;
        var_declarations → ε
        不需要检查
        """
        current_node = self.tree.analysis_tree[node_id]
        if current_node.child_num == 3:
            self.var_declaration(current_node.child[1])

    def var_declaration(self, node_id):
        """
        var_declaration → var_declaration ; idlist : type{insert_item()}
        var_declaration → idlist : type{insert_item()}
        """
        current_node = self.tree.analysis_tree[node_id]
        parameter_list = []
        if current_node.child_num == 3:
            parameter_list = self.idlist(current_node.child[0])
            item_type = self.type(current_node.child[2])
        elif current_node.child_num == 5:
            self.var_declaration(current_node.child[0])
            parameter_list = self.idlist(current_node.child[2])
            item_type = self.type(current_node.child[4])



    def type(self, node_id):
        """
        type → basic_type {type.value = basic_type}
        type → array [ period ] of basic_type{type.id = array;type.value = basic_type;
                                            type.demension=period.demension;type.parameters=period.parameters}
        """


    def basic_type(self, node_id):
        """
        basic_type → integer{basic_type=integer}
        basic_type → real {basic_type=real}
        basic_type → boolean {basic_type=boolean}
        basic_type → char{basic_type=char}
        """


    def period(self, node_id):
        """
        period → period ， num .. num {period.demension++;period.parameters.append()}
        period → num .. num{period.demension++;period.parameters.append()}
        返回值：array_period = [(下限, 上限), ]
        """
        current_node = self.tree.analysis_tree[node_id]
        array_period = []
        if current_node.child_num == 3:
            child1 = self.tree.find_child_node(node_id, 0)
            child2 = self.tree.find_child_node(node_id, 2)
            child1_value = child1.value
            child2_value = child2.value
            if type(child1.value) == type(1.0) or child1.value < 0:
                print('语义错误：第{0}行, 第{1}列: 数组下标必须为非负整数'.format(child1.row, child1.column))  # 同时输出行，列
                self.result = False
                return array_period
            if type(child2.value) == type(1.0) or child1.value < 0:
                print('语义错误：第{0}行, 第{1}列: 数组下标必须为非负整数'.format(child2.row, child2.column))  # 同时输出行，列
                self.result = False
                return array_period
            if child1.value > child2_value:
                print('语义错误：第{0}行, 第{1}列: 数组上下限错误'.format(child2.row, child2.column))  # 同时输出行，列
                self.result = False
                return array_period
            array_period.append((child1.value, child2.value))
        elif current_node.child_num == 5:
            array_period = self.period(current_node.child[0])
            child1 = self.tree.find_child_node(node_id, 2)
            child2 = self.tree.find_child_node(node_id, 4)
            if type(child1.value) == type(1.0) or child1.value < 0:
                print('语义错误：第{0}行, 第{1}列: 数组下标必须为非负整数'.format(child1.row, child1.column))  # 同时输出行，列
                self.result = False
                return array_period
            if type(child2.value) == type(1.0) or child1.value < 0:
                print('语义错误：第{0}行, 第{1}列: 数组下标必须为非负整数'.format(child2.row, child2.column))  # 同时输出行，列
                self.result = False
                return array_period
            if child1.value > child2.value:
                print('语义错误：第{0}行, 第{1}列: 数组上下限错误'.format(child2.row, child2.column))  # 同时输出行，列
                self.result = False
                return array_period
            array_period.append((child1.value, child2.value))
        return array_period

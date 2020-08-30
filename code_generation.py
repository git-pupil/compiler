import os
from grammar_tree import *
from semantics_analysis import *
from symbol_table import STManager

'''
    >>> 非终结符的函数调用接口
	1.此类接口以文法中非终结符作为函数名，参数是当前所处节点

    >>> 输出到文件的接口:output(self, *trans)
    1.主要负责对对应的代码块进行输出，参数是字符串

    >>> 与分析树交互的一些接口:
    1.指定一个token，看一个节点是否有这个祖先has_ ancestor (self, node_id, ancestor _token)，返回True或者False
    2.得到指定节点的孩子以及孩子数量get_child(self, node_id)，返回孩子节点列表以及孩子节点列表长度
    3.得到指定节点的父亲节点的node_id，get_parent(self, node_id)，返回node_id
    4.判断当前节点是否的token是否为指定token，wait(self, node_id, token)

    >>> 与语义分析交互的接口:
    1.获得指定变量是否是按地址传递的函数:is_addr(self, id)
    2.获得指定变量的类型:get_var_type(self, id)
    3.获得数组的上下限:get_bound(self, id)
    4.判断一个id是否为函数:is_func(self, id)
    5.判断一个表达式的类型:get_exp_type(self, node_id)

'''


class Error(Exception):
    pass


class CodeGeneration:

    def __init__(self, analysis_tree=None, semantic=None):
        self.tree = analysis_tree
        
        self.cur_state = []  # 状态栈, 记录当前所处作用域
        self.semantic = semantic
        self.st_manager = STManager
        self.outstr = ''

        self.programstruct(0)



    def get_parent(self, node_id):
        return self.tree.grammar_tree[node_id].parent

    def get_child(self, node_id):
        print(node_id)
        self.tree.output()
        print(self.tree.grammar_tree[node_id])
        return self.tree.grammar_tree[node_id].child, len(self.tree.grammar_tree[node_id].child)

    def has_ancestor(self, node_id, ancestor_token):
        parent = node_id
        while True:
            parent = self.get_parent(parent)
            if self.tree.grammar_tree[parent].token == ancestor_token:
                return True
            if self.tree.grammar_tree[parent].token == 'programstruct':
                return False

    def wait(self, node_id, token):
        if self.tree.grammar_tree[node_id].token != token:
            raise Error('与文法不匹配')

    def output(self, *trans):
        for item in trans:
            print(item, end='')
            self.outstr += item

    def is_addr(self, id):
        # print(self.cur_state)
        return self.st_manager.is_addr(id, self.cur_state[-1])

    def get_var_type(self, id):
        # print(self.cur_state)
        return self.st_manager.get_variable_type(id, self.cur_state[-1])

    def get_bound(self, id):
        # print(self.cur_state)
        arr_range = self.st_manager.get_array_arrange(id, self.cur_state[-1])
        return [low for (low, high) in arr_range]

    def is_func(self, id):
        return self.st_manager.is_func(id)

    def get_exp_type(self, node_id):
        return self.semantic.get_exp_type(node_id, self.cur_state[-1])

    def get_args(self, id):
        return self.st_manager.get_args(id)

    def programstruct(self, node_id):
        child, child_num = self.get_child(node_id)
        print(child)
        if child_num == 4:  # program_head ; program_body .
            self.output('#include<stdio.h>\n')
            self.program_head(child[0])

            self.wait(child[1], ';')
            # self.output('\n{\n')

            self.program_body(child[2])

            self.wait(child[3], '.')
            self.cur_state.pop()
            # self.output('\nreturn 0; \n}')
        else:
            raise Error('文法子树个数不对')

    def program_head(self, node_id):
        child, child_num = self.get_child(node_id)
        if child_num == 5:  # program id ( idlist )
            self.wait(child[0], 'program')

            self.wait(child[1], 'id')

            self.wait(child[2], '(')

            idlist = []
            self.idlist(child[3])  # mat(int a,int b);
            self.output(', '.join(idlist))

            self.wait(child[4], ')')
        else:
            raise Error('文法子树个数不对')

    def program_body(self, node_id):
        child, child_num = self.get_child(node_id)
        if child_num == 4:
            self.cur_state.append('main')
            self.const_declarations(child[0])

            self.var_declarations(child[1])

            self.subprogram_declarations(child[2])

            self.output('int main()')
            self.compound_statement(child[3])

        else:
            raise Error('文法子树个数不对')

    def idlist(self, node_id, idlist=[]):
        child, child_num = self.get_child(node_id)
        parent = self.get_parent(node_id)
        if self.tree.grammar_tree[parent].token == 'program_head':  # program的id不做翻译
            return

        if child_num == 3:  # idlist , id
            self.idlist(child[0], idlist)

            self.wait(child[1], ',')
            # self.output(',')

            self.wait(child[2], 'id')
            idlist.append(self.tree.grammar_tree[child[2]].value)
            # self.output(self.tree.grammar_tree[child[2]].value)
        elif child_num == 1:  # id
            self.wait(child[0], 'id')
            idlist.append(self.tree.grammar_tree[child[0]].value)
            # self.output(self.tree.grammar_tree[child[0]].value)
        else:
            raise Error('文法子树个数不对')

    def const_declarations(self, node_id):
        child, child_num = self.get_child(node_id)
        if child_num == 3:  # const const_declaration ;
            self.wait(child[0], 'const')
            self.output('const ')

            self.const_declaration(child[1])

            self.wait(child[2], ';')
            self.output(';\n')
        elif child_num == 1:  # 空
            print(child[0])
            print(node_id)
            self.wait(child[0], 'e')
            # self.output('')
        else:
            raise Error('文法子树个数不对')

    def const_declaration(self, node_id):
        child, child_num = self.get_child(node_id)
        if child_num == 5:  # const_declaration ; id = const_value
            self.const_declaration(child[0])

            self.wait(child[1], ';')
            self.output(';')

            id_type, id_value = self.const_value(child[4])  # 必须得到value的type才能对id进行翻译
            self.output(id_type, ' ')
            self.wait(child[2], 'id')
            self.output(self.tree.grammar_tree[child[2]].value)
            self.wait(child[3], 'relop')
            self.output(self.tree.grammar_tree[child[3]].value)
            self.output(id_value)
        elif child_num == 3:  # id = const_value
            id_type, id_value = self.const_value(child[2])
            self.output(id_type + ' ')

            self.wait(child[0], 'id')
            self.output(self.tree.grammar_tree[child[0]].value)

            self.wait(child[1], 'relop')
            self.output(self.tree.grammar_tree[child[1]].value)
            self.output(id_value)
        else:
            raise Error('文法子树个数不对')

    def const_value(self, node_id):
        child, child_num = self.get_child(node_id)
        if child_num == 3:  # ′ letter ′
            self.wait(child[0], "'")
            self.wait(child[1], 'letter')
            self.wait(child[2], "'")
            return 'char', "'{}'".format(self.tree.grammar_tree[child[1]].value)
        elif child_num == 2:  # addop num
            self.wait(child[0], 'addop')
            self.wait(child[1], 'int_num')
            num = str(self.tree.grammar_tree[child[1]].value)
            if '.' in num:
                num_type = 'float'
            else:
                num_type = 'int'
            return num_type, "{}{}".format(self.tree.grammar_tree[child[0]].value, self.tree.grammar_tree[child[1]].value)
        elif child_num == 1:  # num
            self.wait(child[0], 'int_num')
            num = str(self.tree.grammar_tree[child[0]].value)
            if '.' in num:
                num_type = 'float'
            else:
                num_type = 'int'
            return num_type, "{}".format(self.tree.grammar_tree[child[0]].value)
        else:
            raise Error('文法子树个数不对')

    def var_declarations(self, node_id):
        child, child_num = self.get_child(node_id)
        if child_num == 3:  # var var_declaration ;
            self.wait(child[0], 'var')
            self.var_declaration(child[1])
            self.wait(child[2], ';')
            self.output(';\n')
        elif child_num == 1:  # 空
            self.wait(child[0], None)
        else:
            raise Error('文法子树个数不对')

    def var_declaration(self, node_id):
        child, child_num = self.get_child(node_id)
        if child_num == 5:  # var_declaration ; idlist : type

            self.var_declaration(child[0])

            self.wait(child[1], ';')
            self.output(';\n')

            # 得到对应的id列表
            idlist = []
            self.idlist(child[2], idlist)
            self.wait(child[3], ':')

            var_type, llist = self.type(child[4])  # 得到变量的类型

        elif child_num == 3:  # idlist : type

            idlist = []
            self.idlist(child[0], idlist)
            self.wait(child[1], ':')
            # print('idlist', idlist)
            var_type, llist = self.type(child[2])
            # print('var_type', var_type, 'llist', llist)

        # 以,分隔idlist中的各个id
        self.output(var_type, ' ')
        def_list = []  # 输出列表
        if llist:  # 数组的定义
            for id in idlist:
                id_str = id
                arr_str = ''.join(['[{}]'.format(l) for l in llist])
                def_list.append(id_str + arr_str)
        else:  # 普通变量的定义
            def_list.extend(idlist)
        # print(def_list, len(def_list))
        if def_list:
            self.output(', '.join(def_list))

    def type(self, node_id):
        child, child_num = self.get_child(node_id)
        if child_num == 1:  # basic_type
            return self.basic_type(child[0]), []
        elif child_num == 6:  # array [ period ] of basic_type
            self.wait(child[0], 'array')
            self.wait(child[1], '[')
            llist = []  # 统计多维数组下标的范围 比如10..20 就是10
            self.period(child[2], llist)
            self.wait(child[3], ']')
            self.wait(child[4], 'of')
            return self.basic_type(child[5]), llist

    def basic_type(self, node_id):
        child, child_num = self.get_child(node_id)
        if child_num == 1:  # integer | real | boolean | char
            var_type = self.tree.grammar_tree[child[0]].value
            if var_type == 'integer':
                return 'int'
            if var_type == 'real':
                return 'float'
            if var_type == 'boolean':
                return 'int'
            if var_type == 'char':
                return 'char'
        else:
            raise Error('文法子树个数不对')

    def period(self, node_id, llist):
        child, child_num = self.get_child(node_id)
        if child_num == 5:  # period , num .. num
            self.period(child[0], llist)
            self.wait(child[1], ',')
            self.wait(child[2], 'int_num')
            self.wait(child[3], '..')
            self.wait(child[4], 'int_num')
            llist.append(str(self.tree.grammar_tree[child[4]].value - self.tree.grammar_tree[child[2]].value + 1))
        elif child_num == 3:  # num .. num
            print(self.tree.grammar_tree[child[0]].token)
            self.wait(child[0], 'int_num')
            self.wait(child[1], '..')
            self.wait(child[2], 'int_num')
            llist.append(str(int(self.tree.grammar_tree[child[2]].value) - int(self.tree.grammar_tree[child[0]].value) + 1))

    def subprogram_declarations(self, node_id):
        child, child_num = self.get_child(node_id)
        if child_num == 3:  # subprogram_declarations subprogram ;
            self.subprogram_declarations(child[0])
            self.subprogram(child[1])
            self.wait(child[2], ';')
        if child_num == 1:  # 空
            self.wait(child[0], 'e')

    def subprogram(self, node_id):
        child, child_num = self.get_child(node_id)
        if child_num == 3:  # subprogram_head ; subprogram_body
            re_type = self.subprogram_head(child[0])
            self.wait(child[1], ';')

            self.output('\n{\n')
            schild, schild_num = self.get_child(child[0])
            if schild_num == 5:  # 带返回值的要先定义返回值
                self.output(re_type + ' ', self.tree.grammar_tree[schild[1]].value + '_re;\n')
            self.subprogram_body(child[2])
            if schild_num == 5:  # 是function的声明，函数结束要返回
                self.output('return ', self.tree.grammar_tree[schild[1]].value + '_re;')
            self.output('\n}\n')
            self.cur_state.pop()

    def subprogram_head(self, node_id):
        child, child_num = self.get_child(node_id)
        if child_num == 3:  # procedure id formal_parameter
            self.wait(child[0], 'procedure')
            self.output('void ')

            self.wait(child[1], 'id')
            self.cur_state.append(self.tree.grammar_tree[child[1]].value)
            self.output(self.tree.grammar_tree[child[1]].value)

            pstr = self.formal_parameter(child[2])  # 输出参数以及左右括号
            self.output(pstr)
            return None
        elif child_num == 5:  # function id formal_parameter : basic_type
            self.wait(child[0], 'function')
            self.wait(child[1], 'id')
            self.cur_state.append(self.tree.grammar_tree[child[1]].value)
            pstr = self.formal_parameter(child[2])
            self.wait(child[3], ':')
            re_type = self.basic_type(child[4])

            self.output(re_type, ' ')
            self.output(self.tree.grammar_tree[child[1]].value)
            self.output(pstr)
            return re_type

    def formal_parameter(self, node_id):
        child, child_num = self.get_child(node_id)
        if child_num == 1:  # 空
            return '()'
        elif child_num == 3:  # ( parameter_list )
            self.wait(child[0], '(')
            plist = []
            self.parameter_list(child[1], plist)
            self.wait(child[2], ')')
            return '(' + ', '.join(plist) + ')'

    def parameter_list(self, node_id, plist=[]):
        child, child_num = self.get_child(node_id)
        if child_num == 3:  # parameter_list ; parameter
            self.parameter_list(child[0], plist)
            self.wait(child[1], ';')
            self.parameter(child[2], plist)
        elif child_num == 1:  # parameter
            self.parameter(child[0], plist)

    def parameter(self, node_id, plist):
        child, child_num = self.get_child(node_id)
        if child_num == 1:  # var_parameter | value_parameter
            if self.tree.grammar_tree[child[0]].token == 'var_parameter':
                self.var_parameter(child[0], plist)
            else:
                self.value_parameter(child[0], plist)

    def var_parameter(self, node_id, plist):
        child, child_num = self.get_child(node_id)
        if child_num == 2:  # var value_parameter
            self.wait(child[0], 'var')
            self.value_parameter(child[1], plist)

    def value_parameter(self, node_id, plist):
        child, child_num = self.get_child(node_id)
        if child_num == 3:  # idlist : simple_type
            idlist = []
            self.idlist(child[0], idlist)
            self.wait(child[1], ':')
            val_type = self.basic_type(child[2])
            parent = self.get_parent(node_id)
            if self.tree.grammar_tree[parent].token == 'var_parameter':
                for id in idlist:
                    plist.append(val_type + '*' + ' ' + id)
            else:
                for id in idlist:
                    plist.append(val_type + ' ' + id)

    def subprogram_body(self, node_id):
        child, child_num = self.get_child(node_id)
        if child_num == 3:  # const_declarations var_declarations compound_statement
            self.const_declarations(child[0])
            self.var_declarations(child[1])
            self.compound_statement(child[2])

    def compound_statement(self, node_id):
        child, child_num = self.get_child(node_id)
        if child_num == 3:  # begin statement_list end

            parent = self.get_parent(node_id)
            if self.tree.grammar_tree[parent].token == 'subprogram_body':
                self.wait(child[0], 'begin')

                self.statement_list(child[1])

                self.wait(child[2], 'end')
            else:
                self.wait(child[0], 'begin')
                self.output('\n{\n')

                self.statement_list(child[1])

                self.wait(child[2], 'end')
                self.output('\n}\n')

    def statement_list(self, node_id):
        child, child_num = self.get_child(node_id)
        if child_num == 3:  # statement_list ; statement
            self.statement_list(child[0])

            self.wait(child[1], ';')

            self.statement(child[2])
            self.output('\n')
        elif child_num == 1:  # statement
            self.statement(child[0])
            self.output('\n')

    def statement(self, node_id):
        child, child_num = self.get_child(node_id)
        if child_num == 3:  # variable assignop expression
            vlist = []
            _, var = self.variable(child[0])
            self.output(var)

            self.wait(child[1], 'assignop')
            self.output('=')

            exp = self.expression(child[2])
            self.output(exp)
            self.output(';')
        if child_num == 1:  # procedure_call | compound_statement | 空
            if self.tree.grammar_tree[child[0]].token == 'procedure_call':
                self.procedure_call(child[0])
                self.output(';')
            elif self.tree.grammar_tree[child[0]].token == 'compound_statement':
                self.compound_statement(child[0])
            else:
                self.wait(child[0], None)
                self.output(';')
        if child_num == 5:  # if expression then statement else_part
            self.wait(child[0], 'if')
            self.output('if')

            self.output('(')
            exp = self.expression(child[1])
            self.output(exp)
            self.output(')')

            self.wait(child[2], 'then')

            self.statement(child[3])
            self.output('\n')

            self.else_part(child[4])
        if child_num == 8:  # for id assignop expression to expression do statement
            self.wait(child[0], 'for')
            self.output('for')

            self.output('(')
            self.wait(child[1], 'id')
            if self.is_addr(self.tree.grammar_tree[child[1]].value):
                self.output('*' + self.tree.grammar_tree[child[1]].value)
            else:
                self.output(self.tree.grammar_tree[child[1]].value)

            self.wait(child[2], 'assignop')
            self.output('=')

            self.output(self.expression(child[3]))
            self.output(';')

            self.wait(child[4], 'to')

            self.output(self.tree.grammar_tree[child[1]].value)
            self.output('<=')
            self.output(self.expression(child[5]))

            self.wait(child[6], 'do')
            self.output(';')

            self.output(self.tree.grammar_tree[child[1]].value)
            self.output('++)')

            self.statement(child[7])
        if child_num == 4:  # read ( variable_list ) | write ( expression_list )
            if self.tree.grammar_tree[child[0]].token == 'read':
                self.wait(child[0], 'read')
                self.output('scanf')

                self.wait(child[1], '(')
                self.output('(')

                vlist = []
                self.variable_list(child[2], vlist)
                self.output('"')
                for (var_type, _) in vlist:
                    if var_type == 'boolean':
                        self.output('%d')
                    if var_type == 'integer':
                        self.output('%d')
                    if var_type == 'char':
                        self.output('%c')
                    if var_type == 'read':
                        self.output('%f')
                self.output('"')

                self.output(',')
                value_list = ['&' + var_value for (_, var_value) in vlist]
                self.output(', '.join(value_list))

                self.wait(child[3], ')')
                self.output(');')
            if self.tree.grammar_tree[child[0]].token == 'write':
                self.wait(child[0], 'write')
                self.output('printf')
                self.wait(child[1], '(')

                self.output('(')
                self.output('"')

                # TODO 这里要加入判断表达值类型的函数
                elist = []
                tlist = []
                self.expression_list(child[2], elist, tlist)

                trans_tlist = []
                for etype in tlist:
                    if etype == 'integer' or etype == 'boolean':
                        trans_tlist.append('%d ')
                    if etype == 'real':
                        trans_tlist.append('%f ')
                    if etype == 'char':
                        trans_tlist.append('%c ')

                self.output(' '.join(trans_tlist))
                self.output('"')
                self.output(',')

                self.output(', '.join(elist))
                self.wait(child[3], ')')
                self.output(');')

            if self.tree.grammar_tree[child[0]].token == 'while':  # while expression do statement
                self.wait(child[0], 'while')
                self.output('while')
                self.output('(')
                self.output(self.expression(child[1]))
                self.output(')')
                self.wait(child[2], 'do')
                self.statement(child[3])

    def variable_list(self, node_id, vlist):
        child, child_num = self.get_child(node_id)
        if child_num == 3:  # variable_list , variable
            self.variable_list(child[0], vlist)
            self.wait(child[1], ',')
            vlist.append(self.variable(child[2]))
        elif child_num == 1:  # variable
            vlist.append(self.variable(child[0]))

    def variable(self, node_id, is_bool=False):
        child, child_num = self.get_child(node_id)
        if child_num == 2:  # id id_varpart
            self.wait(child[0], 'id')
            var_type = self.get_var_type(self.tree.grammar_tree[child[0]].value)
            if var_type == 'boolean':
                is_bool = True
            var_part = self.id_varpart(child[1])
            # 加入一个元组, (var的type, var) eg:(int, a[1][2])
            has_ptr = '*' if self.is_addr(self.tree.grammar_tree[child[0]].value) else ''
            is_func = '_re' if self.is_func(self.tree.grammar_tree[child[0]].value) else ''
            return (var_type, has_ptr + self.tree.grammar_tree[child[0]].value + is_func + var_part)

    def id_varpart(self, node_id):
        child, child_num = self.get_child(node_id)
        if child_num == 3:  # [ expression_list ]
            self.wait(child[0], '[')
            elist = []  # expression 的list
            self.expression_list(child[1], elist)
            self.wait(child[2], ']')

            parent = self.get_parent(node_id)
            id = self.tree.grammar_tree[parent].child[0]
            id_value = self.tree.grammar_tree[id].value
            blist = self.get_bound(id_value)  # bound的list

            elist_trans = ['[{}{}]'.format(exp, '-' + str(bound)) for exp, bound in zip(elist, blist)]
            return ''.join(elist_trans)
        elif child_num == 1:  # 空
            self.wait(child[0], None)
            return ''

    def procedure_call(self, node_id):
        child, child_num = self.get_child(node_id)
        if child_num == 1:  # id
            self.wait(child[0], 'id')
            self.output('{}()'.format(self.tree.grammar_tree[child[0]].value))
        elif child_num == 4:  # id ( expression_list )
            self.wait(child[0], 'id')
            self.output(self.tree.grammar_tree[child[0]].value)

            if self.is_func(self.tree.grammar_tree[child[0]].value):
                args_list = self.get_args(self.tree.grammar_tree[child[0]].value)
                print(args_list)

            self.wait(child[1], '(')
            self.output('(')

            elist = []
            self.expression_list(child[2], elist)
            self.output(', '.join(elist))

            self.wait(child[3], ')')
            self.output(')')

    def else_part(self, node_id):
        child, child_num = self.get_child(node_id)
        if child_num == 2:  # else statement
            self.wait(child[0], 'else')
            self.output('else ')

            self.statement(child[1])
            # self.output(';')
        elif child_num == 1:  # 空
            self.wait(child[0], None)

    def expression_list(self, node_id, elist, tlist=[]):
        child, child_num = self.get_child(node_id)
        if child_num == 3:  # expression_list , expression
            self.expression_list(child[0], elist)
            self.wait(child[1], ',')
            elist.append(self.expression(child[2]))
            tlist.append(self.get_exp_type(child[2]))
        if child_num == 1:  # expression
            elist.append(self.expression(child[0]))
            tlist.append(self.get_exp_type(child[0]))

    def expression(self, node_id, is_bool=False):
        child, child_num = self.get_child(node_id)
        if child_num == 3:  # simple_expression relop simple_expression
            is_bool = True
            front_exp = self.simple_expression(child[0])
            self.wait(child[1], 'relop')
            relop = self.tree.grammar_tree[child[1]].value
            if relop == '<>':
                relop = '!='
            if relop == '=':
                relop = '=='
            back_exp = self.simple_expression(child[2])
            return front_exp + relop + back_exp
        elif child_num == 1:  # simple_expression
            return self.simple_expression(child[0])

    def simple_expression(self, node_id):
        child, child_num = self.get_child(node_id)
        if child_num == 3:  # simple_expression addop term
            exp = self.simple_expression(child[0])
            self.wait(child[1], 'addop')
            addop = self.tree.grammar_tree[child[1]].value
            if addop == 'or':
                addop = '|'
            term = self.term(child[2])
            return exp + addop + term
        elif child_num == 1:  # term
            return self.term(child[0])

    def term(self, node_id):
        child, child_num = self.get_child(node_id)
        if child_num == 3:  # term mulop factor
            term = self.term(child[0])

            self.wait(child[1], 'mulop')
            mulop = self.tree.grammar_tree[child[1]].value
            if mulop == 'div':
                mulop = '/'
            if mulop == 'mod':
                mulop = '%'
            if mulop == 'and':
                mulop = '&&'
            factor = self.factor(child[2])
            return term + mulop + factor
        elif child_num == 1:  # factor
            factor = self.factor(child[0])
            return factor

    def factor(self, node_id, is_bool=None):
        child, child_num = self.get_child(node_id)
        if child_num == 1:  # num | variable
            if self.tree.grammar_tree[child[0]].token == 'int_num':
                return str(self.tree.grammar_tree[child[0]].value)
            if self.tree.grammar_tree[child[0]].token == 'variable':
                _, var = self.variable(child[0])
                return var
        if child_num == 4:  # id ( expression_list )
            self.wait(child[0], 'id')
            self.wait(child[1], '(')

            if self.is_func(self.tree.grammar_tree[child[0]].value):
                is_addr_list = self.get_args(self.tree.grammar_tree[child[0]].value)

            elist = []
            self.expression_list(child[2], elist)
            self.wait(child[3], ')')

            args_list = []
            for exp, is_addr in zip(elist, is_addr_list):
                if is_addr:
                    args_list.append('&' + exp)
                else:
                    args_list.append(exp)

            return self.tree.grammar_tree[child[0]].value + '({})'.format(', '.join(args_list))
        if child_num == 3:  # ( expression )
            self.wait(child[0], '(')
            exp = self.expression(child[1], is_bool)
            self.wait(child[2], ')')
            return '({})'.format(exp)
        if child_num == 2:  # not factor | uminus factor
            if self.tree.grammar_tree[child[0]].token == 'not':
                is_bool_var = False
                factor = self.factor(child[1], is_bool_var)
                if is_bool_var:
                    return '!' + factor
                else:
                    return '~' + factor
            if self.tree.grammar_tree[child[0]].token == 'uminus':
                self.wait(child[0], 'uminus')
                factor = self.factor(child[1])
                return '-' + factor









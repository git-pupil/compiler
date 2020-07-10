class Parameter:
    """
    符号表或者表项中的形式参数的内容，位置及其传递方式
        增加了行号、列号
    """

    def __init__(self, name, type, row, column, vary=False):
        self.name = name  # 参数名
        self.type = type  # 参数类型
        self.row = row  # 行号
        self.column = column  # 列号
        self.vary = vary  # true为传地址, false为传值


class Item:
    """
    符号表中的表项
    """

    def __init__(self, name, identifier_type, value_type, value,
                 dimension=None, parameter_list=[], declare_row=None, used_row=[]):
        self.name = name  # 标识符名称
        self.identifier_type = identifier_type  # 标识符类型 CONST VAR ARRAY ADDR PROGRAM FUNCTION PROCEDURE
        self.value_type = value_type  # 常量，变量：值的类型  INT,REAL,CHAR, boolean
        # 数组：元素的类型
        # 函数：返回值的类型
        self.value = value  # 常量：值；数组：大小；（函数，过程：临时变量个数？？？）
        self.dimension = dimension  # 数组的维数，或者是函数/过程的参数个数
        self.parameter_list = parameter_list  # 如果是数组，则是数组的上下限
        self.declare_row = declare_row  # 声明行
        self.used_row = used_row  # 使用行


class SymbolTable:
    """
    符号表主体
    parent父表中的索引如何找到没有确定(用表名找)
    """

    def __init__(self, name='', parameter_list=[], item_list=[], is_func=False,
                 is_valid=False, return_type=None):
        self.name = name  # 符号表名字，应该是唯一的
        self.parameter_list = parameter_list  # 形参列表
        self.item_list = item_list  # 符号表条目
        self.is_func = is_func  # false为过程，true为函数
        self.is_valid = is_valid  # 表是否有效，用于定位与重定位
        self.return_type = return_type  # 返回值类型


class STManager:
    """
    符号表管理类
    """
    all_symbol_table = {}  # {'名称'：SymbolTable, }
    current_table_name = None  # 当前所在的表

    def make_table(self, name, parameter_list, is_func, return_type):
        """
        创建一个新表，表名为name，并将当前所在的表修改为新表
        Parameters:
            name(str)：要创建的表名
            parameter_list(list)：过程/函数的形参表
            is_func(bool)：是否为函数
            return_type(str)：返回值类型
        Return:
            True
            False
        """
        if self.current_table_name is not None and self.current_table_name != 'main':  # 尝试在子表中建表
            print('不允许嵌套定义')
            return False
        if name in self.all_symbol_table.keys():
            print('符号表中存在重名的子表！')
            return False  # 创建失败
        else:
            self.all_symbol_table[name] = SymbolTable(name, parameter_list, [],
                                                      is_func, False, return_type)

            func_type = ''  # 将子表自身属性作为Item加入新表条目
            if name == 'main':
                func_type = 'program'
            elif is_func == True:
                func_type = 'function'
            else:
                func_type = 'procedure'
            new_table_item = Item(name, func_type, return_type, None,
                                  len(parameter_list), parameter_list, None, [])
            self.insert_item(new_table_item, name)
            if name != 'main':  # 新建的表不是主表，则将此条目插入主表，并定位到新表
                self.insert_item(new_table_item, 'main')
            self.locate(name)

            if parameter_list != []:  # 如果有形参,将形参逐个加入新表条目
                for parameter in parameter_list:
                    if parameter.vary == True:
                        identifier_type = 'addr'
                    else:
                        identifier_type = 'var'
                    new_parameter_item = Item(parameter.name, identifier_type, parameter.type,
                                              None, None, [], parameter.row, [])
                    self.insert_item(new_parameter_item, name)

            return True  # 创建成功

    def insert_item(self, item, table_name):
        """
        将表项item插入到表table_name中，table_name默认存在，因此不做判断
        Parameters:
            item(Item)：要插入的表项
            table_name(str)：要插入的表名
        Returns:
            True：成功
            False：失败
        """
        if self.is_redefined(item.name, table_name) == True:  # 存在重名
            print('存在重名表项')
            return False  # 插入失败
        else:  # 要插入的表中该变量名未定义
            self.all_symbol_table[table_name].item_list.append(item)
            return True  # 插入成功

    def is_redefined(self, item_name, table_name):
        """
        查重定义函数，允许不同表中使用重名变量
        Parameters:
            item_name: 查重的条目名(str)
            table_name: 在哪张表中查重，一般为当前表(str)
        Returns:
            True: 存在重定义
            False: 没有重定义
        """
        for item in self.all_symbol_table[table_name].item_list:
            if item.name == item_name:
                return True  # 同一表中存在重名
        return False

    def search_item(self, item_name, table_name):
        """
        在表table_name中检索表项id_name
        Args:
            item_name(str)
            table_name(str)
        Return:
            item(Item)：找到则返回表项
            未找到返回None
        """
        if len(self.all_symbol_table[table_name].item_list) != 0:
            for item in self.all_symbol_table[table_name].item_list:
                if item.name == item_name:  # 在当前表中检索到
                    return item
            if self.all_symbol_table[table_name].name == 'main':  # 若没有检索到，且当前表为主表
                return None
            else:  # 若没有检索到，但当前表为子表，则继续向上检索
                return self.search_item(item_name, 'main')
        else:
            return None

    def locate(self, sub_table):
        """
        定位
        检测到新的块开始时
        更改当前所在符号表
        """
        self.all_symbol_table[sub_table].is_valid = True
        self.current_table_name = sub_table

    def relocate(self):
        """
        重定位
        块结束时返回上一级符号表
        """
        self.all_symbol_table[self.current_table_name].is_valid = False
        self.current_table_name = 'main'

    '''
    def complare_args(self, func_name='', arguments_list=[]):
        比较函数的实参个数和类型与符号表中的定义是否一致；

    def getpnum(self, func_name):
        从符号表中根据func_name提取形参个数

    def getfunc_type(self, func_name):
        从符号表根据func_name提取函数的返回值类型

    def checkptype(self, func_name, argument_type_list):
            
            根据函数名和实参类型列表，
            与符号表进行比较
            列表形如(int, char, real)
            


    def is_addr(self, id_name, table_name):
            
            判断id_name是引用传递还是按值传递
            返回：true 传地址；false 传值
            

    def get_array_arrange(self, array_name, table_name):
            
            获取数组上下限
            返回：[(下限, 上限), ]
            

    def get_variable_type(self, id_name, table_name):
            
            获取变量的类型
            返回: 'integer|boolean|char|real'
            

    def is_func(self, id_name):
            
            判断是否是一个函数
            返回：true or false
            

    def get_args(self, table_name):
            
            返回对应的参数列表
            


    def output_table_item(self):
            
            输出所有表的表项
           
'''

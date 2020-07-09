class TreeNode:
    """
    分析树节点
    """

    def __init__(self, id, parent,
                 t_symbol=True, token=None, value=None, row=None, column=None):
        self.id = id  # 唯一标号
        self.parent = parent  # 父节点
        # self.child = child  # 子节点
        self.child = []  # 子结点的编号
        self.child_num = 0  # 子节点数量 len(self.child)
        # self.node_type = node_type  # 分析树节点类型
        self.t_symbol = t_symbol  # 是否是终结符
        self.token = token  # 节点的名字（出现在文法表达式中的符号）
        self.value = value  # 节点表示的值（文法表达式中符号代表的内容）
        self.row = row  # 终结符的行号
        self.column = column  # 终结符的列号


class AnalysisTree:

    def __init__(self):
        self.analysis_tree = {0: TreeNode(0, 0, False, 'root')}  # {id:TreeNode, }
        self.current_node = 0
        self.node_num = 1  # 下一个添加节点的id

    def insert_node(self, param=[]):
        """
        insert_node所需的参数为一个list，列表中元素的结构为tuple，tuple的结构为(t_symbol, token, value, row, column)
        """
        if not param:  # 当前节点为ε
            self.analysis_tree[self.node_num] = TreeNode(self.node_num, self.current_node, True, None, None, None, None)
            self.analysis_tree[self.current_node].child.append(self.node_num)
            self.analysis_tree[self.current_node].child_num += 1
            self.node_num += 1
        for element in param:
            self.analysis_tree[self.node_num] = TreeNode(self.node_num, self.current_node,
                                                         element[0], element[1], element[2], element[3], element[4])
            self.analysis_tree[self.current_node].child.append(self.node_num)
            self.analysis_tree[self.current_node].child_num += 1
            self.node_num += 1

        temp_node = self.node_num - 1
        if not self.analysis_tree[temp_node].t_symbol:  # 如果产生式右部的最后一个符号为非终结符，则该非终结符就是当前节点
            self.current_node = temp_node
        else:  # 否则，就向左遍历，直到找到第一个产生式右部的非终结符
            while True:
                if (temp_node - 1) in self.analysis_tree[
                    self.analysis_tree[temp_node].parent].child:  # 判断temp_node是否还有左兄弟节点
                    temp_node -= 1
                    if not self.analysis_tree[temp_node].t_symbol:
                        self.current_node = temp_node
                        break
                else:  # 说明当前产生式的所有右部符号已经遍历，但无满足要求的符号可作为当前节点，则进入上一层
                    temp_node = self.analysis_tree[temp_node].parent
                    if temp_node == 0:  # 此时temp_node为根节点，而且说明该树的构造已完成
                        self.current_node = 0
                        break

    def output(self):
        for a in self.analysis_tree:
            print('id = ', self.analysis_tree[a].id, ', token = ', self.analysis_tree[a].token, ', parent = ',
                  self.analysis_tree[a].parent,
                  ', child:', self.analysis_tree[a].child, ', child_num = ', self.analysis_tree[a].child_num,
                  ', t_symbol = ', self.analysis_tree[a].t_symbol, ', value = ', self.analysis_tree[a].value,
                  ', row = ', self.analysis_tree[a].row, ', column = ', self.analysis_tree[a].column, sep='')

    def find_child_node(self, node_id, child_pos):
        """
        返回TreeNode
        """
        return self.analysis_tree[self.analysis_tree[node_id].child[child_pos]]

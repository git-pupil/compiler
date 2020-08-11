# -*- coding: utf-8 -*-

"""" ==========================================================================
# _version_ = "0.3.5" 2020-07-10
# _author_  = "杨钊颖"
#
# 模块名： 词法分析模块
# 模块描述：
#    输入：需要编译的Pascal文本的绝对路径
#    输出：一个word_analyse_result,其中的元素为list，里层list存储每个单词的信息
#
# 输入：filename
# 输入示例
#     "./word_analyse_test1"
#
# 输出：word_analyse_result
# 输出示例1：如果正确，会返回一个list，存放每个单词的分析结果
#    [
#     [单词分析正确性,单词名字, 单词类型, 行, 列],
#     [True,'program', 'program', '3', '5'],
#     [True,'date', 'id', '7', '4'],
#     [True,'+', 'addop', '7', '9'],
#    ]
#
# 输出示例2：如果词法分析出错，会在控制台打印错误信息
#
#    x行x列，'z_', Unrecognizable id!
#    y行y列，'zxhasndia', The length of id is too long!
#
# 外界可调用函数 word_analyse(filename),详见外部函数块
=========================================================================== """


"""" ==========================================================================
#
#                                   全局变量
#
=========================================================================== """

# #############################################################################
#                 摘自教材《编译原理与技术 第2版》第12章第四节 P395-396
# #############################################################################

# 关键字列表
key_words = ['and', 'array', 'begin', 'boolean', 'case', 'const', 'div', 'do',
             'downto', 'else', 'end', 'for', 'function', 'if', 'integer',
             'mod', 'not', 'of', 'or', 'procedure', 'program', 'real',
             'record', 'repeat', 'then', 'to', 'type', 'until', 'var', 'while',
             ]

# 逻辑算符
boolops = ['<', '<=', '>', '>=', 'and', 'or', 'not']
# 子界符
subbounder = '..'
# 分界符
delimiters = [',', ';', '.', '(', ')', '[', ']', '{', '}']
# 代码注释起止符
annotations = ['(*', '*)', '{', '}']
# 关系运算符relop代表'=', '<>', '<', '<=', '>', '>='
relops = ['=', '<>', '<', '<=', '>', '>=']
# addop代表运算符'+', '-', 'or'
addops = ['+', '-', 'or']
# mulop代表运算符'*', '/', 'div', 'mod' 和 'and'
mulops = ['*', '/', 'div', 'mod', 'and']
# assignop代表赋值符号':='
assignop = ':='

# 读到该字符，则表示单词到此为止
word_end_sign = ['+', '-', '*', '/', '<', '>', ' ', ',', ';', '.', '(', ')',
                 '[', ']', '{', '}', ':', '\n', '='
                 ]


"""" ==========================================================================
#
#                                   内部函数
#
=========================================================================== """


"""" ==========================================================================
#                                   IO函数
=========================================================================== """


def _load_code(filename, source_code):
    """" ======================================================================
    # @brief        把文本中Pascal代码读入内存，去掉注释，存放在SourceCode中
    # @param        filename——存放Pascal代码的文本文件绝对路径
    # @return{None}
    ======================================================================= """

    with open(filename, 'r', encoding="utf-8") as PascalCode:
        # 第一个用于标记'(*'，'*)'
        annotation_flag1 = False
        # 第二个用于标记'{', '}'
        annotation_flag2 = False
        # 只要有一个注释，则处于注释状态
        annotation = annotation_flag1 or annotation_flag2

        # 在最后一行结尾加上一个换行符
        lines = PascalCode.readlines()
        lines[-1] += '\n'

        for line in lines:
            # 去除源代码中注释
            # 用于存储去除注释后的代码
            pure_line = ""

            i = 0
            while i < len(line):

                # 读到'（*'，注释开始
                if (not annotation) and (line[i] == '(' and line[i + 1] == '*'):
                    annotation_flag1 = True
                    annotation = annotation_flag1 or annotation_flag2
                    i += 2

                # 读到'{'，注释开始
                elif (not annotation) and (line[i] == '{'):
                    annotation_flag2 = True
                    annotation = annotation_flag1 or annotation_flag2
                    i += 1

                # 已经读到'(*'，现读到'*)'，第一类注释结束
                elif annotation_flag1 and (line[i] == '*' and line[i + 1] == ')'):
                    annotation_flag1 = False
                    annotation = annotation_flag1 or annotation_flag2
                    i += 2

                # 已经读到'{'，现读到'}'，第二类注释结束
                elif annotation_flag2 and line[i] == '}':
                    annotation_flag2 = False
                    annotation = annotation_flag1 or annotation_flag2
                    i += 1

                # 在注释状态下
                elif annotation:
                    # 在注释状态下，没有读到注释结束标识符, 但读到换行符
                    if line[i] == '\n':
                        pure_line += '\n'
                        i += 1

                    # 在注释状态下,读到的一般字符
                    else:
                        i += 1

                # 不在注释状态下，读到的普通字符
                else:
                    pure_line += line[i]
                    i += 1

            # 读入内存
            source_code.append(pure_line)


def _is_analyse_correct(word_analyse_result):
    """" ======================================================================
    # @brief            检查词法分析结果是否存在错误
    # @param            词法分析结果
    # @return{void}     如果词法分析结果存在错误，则会在控制台打印错误信息，否则无事发生
    ======================================================================= """
    flag = True

    for word_info in word_analyse_result:
        # 如果存在错误，打印错误信息
        if not word_info[0]:
            print("第{}行第{}列,\t\t\"{}\",\t\t{}".format(
                word_info[3], word_info[4], word_info[1], word_info[2]
            ))
            flag = False

    if flag:
        # 完成遍历没有错误
        return True
    else:
        return False


"""" ==========================================================================
#                                 词法分析相关函数
=========================================================================== """


def _is_letter(ch):
    """" ======================================================================
    # @brief            检查一个字符是否为字母
    # @param            需要检查的字符
    # @return{boolean}  如果是字母则返回True，否则返回False
    ======================================================================= """
    if (('a' <= ch) and (ch <= 'z')) or (('A' <= ch) and (ch <= 'Z')):
        return True
    else:
        return False


def _is_digit(ch):
    """" ======================================================================
    # @brief            检查一个字符是否为数字
    # @param            需要检查的字符
    # @return{boolean}  如果是字母则返回True，否则返回False
    ======================================================================= """
    if ('0' <= ch) and (ch <= '9'):
        return True
    else:
        return False


def _is_identifier(word):
    """" ======================================================================
    # @brief            检查一个单词是否为标识符
    # @param            需要检查的单词
    # @return{boolean}  如果是字母则返回True，否则返回False
    ======================================================================= """
    # 遍历单词每一个字符
    for ch in word:
        # 如果有一个字符不是数字或字母，说明这个单词不是标识符
        if not (_is_digit(ch) or _is_letter(ch)):
            return False

    return True


def _is_integer(word):
    """" ======================================================================
    # @brief            检查一个单词是否为整数
    # @param            需要检查的单词
    # @return{boolean}  如果是字母则返回True，否则返回False
    ======================================================================= """
    # 遍历单词每一个字符
    for ch in word:
        # 如果有一个字符不是数字，说明这个单词不是整数
        if not _is_digit(ch):
            return False

    return True


def _analyse(line, line_num, word_analyse_result):
    """" ======================================================================
    # @brief        按行对Pascal代码进行词法分析
    # @param        words——需要词法分析的一行Pascal代码中已完成分割的单词
    # @return{None} 无
    ======================================================================= """
    # 单词首字符列数
    start = 0
    # 单词尾字符列数
    end = 0

    while start < len(line):

        # 去掉行首的空格
        while line[start] == ' ':
            start += 1
            end += 1

        # #####################################################################
        #           单词首字符是letter，检查是否为关键字，标识符，char或者错误
        # #####################################################################
        if _is_letter(line[start]):
            # 将尾指针一直往后移动到单词结尾处,截取出单词
            end += 1
            while line[end] not in word_end_sign:
                end += 1

            # #################################################################
            #                            如果是关键字
            # #################################################################
            word = line[start:end]
            if word in key_words:
                # 进一步判断是否为 addop 或 mulop
                if word == 'or':
                    # 加入存放词法分析结果的list中
                    word_analyse_result.append(
                        [True, word, 'addop', line_num, start + 1]
                    )
                elif word == 'div' or word == 'mod' or word == 'and':
                    # 加入存放词法分析结果的list中
                    word_analyse_result.append(
                        [True, word, 'mulop', line_num, start + 1]
                    )
                else:
                    # 加入存放词法分析结果的list中
                    word_analyse_result.append(
                        [True, word, word, line_num, start + 1]
                    )

            # #################################################################
            #             如果不是关键字，可能是标识符，char或者错误单词
            # #################################################################

            # 如果单词长度大于8，则说明该单词不是合法标识符
            elif len(word) > 8:
                # 错误单词信息输出
                word_analyse_result.append(
                    [False, word, "The length of id is too long!",
                     line_num, start + 1]
                )

            # 如果该单词是由数字字母组成，则是合法标识符
            elif _is_identifier(word):
                # 加入存放词法分析结果的list中
                word_analyse_result.append(
                    [True, word, 'id', line_num, start + 1])

            # 这个单词不是是合法的标识符
            else:
                # 错误单词信息输出
                word_analyse_result.append(
                    [False, word,
                     'Unrecognizable id!', line_num, start + 1]
                )

            # 将单词开始指针向后移动
            start = end

        # #####################################################################
        #             单词首字符是数字，检测单词是否为int_num，real_num或者错误
        # #####################################################################
        elif _is_digit(line[start]):
            # 将尾指针一直往后移动到单词结尾处
            end += 1
            while line[end] not in word_end_sign:
                end += 1

            # #################################################################
            #                尾指针是'.','E+','E-'，单词还有后续部分
            # #################################################################
            if line[end] == '.' or line[end] == '+' or line[end] == '-':

                # #############################################################
                #                         如果有指数部分
                # #############################################################
                if line[end - 1] == 'E' and \
                        (line[end] == '+' or line[end] == '-'):
                    # 取出整数部分
                    integer_part = line[start:end]

                    exponent_start = end + 1
                    # 将尾指针一直往后移动到单词结尾处,截取出单词
                    end += 1
                    while line[end] not in word_end_sign:
                        end += 1
                    # 取出指数部分
                    exponent_part = line[exponent_start:end]

                    # 如果两部分是数字，则是正确的real类型
                    word = line[start:end]
                    if _is_integer(integer_part) \
                       and _is_integer(exponent_part):
                        word_analyse_result.append(
                            [True, word, 'real_num', line_num, start + 1]
                        )
                    else:
                        word_analyse_result.append(
                            [False, word,
                             'There have some invalid characters in word!',
                             line_num, start + 1]
                        )

                # #############################################################
                #                          如果还有有小数部分
                # #############################################################
                elif line[end] == '.' and line[end + 1] != '.':
                    # 取出整数部分
                    integer_part = line[start:end]

                    decimal_start = end + 1
                    # 将尾指针一直往后移动到单词结尾处,截取出单词
                    end += 1
                    while line[end] not in word_end_sign:
                        end += 1

                    # #########################################################
                    #                    如果小数部分后还有指数
                    # #########################################################
                    if line[end - 1] == 'E' and \
                            (line[end] == '+' or line[end] == '-'):
                        # 取出小数部分
                        decimal_part = line[decimal_start:end - 1]

                        exponent_start = end + 1
                        # 将尾指针一直往后移动到单词结尾处,截取出单词
                        end += 1
                        while line[end] not in word_end_sign:
                            end += 1
                        # 取出指数部分
                        exponent_part = line[exponent_start:end]

                        word = line[start:end]
                        # 只有三部分都是integer，这个单词才是一个real
                        if _is_integer(integer_part) \
                           and _is_integer(decimal_part) \
                           and _is_integer(exponent_part):
                            word_analyse_result.append(
                                [True, word, 'real_num', line_num, start + 1]
                            )

                        else:
                            word_analyse_result.append(
                                [False, word,
                                 'There have some invalid characters in word!',
                                 line_num, start + 1]
                            )

                    # #########################################################
                    #                     小数点后只有小数部分
                    # #########################################################
                    else:
                        # 取出小数部分
                        decimal_part = line[decimal_start:end]

                        word = line[start:end]
                        # 只有两部分都是整数，单词才是一个real
                        if _is_integer(integer_part) \
                           and _is_integer(decimal_part):
                            word_analyse_result.append(
                                [True, word, 'real_num', line_num, start + 1]
                            )

                        else:
                            word_analyse_result.append(
                                [False, word,
                                 'There have some invalid characters in word!',
                                 line_num, start + 1]
                            )

                # #############################################################
                #                 以'.'开头的'..'，其实只有整数部分
                # #############################################################
                if line[end] == '.' and line[end + 1] == '.':
                    # 取出整数部分
                    word = line[start:end]

                    # 如果不是整数，则返回错误信息
                    if not _is_integer(word):
                        word_analyse_result.append(
                            [False, word,
                             'There have some invalid characters in word!',
                             line_num, start + 1]
                        )

                    # 如果是整数
                    else:
                        word_analyse_result.append(
                            [True, word, 'int_num', line_num, start + 1]
                        )

            # #################################################################
            #                          单词只有整数部分
            # #################################################################
            else:
                word = line[start:end]
                # 如果不是整数，则返回错误信息
                if not _is_integer(word):
                    word_analyse_result.append(
                        [False, word,
                         'There have some invalid characters in word!',
                         line_num, start + 1]
                    )

                # 如果是整数
                else:
                    word_analyse_result.append(
                        [True, word, 'int_num', line_num, start + 1]
                    )

            # 将单词开始指针向后移动
            start = end

        # #####################################################################
        #             单词首字符是'=','<','>'，检测单词是否为relop或者错误
        # #####################################################################
        elif line[start] == '=' or line[start] == '<' or line[start] == '>':
            # 如果是'='
            if line[start] == '=':
                # 取出单词，放入结果中
                word_analyse_result.append(
                    [True, '=', 'relop', line_num, start + 1]
                )
                end += 1

            # 如果是'>'，'<'
            else:
                # 判断是否为'>=','<='
                if line[start + 1] == '=':
                    end += 2
                    # 取出单词
                    word = line[start:end]
                    word_analyse_result.append(
                        [True, word, 'relop', line_num, start + 1]
                    )

                # 如果不是'='，则说明是'>','<'
                else:
                    end += 1
                    # 取出单词
                    word = line[start:end]
                    word_analyse_result.append(
                        [True, word, 'relop', line_num, start + 1]
                    )

            # 将单词开始指针向后移动
            start = end

        # #####################################################################
        #                 单词首字符是'+','-'，检测单词是否为addop或者错误
        # #####################################################################
        elif line[start] == '+' or line[start] == '-':
            # 将尾指针往后移动一位,截取出单词
            end += 1
            word = line[start:end]

            # 加入存放词法分析结果的list中
            word_analyse_result.append(
                [True, word, 'addop', line_num, start + 1]
            )

            # 将单词开始指针向后移动
            start = end

        # #####################################################################
        #                 单词首字符是'*','/'，检测单词是否为mulop或者错误
        # #####################################################################
        elif line[start] == '*' or line[start] == '/':
            # 将尾指针向后移动一位,截取出单词
            end += 1
            word = line[start:end]

            # 加入存放词法分析结果的list中
            word_analyse_result.append(
                [True, word, 'mulop', line_num, start + 1]
            )

            # 将单词开始指针向后移动
            start = end

        # #####################################################################
        #           单词首字符是'.', ',', ';', '(', '[', '{'等分界符
        # #####################################################################
        elif line[start] in delimiters:
            # 判断是否为分界符'..'
            if line[start] == '.' and line[start + 1] == '.':
                word_analyse_result.append(
                    [True, '..', '..', line_num, start + 1]
                )
                end += 2

            else:
                # 将尾指针往后移动1位,截取出单词
                end += 1
                word = line[start:end]
                word_analyse_result.append(
                    [True, word, word, line_num, start + 1]
                )
            start = end

        # #####################################################################
        #                            单词首字符是':'
        # #####################################################################
        elif line[start] == ':':
            # 如果后一位是=，则说明该单词是':='
            if line[end + 1] == '=':
                word_analyse_result.append(
                    [True, ':=', 'assignop', line_num, start + 1]
                )
                end += 1

            # 其余情况为 ':'
            else:
                word_analyse_result.append(
                    [True, line[start:end+1], ':', line_num, start + 1]
                )
            end += 1
            start = end

        # #####################################################################
        #                           单词首字符是'\n'
        # #####################################################################
        elif line[start] == '\n':
            break

        # #####################################################################
        #                           其余情况均为错误
        # #####################################################################
        else:
            # 将尾指针一直往后移动到单词结尾处,截取出单词
            end += 1
            while line[end] not in word_end_sign:
                end += 1

            word = line[start:end]
            word_analyse_result.append([False, word,
                                        'The first letter of word is bad!',
                                        line_num, start + 1])

            start = end


"""" ==========================================================================
#
#                                    对外函数
#
=========================================================================== """


def word_analyse(filename):
    """" ======================================================================
    # @brief        将文本中的Pascal代码读入内存，将词法分析结果返回给下一模块
    # @param        存放Pascal代码的文本文件的绝对路径
    # @return{list} 完成词法分析的记号流，存放在list中
    ======================================================================= """

    # 用于存放从文本中读到的Pascal代码
    source_code = []
    # 用于存放完成词法分析的记号流
    word_analyse_result = []

    # 将文本中Pascal代码读入内存
    _load_code(filename, source_code)

    # 用于记录这是第几行
    line_num = 1
    # 按行进行词法分析
    for line in source_code:

        # 如果这一行是空行，不处理
        if line[0] == '\n':
            # 行数+1
            line_num += 1
            continue

        # 这一行不是空行，则处理
        else:
            # 对这一行单词进行词法分析
            _analyse(line, line_num, word_analyse_result)
            # 行数+1
            line_num += 1

    # 检查词法分析的正确性,flag用于标记词法分析正确性
    flag = _is_analyse_correct(word_analyse_result)

    # 完成词法分析后，返回分析结果
    if flag:
        return word_analyse_result
    else:
        return []

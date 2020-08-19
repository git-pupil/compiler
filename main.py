from wordanalyse import word_analyse
from grammar_analyse import grammar_analyse
from semantics_analysis import *
from symbol_table import *

filename=[
    "test/word_analyse_test1", # 词法分析 用于测试数字读取
    "test/word_analyse_test2", # 词法分析 用于测试程序段
    "test/word_analyse_test3", # 词法分析 用于测试是否完成各种注释（含多行注释）过滤
    "test/example3.pas",    # 3
    "test/gcd.pas",         # 4
    "test/quicksort.pas",   # 5
    "test/semantics_err1.pas",  # 6
    "test/semantics_err2.pas",  # 7
    "test/test_array.pas",      # 8
    "test/test_const_declarations.pas", # 9
    "test/test_for.pas",        # 10
    "test/test_program.pas",    # 11
    "test/test_subprogram_declarations.pas",    # 12
    "test/test_var_addr.pas",   # 13
    "test/test_var_declarations.pas",   # 14
    "test/right_example.pas",   # 15
    "test/grammar_right_1.pas",  # 16 语法测试 正例1 - 非常简单，便于测试
    "test/grammar_right_2.pas",  # 17 语法测试 正例2 - PPT的正确代码示例
    "test/semantics_right.pas"  # 18
]

result = word_analyse(filename[15])

# for word in result:
#     print(word)

grammar_tree=grammar_analyse(result)


sematic = SemanticAnalyzer(grammar_tree)
sematic.programstruct()

if sematic.result:
    print('语义分析正确')
sematic.st_manager.output_table_item()

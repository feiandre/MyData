import io
import os
import logging


# 代码语句分类
CODE = 'code'
BLANK = 'blank'
INLINE = 'inline'
BLOCK = 'block'

# 语言类型 语言类型和备注字符可以自定义
languages = {
    'python': {
        'lang': 'python',
        'for_short': 'python',
        'suffix': 'py',
        'inline_mark': '#',
        'block_mark': [("'''", "'''"),('"""','"""'),("r'''", "'''"),('r"""','"""')]
    },
    'sql': {
        'lang': 'sql',
        'for_short': 'sql',
        'suffix': 'sql',
        'inline_mark': '--',
        'block_mark': [('/*', '*/')]
    },
    'javascript': {
        'lang': 'javascript',
        'for_short': 'js',
        'suffix': 'js',
        'inline_mark': r"//",
        'block_mark': [('/*', '*/')]
    }
}

class CodeCounter:

    def __init__(self, lang='python', is_cum=False):
        """初始化代码计数实例
            :param version: 版本号 可空
            :param lang: 默认python语言
                language字典里定义的语言类型 python, sql, javascript
            :param cum: 代码行数是否累计计数
        """
        self.code_count = 0 # 代码
        self.blank_count = 0 # 空行
        self.inline_remark_count = 0
        self.block_remark_count = 0
        self.total_remark_count = 0 # 注释
        self.is_cum = is_cum
        self.language = languages[lang]
            


    def count_code(self, content, language=None):
        """统计script文件中代码行数
            :param content: 代码内容或者代码文本文件或者为文件描述符
            :param language: 传入的代码的语言类型 默认为实例初始化时的语言
        """
        if self.is_cum == False:
            self.code_count, self.blank_count, self.remark_count = 0, 0, 0

        if isinstance(content, io.TextIOWrapper):
            lines = content.read()
        elif os.path.isfile(content):
            with open(content, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        else:
            lines = io.StringIO(content)
        
        if language is None:
            lang = self.language
        else:
            lang = languages[language]

        def is_code(line):
            """先判断文本行是否是代码行
                            或者空白行
                            或者行内注释
                :param line: 一行文本行
            """
            if line is None:
                return BLANK
            elif line.strip().startswith(lang['inline_mark']):
                return INLINE
            elif len(line.strip()) == 0:
                return BLANK
            else:
                return CODE
        

        block_lines = []
        start = ''
        end = ''
        for line in lines:
            if is_code(line) == INLINE:
                self.inline_remark_count += 1
            elif is_code(line) == BLANK:
                self.blank_count += 1
            elif is_code(line) == CODE:
                if  len(block_lines) == 0:
                    for block_remark in lang['block_mark']:
                        start = block_remark[0]
                        end = block_remark[1]

                        if line.strip().startswith(start):
                            block_lines.append(line)
                            logging.debug('b1',line)
                            self.block_remark_count += 1
                            break
                    else:
                        self.code_count += 1
                        logging.debug('c',line)
                elif len(block_lines) > 0 and line.strip().endswith(end):
                    self.block_remark_count += 1
                    logging.debug('b2',line)
                    block_lines = []
                elif len(block_lines) > 0 and not line.strip().endswith(end):
                    self.block_remark_count += 1
                    logging.debug('b3',line)
        self.remark_count = self.inline_remark_count + self.block_remark_count
        return (
            ('language', 
            'code', 
            'blank', 
            'inline', 
            'block', 
            'remark'), 
            (lang['lang'], 
            self.code_count,
             self.blank_count, 
             self.inline_remark_count,
              self.block_remark_count, 
              self.remark_count)
            )


if __name__ == "__main__":
    # logging.getLevelName()
    counter = CodeCounter()
    res = counter.count_code("code_demo.py")
    print(res)

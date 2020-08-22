class Builder:

    def __init__(self):

        self.indent = 0
        self.lines = []

    def line(self, line):

        self.lines.append(f'{"    " * self.indent}{line}')
        return self

    def line_empty(self, n: int = 1):

        for _ in range(n): self.lines.append('')
        return self

    def nl(self):

        self.line('')
        return self

    def tab(self, t: int = 1):

        self.indent = max(0, self.indent + t)
        return self

    def anchor_namespace_begin(self):

        self.line('EPI_NAMESPACE_BEGIN()')
        return self

    def anchor_namespace_end(self):

        self.line('EPI_NAMESPACE_END()')
        return self

    def anchor_gen_region(self, caption):

        self.line(f'EPI_GENREGION_BEGIN({caption})')
        return self

    def anchor_gen_endregion(self, caption):

        self.line(f'EPI_GENREGION_END({caption})')
        return self

    def template(self, name: str, **kwargs):

        import os

        dirname = os.path.dirname(__file__)
        path = f'{dirname}/templates/{name}.txt'
        with open(path, 'r') as f:
            content = f.read()

        for k in kwargs:
            assert content.find(f'${{{k}}}') != -1, f'The provided placeholder=`{k}` should be presented in a template at least once'

        for line in content.splitlines():

            for k, v in kwargs.items():
                line = line.replace(f'${{{k}}}', v)

            self.line(line)

        return self

    def build(self):
        return '\n'.join(self.lines)

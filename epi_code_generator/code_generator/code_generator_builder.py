class Builder:

    def __init__(self):

        self.indent = 0
        self.lines = []
        self.genregion_anchor = False
        self.namespace_anchor = False

    def line(self, line):
        self.lines.append(f'{"    " * self.indent}{line}')

    def line_empty(self, n: int = 1):
        for _ in range(n): self.lines.append('')

    def tab(self, t: int = 1):
        self.indent = max(0, self.indent + t)

    def anchor_namespace_begin(self):

        assert not self.namespace_anchor
        self.lines.append('EPI_NAMESPACE_BEGIN()')
        self.namespace_anchor = True

    def anchor_namespace_end(self):

        assert self.namespace_anchor
        self.lines.append('EPI_NAMESPACE_END()')
        self.namespace_anchor = False

    def anchor_gen_region(self, caption):

        assert not self.genregion_anchor

        self.lines.append(f'EPI_GENREGION_BEGIN({caption})')
        self.genregion_anchor = True

    def anchor_gen_endregion(self, caption):

        assert self.genregion_anchor
        self.lines.append(f'EPI_GENREGION_END({caption})')
        self.genregion_anchor = False

    def build(self):

        assert not self.genregion_anchor
        assert not self.namespace_anchor

        return '\n'.join(self.lines)

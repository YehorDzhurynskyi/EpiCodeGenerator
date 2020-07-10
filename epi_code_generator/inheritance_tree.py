from enum import Enum, auto

from .symbol import EpiClass


class InheritanceErrorCode(Enum):

    NoSuchParent = auto()
    DuplicatingSymbol = auto()


INHERITANCE_ERROR_MSGS = {
    InheritanceErrorCode.NoSuchParent: 'No such parent was found',
    InheritanceErrorCode.DuplicatingSymbol: 'Such symbol is already exists'
}

class InheritanceError(Exception):

    def __init__(self, clss: EpiClass, err_code: InheritanceErrorCode, tip: str = ''):

        assert isinstance(clss, EpiClass)
        self.clss = clss
        self.err_code = err_code
        self.err_message = INHERITANCE_ERROR_MSGS[err_code]
        self.tip = tip

    def __str__(self):

        s = f'Linking error {str(self.clss)}: {self.err_message}'
        if len(self.tip) != 0:
            s = f'{s} ({self.tip})'

        return s


class InheritanceTree:

    class Node:

        def __init__(self, clss: EpiClass, parent):

            assert isinstance(clss, EpiClass)

            self.clss = clss
            self.parent = parent
            self.is_leaf = True

    def __init__(self, registry: dict):

        self.nodes = {}
        self._build(registry)

    def _build(self, registry: dict):

        def _insert(k: str, v: EpiClass):

            parent = None
            if v.parent is not None:

                if v.parent not in registry:
                    raise InheritanceError(v, InheritanceErrorCode.NoSuchParent, f'parent: {v.parent}')

                parent = self.nodes[v.parent] if v.parent in self.nodes else _insert(v.parent, registry[v.parent])
                parent.is_leaf = False

            node = InheritanceTree.Node(v, parent)
            self.nodes[k] = node

            return node

        for k, v in registry.items():

            if k in self.nodes:
                continue

            _insert(k, v)

        self._validate()

    def _validate(self):

        memo = {}

        def is_valid(key: str, node: InheritanceTree.Node):

            assert isinstance(node.clss, EpiClass)

            def validate_pedigree(node: InheritanceTree.Node, prts_inherited: set):

                if node.parent is None:

                    memo[key] = True
                    return memo[key]

                prts_parent = set(p.name for p in node.parent.clss.properties)
                prts_intersection = prts_inherited & prts_parent
                if len(prts_intersection) == 0:
                    memo[key] = validate_pedigree(node.parent, prts_inherited.union(prts_parent))
                else:

                    verb = 'is' if len(prts_intersection) == 1 else 'are'
                    tip = f'{",".join(prts_intersection)} {verb} already defined in {node.parent.clss.token.filepath}'
                    raise InheritanceError(node.clss, InheritanceErrorCode.DuplicatingSymbol, tip)

                return memo[key]

            if key in memo:
                return memo[key]

            prts = set(p.name for p in node.clss.properties)
            return validate_pedigree(node, prts)

        leafs = { k: v for k, v in self.nodes.items() if v.is_leaf }

        valid = True
        for k, v in leafs.items():

            if not is_valid(k, v):
                valid = False
                break

        assert valid

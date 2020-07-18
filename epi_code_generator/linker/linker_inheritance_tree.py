from epi_code_generator.linker import linker as ln

from epi_code_generator.tokenizer import TokenType

from epi_code_generator.symbol.symbol import EpiSymbol
from epi_code_generator.symbol.symbol import EpiClass

import zlib


class InheritanceTree:

    class Node:

        def __init__(self, clss: EpiClass, parent):

            assert isinstance(clss, EpiClass)

            self.clss = clss
            self.parent = parent
            self.is_leaf = True

    def __init__(self, registry: dict):

        self.nodes = {}
        self.__registry = registry

    def build(self, linker: ln.Linker):

        def _insert(name: str, sym: EpiClass) -> InheritanceTree.Node:

            parent = None
            if sym.parent is not None:

                if sym.parent not in self.__registry:

                    tip = f'Invalid parent name: {sym.parent}'
                    linker._push_error(sym, ln.LinkerErrorCode.NoSuchSymbol, tip)

                parent = self.nodes[sym.parent] if sym.parent in self.nodes else _insert(sym.parent, self.__registry[sym.parent])
                parent.is_leaf = False

            node = InheritanceTree.Node(sym, parent)
            self.nodes[name] = node

            return node

        for name, sym in self.__registry.items():

            assert isinstance(sym, EpiClass)

            if name in self.nodes:
                continue

            _insert(name, sym)

    def validate(self, linker: ln.Linker):

        memo = {}

        def _validate(key: str, node: InheritanceTree.Node):

            assert isinstance(node.clss, EpiClass)

            def _pids(properties: list) -> set:
                return [(p, hex(zlib.crc32(p.name.encode()) & 0xffffffff)) for p in properties]

            def _validate_properties(node: InheritanceTree.Node, prts: list):

                if node.parent is None:

                    memo[key] = True
                    return memo[key]

                pids = _pids(prts)
                pids_parent = _pids(node.parent.clss.properties)

                import itertools

                generator_pids_pids = ((lhs, rhs) for lhs, rhs in itertools.product(pids))
                generator_pids_pids_parent = ((lhs, rhs) for lhs in pids for rhs in pids_parent)

                def _validate_duplicates(node: InheritanceTree.Node, generator):

                    for lhs, rhs in generator:
                        if lhs[0].name == rhs[0].name:

                            tip = f'The symbol duplicates {rhs[0].name}'
                            linker._push_error(lhs[0], ln.LinkerErrorCode.DuplicatingSymbol, tip)

                        if lhs[1] == rhs[1]:

                            tip = f'Hash collision with {rhs[0].name}'
                            linker._push_error(lhs[0], ln.LinkerErrorCode.HashCollision, tip)

                _validate_duplicates(node, generator_pids_pids)
                _validate_duplicates(node, generator_pids_pids_parent)

                prts = prts[:]
                prts.extend(node.parent.clss.properties[:])
                memo[key] = _validate_properties(node.parent, prts)

                return memo[key]

            if key in memo:
                return memo[key]

            return _validate_properties(node, node.clss.properties)

        leafs = { k: v for k, v in self.nodes.items() if v.is_leaf }

        for k, v in leafs.items():
            _validate(k, v)

        for node in self.nodes.values():

            for p in (p for p in node.sym.properties if p.tokentype == TokenType.Identifier):
                if p.tokentype.text not in self.nodes:

                    tip = f'No such symbol exists with a name {p.tokentype.text}'
                    linker._push_error(p, ln.LinkerErrorCode.NoSuchSymbol, tip)


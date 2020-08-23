from epigen.linker import linker as ln

from epigen.symbol import EpiSymbol
from epigen.symbol import EpiClass
from epigen.symbol import EpiEnum

import zlib


class InheritanceTree:

    class Node:

        def __init__(self, clss: EpiClass, parent):

            assert isinstance(clss, EpiClass)

            self.clss = clss
            self.parent = parent
            self.is_leaf = True

    def __init__(self, registry: dict):

        self.__clss_nodes = {}
        self.__registry = registry

    def build(self, linker: ln.Linker):

        def _insert(name: str, sym: EpiClass) -> InheritanceTree.Node:

            parent = None
            if sym.parent is not None:

                if sym.parent not in self.__registry:

                    tip = f'Invalid parent name: {sym.parent}'
                    linker._push_error(sym, ln.LinkerErrorCode.NoSuchSymbol, tip)
                else:

                    parent = self.__clss_nodes[sym.parent] if sym.parent in self.__clss_nodes else _insert(sym.parent, self.__registry[sym.parent])
                    parent.is_leaf = False

            node = InheritanceTree.Node(sym, parent)
            self.__clss_nodes[name] = node

            return node

        for name, clss in ((name, sym) for name, sym in self.__registry.items() if isinstance(sym, EpiClass)):

            if name in self.__clss_nodes:
                continue

            _insert(name, clss)

    def validate(self, linker: ln.Linker):

        for _, enum in ((name, sym) for name, sym in self.__registry.items() if isinstance(sym, EpiEnum)):
            self._validate_enum(enum, linker)

        self._validate_classes(linker)

    def _validate_enum(self, enum: EpiEnum, linker: ln.Linker):

        assert isinstance(enum, EpiEnum)

        entries_entries = [(lhs, rhs) for lhs in enum.entries for rhs in enum.entries]

        # NOTE: `entries_entries` is cartesian product A * A,
        # so we need exclude (a0, a0), (a1, a1) and (a0, a1), (a1, a0) pairs
        ii = 0
        entries_len = len(enum.entries)
        for i in range(entries_len):

            del entries_entries[i + ii : entries_len + ii]
            ii += i

        for lhs, rhs in entries_entries:

            if lhs.name == rhs.name:

                tip = f'The symbol has been already defined in `{rhs.token.modulepath}`'
                linker._push_error(lhs, ln.LinkerErrorCode.DuplicatingSymbol, tip)

    def _validate_classes(self, linker: ln.Linker):

        memo = {}

        def _validate(key: str, node: InheritanceTree.Node):

            assert isinstance(node.clss, EpiClass)

            def _pids(properties: list) -> set:
                return [(p, hex(zlib.crc32(p.name.encode()) & 0xffffffff)) for p in properties]

            def _validate_properties(node: InheritanceTree.Node, prts: list):

                def _validate_duplicates(pid_pairs: list):

                    for lhs, rhs in pid_pairs:

                        if lhs[0].name == rhs[0].name:

                            tip = f'The symbol has been already defined in `{rhs[0].token.modulepath}`'
                            linker._push_error(lhs[0], ln.LinkerErrorCode.DuplicatingSymbol, tip)

                        elif lhs[1] == rhs[1]:

                            tip = f'Hash collision with `{rhs[0].name}` defined in `{rhs[0].token.modulepath}`'
                            linker._push_error(lhs[0], ln.LinkerErrorCode.HashCollision, tip)

                pids = _pids(prts)
                pids_pids = [(lhs, rhs) for lhs in pids for rhs in pids]

                # NOTE: `pids_pids` is cartesian product A * A,
                # so we need exclude (a0, a0), (a1, a1) and (a0, a1), (a1, a0) pairs
                ii = 0
                pids_len = len(pids)
                for i in range(pids_len):

                    del pids_pids[i + ii : pids_len + ii]
                    ii += i

                _validate_duplicates(pids_pids)

                if node.parent is None:

                    memo[key] = True
                    return memo[key]

                pids_parent = _pids(node.parent.clss.properties)
                pids_pids_parent = [(lhs, rhs) for lhs in pids for rhs in pids_parent]

                _validate_duplicates(pids_pids_parent)

                prts = prts[:]
                prts.extend(node.parent.clss.properties[:])
                memo[key] = _validate_properties(node.parent, prts)

                return memo[key]

            if key in memo:
                return

            _validate_properties(node, node.clss.properties)

        leafs = { k: v for k, v in self.__clss_nodes.items() if v.is_leaf }

        for k, v in leafs.items():
            _validate(k, v)

        for node in self.__clss_nodes.values():

            for inner in node.clss.inner().values():
                self._validate_enum(inner, linker)


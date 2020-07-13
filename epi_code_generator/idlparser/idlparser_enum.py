'''
def _parse_enum(self):

    t = self._next()
    if t.tokentype != TokenType.EnumType:
        return None

    t = self._next()
    if t.tokentype != TokenType.Identifier:
        return None

    enum = EpiEnum(t.text)

    t = self._next()
    if t.tokentype != TokenType.OpenBrace:
        return None

    while True:

        t = self._curr()
        if t.tokentype == TokenType.CloseBrace:
            break
        else:
            enum_entry = self._parse_enum_entry()
            if not enum_entry:
                return None

            enum.entries.append(enum_entry)

    t = self._next(2)
    if t.tokentype != TokenType.Semicolon:
        return None

    return enum

def _parse_enum_entry(self):

    t = self._next()
    if t.tokentype != TokenType.Identifier:
        return None

    return EpiEnumEntry(t.text)
'''

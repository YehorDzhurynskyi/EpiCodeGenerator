'''
def _parse_interface(self):

    t = self._next()
    if t.tokentype != TokenType.InterfaceType:
        return None

    t = self._next()
    if t.tokentype != TokenType.Identifier:
        return None

    interface = EpiInterface(t.text)

    t = self._curr()
    if t.tokentype == TokenType.Colon:

        t = self._next(2)
        if t.tokentype != TokenType.Identifier:
            return None

        interface.parent = t.text

    t = self._next()
    if t.tokentype != TokenType.OpenBrace:
        return None

    while True:

        t = self._curr()
        if t.tokentype == TokenType.CloseBrace:
            self._next()
            break
        else:
            method = self._parse_method()
            if not method:
                return None

            interface.methods.append(method)

    t = self._next()
    if t.tokentype != TokenType.Semicolon:
        return None

    return interface
'''

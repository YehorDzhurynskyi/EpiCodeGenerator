
'''
def _parse_method(self):

    rt_t = self._parse_variable(has_name=False)
    if not rt_t:
        return None

    fn_t = self._next()
    if fn_t.tokentype != TokenType.Identifier:
        return None

    method = EpiMethod(fn_t.text)

    t = self._next()
    if t.tokentype != TokenType.OpenBracket:
        return None

    while self._is_next_variable():

        param = self._parse_variable(has_name=True)
        if not param:
            return None

        method.params.append(param)

        t = self._curr()
        if t.tokentype != TokenType.Comma:
            break

        self._next()

    t = self._next()
    if t.tokentype != TokenType.CloseBracket:
        return None

    t = self._next()
    if t.tokentype != TokenType.Semicolon:
        return None

    return method
'''

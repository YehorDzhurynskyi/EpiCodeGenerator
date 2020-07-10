
'''
def _parse_method(self):

    rt_t = self._parse_variable(has_name=False)
    if not rt_t:
        return None

    fn_t = self._next()
    if fn_t.type != TokenType.Identifier:
        return None

    method = EpiMethod(fn_t.text)

    t = self._next()
    if t.type != TokenType.OpenBracket:
        return None

    while self._is_next_variable():

        param = self._parse_variable(has_name=True)
        if not param:
            return None

        method.params.append(param)

        t = self._curr()
        if t.type != TokenType.Comma:
            break

        self._next()

    t = self._next()
    if t.type != TokenType.CloseBracket:
        return None

    t = self._next()
    if t.type != TokenType.Semicolon:
        return None

    return method
'''

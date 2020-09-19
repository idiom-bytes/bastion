def dex_sample() :
    symbol = Variable()

    # Cannot set breakpoint in @construct
    @construct
    def seed(s_symbol: str):
        symbol.set(s_symbol)

    @export
    def symbol():
        return symbol.get()
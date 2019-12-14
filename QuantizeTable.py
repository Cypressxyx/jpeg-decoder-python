class QuantizeTable:
    def __init__(self, stream):
        self.tables = decode_quantize_stream(stream)


def decode_quantize_stream(stream):
    high_bit = stream.pop(0)
    low_bit = stream.pop(0)
    stream_length = (high_bit | low_bit) - 2 # remove low and high bits
    tables = {}
    while stream:
        table_idx = stream.pop(0)
        table = []
        for i in range(64):
            table.append(stream.pop(0))
        tables[table_idx] = table
    return tables

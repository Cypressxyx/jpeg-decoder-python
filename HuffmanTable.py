class HuffmanTable:
    def __init__(self, stream):
        self.tables, self.code_lengths = decode_huffman_table(stream)
    def get_table(self):
        return self.tables
    def get_code_lengths(self):
        return self.code_lengths


def decode_huffman_table(stream):
    tables = {}
    all_code_lengths = {}
    # remove ht len
    #length = stream.pop(0) | stream.pop(0)
    curr_table = 0
    curr_code_len = 0
    while stream:
        #stream.pop(0)  #remove table type
        length = stream.pop(0) | stream.pop(0)
        stream.pop(0)  #remove table type
        # save first 16 code lengths, look into uint 16
        code_lengths = []
        code_length_count = 0
        for i in range(16): # max of 16 code lengths
            value = stream.pop(0)
            code_lengths.append(value)
            code_length_count += value
        all_code_lengths[curr_code_len] = code_lengths
        curr_code_len += 1

        # save the code Values
        values = [stream.pop(0) for i in range(code_length_count)]

        # map bits to values
        mappings = {}
        mapping_value = 0
        itr = 0
        for value in code_lengths:
            for j in range(value):
                mappings[mapping_value] = values[itr]
                itr += 1
                mapping_value += 1
            mapping_value <<= 1
        tables[curr_table] = mappings
        curr_table += 1
        #if stream:
            #stream.pop(0)  # remove ht type
    return tables, all_code_lengths
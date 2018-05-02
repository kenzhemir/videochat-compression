import numpy as np


class LZW():
    def __init__(self):
        self.dictionary = {}
        for i in range(256):
            self.dictionary[i] = i


class CompressorLZW(LZW):
    # Compression function
    def compress(self, uncompressed, withColorMap=False):

        # Declare variables
        if withColorMap:
            colormap = []
        compressed = []  # compressed image
        bseq = ""  # binary sequence for encoding
        CR = None  # current sequence

        for row in uncompressed:
            for P in row:
                if CR == None:  # for the first pixel
                    CR = P
                    continue

                # New sequence
                CS = CR + [P] if isinstance(CR, list) else [CR, P]
                if tuple(CS) in self.dictionary:
                    # if new sequence is already in dictionary, then move on
                    CR = CS
                else:
                    # if new sequence is not in dictionary
                    # write previous sequence (CR)
                    # save new sequence to dictionary
                    key = tuple(CR) if isinstance(CR, list) else CR

                    # for colormapping we need the length of CR
                    if withColorMap:
                        if type(CR) == np.uint8:
                            colormap.append(1)
                        else:
                            colormap.append(len(CR))

                    value = self.dictionary[key]
                    # number of bits for dictionary size
                    dictlen = np.int(np.ceil(np.log2(len(self.dictionary))))
                    # add new value to bitstream
                    bseq += "{0:0{size}b}".format(value, size=dictlen)

                    # add all available bytes to encoded array
                    # and leave remainder in bitstream
                    seqlen = len(bseq) - (len(bseq) % 8)
                    seq = bseq[:seqlen]
                    bseq = bseq[seqlen:]
                    compressed += [
                        int(seq[(8 * i):(8 * (i + 1))], 2)
                        for i in range(int(seqlen / 8))
                    ]

                    # add new sequence to dictionary
                    self.dictionary[tuple(CS)] = len(self.dictionary)

                    # rewrite current sequence
                    CR = P

        # Write down last bits
        if isinstance(CR, list):
            key = tuple(CR) if isinstance(CR, list) else CR
            value = self.dictionary[key]
            dictlen = np.int(np.ceil(np.log2(len(self.dictionary))))
            bseq += "{0:0{size}b}".format(value, size=dictlen)
            bseq += '0' * ((8 - len(bseq) % 8) % 8)
            for i in range(np.int(len(bseq) / 8)):
                compressed.append(int(bseq[0:8], 2))
                bseq = bseq[8:]

        # convert array
        compressed = np.array(compressed, dtype='uint8')
        self.compressedsize = compressed.size
        self.uncompressedsize = uncompressed.size
        if withColorMap:
            return compressed, colormap
        else:
            return compressed


class DecompressorLZW(LZW):
    def decompress(self, compressed):

        # Read first byte and initialize variables
        CR = [compressed[0]]  # previous code
        uncompressed = CR  # uncompressed bytes array
        bseq = ""  # bitstream
        i = 1  # iterator over input compressed file
        dict_size = 256  # size of dictionary

        # loop through all compressed bytes
        while i < len(compressed):
            # number of bits in dictionary length
            dictlenbit = np.int(np.ceil(np.log2(dict_size + 1)))

            # Read bytes until enough for reading encoded value
            while len(bseq) < dictlenbit:
                if i >= len(compressed):
                    break
                bseq += "{0:08b}".format(compressed[i])
                i += 1
            # save encoded value, left remainder in bitstream
            enc = bseq[:dictlenbit]
            bseq = bseq[dictlenbit:]

            # Decode value using dictionary or deduce if it should be generated
            key = int(enc, 2)
            if key in self.dictionary:
                P = self.dictionary[key]
            elif key == dict_size:
                P = CR + [CR[0]]
            else:
                raise ValueError("Bad coding")
            # save value and add new entry to dictionary
            self.dictionary[dict_size] = CR + [P[0]]
            dict_size += 1
            uncompressed += P
            CR = P
        uncompressed = np.array(uncompressed)
        return uncompressed
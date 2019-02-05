import string


class BytesIntEncoder:  # Ref: https://stackoverflow.com/a/54500910/

    def __init__(self, chars: bytes = (string.ascii_letters + string.digits).encode()):
        num_chars = len(chars)
        translation = ''.join(chr(i) for i in range(1, num_chars + 1)).encode()
        self._translation_table = bytes.maketrans(chars, translation)
        self._reverse_translation_table = bytes.maketrans(translation, chars)
        self._num_bits_per_char = (num_chars + 1).bit_length()

    def encode(self, chars: bytes) -> int:
        num_bits_per_char = self._num_bits_per_char
        output, bit_idx = 0, 0
        for chr_idx in chars.translate(self._translation_table):
            output |= (chr_idx << bit_idx)
            bit_idx += num_bits_per_char
        return output

    def decode(self, i: int) -> bytes:
        maxint = (2 ** self._num_bits_per_char) - 1
        output = bytes(((i >> offset) & maxint) for offset in range(0, i.bit_length(), self._num_bits_per_char))
        return output.translate(self._reverse_translation_table)


# Test
import itertools
import random
import unittest


class TestBytesIntEncoder(unittest.TestCase):

    chars = string.ascii_letters + string.digits
    encoder = BytesIntEncoder(chars.encode())

    def _test_encoding(self, b_in: bytes) -> None:
        i = self.encoder.encode(b_in)
        self.assertIsInstance(i, int)
        b_out = self.encoder.decode(i)
        self.assertIsInstance(b_out, bytes)
        self.assertEqual(b_in, b_out)
        # print(b_in, i)

    def test_thoroughly_with_small_str(self):
        for s_len in range(4):
            for s in itertools.combinations_with_replacement(self.chars, s_len):
                s = ''.join(s)  # type: ignore
                b_in = s.encode()  # type: ignore
                self._test_encoding(b_in)

    def test_randomly_with_large_str(self):
        for s_len in range(256):
            num_samples = {s_len <= 16: 2 ** s_len,
                           16 < s_len <= 32: s_len ** 2,
                           s_len > 32: s_len * 2,
                           s_len > 64: s_len,
                           s_len > 128: 2}[True]
            # print(s_len, num_samples)
            for _ in range(num_samples):
                b_in = ''.join(random.choices(self.chars, k=s_len)).encode()
                self._test_encoding(b_in)


if __name__ == '__main__':
    unittest.main()


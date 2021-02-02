import unittest
from unittest.mock import patch
from logdna.utils import is_jsonable, sanitize_meta, get_ip

IP = '10.0.50.10'
VIP = '10.1.60.20'


class JSONTest(unittest.TestCase):
    def setUp(self):
        self.valid = {'key': 'value'}
        self.invalid = {'key': set()}

    def test_serialize_valid_json(self):
        self.assertTrue(is_jsonable(self.valid), 'json serializeble = True')

    def test_serialize_invalid_json(self):
        self.assertFalse(is_jsonable(self.invalid),
                         'non json serializable = False')


class SanitizeTest(unittest.TestCase):
    def setUp(self):
        self.valid = {'foo': 'bar', 'baz': 'whizbang'}
        self.invalid = {'bar': 'foo', 'baz': set()}

    def test_sanitize_simple(self):
        clean = sanitize_meta(self.valid)
        self.assertDictEqual(clean, self.valid)

    def test_sanitize_complex(self):
        clean = sanitize_meta(self.invalid)
        self.assertDictEqual(clean, {
            'bar': 'foo',
            '__errors': 'These keys have been sanitized: baz'
        })


class IPTest(unittest.TestCase):
    @patch('socket.socket', **{'return_value.connect.side_effect': OSError()})
    def test_get_ip_socket_error(self, _):
        self.assertEqual(get_ip(), '127.0.0.1',
                         'default to localhost on error')

    @patch(
        'socket.socket',
        **{'return_value.getsockname.return_value': [IP, VIP]}
    )
    def test_get_ip_default(self, _):
        self.assertEqual(get_ip(), IP, 'default to localhost on error')

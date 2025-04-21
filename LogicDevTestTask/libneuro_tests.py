import unittest

from LogicDevTestTask import InvalidCallStateError
from lib import libneuro
from unittest import mock

from lib.libneuro import NeuroNluRecognitionResult


class TestNN(unittest.TestCase):
    def setUp(self):
        self.nn = libneuro.NeuroNetLibrary(for_test=True)

    def test_nn_call(self):
        def test_call():
            pass

        dump = self.nn.call('test', entry_point=test_call)

        expected = {'msisdn': 'test', 'call_status': 'SUCCESS', 'call_transcription': None, 'result': None, 'films': None}
        fact = {k: dump.get(k) for k in expected}

        self.assertEqual(expected, fact)

    def test_nn_has_records(self):
        assert self.nn.has_records('hangup_hi', 'hangup_goodbye') == ['hangup_hi']

    def test_nn_env(self):
        self.nn.env('a', 1)
        self.nn.env(b=2)

        assert self.nn.env('a') == 1
        assert self.nn.env('b') == 2
        assert self.nn.env('с') is None


    def test_nn_counter(self):
        counter = self.nn.counter('some_counter')
        assert counter == 0

        counter = self.nn.counter('some_counter', '+')
        assert counter == 1

        counter = self.nn.counter('some_counter', 5)
        assert counter == 5

        counter = self.nn.counter('some_counter', '-')
        assert counter == 4

    def test_nn_log(self):
        name = 'test'
        assert self.nn.log(name, 'nn_log') == ['test_nn_log', name, 'nn_log']

    def test_nn_dump(self):
        self.nn.env(result='Проверка')
        assert self.nn.dump() == {
            'msisdn': None,
            'call_uuid': None,
            'call_start_time': None,
            'call_status': None,
            'call_transcription': None,
            'result': 'Проверка',
            'films': None,
        }

    def test_nn_storage(self):
        assert self.nn.storage('BASE_URL') == 'https://api.kinopoisk.dev/v1.4/movie'
        assert self.nn.storage('HOST') is None


class TestNV(unittest.TestCase):
    def setUp(self):
        self.nv = libneuro.NeuroVoiceLibrary(for_test=True)

    def test_nv_say(self):
        self.assertEqual(self.nv.say('hangup_goodbye'), 'До свидания!')

    def test_nv_synthesize(self):
        self.assertEqual(self.nv.synthesize('До свидания!'), 'До свидания!')

    @mock.patch('builtins.input', side_effect=['Привет!'])
    def test_nv_listen(self, mocked_input):
        with self.nv.listen() as result:
            pass

        self.assertEqual(result.utterance(), 'привет')

    def test_nv_set_default(self):
        self.nv.set_default('listen', entities=['horror'])
        self.assertEqual(self.nv.DEFAULT_PARAMS, {'listen': {'entities': ['horror']}})

    def test_nv_hangup(self):
        with self.assertRaises(InvalidCallStateError):
            self.nv.hangup()


class TestResult(unittest.TestCase):
    side_effect = ['Ну не знаю, пусть будет сериал']

    @mock.patch('builtins.input', side_effect=side_effect)
    def test_utterance(self, mocked_input):
        with NeuroNluRecognitionResult() as result:
            pass

        self.assertEqual(result.utterance(), 'ну не знаю пусть будет сериал')

    @mock.patch('builtins.input', side_effect=side_effect)
    def test_all_entity(self, mocked_input):
        with NeuroNluRecognitionResult() as result:
            pass

        self.assertEqual(result.entity('dont_know'), 'true')
        self.assertEqual(result.entity('series'), 'true')
        self.assertEqual(result.entity('horror'), None)

    @mock.patch('builtins.input', side_effect=side_effect)
    def test_not_all_entity(self, mocked_input):
        with NeuroNluRecognitionResult(entities=['horror']) as result:
            pass

        self.assertEqual(result.entity('dont_know'), None)
        self.assertEqual(result.entity('series'), None)
        self.assertEqual(result.entity('horror'), None)


if __name__ == '__main__':
    unittest.main()

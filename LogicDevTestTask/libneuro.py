import datetime
import inspect
import pprint
from time import sleep
from uuid import uuid4

from lib.content import ENTITIES, PROMPTS, STORAGE, OUTPUT_PARAMS


class InvalidCallStateError(Exception):
    pass


class NeuroNetLibrary:
    _env = {}

    def __init__(self, for_test=False, **env):
        self.__for_test = for_test
        self._counters = {}
        self._env = env

    def call(self, msisdn: str, entry_point: callable, after_call: callable = None):
        try:
            if not msisdn:
                raise Exception('Не указан номер телефона')

            call_start_time = str(datetime.datetime.now())

            with open('logs.txt', 'w', encoding='utf-8', errors='replace') as logs:
                pass

            if self.__for_test:
                self.log('=== TEST STARTED ===')
            else:
                self.log('=== CALL STARTED ===')

            self._env.update(msisdn=msisdn,
                             call_uuid=str(uuid4()),
                             call_start_time=call_start_time)
            entry_point()
        except Exception as e:
            self.log('nn.call: Ошибка во время выполнения entry_point', e)
            self._env.update(call_status='FAIL')
        else:
            self._env.update(call_status='SUCCESS')
        finally:
            if self.__for_test:
                self.log('=== TEST FINISHED ===')
            else:
                self.log('=== CALL FINISHED ===')

            try:
                if after_call:
                    return after_call()
            except Exception as e:
                self.log('nn.call: Ошибка во время выполнения after_call', e)
            finally:
                return self.dump()

    @staticmethod
    def has_records(*args):
        return [name for name in args if not isinstance(PROMPTS.get(name), str)]

    def env(self, *args, **kwargs):
        if args and kwargs:
            raise AttributeError

        if kwargs:
            self._env.update(kwargs)
            return

        if len(args) == 2:
            self._env.update({args[0]: args[1]})
            return

        return self._env.get(args[0])

    def counter(self, name, op=None):
        c = self._counters.setdefault(name, 0)
        if not op:
            return c
        elif op == '+':
            c += 1
        elif op == '-':
            c -= 1
        elif isinstance(op, int):
            c = op
        self._counters.update({name: c})
        return c

    def log(self, name, data=None):
        list_data = [str(_) for _ in [inspect.stack()[1][3], name, data] if _]
        with open('logs.txt', 'a', encoding='utf-8', errors='replace') as logs:
            logs.writelines(['\n', ' - '.join([str(datetime.datetime.now()), *list_data])])
        if self.__for_test:
            return list_data

    def dump(self):
        out = {k: self._env.get(k) for k in OUTPUT_PARAMS}
        if not self.__for_test:
            with open('logs.txt', 'a', encoding='utf-8', errors='replace') as logs:
                logs.write('\n\nDUMP:\n')
                logs.write(pprint.pformat(out))
        return out

    @staticmethod
    def storage(name):
        return STORAGE.get(name)


def print_partial_text(who: str, text: str):
    for i in range(len(text)):
        print(f'\r{who.upper()}: {text[:i + 1]}', end='')
        sleep(0.02)
    print(end='\n')


def get_clear_utterance(utterance):
    return utterance.replace('?', '').replace('!', '').replace(',', '').replace('.', '').strip().lower()


class NeuroVoiceLibrary:
    DEFAULT_PARAMS = {}

    def __init__(self, for_test=False):
        self.__for_test = for_test

    def say(self, prompt):
        text = PROMPTS.get(prompt, '')
        NeuroNetLibrary._env.setdefault('call_transcription', []).append({'bot': text})
        if self.__for_test:
            return text
        print_partial_text('bot', text)

    def synthesize(self, text):
        NeuroNetLibrary._env.setdefault('call_transcription', []).append({'bot': text})
        if self.__for_test:
            return text
        print_partial_text('bot', text)

    def listen(self, **kwargs):
        listen_params = self.DEFAULT_PARAMS.get('listen') or {}
        return NeuroNluRecognitionResult(**{k: kwargs.get(k) or listen_params.get(k) for k in ['entities']})

    def set_default(self, param, **kwargs):
        self.DEFAULT_PARAMS[param] = kwargs

    @staticmethod
    def hangup():
        raise InvalidCallStateError('Бот положил трубку')


class NeuroNluRecognitionResult:
    def __init__(self, **kwargs):
        self._utterance = ""
        self._entities = kwargs.get('entities') or list(ENTITIES)
        self._recognized_entities = {}

    def __enter__(self):
        return self

    def utterance(self):
        return self._utterance

    def __exit__(self, _type, _value, _traceback):
        utterance = input('HUMAN: ')
        self._utterance = get_clear_utterance(utterance)
        if self._utterance in ('h', 'hangup'):
            raise InvalidCallStateError('Абонент положил трубку')

        NeuroNetLibrary._env.setdefault('call_transcription', []).append({'human': utterance})

        for entity in self._entities:
            for flag, patterns in ENTITIES.get(entity, {}).items():
                if any(p.lower() in utterance.lower() for p in patterns):
                    self._recognized_entities[entity] = flag
                    break
        return self

    def entity(self, value):
        return self._recognized_entities.get(value)


def check_call_state(nv: NeuroVoiceLibrary):
    def wrapper(f):
        def inner(*args, **kwargs):
            try:
                f(*args, **kwargs)
            except InvalidCallStateError as i:
                raise i
        return inner
    return wrapper

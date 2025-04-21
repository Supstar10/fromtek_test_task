from lib import libneuro
import requests
from lib.content import PROMPTS, ENTITIES, STORAGE

# Инициализация библиотек
nn = libneuro.NeuroNetLibrary()
nv = libneuro.NeuroVoiceLibrary()
InvalidCallStateError = libneuro.InvalidCallStateError
check_call_state = libneuro.check_call_state


def main():
    # Создаем звонок
    nn.call(msisdn='1234567890', entry_point=entry_point)


def entry_point():
    try:
        start_main()
    except InvalidCallStateError as e:
        nn.log('Звонок завершён', str(e))
    except Exception as e:
        nn.log('Произошла ошибка', str(e))


@check_call_state(nv)
def start_main():
    # Начинаем диалог
    nv.say(PROMPTS['start_main'])

    # Спрашиваем, что хочет посмотреть абонент
    with nv.listen(entities=['movie', 'series']) as result:
        movie = result.entity('movie')
        series = result.entity('series')

        if movie:
            handle_movie_search()
        elif series:
            handle_tv_series_search()
        else:
            nv.say(PROMPTS['unknown_command'])
            end_call()


def handle_movie_search():
    """Обработка запроса фильма."""
    nv.say(PROMPTS['ask_movie_details'])

    # Получаем ответ абонента
    with nv.listen(entities=['genres', 'year', 'rating']) as result:
        genre = result.entity('genres')
        year = result.entity('year')
        rating = result.entity('rating')

        movies = []
        if genre:
            movies = search_movies_by_genre(genre)
        elif year:
            movies = search_movies_by_year(year)
        elif rating:
            movies = search_movies_by_rating(rating)

        if movies:
            nv.say(f"Я нашёл фильмы: {', '.join(movies)}")
        else:
            nv.say(PROMPTS['no_movies_found'])

        end_call()


def handle_tv_series_search():
    """Обработка запроса сериала."""
    nv.say(PROMPTS['ask_tv_series_details'])

    # Получаем ответ абонента
    with nv.listen(entities=['genres', 'year']) as result:
        genre = result.entity('genres')
        year = result.entity('year')

        series = []
        if genre:
            series = search_tv_series_by_genre(genre)
        elif year:
            series = search_tv_series_by_year(year)

        if series:
            nv.say(f"Я нашёл сериалы: {', '.join(series)}")
        else:
            nv.say(PROMPTS['no_series_found'])

        end_call()


def search_movies_by_genre(genre):
    """Поиск фильмов по жанру через API Кинопоиск."""
    token = STORAGE.get('X-API-KEY')
    url = "https://api.kinopoisk.dev/v1.4/movie"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"genres.name": genre}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return [movie['name'] for movie in data.get('docs', [])]
    except Exception as e:
        nn.log(f"Ошибка при вызове API Кинопоиск: {str(e)}")
        return []


def search_movies_by_year(year):
    """Поиск фильмов по году через API Кинопоиск."""
    token = STORAGE.get('X-API-KEY')
    url = "https://api.kinopoisk.dev/v1.4/movie"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"year": year}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return [movie['name'] for movie in data.get('docs', [])]
    except Exception as e:
        nn.log(f"Ошибка при вызове API Кинопоиск: {str(e)}")
        return []


def search_movies_by_rating(rating):
    """Поиск фильмов по рейтингу через API Кинопоиск."""
    token = STORAGE.get('X-API-KEY')
    url = "https://api.kinopoisk.dev/v1.4/movie"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"rating.kinopoisk": rating}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return [movie['name'] for movie in data.get('docs', [])]
    except Exception as e:
        nn.log(f"Ошибка при вызове API Кинопоиск: {str(e)}")
        return []


def search_tv_series_by_genre(genre):
    """Поиск сериалов по жанру через API Кинопоиск."""
    token = STORAGE.get('X-API-KEY')
    url = "https://api.kinopoisk.dev/v1.4/tv-series"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"genres.name": genre}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return [series['name'] for series in data.get('docs', [])]
    except Exception as e:
        nn.log(f"Ошибка при вызове API Кинопоиск: {str(e)}")
        return []


def search_tv_series_by_year(year):
    """Поиск сериалов по году через API Кинопоиск."""
    token = STORAGE.get('X-API-KEY')
    url = "https://api.kinopoisk.dev/v1.4/tv-series"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"year": year}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        return [series['name'] for series in data.get('docs', [])]
    except Exception as e:
        nn.log(f"Ошибка при вызове API Кинопоиск: {str(e)}")
        return []


def end_call():
    """Завершение звонка."""
    nv.say(PROMPTS['hangup_goodbye'])
    nv.hangup()


if __name__ == '__main__':
    main()
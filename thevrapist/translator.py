def translate(text, to_lang='pl'):
    from yandex_translate import YandexTranslate
    api_key = 'trnsl.1.1.20160319T135251Z.bcb346804d0b4a8c.0ccd878aac0d48e1c3d743055cf0119c6c813627'
    translator = YandexTranslate(api_key)
    response = translator.translate(text, to_lang)
    return response.get('text')[0]

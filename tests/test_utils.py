from cocoon import utils


def test_string_word_splitter():

    source = "Render_Scene_acescg.0101.exr"
    result = utils.split_at_words(source, split_camel_case=False)
    assert result == ["Render", "Scene", "acescg", "0101", "exr"]

    source = "mytextureAcescg-base.1001"
    result = utils.split_at_words(source, split_camel_case=False)
    assert result == ["mytextureAcescg", "base", "1001"]

    source = "__image..foo-bar"
    result = utils.split_at_words(source, split_camel_case=False)
    assert result == ["image", "foo", "bar"]

    source = "5D Mark II - Spac-o-ween - XS - 001"
    result = utils.split_at_words(source, split_camel_case=False)
    assert result == ["5D", "Mark", "II", "Spac", "o", "ween", "XS", "001"]

    source = "A009C002_190210_R0EI_Alexa_LogCWideGamut"
    result = utils.split_at_words(source, split_camel_case=False)
    assert result == ["A009C002", "190210", "R0EI", "Alexa", "LogCWideGamut"]

    # split_camel_case=True

    source = "Render_Scene_acescg.0101.exr"
    result = utils.split_at_words(source, split_camel_case=True)
    assert result == ["Render", "Scene", "acescg", "0101", "exr"]

    source = "mytextureAcescg-base.1001"
    result = utils.split_at_words(source, split_camel_case=True)
    assert result == ["mytexture", "Acescg", "base", "1001"]

    source = "__image..foo-bar"
    result = utils.split_at_words(source, split_camel_case=True)
    assert result == ["image", "foo", "bar"]

    source = "5D Mark II - Spac-o-ween - XS - 001"
    result = utils.split_at_words(source, split_camel_case=True)
    assert result == ["5D", "Mark", "II", "Spac", "o", "ween", "XS", "001"]

    source = "A009C002_190210_R0EI_Alexa_LogCWideGamut"
    result = utils.split_at_words(source, split_camel_case=True)
    assert result == [
        "A009C002",
        "190210",
        "R0EI",
        "Alexa",
        "Log",
        "C",
        "Wide",
        "Gamut",
    ]

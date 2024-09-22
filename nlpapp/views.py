from django.http import JsonResponse
import django.views.decorators.csrf
import json
import spacy

parse = spacy.load('en_core_web_sm')


def __create_dict_from_doc(parsed_text):
    return {
        pos: [
            {'lemma': token.text, 'start': token.idx, 'end': token.idx + len(token.text)}
            for token in parsed_text if token.pos_ == pos
        ]
        for pos in {token.pos_ for token in parsed_text}
    }


def __parse_input_into_dict(input_text: str):
    return __create_dict_from_doc(parse(input_text))


def __parse_and_get_response(input_text: str):
    return JsonResponse(__parse_input_into_dict(input_text), status=200) \
        if isinstance(input_text, str) \
        else JsonResponse(
            {'error': f'Invalid request format {input_text} should be a string, not a {type(input_text)}'}, status=400) \
            if input_text != -1 \
            else JsonResponse({'error': 'No text provided'}, status=400)


@django.views.decorators.csrf.csrf_exempt
def process_text(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    try:
        return __parse_and_get_response(json.loads(request.body.decode('utf-8')).get('text', -1))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

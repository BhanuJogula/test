from app.clients.bifrost.validators.base import TokenSubject, ValidationResult
from app.context import Context
from app.exception import AppException
from app.nf_token import Token, UnknownKeyAppException
from ddtrace import tracer

import jwt

@tracer.wrap()
async def validate(token, context : Context = None) -> ValidationResult:
    """Make sure the authenticated user has access to the requested target resource.

    Args:
        token(str): token string that was used to authenticate the API request

    Returns:
        (ValidationResult): object representing the results of the validation check
    """

    exception = None

    try:
        token_data = Token.decode(token)
        token_subject = TokenSubject.parse(token_data)
        token_data['brand'] = token_subject.brand
        token_data['platform'] = token_subject.platform

        if context:
            context.set('brand', token_subject.brand)
            context.set('platform', token_subject.platform)
            context.set('debug.target.raw_subject', token_data['sub'])
            context.set('http.details.authorization', token_data)

    except UnknownKeyAppException as e:
        exception = e
    #except jwt.ExpiredSignatureError:
    #    exception = AppException('', event='Auth.Token.Expired', status_code=401, customer_message='token expired')
    except Exception as e:
        exception = AppException('', event='Auth.Token.Decode', status_code=401, exception=e)
    finally:
        if exception:
            if context:
                decoded = Token.decode_unverified(token)
                if not decoded:
                    decoded = token
                context.set('http.details.authorization', decoded)
            raise exception

    try:
        result =  ValidationResult(
                    True, 
                    token_data, message = ""
                )

        if context:
            context.set('auth.is_valid', result.is_valid)
        return result

    except Exception as e:
        if context:
            context.set('auth.is_valid', False)
        raise AppException('', event='Auth.Error', status_code=401, exception=e)



from datetime import datetime

from yaki import HttpViewFunc, HttpRequest, HttpResponse


async def logging_middleware(view_func: HttpViewFunc,
                             request: HttpRequest) -> HttpResponse:
    print(request.path)

    return await view_func(request)


async def timing_middleware(view_func: HttpViewFunc,
                            request: HttpRequest) -> HttpResponse:
    start = datetime.now()

    result = await view_func(request)

    end = datetime.now()

    print(f"took {end - start}")

    return result

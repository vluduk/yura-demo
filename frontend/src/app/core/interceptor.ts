import { HttpHandlerFn, HttpInterceptorFn, HttpRequest } from "@angular/common/http";

export const Interceptor: HttpInterceptorFn = (request: HttpRequest<any>, next: HttpHandlerFn) => {
    let newRequest: HttpRequest<any> = request;

    return next(newRequest);
};

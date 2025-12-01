// ToastService disabled — kept to avoid breaking imports while feature is removed.
import { Injectable } from "@angular/core";

@Injectable({ providedIn: 'root' })
export class ToastService {
    success(_message: string) {
        // noop
    }
    error(_message: string) {
        // noop
    }
    show(_message: string) {
        // noop
    }
    dismiss(_id: string) {
        // noop
    }
}

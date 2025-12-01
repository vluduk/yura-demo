import { Injectable, signal, WritableSignal } from "@angular/core";

@Injectable({
    providedIn: "root",
})
export class CabinetPopupService {
    public readonly isVisible: WritableSignal<boolean> = signal<boolean>(false);

    public showCabinetPopup(): void {
        this.isVisible.set(true);
    }

    public hideCabinetPopup(): void {
        this.isVisible.set(false);
    }
}

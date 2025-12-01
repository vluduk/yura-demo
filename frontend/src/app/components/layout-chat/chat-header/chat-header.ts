import { Component, inject } from "@angular/core";
import { CabinetPopupService } from "@shared/services/cabinetPopup.service";
import { Link } from "@shared/components/link/link";

@Component({
    selector: "chat-header",
    imports: [Link],
    templateUrl: "./chat-header.html",
    styleUrl: "./chat-header.css",
})
export class ChatHeader {
    private readonly cabinetPopupService: CabinetPopupService = inject(CabinetPopupService);

    protected showCabinet(): void {
        this.cabinetPopupService.showCabinetPopup();
    }
}

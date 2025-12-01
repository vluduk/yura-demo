import { Component, inject, OnInit, Signal, signal, WritableSignal } from "@angular/core";
import { CabinetPopupService } from "@shared/services/cabinetPopup.service";
import { Account } from "./account/account";
import { Settings } from "./settings/settings";
import { Title } from "@shared/components/title/title";

type CabinetTab = {
    label: string;
    id: string;
};

@Component({
    selector: "cabinet-popup",
    imports: [Account, Settings, Title],
    templateUrl: "./cabinet.html",
    styleUrl: "./cabinet.css",
})
export class CabinetPopup implements OnInit {
    protected isVisible: Signal<boolean> = signal<boolean>(false);

    protected readonly tabs: WritableSignal<CabinetTab[]> = signal<CabinetTab[]>([]);
    protected readonly activeTab: WritableSignal<CabinetTab | null> = signal<CabinetTab | null>(null);

    private readonly cabinetPopupService: CabinetPopupService = inject(CabinetPopupService);

    ngOnInit(): void {
        this.isVisible = this.cabinetPopupService.isVisible;

        this.tabs.set([
            { label: "Акаунт", id: "account" },
            { label: "Налаштування", id: "settings" },
        ]);

        this.activeTab.set(this.tabs()[0]);
    }

    protected hideCabinet(): void {
        this.cabinetPopupService.hideCabinetPopup();
    }

    protected setActiveTab(tab: CabinetTab): void {
        this.activeTab.set(tab);
    }
}

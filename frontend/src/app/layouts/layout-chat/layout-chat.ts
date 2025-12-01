import { Component } from "@angular/core";
import { RouterOutlet } from "@angular/router";
import { ChatSidebar } from "@components/layout-chat/chat-sidebar/chat-sidebar";
import { ChatHeader } from "@components/layout-chat/chat-header/chat-header";
import { ChatSearchPopup } from "@components/layout-chat/chat-search-popup/chat-search-popup";
import { CabinetPopup } from "@components/cabinet/cabinet";

@Component({
    selector: "app-layout-chat",
    imports: [RouterOutlet, ChatSidebar, ChatHeader, ChatSearchPopup, CabinetPopup],
    templateUrl: "./layout-chat.html",
    styleUrl: "./layout-chat.css",
})
export class LayoutChat {}

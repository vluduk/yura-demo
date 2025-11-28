import { Component } from "@angular/core";
import { RouterOutlet } from "@angular/router";
import { ChatSidebar } from "@components/layout-chat/chat-sidebar/chat-sidebar";
import { ChatHeader } from "@components/layout-chat/chat-header/chat-header";

@Component({
    selector: "app-layout-chat",
    imports: [RouterOutlet, ChatSidebar, ChatHeader],
    templateUrl: "./layout-chat.html",
    styleUrl: "./layout-chat.css",
})
export class LayoutChat {}

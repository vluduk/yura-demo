import { Component } from "@angular/core";
import { RouterOutlet } from "@angular/router";
import { ChatSidebar } from "@components/chat-sidebar/chat-sidebar";

@Component({
    selector: "app-layout-chat",
    imports: [RouterOutlet, ChatSidebar],
    templateUrl: "./layout-chat.html",
    styleUrl: "./layout-chat.css",
})
export class LayoutChat {}

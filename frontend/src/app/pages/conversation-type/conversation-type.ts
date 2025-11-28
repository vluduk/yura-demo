import { Component } from "@angular/core";
import { Title } from "@shared/components/title/title";
import { Button } from "@shared/components/button/button";

@Component({
    selector: "app-conversation-type",
    imports: [Title, Button],
    templateUrl: "./conversation-type.html",
    styleUrl: "./conversation-type.css",
})
export class ConversationType {}

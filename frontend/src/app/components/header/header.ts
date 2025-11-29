import { Component } from "@angular/core";
import { RouterLink } from "@angular/router";
import { Button } from "@shared/components/button/button";
import { Link } from "@shared/components/link/link";
import { Logo } from "@shared/components/logo/logo";

@Component({
    selector: "app-header",
    imports: [Logo, Link, Button, RouterLink],
    templateUrl: "./header.html",
    styleUrl: "./header.css",
})
export class Header {}

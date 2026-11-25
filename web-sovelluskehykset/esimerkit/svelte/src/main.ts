import { mount } from "svelte";
import "../../yhteinen/tyyli.css";
import Sovellus from "./Sovellus.svelte";

mount(Sovellus, { target: document.getElementById("juuri")! });
